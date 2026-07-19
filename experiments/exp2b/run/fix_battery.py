"""Fix the scored battery from completed M1 inclusion results (design §2).

Usage:  python -m run.fix_battery [--dry-run]

Preregistered inclusion rule, frozen at exp2b-preregistered — applied, not chosen,
here: a candidate enters the scored battery iff the CP-95 UPPER bound on its
normalized argmax margin at pythia-1b is < 0.25. Positive controls are never
scored. Minimum 20 survivors or the experiment reports INSUFFICIENT_DATA rather
than running a smaller test. Battery order is the fixed order of the item files.

Writes battery/items/scored_battery.json; refuses to overwrite (battery
membership cannot change after Stage 1 begins — anti-garden-path, design §3).
"""

from __future__ import annotations

import json
import sys

from battery.base import ITEMS_DIR, load_items
from harness import normalized_margin, result_path
from run.run_inclusion import all_capability_names

INCLUSION_UB = 0.25   # frozen, design §2
MIN_BATTERY = 20      # frozen, design §4 gate 5 / §5


def main() -> None:
    dry = "--dry-run" in sys.argv
    out = ITEMS_DIR / "scored_battery.json"
    if out.exists() and not dry:
        sys.exit(f"{out} already exists — battery membership is fixed (design §3)")

    scored, rows = [], []
    for name in all_capability_names():
        cap = load_items(name)
        trained = json.loads(result_path("inclusion", "1b", "trained", name).read_text())
        chance = json.loads(result_path("inclusion", "1b", "untrained", name).read_text())
        m = normalized_margin(trained, chance)
        ub = m["margin_cp95"][1]
        included = bool(cap["scored"]) and ub < INCLUSION_UB
        rows.append((name, cap["scored"], m["margin"], ub, included))
        if included:
            scored.append(name)

    for name, is_cand, margin, ub, inc in rows:
        tag = "scored" if inc else ("control" if not is_cand else "EXCLUDED (above threshold)")
        print(f"[m1] {name:16s} margin={margin:+.4f} ub={ub:+.4f}  {tag}", flush=True)
    print(f"[m1] scored battery: {len(scored)}/{sum(1 for r in rows if r[1])} candidates",
          flush=True)

    if len(scored) < MIN_BATTERY:
        sys.exit(f"[m1] INSUFFICIENT_DATA: {len(scored)} < {MIN_BATTERY} — "
                 "report this, do not shrink the test (design §4)")
    if not dry:
        out.write_text(json.dumps(scored, indent=1))
        print(f"[m1] wrote {out} — commit this file to fix the battery", flush=True)


if __name__ == "__main__":
    main()
