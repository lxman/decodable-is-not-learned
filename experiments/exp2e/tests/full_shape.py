"""Synthetic full-shape 2e trees for the freeze rule: every §6
terminal executed end to end through the frozen loaders (2d's) and
2e's own referent phase, before the tag.

A 2e world is a complete 2d tree in 2d's runner layout, built by 2d's
own world builder (`experiments/exp2d/tests/full_shape.build_world`),
then CLOSED the way 2d's campaign was closed — 2d's frozen analyzer
writes the world's `results/verdict.json` — and then PINNED the way
2e pins the real tree: `make_referents_2e.build` over the world's
272 tier files + verdict.json, the manifest's own sha, the per-cell
main tally pin and 2d's primary literals all taken FROM THE WORLD.
So every world runs the production referent path; the refusal worlds
alter one thing AFTER pinning. The OUTCOME is never synthetic.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2E = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2E.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d.tests import full_shape as fs2d  # noqa: E402
from experiments.exp2e import analyze_2e as a  # noqa: E402
from experiments.exp2e import make_referents_2e as mk  # noqa: E402

battery = fs2d.battery
outcome = fs2d.outcome
rising_rungs = fs2d.rising_rungs
flat_rungs = fs2d.flat_rungs
counts_for = fs2d.counts_for
FILLER = fs2d.FILLER


def pins_from_world(root) -> dict:
    """What the real tree pins by literal, read from the world: the
    manifest (built here), its sha, the main tally table and 2d's
    primary from the world's own verdict.json."""
    root = Path(root)
    manifest_path = root / "referents_2e.json"
    rec = mk.build(root, manifest_path)
    sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    v2d = json.loads((root / "results" / "verdict.json").read_text())
    tally = {}
    for size in a2d.PROBE_SIZES:
        for rung in a2d.RUNGS:
            r = json.loads(a2d.tier_record_path(root, "main", size, rung)
                           .read_text())
            tally[(rung, size)] = int(r["per_seed_tallies"]["0"]["full_string"])
    return {"manifest_path": manifest_path, "manifest_sha_pin": sha,
            "tally_pin": tally,
            "verdict_2d_pin": a.verdict_2d_pin_from_record(v2d),
            "n_files": rec["n_files"]}


def build_world(root, *, main_verified, pilot_verified=None,
                argmax_correct=None, run=True, mutate=None) -> dict:
    """2d's builder → 2d's analyzer (writes the world's verdict.json)
    → 2e's pins from the world → optional `mutate(root, pins)` (the
    refusal worlds) → `analyze_2e.run` with the world's pins."""
    root = Path(root)
    fs2d.build_world(root, main_verified=main_verified,
                     pilot_verified=pilot_verified,
                     argmax_correct=argmax_correct, run=False)
    v2d = a2d.run(root, write=True)
    assert (root / "results" / "verdict.json").exists()
    pins = pins_from_world(root)
    pins["verdict_2d"] = v2d["verdict"]
    if mutate is not None:
        mutate(root, pins)
    if not run:
        return pins
    v = a.run(root, manifest_path=pins["manifest_path"],
              manifest_sha_pin=pins["manifest_sha_pin"],
              tally_pin=pins["tally_pin"],
              verdict_2d_pin=pins["verdict_2d_pin"])
    v["_pins"] = pins
    return v


# ------------------------------------------------------------ mutators

def mutate_manifest_file(root, pins):
    """W4: one committed pilot record's bytes change AFTER pinning."""
    p = a2d.tier_record_path(root, "pilot", "410m", "mod17")
    p.write_text(p.read_text() + "\n")


def mutate_stored_tally(root, pins):
    """W5: a main record's stored tally edited, manifest REBUILT so
    the file pins hold — the re-tally disagreement must be the
    terminal's reason, delivered not raised."""
    p = a2d.tier_record_path(root, "main", "1b", "mod17")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"]["0"]["full_string"] += 1
    p.write_text(json.dumps(rec, indent=1))
    pins.update(pins_from_world(root))
    pins["tally_pin"][("mod17", "1b")] += 1   # the pin follows the record


