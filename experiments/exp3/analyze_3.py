"""Frozen analysis for Experiment 3 (design §5, §6): elicitation — is the
dissociated information in the output distribution?

3b certified signature 1 on a real model: the reversal answer's first
character is linearly decodable at margins .6263/.7725 (rev_string7) and
.5731/.6749 (reverse_string) from the same residual streams whose greedy
emission sits at floor. This module adjudicates signature 2 on the same
cells, with two preregistered instruments: first-character MASS (the
distribution itself, read exactly through the unembedding, depth-2
whitespace expansion) and full-string REACHABILITY (verified exact-match
successes among k seeded ancestral draws at T = 1.0, no truncation).
Four worlds are named in advance — ELICITABLE / BULK-ONLY / TAIL-ONLY /
WALL — adjudicated per reversal rung × probe size; any mixture is
PARTIAL with the per-cell table as headline.

THE PRIMARY MASS STATISTIC IS WITHIN-DISTRIBUTION (design §2.2, §5): per
item, s_i = m_i(y_i) − Σ_{c≠y_i} w̃_c m_i(c), exact one-sided sign test
across items. The twin-paired version was KILLED at design time by the
dumbest-baseline analysis — a format-only emitter beats an untrained
twin ~500/0 with zero reversal knowledge — and the untrained twin
demotes to a contamination gate. A format-only emitter and a
letter-uniform guesser both sit at θ = .5 under this statistic by
construction, because correct letters are reversals of random strings.

BUILD-SESSION STATE. This module grows through the build session (doc
Open items 1–8) and freezes, with its fixture suite and its own loaders,
at tag `exp3-preregistered` after a third session that opens
adversarially. No mass or sampling quantity is computed for any real
cell or model before that tag. Four readings of §5/§6 wording were
declared in PROGRESS.md before implementation (bracket ends, gate-3
trigger scope, all-ties cells, the stream map) for the freeze to ratify
or amend.

LINEAGE. first_char scoring, the CP helpers, the floors pin with its
recompute-assert, and the loader discipline (every input verdict() takes
is either a committed record verified present with a defined value, or
produced by a frozen loader that hard-errors on anything malformed) are
3b's, ported and re-fixtured here. Gate 2's byte referents are 3b's own
16 probe-size greedy cells; item files, prompts, and shots are 2c's
committed ones verbatim (reverse_string from 2b's tree).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scipy.stats import beta, binom

# ------------------------------------------------------------ the matrix

PROBE_SIZES = ("410m", "1b")          # adjudication happens here only
EVAL_SIZES = ("2.8b", "6.9b", "12b")  # mass ladder: descriptive, never read
SIZES = PROBE_SIZES + EVAL_SIZES      # by any verdict branch (design §9)
MODES = ("trained", "untrained")
REVERSAL_RUNGS = ("rev_string7", "reverse_string")   # the claim
POSITIVE_CONTROL = "ctrl_copy"                        # gate 1
MATCHED_CONTROL = "clock24_d999"                      # agreement quadrant
RUNGS = REVERSAL_RUNGS + (POSITIVE_CONTROL, MATCHED_CONTROL)
RUNGS_2B = ("reverse_string",)        # the 2b survivor; its items live there

# mass cells: 4 rungs × (5 trained sizes + 2 untrained probe sizes) = 28
# sampling cells: 4 rungs × 2 probe sizes × 2 modes = 16
# gate-2 re-decode cells: the same 16 keys, greedy, byte-gated against 3b
MASS_CELLS = tuple((r, s, m) for r in RUNGS for m in MODES
                   for s in (SIZES if m == "trained" else PROBE_SIZES))
SAMPLING_CELLS = tuple((r, s, m) for r in RUNGS for s in PROBE_SIZES
                       for m in MODES)

ALPHA = 0.01
N_ADJ_TESTS = 4        # §5: Bonferroni across the 4 adjudicated reversal cells
N_COHERENCE_TESTS = 16  # §6.3: CP level Bonferroni across the sampling cells
BYTE_TOLERANCE = 2     # §6.2: >2 of 500 differing continuations fires (3b's own)
RESIDUAL_BRACKET_THRESHOLD = 0.01   # §5: bracket rule fires above this

SEEDS = (0, 1, 2, 3)   # §3: preregistered RNG streams; per-seed tallies kept
DRAWS_PER_SEED = {r: (64 if r in REVERSAL_RUNGS else 8) for r in RUNGS}
K_TOTAL = {r: len(SEEDS) * DRAWS_PER_SEED[r] for r in RUNGS}  # 256 / 32
SAMPLING_MAX_NEW_TOKENS = 12   # §5, flat for sampling (re-decode uses the
SAMPLING_TEMPERATURE = 1.0     # referent record's own committed cap)
SAMPLING_BATCH = 16
UNTRAINED_SEED = 0             # 2c's own twin seed, unchanged since

EXP3 = Path(__file__).resolve().parent
EXPERIMENTS = EXP3.parent

# results layout (PROGRESS.md, decided at build). Only these canonical
# subdirectory families are ever read back; verdict artifacts at
# results/ top level can never be re-ingested as data (3b's rule).
RESULTS = EXP3 / "results"
MASS_ROOT = RESULTS / "mass"
SAMPLING_ROOT = RESULTS / "sampling"
REDECODE_ROOT = RESULTS / "redecode"

# ----------------------------------------------------- committed referents
#
# Design §4: every input, a committed value, existing before any Exp 3
# code. The verdict reads nothing produced outside this list and the
# campaign's own cells.

GATE2_REFERENT_ROOT = EXPERIMENTS / "exp3b" / "results"

# 3a's committed floors — DESCRIPTIVE in exp3 (marginal context for the
# sampled first-char rate; no verdict branch reads them) but pinned and
# recompute-asserted exactly as 3b pinned them, so the descriptives are
# as trustworthy as the adjudicated numbers.
FLOORS_PATH = EXPERIMENTS / "exp3a" / "chance_floors.json"
FLOORS_SHA256 = "f299fa08314b138c5f741739c7de35e22c0b41e3c6be838505f6c6a22c1a5318"

MARGINS_PATH = EXPERIMENTS / "exp3b" / "probe_margins.json"
# The doc quotes these to 4dp (§3, §Predecessors); a margins file that
# rounds elsewhere is not the file the design was written against.
PROBE_MARGINS_DOC = {"rev_string7": {"410m": 0.6263, "1b": 0.7725},
                     "reverse_string": {"410m": 0.5731, "1b": 0.6749}}

ITEMS_2C = EXPERIMENTS / "exp2c" / "battery" / "items"
ITEMS_2B = EXPERIMENTS / "exp2b" / "battery" / "items"

# Gate-1 anchors (§4): ctrl_copy's committed record. Full-string argmax
# 480/500 and 490/500 at the probe sizes (2c inclusion); first-char
# 497/500 = .9940 at both (3b's closed verdict record) — the recompute
# target verify_referents scores with THIS module's first_char.
GATE1_INCLUSION_REFERENT = {"410m": 480, "1b": 490}
GATE1_FIRST_CHAR_REFERENT = {"410m": 497, "1b": 497}

TWIN_HASH_PATH = EXPERIMENTS / "exp3b" / "referent_check.json"


# ----------------------------------------------------------------- floors
# Exp 3a's chance_floors verbatim (via 3b), recompute-assert wrapper kept.

def chance_floors(eval_items) -> dict:
    """The three floors and their maximum, from the items alone.

    `copy_first` is the rate at which the input's first character already
    equals the answer's first character — what a model that echoes rather
    than reverses would score. For random strings it is ~1/26, but it is
    measured because a systematic generator could make it larger.
    """
    n = len(eval_items)
    if not n:
        raise ValueError("no eval items to compute a floor from")
    firsts = [str(it["answer"])[0].casefold() for it in eval_items]
    counts: dict[str, int] = {}
    for c in firsts:
        counts[c] = counts.get(c, 0) + 1
    marginal = max(counts.values()) / n

    copy_first, copy_whole = 0, 0
    for it, f in zip(eval_items, firsts):
        q = str(it["question"])
        if "'" in q:
            inp = q.split("'")[1]
            if inp and inp[0].casefold() == f:
                copy_first += 1
            if inp.casefold() == str(it["answer"]).casefold():
                copy_whole += 1
    copy_first /= n
    copy_whole /= n

    copy_is_the_task = copy_whole > 0.5

    vals = {"uniform": 1.0 / 26, "marginal": marginal, "copy_first": copy_first}
    eligible = {k: v for k, v in vals.items()
                if not (k == "copy_first" and copy_is_the_task)}
    src = max(eligible, key=lambda k: eligible[k])
    return {**vals, "copy_whole": copy_whole,
            "copy_is_the_task": copy_is_the_task,
            "primary": vals[src], "primary_source": src, "n_items": n}


def load_battery_items(rung: str, *, items_2c=None, items_2b=None) -> list:
    """Committed eval items for a rung, from the tree that owns it."""
    root = (items_2b if rung in RUNGS_2B else items_2c)
    root = Path(root) if root is not None else (
        ITEMS_2B if rung in RUNGS_2B else ITEMS_2C)
    p = root / f"{rung}.json"
    if not p.is_file():
        raise FileNotFoundError(f"no committed item file for {rung!r} at {p}")
    return json.loads(p.read_text())["eval_items"]


def load_floors(floors_path=FLOORS_PATH, *, expected_sha=FLOORS_SHA256,
                items_loader=load_battery_items) -> dict:
    """3a's committed floors: sha-pinned, then recomputed and asserted.

    Two failure modes, both fatal by design: the committed file differing
    from the pinned hash (the file moved under us), and the recompute from
    the committed items differing from the file (the items moved under the
    file). Either way the floors this experiment was designed against no
    longer exist, and nothing downstream is interpretable.
    """
    raw = Path(floors_path).read_bytes()
    got_sha = hashlib.sha256(raw).hexdigest()
    if got_sha != expected_sha:
        raise ValueError(
            f"floors file {floors_path} has sha256 {got_sha}, expected "
            f"{expected_sha} — the committed floors changed after the pin")
    committed = json.loads(raw)
    for rung in RUNGS:
        recomputed = json.loads(json.dumps(chance_floors(items_loader(rung))))
        if recomputed != committed.get(rung):
            raise ValueError(
                f"floors recompute mismatch for {rung!r}: items no longer "
                f"produce the committed floors — {recomputed} vs "
                f"{committed.get(rung)}")
    return committed


# ---------------------------------------------------------------- scoring
# 3b verbatim (itself 3a's, with the non-alphabetic fix its mutation
# testing forced). Applied to every sampled draw (§5 "sampled first-char
# rate") and to the gate-1 anchor recompute; never to a mass.

def first_char(continuation) -> str | None:
    """First non-whitespace character of the continuation, case-folded.

    An empty or whitespace-only continuation returns None and is scored
    INCORRECT rather than dropped: failing to emit anything is the
    behaviour under measurement, not missing data.

    Any non-whitespace character counts. An isalpha filter would zero
    the matched control by construction: clock24_d999's probe label is a
    DIGIT (3a's mutation testing found the original; the regression is
    pinned in this tree's fixtures too).
    """
    s = str(continuation).lstrip()
    if not s:
        return None
    return s[0].casefold()


def score_first_char(continuation, probe_label) -> bool:
    got = first_char(continuation)
    return bool(got is not None and got == str(probe_label)[0].casefold())


def score_cell(continuations, probe_labels) -> dict:
    if len(continuations) != len(probe_labels):
        raise ValueError(
            f"{len(continuations)} continuations against {len(probe_labels)} "
            f"labels — an item cannot be dropped from this metric")
    correct = sum(score_first_char(c, l)
                  for c, l in zip(continuations, probe_labels))
    return {"n": len(probe_labels), "correct": int(correct),
            "acc": correct / len(probe_labels)}


# ------------------------------------------------------------- CP helpers

def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact two-sided binomial CI (3b verbatim). Gate 3 calls it at
    level 1 − ALPHA/N_COHERENCE_TESTS; reporting uses .95."""
    alpha = 1.0 - level
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def cp_upper(k: int, n: int, level: float = 0.95) -> float:
    """Exact one-sided upper bound. Every zero ships as this bound
    (program rule since 1c): 0/128,000 at .95 is the doc's ≈2.3×10⁻⁵
    WALL statement, pooled form; the per-item-max form uses the same
    function at the item's own draw count."""
    if k == n:
        return 1.0
    return float(beta.ppf(level, k + 1, n - k))


# ---------------------------------------------------- referent loaders
#
# Frozen WITH the analysis (§11). Every one hard-errors on anything
# malformed or valueless — 3a's death class is refused at load, never
# discovered mid-verdict.

def load_gate2_referents(root=GATE2_REFERENT_ROOT) -> dict:
    """3b's 16 probe-size greedy cells: gate 2's byte referents (§4).

    Structural checks only — nothing here scores anything. Each record
    must carry 500 continuations, labels, and answers in agreement with
    its path and its own n_items, a nonempty items_sha256 (the §4 item-
    file pin exp3's loads are checked against), an integral
    max_new_tokens (the cap the re-decode must reuse), and the twin
    seed discipline (untrained_seed 0 on twins, None on trained).
    """
    out = {}
    base = Path(root)
    for rung in RUNGS:
        for size in PROBE_SIZES:
            for mode in MODES:
                p = base / f"{size}_{mode}" / f"{rung}.json"
                if not p.is_file():
                    raise FileNotFoundError(
                        f"no gate-2 byte referent for {rung}/{size}/{mode} "
                        f"at {p}")
                rec = json.loads(p.read_text())
                if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
                        (rung, size, mode):
                    raise ValueError(
                        f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
                        f"{rec.get('mode')}) disagree with its path")
                n = rec.get("n_items")
                for field in ("continuations", "probe_labels", "answers"):
                    v = rec.get(field)
                    if not isinstance(v, list) or len(v) != n:
                        raise ValueError(
                            f"{p}: {field} has "
                            f"{len(v) if isinstance(v, list) else v!r} "
                            f"entries against n_items {n}")
                sha = rec.get("items_sha256")
                if not isinstance(sha, str) or not sha:
                    raise ValueError(
                        f"{p} carries no items_sha256 — the item-file pin "
                        f"has no value there (3a's class, refused)")
                mnt = rec.get("max_new_tokens")
                if not isinstance(mnt, int) or mnt <= 0:
                    raise ValueError(f"{p}: max_new_tokens {mnt!r} is not a "
                                     f"usable generation cap")
                if rec.get("untrained_seed") != \
                        (UNTRAINED_SEED if mode == "untrained" else None):
                    raise ValueError(
                        f"{p}: untrained_seed {rec.get('untrained_seed')!r} "
                        f"violates the twin seed discipline for {mode}")
                out[(rung, size, mode)] = {
                    "continuations": [str(c) for c in rec["continuations"]],
                    "probe_labels": [str(l) for l in rec["probe_labels"]],
                    "answers": [str(x) for x in rec["answers"]],
                    "n": int(n),
                    "items_sha256": sha,
                    "max_new_tokens": int(mnt),
                    "model_sha": rec.get("model_sha"),
                }
    return out


def items_sha_referents(gate2_refs: dict) -> dict:
    """The §4 item-file pins, one per rung, from 3b's cell records.

    All four cells of a rung (2 sizes × 2 modes) must pin the same file;
    two different pins would leave no single referent for what exp3 must
    load, and that is a hard error, not a choice.
    """
    out: dict[str, str] = {}
    for (rung, _size, _mode), ref in sorted(gate2_refs.items()):
        sha = ref["items_sha256"]
        if rung in out and out[rung] != sha:
            raise ValueError(
                f"items_sha256 disagrees across {rung}'s cells: "
                f"{out[rung]} vs {sha} — no single item-file referent")
        out[rung] = sha
    missing = [r for r in RUNGS if r not in out]
    if missing:
        raise ValueError(f"no items_sha256 referent for {missing}")
    return out


def load_probe_margins(path=MARGINS_PATH) -> dict:
    """Per-size m3 probe margins (context, and the preregistered arbiter
    wherever sampling and probing disagree — forward-note, binding).
    Quoted per size, never pooled. Checked against the doc's own 4dp
    quotes: a drifted margins file is not the design's file."""
    d = json.loads(Path(path).read_text())
    out = {}
    for rung in REVERSAL_RUNGS:
        out[rung] = {}
        for size in PROBE_SIZES:
            v = float(d[rung][size]["mean"])
            if not 0.0 < v < 1.0:
                raise ValueError(f"probe margin {rung}/{size} = {v!r} is "
                                 f"not a margin")
            want = PROBE_MARGINS_DOC[rung][size]
            if round(v, 4) != want:
                raise ValueError(
                    f"probe margin {rung}/{size} rounds to {round(v, 4)}, "
                    f"but the design doc quotes {want} — this is not the "
                    f"margins file the design was written against")
            out[rung][size] = v
    return out


def load_twin_hash_referents(path=TWIN_HASH_PATH) -> dict:
    """3b's recorded seed-0 twin state hashes, one per probe size — what
    exp3's own construction check must reproduce (§4: 'construct at
    untrained_seed = 0, state-hash verified'). A missing hash is a
    valueless referent and is refused."""
    rec = json.loads(Path(path).read_text())
    out: dict[str, str] = {}
    for c in rec.get("checks", []):
        for size in PROBE_SIZES:
            if c.get("check") == f"untrained twin constructs {size} seed=0":
                h = c.get("state_sha256")
                if not isinstance(h, str) or not h:
                    raise ValueError(f"twin hash referent for {size} has no "
                                     f"value in {path}")
                out[size] = h
    missing = [s for s in PROBE_SIZES if s not in out]
    if missing:
        raise ValueError(f"no twin hash referent for {missing} in {path}")
    return out
