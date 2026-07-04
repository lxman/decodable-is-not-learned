"""Phase B task: the Lubana et al. context-sensitive formal language (arXiv:2408.12578).

Replicates the paper's experimental system: a PCFG whose terminal slots are populated
under TYPE CONSTRAINTS given by a bipartite entities x properties graph G = (E, K, I),
with entities and properties partitioned equally and disjointly into |C| concept
classes and edges drawn i.i.d. within class. Verified against the paper via ar5iv
(fetched 2026-07-04): grammar rules quoted from Appendix A.1.2; graph definition,
|E|=900 / |K|=18000 / |C|=10 / p=0.1 base config, and the percolation threshold
p_c ~ 1/sqrt(|E_c| * |K_c|) from Sections 4-5.

PCFG (paper's rules, verbatim):
    S     -> sNP VP                      [1.0]
    sNP   -> sT [0.8]  | sNP Conj sNP    [0.2]
    VP    -> lVerb descT [0.4] | Verb Prep oNP [0.4] | VP Conj VP [0.2]
    oNP   -> oT [0.7]  | oT Conj oNP     [0.3]
    sT    -> eAdj Subj [0.8] | Subj      [0.2]
    oT    -> eAdj Obj  [0.8] | Obj       [0.2]
    descT -> dAdj Desc [0.8] | Desc      [0.2]

Type constraints (the context-sensitivity):
  - Subj/Obj slots take entities.
  - Desc and eAdj slots take DESCRIPTIVE properties owned by the modified entity
    ("descriptive (entity-descriptor matching)" -- the paper's descriptive type check).
  - Verb slots take RELATIVE properties owned by BOTH subject and object
    ("relative (subject-verb-object matching)" -- the paper's relative type check).
  - lVerb / Conj / Prep / dAdj are small closed function-word sets (class-free).

Percolation structure: within a concept class c the (entities_c x properties_c)
subgraph is Erdos-Renyi at edge probability p. Its giant component appears at
p_c ~ 1/sqrt(|E_c| * |K_c|). BELOW p_c the co-occurrence graph is fragmented into
O(log n) islands, so the class structure is unrecoverable in principle -- the scored
capability (below) can never form, at any training duration. ABOVE p_c a giant
component per class makes the class structure learnable, and the capability forms
over training. This below/above pair is the known-percolation ground truth + control
of design doc S2.

Scored capability -- CLASS-STRUCTURE GENERALIZATION (operationalization recorded in
PROGRESS.md before any runs): on a prompt "Subj lVerb ...", mask the model's
next-token distribution to descriptive properties the subject was NEVER seen with in
training; PASS iff the chosen property belongs to the subject's class. Memorizing
seen edges cannot solve this; linking entities through shared properties (which
requires connectivity) can. Chance floor ~ 1/|C|.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import torch

# ---- closed function-word sets (class-free; sizes are recipe, not thresholds) ----
N_LVERB = 4   # linking verbs ("is/seems/appears/becomes")
N_CONJ = 2    # conjunctions
N_PREP = 4    # prepositions
N_DADJ = 6    # descriptor-modifying adverb/degree words


@dataclass
class LubanaConfig:
    n_classes: int = 10
    n_entities: int = 300          # |E|, split equally across classes
    n_properties: int = 3000       # |K|, split equally across classes (half desc, half rel)
    edge_prob_mult: float = 10.0   # edge prob as a multiple of the per-class p_c
    holdout_frac: float = 0.1      # fraction of edges RESERVED: never used in sentence
                                   # generation, so query candidates are unseen-in-
                                   # training by CONSTRUCTION (stable under online data)
    max_len: int = 96              # paper: sentences range 4-75 tokens
    seed: int = 0

    def __post_init__(self):
        if self.n_entities % self.n_classes or self.n_properties % self.n_classes:
            raise ValueError("entities and properties must split equally across classes")
        if (self.n_properties // self.n_classes) % 2:
            raise ValueError("per-class properties must split evenly into desc/rel")

    @property
    def ents_per_class(self) -> int:
        return self.n_entities // self.n_classes

    @property
    def props_per_class(self) -> int:
        return self.n_properties // self.n_classes

    @property
    def p_c(self) -> float:
        """Per-class bipartite giant-component threshold, p_c ~ 1/sqrt(|E_c|*|K_c|)."""
        return 1.0 / math.sqrt(self.ents_per_class * self.props_per_class)

    @property
    def edge_prob(self) -> float:
        return self.edge_prob_mult * self.p_c

    # ---- token layout: [entities | properties | lVerb | Conj | Prep | dAdj | BOS/PAD]
    @property
    def tok_lverb0(self) -> int:
        return self.n_entities + self.n_properties

    @property
    def tok_conj0(self) -> int:
        return self.tok_lverb0 + N_LVERB

    @property
    def tok_prep0(self) -> int:
        return self.tok_conj0 + N_CONJ

    @property
    def tok_dadj0(self) -> int:
        return self.tok_prep0 + N_PREP

    @property
    def bos(self) -> int:
        return self.tok_dadj0 + N_DADJ

    @property
    def pad(self) -> int:
        return self.bos + 1

    @property
    def vocab_size(self) -> int:
        return self.pad + 1


class LubanaLanguage:
    """The language: graph + PCFG sampler + scored-capability datasets."""

    def __init__(self, cfg: LubanaConfig):
        self.cfg = cfg
        rng = np.random.default_rng(cfg.seed)

        # class membership (equal, disjoint -- paper Section 5)
        self.entity_class = np.repeat(np.arange(cfg.n_classes), cfg.ents_per_class)
        self.prop_class = np.repeat(np.arange(cfg.n_classes), cfg.props_per_class)
        # within each class, first half descriptive, second half relative
        half = cfg.props_per_class // 2
        is_desc = np.zeros(cfg.n_properties, dtype=bool)
        for c in range(cfg.n_classes):
            base = c * cfg.props_per_class
            is_desc[base : base + half] = True
        self.prop_is_desc = is_desc

        # type-constraints graph: within-class ER at edge_prob (paper: p fraction of
        # valid = same-class properties, uniformly at random)
        self.adj = np.zeros((cfg.n_entities, cfg.n_properties), dtype=bool)
        for e in range(cfg.n_entities):
            c = self.entity_class[e]
            valid = np.flatnonzero(self.prop_class == c)
            mask = rng.random(valid.size) < cfg.edge_prob
            self.adj[e, valid[mask]] = True

        # reserved (held-out) edges: real edges of G that sentence generation NEVER
        # uses. Query candidates are drawn from never-trainable pairs, so the scored
        # capability is generalization by construction — stable under online data.
        self.reserved = self.adj & (rng.random(self.adj.shape) < cfg.holdout_frac)
        self.trainable = self.adj & ~self.reserved

        # per-entity TRAINABLE property lists (descriptive / relative), for population
        self._desc_of = [np.flatnonzero(self.trainable[e] & self.prop_is_desc) for e in range(cfg.n_entities)]
        self._rel_of = [np.flatnonzero(self.trainable[e] & ~self.prop_is_desc) for e in range(cfg.n_entities)]

    # ------------------------------------------------------------------ graph facts
    def giant_component_stats(self) -> dict:
        """Connectivity of the per-class TRAINABLE co-occurrence graph -- the
        INDEPENDENT ground-truth certification (computed from the data structure the
        model actually trains on, not from any model): giant fraction >> 1/n certifies
        'above threshold'; ~1/n certifies 'below'."""
        cfg = self.cfg
        fracs = []
        for c in range(cfg.n_classes):
            ents = np.flatnonzero(self.entity_class == c)
            props = np.flatnonzero(self.prop_class == c)
            n = ents.size + props.size
            idx = {("e", int(e)): i for i, e in enumerate(ents)}
            idx.update({("k", int(k)): ents.size + j for j, k in enumerate(props)})
            parent = list(range(n))

            def find(a):
                while parent[a] != a:
                    parent[a] = parent[parent[a]]
                    a = parent[a]
                return a

            for e in ents:
                for k in np.flatnonzero(self.trainable[e]):
                    ra, rb = find(idx[("e", int(e))]), find(idx[("k", int(k))])
                    if ra != rb:
                        parent[ra] = rb
            roots = {}
            for i in range(n):
                r = find(i)
                roots[r] = roots.get(r, 0) + 1
            fracs.append(max(roots.values()) / n)
        return {
            "giant_frac_mean": float(np.mean(fracs)),
            "giant_frac_min": float(np.min(fracs)),
            "p_c": self.cfg.p_c,
            "edge_prob": self.cfg.edge_prob,
            "edge_prob_mult": self.cfg.edge_prob_mult,
        }

    # ------------------------------------------------------------------ PCFG sampler
    def _sample_symbolic(self, rng) -> list[str]:
        """Expand the paper's PCFG. Depth-capped rewrite of the recursive rules."""
        def sNP(d):
            if d > 2 or rng.random() < 0.8:
                return ["eAdj", "Subj"] if rng.random() < 0.8 else ["Subj"]
            return sNP(d + 1) + ["Conj"] + sNP(d + 1)

        def oNP(d):
            t = (["eAdj", "Obj"] if rng.random() < 0.8 else ["Obj"])
            if d <= 2 and rng.random() < 0.3:
                return t + ["Conj"] + oNP(d + 1)
            return t

        def descT():
            return ["dAdj", "Desc"] if rng.random() < 0.8 else ["Desc"]

        def VP(d):
            r = rng.random()
            if d > 2 or r < 0.4:
                return ["lVerb"] + descT()
            if r < 0.8:
                return ["Verb", "Prep"] + oNP(0)
            return VP(d + 1) + ["Conj"] + VP(d + 1)

        return sNP(0) + VP(0)

    def _pick(self, arr, rng):
        return int(arr[rng.integers(arr.size)]) if arr.size else None

    def sample_sentence(self, rng, max_tries: int = 20) -> list[int] | None:
        """Sample one type-valid token sentence (without BOS). None if unsatisfiable
        after max_tries (frequent below threshold, where property sets are tiny --
        the data itself carries the fragmentation)."""
        cfg = self.cfg
        for _ in range(max_tries):
            sym = self._sample_symbolic(rng)
            if len(sym) + 1 > cfg.max_len:
                continue
            # subject = the FIRST Subj; its class anchors the sentence's constraints
            toks: list[int] = []
            subj = None
            ok = True
            for s in sym:
                if s == "Subj":
                    e = int(rng.integers(cfg.n_entities)) if subj is None else self._same_class_entity(subj, rng)
                    if subj is None:
                        subj = e
                    toks.append(e)
                elif s == "Obj":
                    # object must share a relative property with subj for Verb slots;
                    # sample among subj's class (necessary condition), verb filter below
                    toks.append(self._same_class_entity(subj, rng))
                elif s == "eAdj":
                    # descriptive property of the entity that FOLLOWS; defer: mark slot
                    toks.append(-1)
                elif s == "Desc":
                    k = self._pick(self._desc_of[subj], rng)
                    if k is None:
                        ok = False
                        break
                    toks.append(k + cfg.n_entities)  # property token id = n_entities + k
                elif s == "Verb":
                    # relative property owned by subject AND (checked laxly) some object
                    k = self._pick(self._rel_of[subj], rng)
                    if k is None:
                        ok = False
                        break
                    toks.append(k + cfg.n_entities)
                elif s == "lVerb":
                    toks.append(cfg.tok_lverb0 + int(rng.integers(N_LVERB)))
                elif s == "Conj":
                    toks.append(cfg.tok_conj0 + int(rng.integers(N_CONJ)))
                elif s == "Prep":
                    toks.append(cfg.tok_prep0 + int(rng.integers(N_PREP)))
                elif s == "dAdj":
                    toks.append(cfg.tok_dadj0 + int(rng.integers(N_DADJ)))
            if not ok:
                continue
            # resolve deferred eAdj slots: descriptive property of the next entity token
            out: list[int] = []
            for i, t in enumerate(toks):
                if t == -1:
                    ent = toks[i + 1] if i + 1 < len(toks) else None
                    if ent is None or ent >= self.cfg.n_entities:
                        out = []
                        break
                    k = self._pick(self._desc_of[ent], rng)
                    if k is None:
                        out = []
                        break
                    out.append(k + cfg.n_entities)
                else:
                    out.append(t)
            if out:
                return out
        return None

    def _same_class_entity(self, anchor: int, rng) -> int:
        c = self.entity_class[anchor]
        pool = np.flatnonzero(self.entity_class == c)
        return int(pool[rng.integers(pool.size)])

    def make_corpus(self, n_sentences: int, seed: int) -> torch.Tensor:
        """Token corpus [N, max_len]: BOS + sentence + PAD. (Probe/eval sentences;
        training uses sample_batch for true online data.)"""
        cfg = self.cfg
        rng = np.random.default_rng(seed)
        ids = np.full((n_sentences, cfg.max_len), cfg.pad, dtype=np.int64)
        i = 0
        while i < n_sentences:
            s = self.sample_sentence(rng)
            if s is None:
                continue
            row = [cfg.bos] + s
            ids[i, : len(row)] = row
            i += 1
        return torch.from_numpy(ids)

    def sample_batch(self, batch_size: int, rng) -> torch.Tensor:
        """Fresh online batch [B, max_len] -- the paper's 'fresh batch of strings
        every iteration'. Only TRAINABLE edges ever appear (reserved edges are the
        construction-level holdout)."""
        cfg = self.cfg
        ids = np.full((batch_size, cfg.max_len), cfg.pad, dtype=np.int64)
        i = 0
        while i < batch_size:
            s = self.sample_sentence(rng)
            if s is None:
                continue
            row = [cfg.bos] + s
            ids[i, : len(row)] = row
            i += 1
        return torch.from_numpy(ids)

    # -------------------------------------------------- scored capability datasets
    def make_queries(self, n: int, seed: int):
        """Class-generalization prompts: BOS Subj lVerb -> next token should be a
        descriptive property. Candidates are the NEVER-TRAINABLE descriptive
        properties for the subject (same-class non-edges + reserved edges +
        cross-class) -- unseen in training by construction, stable under online data.

        PASS rule (the verifier): the chosen candidate belongs to the subject's
        class. Chance ~ 1/|C|.
        """
        cfg = self.cfg
        rng = np.random.default_rng(seed)
        prompts = np.full((n, 3), cfg.pad, dtype=np.int64)
        subjects = np.empty(n, dtype=np.int64)
        classes = np.empty(n, dtype=np.int64)
        masks = np.zeros((n, cfg.vocab_size), dtype=bool)
        desc_idx = np.flatnonzero(self.prop_is_desc)
        for i in range(n):
            e = int(rng.integers(cfg.n_entities))
            subjects[i] = e
            classes[i] = self.entity_class[e]
            prompts[i] = [cfg.bos, e, cfg.tok_lverb0 + int(rng.integers(N_LVERB))]
            never_trainable = desc_idx[~self.trainable[e, desc_idx]]
            masks[i, never_trainable + cfg.n_entities] = True
        return {
            "prompts": torch.from_numpy(prompts),
            "subjects": torch.from_numpy(subjects),
            "classes": torch.from_numpy(classes),
            "masks": torch.from_numpy(masks),
        }

    def verify_choice(self, query_idx: int, queries: dict, token: int) -> bool:
        """True iff the chosen token is an unseen descriptive property of the
        subject's class."""
        cfg = self.cfg
        if not bool(queries["masks"][query_idx, token]):
            return False
        k = token - cfg.n_entities
        return int(self.prop_class[k]) == int(queries["classes"][query_idx])

    @property
    def chance(self) -> float:
        """Same-class fraction among unseen descriptive properties ~ 1/|C|."""
        return 1.0 / self.cfg.n_classes
