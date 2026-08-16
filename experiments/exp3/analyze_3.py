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

import gzip
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


# ------------------------------------------------------ the §5 statistic
#
# s_i = m_i(y_i) − Σ_{c≠y_i} w̃_c m_i(c): the item's correct-letter mass
# against the w̃-weighted competitor masses, w̃ the empirical answer-
# first-letter distribution over the rung's items, renormalized per item
# to exclude y_i. A format-only emitter (mass spread indifferently) and
# a letter-uniform guesser both land at θ = P(s_i > 0) = .5 by
# construction — the §2.2 kill test that demoted the untrained twin.

LETTERS = tuple("abcdefghijklmnopqrstuvwxyz")

# Sign-vs-tie resolution for s_i. Exact ties are real (all-zero masses;
# the format-only degenerate case cancels algebraically) but float
# summation leaves O(1e-16) dust on what is algebraically zero, and a
# dust-signed item would smuggle a sign into K. 1e-12 sits orders of
# magnitude above accumulated f64 roundoff on 26-term sums and orders
# below any mass difference fp32 logits can express, so nothing
# physical is ever eaten.
SIGN_TIE_EPS = 1e-12


def rung_sign_test(mass_items, answers, *, n_tests, alpha: float = ALPHA,
                   upper: bool = False) -> dict:
    """The exact one-sided sign test on s_i across a cell's items (§5).

    `upper=True` computes the bracket's upper end (reading 1):
    s_i_hi = (m_i(y_i) + r_i) − Σ w̃_c m_i(c) — the whole per-item
    residual credited to the correct letter, competitors held at their
    computed masses. Adjudication always reads the lower end.

    Reading 5 (letter support): w̃ and the competitor sum are defined
    over the empirical answer-first-character support, which must lie
    inside the stored a–z block. A rung whose support leaves a–z
    (clock24_d999's digit answers) records computable=False and can
    never be significant; hard-erroring on ADJUDICATED cells without
    computable support is the verdict tree's job.

    Reading 3 (all ties): n_eff = 0 → significant=False, p = 1.0,
    disclosed — a cell with no usable items argues nothing either way.
    """
    if len(mass_items) != len(answers):
        raise ValueError(f"{len(mass_items)} mass items against "
                         f"{len(answers)} answers")
    y = [str(ans)[0].casefold() for ans in answers]
    base = {"end": "upper" if upper else "lower", "n_tests": n_tests,
            "alpha": alpha}
    outside = sorted(set(y) - set(LETTERS))
    if outside:
        return {**base, "computable": False, "significant": False,
                "p": 1.0, "K": 0, "n_eff": 0, "n_ties": 0,
                "reason": f"answer first characters {outside} lie outside "
                          f"the stored a–z letter block, so the competitor "
                          f"sum has no computable value (reading 5)"}
    n = len(y)
    w = {c: 0.0 for c in sorted(set(y))}
    for c in y:
        w[c] += 1.0 / n
    if len(w) == 1:
        raise ValueError(
            f"every answer begins with {y[0]!r} (w = 1): excluding y_i "
            f"leaves nothing to renormalize w̃ over, and the statistic "
            f"does not exist on this rung")

    signs = []
    for it, yi in zip(mass_items, y):
        m_y = float(it["letters"][yi])
        if upper:
            m_y += float(it["residual"])
        denom = 1.0 - w[yi]
        comp = sum((w[c] / denom) * float(it["letters"][c])
                   for c in w if c != yi)
        signs.append(m_y - comp)

    K = sum(1 for s in signs if s > SIGN_TIE_EPS)
    n_ties = sum(1 for s in signs if abs(s) <= SIGN_TIE_EPS)
    n_eff = len(signs) - n_ties
    if n_eff == 0:
        return {**base, "computable": True, "significant": False,
                "p": 1.0, "K": 0, "n_eff": 0, "n_ties": n_ties}
    p = float(binom.sf(K - 1, n_eff, 0.5))
    return {**base, "computable": True,
            "significant": bool(p * n_tests < alpha),
            "p": p, "K": int(K), "n_eff": int(n_eff),
            "n_ties": int(n_ties)}


def cell_mass_bracket(mass_items) -> tuple[float, float]:
    """[mean label mass, mean(label mass + residual)] over the cell's
    items — gate 3's referent interval (readings 2 and 9). Reads
    label_mass, not the letter block, so the digit-label control
    carries a bracket too."""
    if not mass_items:
        raise ValueError("no mass items to bracket")
    n = len(mass_items)
    lo = sum(float(it["label_mass"]) for it in mass_items) / n
    hi = sum(float(it["label_mass"]) + float(it["residual"])
             for it in mass_items) / n
    return lo, hi


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