def mutate_2d_verdict(root, pins):
    """W6: 2d's verdict.json primary altered, manifest rebuilt and the
    literal pin taken from the altered file — the re-derivation of 2d's
    primary no longer matches: the comparison gate fires."""
    p = root / "results" / "verdict.json"
    v = json.loads(p.read_text())
    v["primary"]["auc"] = v["primary"]["auc"] + 0.01
    p.write_text(json.dumps(v, indent=1))
    pins.update(pins_from_world(root))


def mutate_tally_pin(root, pins):
    """W7: the doc's literal tally table disagrees with the tree."""
    pins["tally_pin"][("antonym", "410m")] += 1


def mutate_missing_file(root, pins):
    """W8: a pilot draws file deleted after pinning."""
    a2d.tier_draws_path(root, "pilot", "1b", "base7").unlink()


# --------------------------------------------------------------- worlds

def world_specs() -> list:
    """(name, build_world kwargs, expected verdict). Rates are chosen
    against the REAL floors; F1 is unthresholded so the flat rungs'
    zero-draw scores log(ε/c) order by floor among themselves."""
    _, floors = battery()
    ris, fla = rising_rungs(), flat_rungs()
    specs = []
    specs.append(("W1 PASS clean separation",
                  {"main_verified": counts_for(
                      {r: floors[r]["floor"] + 0.2 for r in ris})},
                  "PASS"))
    # W2 FAIL: the label carries nothing — six flat rungs well above
    # floor, the rising rungs at zero except two
    specs.append(("W2 FAIL predictor uninformative",
                  {"main_verified": counts_for(
                      {**{r: floors[r]["floor"] + 0.2 for r in fla[:6]},
                       **{r: floors[r]["floor"] + 0.2 for r in ris[:2]}})},
                  "FAIL"))
    # W3 INDETERMINATE: CI excludes .5 but AUC < .75 and block p ≥ .01
    # — 2d's own W3 spec: five rising rungs above floor, one per
    # family across five families, the other six rising rungs at zero
    # with the flat (under F1: AUC .727, block p .144, CI [.53, .93])
    five = ["sub3_mid", "antonym", "arith_next", "count_div13", "median5"]
    specs.append(("W3 INDETERMINATE partial separation",
                  {"main_verified": counts_for(
                      {r: floors[r]["floor"] + 0.2 for r in five})},
                  "INDETERMINATE"))
    base = {"main_verified": counts_for(
        {r: floors[r]["floor"] + 0.2 for r in ris})}
    specs.append(("W4 INSUFFICIENT_DATA manifest file changed",
                  {**base, "mutate": mutate_manifest_file},
                  "INSUFFICIENT_DATA"))
    specs.append(("W5 INSUFFICIENT_DATA stored tally disagrees",
                  {**base, "mutate": mutate_stored_tally},
                  "INSUFFICIENT_DATA"))
    specs.append(("W6 INSUFFICIENT_DATA 2d primary not reproduced",
                  {**base, "mutate": mutate_2d_verdict},
                  "INSUFFICIENT_DATA"))
    specs.append(("W7 INSUFFICIENT_DATA tally pin disagrees",
                  {**base, "mutate": mutate_tally_pin},
                  "INSUFFICIENT_DATA"))
    specs.append(("W8 INSUFFICIENT_DATA tier file missing",
                  {**base, "mutate": mutate_missing_file},
                  "INSUFFICIENT_DATA"))
    # W9 PASS where the floor covariate is the whole story: every
    # rising rung at 1.05 × its floor, every flat rung at 0.95 × its
    # floor — F1 separates perfectly, the raw log rate F2 does not
    # (.60, the probe's number by coincidence of the floor ordering)
    specs.append(("W9 PASS floor-relative only",
                  {"main_verified": counts_for(
                      {**{r: floors[r]["floor"] * 1.05 for r in ris},
                       **{r: floors[r]["floor"] * 0.95 for r in fla}})},
                  "PASS"))
    return specs
