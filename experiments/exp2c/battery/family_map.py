"""Scored-battery family map (Michael's ruling 2026-08-01).

The MC power table (run/power_table.py) must model the FULL scored
battery `analyze.py` will adjudicate -- not just the 14-rung new-spec
pool. `run/power_table.py::_family_sizes` (pre-ruling) had two defects:
it counted the screen-ejected `base12`'s item file (tier-1 verdict
"reject"), and it omitted the 12 reused 2b survivors entirely.

Ruling: reused `reverse_string` and `clock24` JOIN their new siblings'
families (`rev_string7` -> reversal, `clock24_d999` -> clock),
superseding design doc §2's older singleton note (written before the
new-rung build existed). `antonym` and `odd_one_out` stay singleton
families -- no new sibling was built for either.

Resulting shape (26 rungs, 13 families):
    modulus         4  mod13(reused), mod17, mod19, mod13_comp
    mid_digit       4  add3_mid(reused), sub3_mid(reused), add4_mid, sub4_mid
    base_repr       3  base7(reused), oct2dec(reused), base12_digitsum
                        (base12 excluded: tier-1 verdict "reject")
    base_arith      2  add_base8(reused), sub_base8
    rotation        2  caesar(reused), caesar_len8
    counting        2  count_div7(reused), count_div13
    reversal        2  reverse_string(reused), rev_string7
    clock           2  clock24(reused), clock24_d999
    antonym         1  antonym(reused)
    odd_one_out     1  odd_one_out(reused)
    rescue_roman    1  roman_sum7
    rescue_collatz  1  collatz_step2
    rescue_isqrt    1  isqrt_gap

This module is the freeze-facing family artifact: `run/power_table.py`
uses it for the MC power table's family-size vector, and the analysis-
stage family-cluster bootstrap will use it too.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent   # experiments/exp2c
ITEMS_DIR = HERE / "battery" / "items"
SCREEN_DIR = HERE / "results" / "screen"

# The 12 reused 2b survivors (results/reuse_manifest.json's `survivors`
# keys) mapped to the family they join per the ruling above. Verified
# against the committed manifest by test_family_map.py.
REUSED_FAMILIES: dict[str, str] = {
    "mod13": "modulus",
    "add3_mid": "mid_digit",
    "sub3_mid": "mid_digit",
    "base7": "base_repr",
    "oct2dec": "base_repr",
    "add_base8": "base_arith",
    "caesar": "rotation",
    "count_div7": "counting",
    "reverse_string": "reversal",
    "clock24": "clock",
    "antonym": "antonym",
    "odd_one_out": "odd_one_out",
}


def scored_battery_families(items_dir: Path = ITEMS_DIR,
                            screen_dir: Path = SCREEN_DIR) -> dict[str, str]:
    """rung name -> family, for the scored battery.

    New-pool part: every `items_dir/*.json` spec (skipping
    `ejections.json`, a bare JSON record, not a spec dict) whose tier-1
    verdict in `screen_dir/tier1/<name>.json` is "pass". A missing
    verdict file or a "reject" verdict excludes the rung -- screen-aware
    by construction, so an ejected candidate (e.g. `base12`) never enters
    the map even if its item file is still on disk.

    Reused part: `REUSED_FAMILIES` merged in verbatim (the 12 survivors
    have no item file under `items_dir` -- they live under exp2b's frozen
    tree -- so they can't be discovered by the new-pool scan above).
    """
    items_dir = Path(items_dir)
    screen_dir = Path(screen_dir)
    out: dict[str, str] = {}
    for f in sorted(items_dir.glob("*.json")):
        if f.stem == "ejections":
            continue
        verdict_path = screen_dir / "tier1" / f"{f.stem}.json"
        if not verdict_path.exists():
            continue
        verdict = json.loads(verdict_path.read_text())
        if verdict.get("verdict") != "pass":
            continue
        spec = json.loads(f.read_text())
        out[f.stem] = spec["family"]
    out.update(REUSED_FAMILIES)
    return out


def family_sizes(items_dir: Path = ITEMS_DIR,
                 screen_dir: Path = SCREEN_DIR) -> list[int]:
    """Size vector derived from scored_battery_families: rung count per
    family, in order of each family's first appearance."""
    families = scored_battery_families(items_dir, screen_dir)
    counts: dict[str, int] = {}
    for fam in families.values():
        counts[fam] = counts.get(fam, 0) + 1
    return list(counts.values())