# ----------------------------------------------------- battery loaders
#
# The campaign's own cells, read back through frozen producers (§11)
# from the canonical subdirectories only. A file the preregistered
# battery does not name, sitting inside a canonical subdirectory, is a
# half-copied or wrong-tree directory and is refused, not skipped;
# anything malformed is a hard error before any gate (3a's class).

_MASS_SUM_TOL = 1e-3   # masses._SUM_TOL: fp32 logits softmaxed in f64


def load_verify():
    """2c's exact-match verify, resolved from the exp2c tree with
    run_cell's sys.path discipline (exp2c must win the `harness` name)
    and provenance-asserted: the fire recompute with any other tree's
    verify would not be the committed criterion."""
    import sys
    for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
    import harness
    got = Path(harness.__file__).resolve()
    if (EXPERIMENTS / "exp2c").resolve() not in got.parents:
        raise ImportError(
            f"harness resolved to {got}, which is not under the exp2c "
            f"tree — the fire recompute would use the wrong verify")
    return harness.verify


def _check_provenance(rec, p, rung, size, mode, *, want_dtype) -> None:
    """The provenance block every runner record carries, validated the
    same way for all three batteries. The dtype check makes the
    ledgered policy executable at load: a cell produced at the wrong
    precision is not this design's cell, whatever its numbers say."""
    if (rec.get("rung"), rec.get("size"), rec.get("mode")) != \
            (rung, size, mode):
        raise ValueError(
            f"{p} contents ({rec.get('rung')}/{rec.get('size')}/"
            f"{rec.get('mode')}) disagree with its path")
    n = rec.get("n_items")
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"{p}: n_items {n!r} is not a count")
    for field in ("probe_labels", "answers"):
        v = rec.get(field)
        if not isinstance(v, list) or len(v) != n:
            raise ValueError(
                f"{p}: {field} has "
                f"{len(v) if isinstance(v, list) else v!r} entries "
                f"against n_items {n}")
    sha = rec.get("items_sha256")
    if not isinstance(sha, str) or not sha:
        raise ValueError(f"{p} carries no items_sha256 — the item-file "
                         f"pin has no value there (3a's class, refused)")
    if rec.get("dtype") != want_dtype:
        raise ValueError(
            f"{p}: dtype {rec.get('dtype')!r} violates the ledgered "
            f"policy — this cell must be {want_dtype}")
    if rec.get("untrained_seed") != \
            (UNTRAINED_SEED if mode == "untrained" else None):
        raise ValueError(
            f"{p}: untrained_seed {rec.get('untrained_seed')!r} violates "
            f"the twin seed discipline for {mode}")


def _refuse_strays(base, want_dirs, want_names) -> None:
    base = Path(base)
    if not base.is_dir():
        return
    for d in sorted(base.iterdir()):
        if d.name.startswith("."):
            continue
        if d.is_file() or d.name not in want_dirs:
            raise ValueError(
                f"unexpected entry {d} inside a canonical battery "
                f"directory — this tree is not the preregistered battery")
        for f in sorted(d.iterdir()):
            if f.name.startswith("."):
                continue
            if f.name not in want_names:
                raise ValueError(
                    f"unexpected file {f} inside a canonical battery "
                    f"subdirectory — this tree is not the preregistered "
                    f"battery")


