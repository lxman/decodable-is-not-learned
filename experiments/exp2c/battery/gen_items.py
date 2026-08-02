"""Generate exp2c's committed battery item files (M0 task 6; design open
item 7). Adapts exp2b's battery/gen_items.py (read, not imported: 2b's
battery modules fire register() at import time and 2c's registry must stay
clean of 2b side effects): same probe/eval targets and starving-split
feasibility machinery through the frozen `splits` module (reached only via
the instrument.py shim, per Task 1), plus the three family fields (design
§2) and eval_items raised to the >=500 floor. Run under the canonical venv:
`cd experiments/exp2c && ~/emergence-lab/.venv/bin/python -m battery.gen_items <name|all>`.

QUESTION vs BASIS (read this before touching either dict below):
  TEMPLATES render the question text directly from gen() output -- gen
  output IS the item surface, no post-hoc value conversion for display.
  BASIS is a *different* thing: the tuple recorded for the starving split
  (splits.py), which must match each spec's committed `basis_kind` field
  and clear the split's feasibility floors (min_holdout_values=15,
  min_val_items=300). Using the raw gen() tuple as basis fails both:
    - mod17's basis_kind is "first operand token" (single component) even
      though gen() also returns the decoy operand b the question displays;
      recording basis=(a, b) makes the split hold out BOTH components
      independently (join of two 20% holds ~= 4% of items), which starves
      mod17's ~2000 probe items down to ~80 validation items -- confirmed
      empirically below the 300 floor.
    - a bare (letter, shift) 2-component basis for caesar_len8 forces a
      per-component holdout on the shift, which only has 5 possible
      values -- structurally below min_holdout_values=15 regardless of
      item count.
  BASIS below is this task's derivation, one entry per spec, reduced or
  combined to match each spec's own basis_kind text (mirroring 2b's
  basis_fn discipline, which 2c's CapabilitySpec has no field for). Every
  entry was checked against splits.feasibility_report before being
  committed here; see task-6-report.md for the per-spec numbers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

try:
    from .. import instrument  # experiments.exp2c.battery.gen_items (pytest/absolute import)
except ImportError:
    import instrument  # `python -m battery.gen_items` from experiments/exp2c (battery is top-level)

from . import generators_rescues, generators_rungs  # noqa: F401  (populate SPECS via register())
from .base import SPECS

SplitParams = instrument.splits.SplitParams
feasibility_report = instrument.splits.feasibility_report
SplitInfeasible = instrument.splits.SplitInfeasible

ITEMS_DIR = Path(__file__).parent / "items"

N_EVAL = 500        # design open item 7 floor
N_PROBE = 2000       # default target; overridden per spec below where the
                      # spec's own value space or basis structure requires it
N_SHOTS = 2
_LETTERS = "abcdefghijklmnopqrstuvwxyz"

# --------------------------------------------------------------- templates
# One question template per registered spec (Tasks 4-5). Placeholders map
# positionally onto spec.gen()'s output tuple: a=element 0, b=element 1,
# c=element 2, in gen's own order (the same order oracle(*gen_output)
# consumes). No per-spec value conversion beyond Python's own format-spec
# mini-language (":o" for sub_base8's octal display, a format string
# builtin, not extra code).
TEMPLATES = {
    "add4_mid": "What is {a} + {b}?",
    "sub4_mid": "What is {a} - {b}?",
    "base12": "Write {a} in base 12.",
    "base12_digitsum": "Write {a} in base 12.",
    "sub_base8": "What is {a:o} - {b:o} in base 8 (both numbers are octal)?",
    "mod17": "What is ({a} + {b}) mod 17?",
    "mod19": "What is ({a} + {b}) mod 19?",
    "mod13_comp": "What is (({a} + {b}) * {c}) mod 13?",
    "caesar_len8": "The word '{a}' was made by shifting each letter of a "
                   "word forward by {b}. What is the original word?",
    "count_div13": "How many multiples of 13 are there in the range {a} "
                   "to {b} inclusive?",
    "clock24_d999": "On a 24-hour clock, what hour is it {b} hours after "
                    "hour {a}?",
    "rev_string7": "Spell the string '{a}' backwards.",
    "letter_sum": "The string is '{a}'. Let p = (({b} + {c}) mod 6) + 2. "
                  "What is the letter at position p of the string, "
                  "counting from 1?",
    "letter_prod": "The string is '{a}'. Let p = (({b} * {c}) mod 6) + 2. "
                   "What is the letter at position p of the string, "
                   "counting from 1?",
    "roman_sum7": "What is the sum of the roman numerals {a} and {b}, "
                  "mod 7?",
    "collatz_step2": "Apply the Collatz rule (if even, halve; if odd, "
                     "triple and add 1) twice to {a}. What is the result "
                     "mod 7?",
    "isqrt_gap": "For N = {a}, what is (N - isqrt(N)^2) mod 7?",
}

# ------------------------------------------------------------------ basis
# name -> callable(*gen_output) -> basis tuple (pre-stringification).
_TOKENIZER = None


def _final_chunk(s: str) -> str:
    """Final BPE chunk of the quoted string, exactly as exp2b's
    reverse_string basis_fn computes it (battery/generators_t2.py's sibling
    in generators.py) -- rev_string7's own basis_kind says "as
    reverse_string". Loads the pinned Pythia tokenizer (a fixed vocabulary,
    identical for trained and untrained checkpoints of the same
    architecture) via exp2b's models.py, reached through the sys.path entry
    `instrument` already opened -- no new access path, no forward pass, no
    model weights, no prediction: this is not the "language model...
    loaded or queried" the two-stage lock guards against. exp2b's own
    committed reverse_string.json shows this same computation running at
    generation time (basis values like 'ipe', 'cki', 'db' -- real BPE
    chunks, not truncated substrings)."""
    global _TOKENIZER
    if _TOKENIZER is None:
        try:
            import models
            _TOKENIZER = models.load_tokenizer("410m")
        except Exception as e:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                f"rev_string7: tokenizer unavailable ({type(e).__name__}: {e})") from e
    ids = _TOKENIZER(f"'{s}'", add_special_tokens=False)["input_ids"]
    toks = [_TOKENIZER.decode([t]) for t in ids]
    return toks[-2] if toks[-1] == "'" else toks[-1].rstrip("'")


BASIS = {
    "add4_mid": lambda a, b: (f"{(a // 100) % 10}h{(b // 100) % 10}",),
    "sub4_mid": lambda a, b: (f"{(a // 100) % 10}h{(b // 100) % 10}",),
    "base12": lambda n: (n,),
    "base12_digitsum": lambda n: (n,),
    "sub_base8": lambda a, b: (f"{a % 8}o{b % 8}",),
    "mod17": lambda a, b: (a,),
    "mod19": lambda a, b: (a,),
    "mod13_comp": lambda a, b, c: (a,),
    "caesar_len8": lambda enc, k: (f"{enc[0]}{k}",),
    "count_div13": lambda a, b: (a, b),
    "clock24_d999": lambda h, d: (d,),
    "rev_string7": lambda s: (_final_chunk(s),),
    # string-as-basis (ruling 2026-08-01): the printed string S itself,
    # one component, per-string holdout; i and j are printed decoys that
    # never enter the basis (the position map is disclosed-unstarvable,
    # see each spec's dumbest_baseline).
    "letter_sum": lambda s, i, j: (s,),
    "letter_prod": lambda s, i, j: (s,),
    "roman_sum7": lambda a, b: (a, b),
    "collatz_step2": lambda n: (n,),
    "isqrt_gap": lambda n: (n,),
}

# name -> (SplitParams, n_probe). Defaults (holdout_frac 0.2,
# min_holdout_values 15, min_val_items 300, n_probe 2000) unless the
# spec's own basis structure or value space requires an override; every
# override is checked feasible (5/5 seeds) before being committed here.
SPLIT_PLAN = {
    "add4_mid": (SplitParams(), N_PROBE),
    "sub4_mid": (SplitParams(), N_PROBE),
    "base12": (SplitParams(), N_PROBE),
    "base12_digitsum": (SplitParams(), N_PROBE),
    # sub_base8's value space (two-digit octal operands, a>b) has only
    # 1540 unique (a, b) pairs -- below N_EVAL+N_PROBE=2500, so n_probe is
    # cut to 1000 (1500 total, comfortably under 1540). Its basis
    # cardinality is capped at 64 (8x8 ones-digit pairs), so holdout_frac
    # 0.2 would hold out only 12-13 values (< the 15 floor); 0.35 clears
    # it (23 held) while keeping n_val well above 300 across all 5 seeds.
    "sub_base8": (SplitParams(holdout_frac=0.35), 1000),
    "mod17": (SplitParams(), N_PROBE),
    "mod19": (SplitParams(), N_PROBE),
    "mod13_comp": (SplitParams(), N_PROBE),
    # caesar_len8's basis value (first cipher letter + shift) determines
    # its label (decoded first letter) exactly -- one basis value, one
    # class, exp2b's caesar precedent (battery/generators_t2.py) needs
    # stratify_by_label=True so every decoded-letter class survives on
    # both sides of a random 20% holdout of the ~115-120 combos.
    "caesar_len8": (SplitParams(stratify_by_label=True), N_PROBE),
    # both endpoints share one numeric value space (design's "shared
    # value space" text) -- shared_components draws one holdout set from
    # their union. As with 2b's gcd/sort3_mid (same shared-2-component
    # shape), the joint AND over two 0.2-holds would starve val to ~4% of
    # items; 0.45 (2b's gcd figure) and a wider n_probe clear the floor.
    "count_div13": (SplitParams(holdout_frac=0.45, min_val_items=300,
                                shared_components=True), 4000),
    "clock24_d999": (SplitParams(), N_PROBE),
    "rev_string7": (SplitParams(), N_PROBE),
    # pos_letter (proposal §3 F3 feasibility block): default SplitParams +
    # stratify_by_label=True (the caesar precedent -- 26 letter classes
    # must survive both sides of the per-string holdout). Basis values are
    # per-item unique (fresh-random strings), so the 0.2 holdout reduces
    # to a ~20% item split: ~400 val items and ~400 held-out basis values,
    # comfortably above the 300/15 floors.
    "letter_sum": (SplitParams(stratify_by_label=True), N_PROBE),
    "letter_prod": (SplitParams(stratify_by_label=True), N_PROBE),
    # roman_sum7's basis_kind names this explicitly: "single shared
    # holdout over the union of numeral values (shared-component
    # variant)" -- same shape and same fix as count_div13.
    "roman_sum7": (SplitParams(holdout_frac=0.45, min_val_items=300,
                               shared_components=True), 4000),
    "collatz_step2": (SplitParams(), N_PROBE),
    "isqrt_gap": (SplitParams(), N_PROBE),
}


def _as_tuple(raw):
    return raw if isinstance(raw, tuple) else (raw,)


def _render(name, args):
    return TEMPLATES[name].format(**dict(zip(_LETTERS, args)))


def _make_item(spec, args):
    """Review ruling 2026-07-29 (Fix A): `answer` is the full task result
    the question text demands -- spec.surface_answer(*args) where set; the
    specs without one (the rescue-style templates) ask for the oracle
    output directly, so there answer == probe_label as in 2b's div7/
    month_offset. `probe_label` always stays on `oracle`."""
    label = spec.oracle(*args)
    ans = (spec.surface_answer(*args) if spec.surface_answer is not None
           else label)
    basis = tuple(str(v) for v in BASIS[spec.name](*args))
    return {"question": _render(spec.name, args), "answer": str(ans),
            "probe_label": str(label), "basis": list(basis)}


def generate(name: str) -> dict:
    """Build and commit one spec's item file. Raises SplitInfeasible (from
    the frozen splits module) or RuntimeError ("cannot reach item count")
    on infeasibility -- callers (main() below) catch these and eject."""
    spec = SPECS[name]
    if name not in TEMPLATES or name not in BASIS or name not in SPLIT_PLAN:
        raise KeyError(f"{name}: no TEMPLATES/BASIS/SPLIT_PLAN entry registered")
    split_params, n_probe = SPLIT_PLAN[name]

    rng = np.random.default_rng(spec.seed)
    seen_args = set()
    seen_q = set()

    shots = []
    while len(shots) < N_SHOTS:
        args = _as_tuple(spec.gen(rng))
        if args in seen_args:
            continue
        item = _make_item(spec, args)
        if item["question"] in seen_q:
            continue
        seen_args.add(args)
        seen_q.add(item["question"])
        shots.append([item["question"], item["answer"]])

    n_total = N_EVAL + n_probe
    items = []
    attempts = 0
    while len(items) < n_total:
        attempts += 1
        if attempts > 60 * n_total:
            raise RuntimeError(f"{name}: cannot reach item count "
                              f"({n_total} needed; space too small?)")
        args = _as_tuple(spec.gen(rng))
        if args in seen_args:
            continue
        item = _make_item(spec, args)
        if item["question"] in seen_q:
            continue
        seen_args.add(args)
        seen_q.add(item["question"])
        items.append(item)

    payload = {
        "name": spec.name,
        "description": spec.description,
        "probe_label_space": spec.probe_label_space,
        "basis_kind": spec.basis_kind,
        "family": spec.family,
        "dial_name": spec.dial_name,
        "dial_value": spec.dial_value,
        "seed": spec.seed,
        "shots": shots,
        "eval_items": items[:N_EVAL],
        "probe_items": items[N_EVAL:],
    }
    probe = payload["probe_items"]
    payload["feasibility"] = feasibility_report(
        [tuple(it["basis"]) for it in probe],
        [it["probe_label"] for it in probe],
        split_params)

    ITEMS_DIR.mkdir(exist_ok=True)
    (ITEMS_DIR / f"{name}.json").write_text(json.dumps(payload, indent=1))
    return payload


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python -m battery.gen_items <name|all>")
        raise SystemExit(1)
    target = argv[0]
    names = list(SPECS) if target == "all" else [target]

    ejections = {}
    for name in names:
        try:
            payload = generate(name)
        except (SplitInfeasible, RuntimeError) as e:
            ejections[name] = str(e)
            print(f"[gen] EJECTED {name}: {e}", flush=True)
            continue
        per_seed = payload["feasibility"]["per_seed"]
        n_val = min(s["n_val"] for s in per_seed.values())
        print(f"[gen] {name}: {len(payload['eval_items'])} eval / "
              f"{len(payload['probe_items'])} probe -> {name}.json  "
              f"(min val across seeds: {n_val})", flush=True)

    if target == "all":
        ITEMS_DIR.mkdir(exist_ok=True)
        (ITEMS_DIR / "ejections.json").write_text(json.dumps(ejections, indent=1))
        print(f"[gen] done; {len(ejections)} ejection(s) recorded", flush=True)


if __name__ == "__main__":
    main()
