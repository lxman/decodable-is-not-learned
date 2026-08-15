"""Synthetic full-shape batteries for the Exp 3b freeze rule (design §2
item 3, §11): the frozen verdict tree must be EXECUTED to every terminal
branch, end to end through the frozen loaders, before the tag.

Each battery is a complete on-disk world: all 40 cell records in the
runner's schema, all 16 inclusion referents split across a synthetic 2c
tree and a synthetic 2b tree (reverse_string routes through the 2b root,
as in reality), and all 24 byte referents in 3a's layout. `run_battery`
then loads it through analyze_3b's own producers — load_cells,
load_inclusion_referents, load_byte_referents — with the REAL committed
floors and the REAL committed probe margins, and adjudicates.

The floors are real, so every count below is chosen against them:
rev_string7 .056 (crit 46/500 at alpha .01/8), reverse_string .054 (44),
ctrl_copy .052 (43), clock24_d999 .496 (283). 3a's lesson — a producer can
exist and return None — is why these worlds exercise VALUES through the
loaders rather than calling verdict() on hand-built dicts alone.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments.exp3b import analyze_3b as a

# probe labels per rung: letters for the three word rungs, a DIGIT for the
# matched control, so every battery exercises the non-alphabetic first_char
# path through the real loader
LABELS = {"rev_string7": "r", "reverse_string": "s", "ctrl_copy": "c",
          "clock24_d999": "8"}

# design §4's committed inclusion values, used verbatim as the synthetic
# referents so gate 2 passes wherever a battery does not deliberately break it
INCLUSION_REFERENTS = {}
for _r in a.RUNGS:
    for _s in a.PROBE_SIZES:
        INCLUSION_REFERENTS[(_r, _s, "trained")] = 0
        INCLUSION_REFERENTS[(_r, _s, "untrained")] = 0
INCLUSION_REFERENTS[("ctrl_copy", "410m", "trained")] = 480
INCLUSION_REFERENTS[("ctrl_copy", "1b", "trained")] = 490
INCLUSION_REFERENTS[("clock24_d999", "410m", "trained")] = 18
INCLUSION_REFERENTS[("clock24_d999", "1b", "trained")] = 24

N = 500
AT_FLOOR = {"rev_string7": 28, "reverse_string": 27, "ctrl_copy": 26,
            "clock24_d999": 240}          # ~floor * 500, all non-significant
QUIET_UNTRAINED = 20                       # far below every letter floor
FIRES = 300                                # far above every floor
UNTRAINED_FIRE = 400


def default_counts() -> dict:
    """A physically plausible world: the positive control emits, reversal
    sits at floor, the matched control sits under its .496 marginal floor,
    every twin is quiet. This is the DISSOCIATION world; batteries edit it."""
    fc = {}
    for r in a.RUNGS:
        for s in a.SIZES:
            fc[(r, s, "trained")] = AT_FLOOR[r]
            fc[(r, s, "untrained")] = QUIET_UNTRAINED
    for s in a.PROBE_SIZES:
        fc[("ctrl_copy", s, "trained")] = 480
    return fc


def make_battery(root: Path, *, fc_overrides=None, full_overrides=None,
                 byte_mutations=None) -> None:
    """Write one complete synthetic world under `root`.

    fc_overrides:   {(rung,size,mode): first-char-correct count}
    full_overrides: {(rung,size,mode): full_string_correct} — default is the
                    inclusion referent at probe sizes (gate 2 passes) and 0
                    at eval sizes
    byte_mutations: {(rung,size,mode): n items whose CELL continuation is
                    made to differ from the byte referent}
    """
    fc = {**default_counts(), **(fc_overrides or {})}
    full_overrides = full_overrides or {}
    byte_mutations = byte_mutations or {}

    for (rung, size, mode), k in fc.items():
        label = LABELS[rung]
        conts = [f" {label}x{i}" if i < k else f" z{i}" for i in range(N)]
        ref_conts = list(conts)
        for i in range(byte_mutations.get((rung, size, mode), 0)):
            conts[N - 1 - i] = conts[N - 1 - i] + " DRIFT"
        full = full_overrides.get(
            (rung, size, mode),
            INCLUSION_REFERENTS.get((rung, size, mode), 0))
        rec = {"rung": rung, "size": size, "mode": mode, "n_items": N,
               "continuations": conts,
               "probe_labels": [label] * N,
               "answers": [label + "bcdefg"] * N,
               "full_string_correct": int(full),
               "full_string_acc": full / N,
               "max_new_tokens": 12, "n_shots": 2,
               "untrained_seed": 0 if mode == "untrained" else None,
               "model_sha": "synthetic", "items_sha256": "synthetic"}
        p = root / "results" / f"{size}_{mode}" / f"{rung}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))

        if size in a.EVAL_SIZES:
            bp = root / "byte_referents" / f"{size}_{mode}" / f"{rung}.json"
            bp.parent.mkdir(parents=True, exist_ok=True)
            bp.write_text(json.dumps({"rung": rung, "size": size,
                                      "mode": mode,
                                      "continuations": ref_conts}))

    for (rung, size, mode), correct in INCLUSION_REFERENTS.items():
        tree = "inclusion_2b" if rung in a.RUNGS_2B else "inclusion_2c"
        p = root / tree / f"{size}_{mode}" / f"{rung}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"capability": rung, "n": N,
                                 "correct": int(correct),
                                 "acc": correct / N}))


def run_battery(root: Path) -> dict:
    """End to end through the frozen loaders; floors and margins are the
    real committed artifacts."""
    return a.verdict(a.load_cells(root),
                     a.load_floors(),
                     a.load_inclusion_referents(root / "inclusion_2c",
                                                root / "inclusion_2b"),
                     a.load_byte_referents(root / "byte_referents"),
                     a.load_probe_margins())


# ---------------------------------------------------------- the six worlds
# (plus the two contamination interactions; specs consumed by the tests and
# by the freeze checklist run)

REV_TRAINED_PROBE = [(r, s, "trained") for r in a.REVERSAL_RUNGS
                     for s in a.PROBE_SIZES]

BATTERIES = {
    # gate 1: the positive control is dead at ONE probe size — "both" means
    # both, and one blind size already invalidates the instrument
    "id_gate1_ctrl_dead": {
        "fc_overrides": {("ctrl_copy", "1b", "trained"): 30},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "ctrl_copy"},
    # gate 2: one probe-size cell's full-string count is CP-incompatible
    # with its committed inclusion referent
    "id_gate2_replication": {
        "full_overrides": {("ctrl_copy", "410m", "trained"): 100},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "replication"},
    # gate 3: >2 of 500 continuations differ from 3a's stored referent
    "id_gate3_bytes": {
        "byte_mutations": {("rev_string7", "2.8b", "trained"): 3},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "byte gate"},
    # the claim, three ways — with 2 byte diffs in the UNITS_ARTIFACT world
    # so the ≤2 tolerance and the disclose-regardless provision are
    # exercised on a passing battery
    "units_artifact": {
        "fc_overrides": {k: FIRES for k in REV_TRAINED_PROBE},
        "byte_mutations": {("reverse_string", "12b", "untrained"): 2},
        "expect": "UNITS_ARTIFACT"},
    "dissociation": {
        "expect": "DISSOCIATION"},
    "partial": {
        "fc_overrides": {("rev_string7", "1b", "trained"): FIRES},
        "expect": "PARTIAL", "expect_reason": "rev_string7/1b"},
    # gate 4 × step 5 interaction: rev_string7's twin fires, so step 5
    # quantifies over reverse_string alone — which fires everywhere, so the
    # verdict is UNITS_ARTIFACT. An implementation that ignores the
    # exclusion sees rev_string7 at floor and returns PARTIAL instead.
    "contaminated_one_rung": {
        "fc_overrides": {("rev_string7", "410m", "untrained"): UNTRAINED_FIRE,
                         ("reverse_string", "410m", "trained"): FIRES,
                         ("reverse_string", "1b", "trained"): FIRES},
        "expect": "UNITS_ARTIFACT", "expect_contaminated": ["rev_string7"]},
    # both reversal twins fire: the universal quantifiers have no cells
    # left, and a vacuous "all of zero" must not be allowed to adjudicate
    "contaminated_both_rungs": {
        "fc_overrides": {("rev_string7", "410m", "untrained"): UNTRAINED_FIRE,
                         ("reverse_string", "1b", "untrained"): UNTRAINED_FIRE},
        "expect": "INSUFFICIENT_DATA", "expect_reason": "contamination",
        "expect_contaminated": ["rev_string7", "reverse_string"]},
    # gate 4's scope is the PROBE-size twins (§6: eval-size cells take no
    # significance tests): an eval-size twin emitting loudly is visible in
    # the descriptives but contaminates nothing
    "eval_twin_fire_is_not_contamination": {
        "fc_overrides": {("rev_string7", "12b", "untrained"): UNTRAINED_FIRE},
        "expect": "DISSOCIATION", "expect_contaminated": []},
}


def run_all(base: Path) -> dict:
    out = {}
    for name, spec in BATTERIES.items():
        root = Path(base) / name
        make_battery(root,
                     fc_overrides=spec.get("fc_overrides"),
                     full_overrides=spec.get("full_overrides"),
                     byte_mutations=spec.get("byte_mutations"))
        out[name] = run_battery(root)
    return out


if __name__ == "__main__":
    import sys
    import tempfile

    base = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(tempfile.mkdtemp(prefix="exp3b_full_shape_"))
    results = run_all(base)
    ok = True
    for name, spec in BATTERIES.items():
        v = results[name]
        good = v["verdict"] == spec["expect"] \
            and spec.get("expect_reason", "") in v.get("reason", "") \
            and v["contaminated"] == spec.get("expect_contaminated",
                                              v["contaminated"])
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {name}: {v['verdict']}"
              f" (contaminated={v['contaminated']})")
    print("ALL TERMINAL BRANCHES REACHED" if ok else "FULL-SHAPE RUN FAILED")
    sys.exit(0 if ok else 1)