def load_mass_cells(root=EXP3) -> dict:
    """The 28 mass cells (§3), per-item records validated against
    masses.py's stored shape: exact a–z letter vector, non-negative
    buckets summing to at most 1, label_char equal to both the probe
    label's and the answer's first character (the statistic reads
    m(y_i) through it), label_mass equal to its letter/extra source,
    and the ledgered depth/dtype policy (12b's fp16 depth-1 exception,
    float32 depth-2 everywhere else)."""
    base = Path(root) / "results" / "mass"
    want_dirs = {f"{s}_{m}" for (_r, s, m) in MASS_CELLS}
    _refuse_strays(base, want_dirs, {f"{r}.json" for r in RUNGS})
    out = {}
    for (rung, size, mode) in MASS_CELLS:
        p = base / f"{size}_{mode}" / f"{rung}.json"
        if not p.is_file():
            raise FileNotFoundError(
                f"no mass cell for {rung}/{size}/{mode} at {p}")
        rec = json.loads(p.read_text())
        want_dtype = "float16" if size == "12b" else "float32"
        want_depth = 1 if size == "12b" else 2
        _check_provenance(rec, p, rung, size, mode, want_dtype=want_dtype)
        if rec.get("depth") != want_depth:
            raise ValueError(
                f"{p}: depth {rec.get('depth')!r} violates the ledgered "
                f"policy — this cell must be depth {want_depth}")
        items = rec.get("items")
        n = rec["n_items"]
        if not isinstance(items, list) or len(items) != n:
            raise ValueError(
                f"{p}: {len(items) if isinstance(items, list) else items!r} "
                f"items against n_items {n}")
        for i, it in enumerate(items):
            letters = it.get("letters")
            if not isinstance(letters, dict) or set(letters) != set(LETTERS):
                raise ValueError(
                    f"{p} item {i}: letter vector keys are not exactly "
                    f"a–z")
            extra = it.get("extra") or {}
            buckets = ([("residual", it.get("residual")),
                        ("terminal_mass", it.get("terminal_mass"))]
                       + [(f"letters[{c}]", v) for c, v in letters.items()]
                       + [(f"extra[{c}]", v) for c, v in extra.items()])
            for name, v in buckets:
                if not isinstance(v, (int, float)):
                    raise ValueError(
                        f"{p} item {i}: {name} = {v!r} is not a mass")
                if v < 0:
                    raise ValueError(
                        f"{p} item {i}: {name} carries negative "
                        f"probability {v}")
            total = (sum(letters.values()) + sum(extra.values())
                     + it["residual"] + it["terminal_mass"])
            if total > 1.0 + _MASS_SUM_TOL:
                raise ValueError(
                    f"{p} item {i}: buckets sum to {total} > 1 — these "
                    f"are not masses from one distribution")
            lc = it.get("label_char")
            want_label = str(rec["probe_labels"][i])[0].casefold()
            want_ans = str(rec["answers"][i])[0].casefold()
            if lc != want_label or lc != want_ans:
                raise ValueError(
                    f"{p} item {i}: label_char {lc!r} does not match the "
                    f"probe label's first character {want_label!r} and "
                    f"the answer's {want_ans!r} — the record cannot "
                    f"support m(y_i)")
            src = letters[lc] if lc in letters else extra.get(lc)
            if src is None or float(it.get("label_mass")) != float(src):
                raise ValueError(
                    f"{p} item {i}: label_mass {it.get('label_mass')!r} "
                    f"disagrees with its letter/extra source {src!r}")
            if it.get("depth") != want_depth:
                raise ValueError(
                    f"{p} item {i}: depth {it.get('depth')!r} against the "
                    f"cell's policy depth {want_depth}")
        out[(rung, size, mode)] = {
            "rung": rung, "size": size, "mode": mode, "n": n,
            "items": items,
            "probe_labels": [str(x) for x in rec["probe_labels"]],
            "answers": [str(x) for x in rec["answers"]],
            "items_sha256": rec["items_sha256"],
            "dtype": rec["dtype"], "depth": rec["depth"],
            "model_sha": rec.get("model_sha"),
        }
    return out


def _read_draw_rows(path, n_items, dps) -> list:
    """The analyzer's own raw-draws reader (its loaders are its own,
    §11): duplicate-refusing, coverage-checking, stream-complete."""
    rows, seen = [], set()
    with gzip.open(Path(path), "rt") as f:
        for line in f:
            row = json.loads(line)
            i = row.get("item")
            if i in seen:
                raise ValueError(f"duplicate item {i} in {path}")
            seen.add(i)
            draws = row.get("draws")
            if not isinstance(draws, dict) or \
                    set(draws) != {str(s) for s in SEEDS}:
                raise ValueError(
                    f"{path} item {i}: seed streams "
                    f"{sorted(draws) if isinstance(draws, dict) else draws!r} "
                    f"are not the preregistered seeds {list(SEEDS)}")
            for s in SEEDS:
                stream = draws[str(s)]
                if not isinstance(stream, list) or len(stream) != dps or \
                        not all(isinstance(d, str) for d in stream):
                    raise ValueError(
                        f"{path} item {i} seed {s}: stream of "
                        f"{len(stream) if isinstance(stream, list) else stream!r} "
                        f"draws against draws_per_seed {dps}")
            rows.append(row)
    if len(rows) != n_items or seen != set(range(n_items)):
        raise ValueError(
            f"{path}: {len(rows)} item rows covering {len(seen)} distinct "
            f"items against n_items {n_items}")
    return rows


def recompute_seed_tallies(rows, answers, labels, *, answer_type,
                           verify_fn) -> tuple[dict, list]:
    """Per-seed tallies and per-item full-string counts, recomputed
    from the raw draws with 2c's verify and 3b's first_char — the same
    functions the runner's convenience copies used, applied again."""
    out = {str(s): {"full_string": 0, "first_char": 0, "n_draws": 0}
           for s in SEEDS}
    per_item_full = [0] * len(answers)
    for row in rows:
        i = row["item"]
        for s in SEEDS:
            k = str(s)
            for d in row["draws"][k]:
                out[k]["n_draws"] += 1
                if verify_fn(d, answers[i], answer_type):
                    out[k]["full_string"] += 1
                    per_item_full[i] += 1
                if score_first_char(d, labels[i]):
                    out[k]["first_char"] += 1
    return out, per_item_full


def load_sampling_cells(root=EXP3, verify_fn=None) -> dict:
    """The 16 sampling cells (§3) with their raw draws. The stored
    per-seed tallies are convenience copies: the analyzer RECOMPUTES
    them from the raw draws and refuses any disagreement — a battery
    whose runner and analyzer no longer agree on what was drawn has no
    usable value anywhere (3a's class)."""
    if verify_fn is None:
        verify_fn = load_verify()
    base = Path(root) / "results" / "sampling"
    want_dirs = {f"{s}_{m}" for (_r, s, m) in SAMPLING_CELLS}
    want_names = ({f"{r}.json" for r in RUNGS}
                  | {f"{r}.draws.jsonl.gz" for r in RUNGS})
    _refuse_strays(base, want_dirs, want_names)
    out = {}
    for (rung, size, mode) in SAMPLING_CELLS:
        d = base / f"{size}_{mode}"
        p = d / f"{rung}.json"
        if not p.is_file():
            raise FileNotFoundError(
                f"no sampling cell for {rung}/{size}/{mode} at {p}")
        rec = json.loads(p.read_text())
        _check_provenance(rec, p, rung, size, mode, want_dtype="float32")
        dps = rec.get("draws_per_seed")
        if dps != DRAWS_PER_SEED[rung]:
            raise ValueError(
                f"{p}: draws_per_seed {dps!r} against the preregistered "
                f"{DRAWS_PER_SEED[rung]} for {rung}")
        if rec.get("seeds") != list(SEEDS):
            raise ValueError(f"{p}: seeds {rec.get('seeds')!r} are not "
                             f"the preregistered {list(SEEDS)}")
        if rec.get("k_total") != len(SEEDS) * dps:
            raise ValueError(f"{p}: k_total {rec.get('k_total')!r} against "
                             f"{len(SEEDS)} seeds × {dps} draws")
        dpath = d / f"{rung}.draws.jsonl.gz"
        if not dpath.is_file():
            raise FileNotFoundError(
                f"no raw draws file for {rung}/{size}/{mode} at {dpath}")
        n = rec["n_items"]
        rows = _read_draw_rows(dpath, n, dps)
        answers = [str(x) for x in rec["answers"]]
        labels = [str(x) for x in rec["probe_labels"]]
        recomputed, per_item_full = recompute_seed_tallies(
            rows, answers, labels, answer_type=rec.get("answer_type"),
            verify_fn=verify_fn)
        stored = rec.get("per_seed_tallies")
        normalized = None
        if isinstance(stored, dict):
            try:
                normalized = {k: {f: int(v[f]) for f in
                                  ("full_string", "first_char", "n_draws")}
                              for k, v in stored.items()}
            except (KeyError, TypeError, ValueError):
                normalized = None
        if normalized != recomputed:
            raise ValueError(
                f"{p}: stored per-seed tallies disagree with the "
                f"recompute from the raw draws — stored {stored!r}, "
                f"recomputed {recomputed!r}; this battery's runner and "
                f"analyzer do not agree on what was drawn")
        full_total = sum(v["full_string"] for v in recomputed.values())
        out[(rung, size, mode)] = {
            "rung": rung, "size": size, "mode": mode, "n": n,
            "answers": answers, "probe_labels": labels,
            "answer_type": rec.get("answer_type"),
            "items_sha256": rec["items_sha256"], "dtype": rec["dtype"],
            "seeds": list(SEEDS), "draws_per_seed": dps,
            "k_total": rec["k_total"],
            "recomputed": {
                "per_seed": recomputed,
                "full_string_total": int(full_total),
                "first_char_total": int(sum(v["first_char"]
                                            for v in recomputed.values())),
                "n_draws_total": int(sum(v["n_draws"]
                                         for v in recomputed.values())),
                "per_item_full_string": per_item_full,
                "fired": bool(full_total > 0),
            },
        }
    return out


def load_redecode_cells(root=EXP3) -> dict:
    """The 16 gate-2 re-decode cells: 3b's record shape, produced by
    3b's exact path (fp16 + generate — the dtype check pins it), ready
    for the byte comparison against load_gate2_referents."""
    base = Path(root) / "results" / "redecode"
    want_dirs = {f"{s}_{m}" for (_r, s, m) in SAMPLING_CELLS}
    _refuse_strays(base, want_dirs, {f"{r}.json" for r in RUNGS})
    out = {}
    for (rung, size, mode) in SAMPLING_CELLS:
        p = base / f"{size}_{mode}" / f"{rung}.json"
        if not p.is_file():
            raise FileNotFoundError(
                f"no re-decode cell for {rung}/{size}/{mode} at {p}")
        rec = json.loads(p.read_text())
        _check_provenance(rec, p, rung, size, mode, want_dtype="float16")
        n = rec["n_items"]
        conts = rec.get("continuations")
        if not isinstance(conts, list) or len(conts) != n:
            raise ValueError(
                f"{p}: continuations has "
                f"{len(conts) if isinstance(conts, list) else conts!r} "
                f"entries against n_items {n}")
        mnt = rec.get("max_new_tokens")
        if not isinstance(mnt, int) or mnt <= 0:
            raise ValueError(f"{p}: max_new_tokens {mnt!r} is not a "
                             f"usable generation cap")
        out[(rung, size, mode)] = {
            "rung": rung, "size": size, "mode": mode, "n": n,
            "continuations": [str(c) for c in conts],
            "probe_labels": [str(x) for x in rec["probe_labels"]],
            "answers": [str(x) for x in rec["answers"]],
            "items_sha256": rec["items_sha256"], "dtype": rec["dtype"],
            "max_new_tokens": mnt,
            "full_string_correct": rec.get("full_string_correct"),
        }
    return out


# ----------------------------------------------------------- verdict tree

ADJUDICATED = tuple((r, s, "trained") for r in REVERSAL_RUNGS
                    for s in PROBE_SIZES)

WORLD_LABEL = {(True, True): "ELICITABLE", (True, False): "BULK-ONLY",
               (False, True): "TAIL-ONLY", (False, False): "WALL"}


def _key(k) -> str:
    return "/".join(k)


def _shape_check_3(mass_cells, sampling_cells, redecode_cells,
                   gate2_refs, floors) -> dict:
    """The battery must be exactly the preregistered 28 + 16 + 16 cells
    with every referent present and every cell pinned to its rung's
    single §4 item file (reading 7). Anything else is a malformed
    battery and a hard error, not a verdict: INSUFFICIENT_DATA is a
    statement about the world, and a half-copied directory is not the
    world."""
    if set(mass_cells) != set(MASS_CELLS):
        raise ValueError(
            f"battery is not the preregistered 28 mass cells: missing "
            f"{sorted(set(MASS_CELLS) - set(mass_cells))}, extra "
            f"{sorted(set(mass_cells) - set(MASS_CELLS))}")
    for name, got in (("16 sampling", sampling_cells),
                      ("16 re-decode", redecode_cells),
                      ("16 gate-2 referent", gate2_refs)):
        if set(got) != set(SAMPLING_CELLS):
            raise ValueError(
                f"battery is not the preregistered {name} cells: missing "
                f"{sorted(set(SAMPLING_CELLS) - set(got))}, extra "
                f"{sorted(set(got) - set(SAMPLING_CELLS))}")
    for r in RUNGS:
        if r not in floors or "primary" not in floors[r]:
            raise ValueError(f"no committed floor for rung {r!r}")

    sha_refs = items_sha_referents(gate2_refs)
    anchor = {r: gate2_refs[(r, PROBE_SIZES[0], "trained")] for r in RUNGS}
    for battery in (mass_cells, sampling_cells, redecode_cells):
        for (rung, size, mode), c in sorted(battery.items()):
            if c["items_sha256"] != sha_refs[rung]:
                raise ValueError(
                    f"cell {rung}/{size}/{mode} carries items_sha256 "
                    f"{c['items_sha256']!r} against the rung's single §4 "
                    f"pin {sha_refs[rung]!r}")
            ref = anchor[rung]
            if c["n"] != ref["n"]:
                raise ValueError(
                    f"cell {rung}/{size}/{mode} has n {c['n']} against "
                    f"the referent's {ref['n']}")
            for field in ("answers", "probe_labels"):
                if c[field] != ref[field]:
                    raise ValueError(
                        f"cell {rung}/{size}/{mode}: {field} disagree "
                        f"with the gate-2 referent's — not this "
                        f"experiment's items")
    for k in sorted(SAMPLING_CELLS):
        if redecode_cells[k]["max_new_tokens"] != \
                gate2_refs[k]["max_new_tokens"]:
            raise ValueError(
                f"re-decode cell {_key(k)} used max_new_tokens "
                f"{redecode_cells[k]['max_new_tokens']} against the "
                f"referent's {gate2_refs[k]['max_new_tokens']} — not "
                f"3b's generation path")
    return sha_refs


def verdict(mass_cells, sampling_cells, redecode_cells, gate2_refs,
            floors, margins, *, alpha: float = ALPHA) -> dict:
    """Design §6, adjudicated in precedence order, with everything
    computed and disclosed BEFORE the first branch so no gate can hide
    another's evidence. Gate 4 (sampler reproducibility) is a
    freeze-time gate, not a runtime branch."""
    _shape_check_3(mass_cells, sampling_cells, redecode_cells,
                   gate2_refs, floors)

    # ---- the §5 statistic on every probe-size mass cell (reading 8:
    # eval-size cells take no test and appear only in the descriptives)
    sign_tests = {}
    bracket_findings = []
    for key in sorted(mass_cells):
        rung, size, mode = key
        if size not in PROBE_SIZES:
            continue
        c = mass_cells[key]
        adjudicated = key in ADJUDICATED
        n_tests = N_ADJ_TESTS if adjudicated else 1
        lower = rung_sign_test(c["items"], c["answers"],
                               n_tests=n_tests, alpha=alpha)
        if adjudicated and not lower["computable"]:
            raise ValueError(
                f"the §5 statistic has no computable value on "
                f"adjudicated cell {_key(key)} ({lower.get('reason')}) — "
                f"a vacuous statistic must never adjudicate; this "
                f"battery cannot be the pinned one")
        rec = {"lower": lower}
        mean_residual = (sum(float(it["residual"]) for it in c["items"])
                         / c["n"])
        rec["mean_residual"] = mean_residual
        if adjudicated and mean_residual > RESIDUAL_BRACKET_THRESHOLD:
            upper = rung_sign_test(c["items"], c["answers"],
                                   n_tests=n_tests, alpha=alpha,
                                   upper=True)
            rec["upper"] = upper
            if upper["significant"] != lower["significant"]:
                bracket_findings.append(_key(key))
        sign_tests[_key(key)] = rec

    def sig_of(key) -> bool:
        return sign_tests[_key(key)]["lower"]["significant"]

    # ---- fires and zero bounds for the 16 sampling cells
    fires = {}
    for key in sorted(sampling_cells):
        rc = sampling_cells[key]["recomputed"]
        entry = {"full_string_total": rc["full_string_total"],
                 "first_char_total": rc["first_char_total"],
                 "n_draws": rc["n_draws_total"],
                 "per_seed_full_string": {s: v["full_string"]
                                          for s, v in
                                          rc["per_seed"].items()},
                 "fired": rc["fired"]}
        if rc["fired"]:
            entry["fired_seeds"] = {s: v["full_string"]
                                    for s, v in rc["per_seed"].items()
                                    if v["full_string"] > 0}
            entry["per_item_max"] = max(rc["per_item_full_string"])
        else:
            # every zero as a CP bound (§5, program rule since 1c):
            # pooled across the cell's draws, and per-item-max at the
            # item's own draw count
            entry["cp95_upper_pooled"] = cp_upper(0, rc["n_draws_total"])
            entry["cp95_upper_per_item_max"] = cp_upper(
                0, sampling_cells[key]["k_total"])
        fires[_key(key)] = entry

    # ---- gate-3 coherence, computed for all 16 (readings 2 and 9),
    # ID trigger on the four adjudicated cells only
    level = 1.0 - alpha / N_COHERENCE_TESTS
    coherence = {}
    for key in sorted(sampling_cells):
        rc = sampling_cells[key]["recomputed"]
        ci_lo, ci_hi = clopper_pearson(rc["first_char_total"],
                                       rc["n_draws_total"], level=level)
        b_lo, b_hi = cell_mass_bracket(mass_cells[key]["items"])
        coherence[_key(key)] = {
            "first_char_count": rc["first_char_total"],
            "n_draws": rc["n_draws_total"],
            "cp_interval": [ci_lo, ci_hi], "cp_level": level,
            "mass_bracket": [b_lo, b_hi],
            "coherent": not (ci_hi < b_lo or b_hi < ci_lo)}

    # ---- gate-5 contamination evidence (probe-size twins; reading 5
    # keeps the mass arm inert where the statistic is not computable)
    contamination_evidence = {}
    for rung in RUNGS:
        ev = []
        for size in PROBE_SIZES:
            key = (rung, size, "untrained")
            mass_arm = sig_of(key)
            fire_arm = fires[_key(key)]["fired"]
            if mass_arm or fire_arm:
                ev.append({"size": size, "mass_arm": mass_arm,
                           "fire_arm": fire_arm})
        if ev:
            contamination_evidence[rung] = ev
    contaminated = sorted(contamination_evidence)

    # ---- descriptives: the scale trend (§5 "the precursor curve"),
    # the matched control's agreement quadrant, floors, margins
    def mean_label_mass(key) -> float:
        c = mass_cells[key]
        return sum(float(it["label_mass"]) for it in c["items"]) / c["n"]

    mass_scale_trend = {r: {s: mean_label_mass((r, s, "trained"))
                            for s in SIZES} for r in RUNGS}
    twin_mass = {r: {s: mean_label_mass((r, s, "untrained"))
                     for s in PROBE_SIZES} for r in RUNGS}
    matched_control = {}
    for size in PROBE_SIZES:
        k = (MATCHED_CONTROL, size, "trained")
        rc = sampling_cells[k]["recomputed"]
        matched_control[size] = {
            "mean_label_mass": mean_label_mass(k),
            "sampled_first_char_rate": rc["first_char_total"]
            / rc["n_draws_total"],
            "sampled_full_string_rate": rc["full_string_total"]
            / rc["n_draws_total"]}

    # ---- gate-2 byte comparison: every differing item disclosed
    # verbatim whether or not the gate fires
    byte_diffs = {}
    for key in sorted(SAMPLING_CELLS):
        diffs = [{"item": i, "got": g, "referent": w}
                 for i, (g, w) in enumerate(zip(
                     redecode_cells[key]["continuations"],
                     gate2_refs[key]["continuations"]))
                 if str(g) != str(w)]
        if diffs:
            byte_diffs[_key(key)] = diffs

    gate1 = {
        "mass_significant": {s: sig_of((POSITIVE_CONTROL, s, "trained"))
                            for s in PROBE_SIZES},
        "full_string_cp95_lower": {}}
    for s in PROBE_SIZES:
        rc = sampling_cells[(POSITIVE_CONTROL, s, "trained")]["recomputed"]
        lo, _hi = clopper_pearson(rc["full_string_total"],
                                  rc["n_draws_total"], level=0.95)
        gate1["full_string_cp95_lower"][s] = lo

    out = {
        "alpha": alpha, "n_adjudicated_tests": N_ADJ_TESTS,
        "mass_sign_tests": sign_tests, "bracket_findings": bracket_findings,
        "fires": fires, "coherence": coherence, "byte_diffs": byte_diffs,
        "gate1": gate1, "contaminated": contaminated,
        "contamination_evidence": contamination_evidence,
        "mass_scale_trend": mass_scale_trend, "twin_mass": twin_mass,
        "matched_control": matched_control,
        "floors": {r: floors[r]["primary"] for r in RUNGS},
        "probe_margins": margins,
    }

    # 1. positive control: the instrument pair must see the
    # distribution and reachability of a capability committed at
    # .960/.980 argmax and .9940 first-char on these same weights
    if not (all(gate1["mass_significant"].values())
            and all(v > 0.5 for v in
                    gate1["full_string_cp95_lower"].values())):
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": f"{POSITIVE_CONTROL} fails as positive control "
                          f"— mass sign test significant per size: "
                          f"{gate1['mass_significant']}; pooled "
                          f"full-string 95% CP lower bounds: "
                          f"{gate1['full_string_cp95_lower']} (gate "
                          f"passes only when the sign test clears at "
                          f"both sizes AND every lower bound exceeds "
                          f".5) — an instrument pair that cannot see a "
                          f"capability committed at .960/.980 argmax "
                          f"and .9940 first-char is not measuring "
                          f"either"}

    # 2. harness continuity: 3b's own tolerance, diffs already disclosed
    over = {k: len(v) for k, v in byte_diffs.items()
            if len(v) > BYTE_TOLERANCE}
    if over:
        n_ref = next(iter(redecode_cells.values()))["n"]
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "byte gate failed — greedy decoding is "
                          "deterministic on this stack, and more than "
                          f"{BYTE_TOLERANCE} of {n_ref} re-decoded "
                          f"continuations differ from 3b's committed "
                          f"record at: "
                          + "; ".join(f"{k} ({n} items)"
                                      for k, n in sorted(over.items()))}

    # 3. instrument coherence, ID trigger on the adjudicated cells
    incoherent_adj = [_key(k) for k in ADJUDICATED
                      if not coherence[_key(k)]["coherent"]]
    if incoherent_adj:
        details = "; ".join(
            f"{k}: {coherence[k]['first_char_count']}/"
            f"{coherence[k]['n_draws']} sampled first-char against mass "
            f"bracket [{coherence[k]['mass_bracket'][0]:.4f}, "
            f"{coherence[k]['mass_bracket'][1]:.4f}]"
            for k in incoherent_adj)
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "instrument coherence failed in adjudicated "
                          f"cell(s): {details} — the exact two-sided CP "
                          f"interval at α = {alpha}/{N_COHERENCE_TESTS} "
                          f"is disjoint from [mass, mass + residual]; "
                          f"the two instruments measure the same "
                          f"distribution, so disagreement is a "
                          f"code-path defect (BOS, padding, prompt "
                          f"drift), not a finding"}

    # 5. contaminated rungs leave step 6's quantifiers; both reversal
    # rungs contaminated leaves them empty, and a universal quantifier
    # over zero cells decides nothing (the all([]) guard, 3b §6)
    eligible = [(r, s) for r in REVERSAL_RUNGS if r not in contaminated
                for s in PROBE_SIZES]
    if not eligible:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "both reversal rungs' probe-size twins fired "
                          f"(evidence: {contamination_evidence}) — "
                          f"contamination emptied the claim, and a "
                          f"universal quantifier over zero cells "
                          f"decides nothing"}

    # 6. adjudicate the claim per eligible (rung × size) trained cell
    cell_labels = {}
    for (r, s) in eligible:
        key = (r, s, "trained")
        cell_labels[f"{r}/{s}"] = WORLD_LABEL[
            (sig_of(key), fires[_key(key)]["fired"])]
    out = {**out, "cell_labels": cell_labels}
    worlds = set(cell_labels.values())

    if worlds == {"ELICITABLE"}:
        return {**out, "verdict": "ELICITABLE",
                "reason": "mass significantly above its "
                          "within-distribution floor AND at least one "
                          "verified full-string draw in every "
                          f"adjudicated cell ({sorted(cell_labels)}) — "
                          "the famous zero was an argmax cliff over "
                          "nonzero distribution mass; signature 2 "
                          "fires, per-seed spread in the fires table"}
    if worlds == {"BULK-ONLY"}:
        bounds = "; ".join(
            f"{_key((r, s, 'trained'))} ≤ "
            f"{fires[_key((r, s, 'trained'))]['cp95_upper_pooled']:.2e}"
            for r, s in eligible)
        return {**out, "verdict": "BULK-ONLY",
                "reason": "mass elevated but full-string walled in every "
                          f"adjudicated cell (pooled per-draw CP bounds: "
                          f"{bounds}) — the first character is in the "
                          f"distribution's bulk; the seven-character "
                          f"joint path carries no measurable mass, and "
                          f"the units gap relocates from the metric "
                          f"into the autoregressive channel"}
    if worlds == {"TAIL-ONLY"}:
        return {**out, "verdict": "TAIL-ONLY",
                "reason": "full-string fires without mass elevation in "
                          "every adjudicated cell — rare-event "
                          "reachability below the mass floor's "
                          "resolution; by the forward-note's asymmetry "
                          "rule a fire is strong evidence, so this is "
                          "reported as elicitation with the mass result "
                          "beside it"}
    if worlds == {"WALL"}:
        pooled = "; ".join(
            f"{_key((r, s, 'trained'))} ≤ "
            f"{fires[_key((r, s, 'trained'))]['cp95_upper_pooled']:.2e} "
            f"pooled, ≤ "
            f"{fires[_key((r, s, 'trained'))]['cp95_upper_per_item_max']:.2e}"
            f" per item"
            for r, s in eligible)
        pm = "; ".join(
            f"{r} " + "/".join(f"{margins[r][s]:.4f}@{s}"
                               for s in PROBE_SIZES)
            for r in REVERSAL_RUNGS if r not in contaminated)
        return {**out, "verdict": "WALL",
                "reason": "mass at floor AND zero verified successes in "
                          f"every adjudicated cell ({pooled}) — the "
                          f"dissociation extends through the entire "
                          f"output channel at this resolution, against "
                          f"same-weights probe margins {pm}. Per the "
                          f"forward-note the frozen probe module is the "
                          f"preregistered arbiter: WALL means 'present "
                          f"in representation, absent from the output "
                          f"channel at this depth', not evidence "
                          f"against signature 1; sampling silence is "
                          f"weak evidence, and the design is blind "
                          f"below p ≈ 1e-5"}
    table = "; ".join(f"{k} {v}" for k, v in sorted(cell_labels.items()))
    return {**out, "verdict": "PARTIAL",
            "reason": f"the adjudicated cells disagree — per-cell table "
                      f"as headline, not caveat: {table}"}


# ----------------------------------------------------------------- driver

def run(root=EXP3) -> dict:
    """Load everything through the frozen producers and adjudicate."""
    return verdict(load_mass_cells(root), load_sampling_cells(root),
                   load_redecode_cells(root), load_gate2_referents(),
                   load_floors(), load_probe_margins())


if __name__ == "__main__":
    v = run()
    print(json.dumps({k: v[k] for k in
                      ("verdict", "reason", "contaminated",
                       "cell_labels", "bracket_findings", "gate1")
                      if k in v}, indent=1))
