"""Generate the committed battery item files (run under the canonical venv:
`cd experiments/exp2b && ~/emergence-lab/.venv/bin/python -m battery.gen_items`).

Feasibility ejection (design §2 field 5): a spec that cannot reach its item
counts (question space too small under the uniqueness rule) or cannot construct
a valid starving split for all 5 seeds is EJECTED — recorded in
items/ejections.json with the reason, never silently patched. The reserve
absorbs ejections; the scored battery is whatever survives inclusion (M1) on
the survivors.

BASE_SEED and the per-spec seed derivation mirror Exp 2 (ledgered convention:
seed = BASE_SEED + spec_index over the FULL candidate list including ejected
specs, so late ejections never shift earlier capabilities' item streams).
"""

from __future__ import annotations

import json

from splits import SplitInfeasible

from .base import ITEMS_DIR, generate_items, save_items
from .generators import SPECS

BASE_SEED = 20260718


def main() -> None:
    ejections = {}
    for i, spec in enumerate(SPECS):
        try:
            payload = generate_items(spec, BASE_SEED + i)
        except (SplitInfeasible, RuntimeError) as e:
            ejections[spec.name] = str(e)
            print(f"[gen] EJECTED {spec.name}: {e}", flush=True)
            continue
        path = save_items(payload)
        feas = payload.get("feasibility", {})
        per_seed = feas.get("per_seed", {})
        n_val = min((s["n_val"] for s in per_seed.values()), default="-")
        print(f"[gen] {spec.name}: {len(payload['eval_items'])} eval / "
              f"{len(payload['probe_items'])} probe -> {path.name}  "
              f"(min val across seeds: {n_val})", flush=True)
    ITEMS_DIR.mkdir(exist_ok=True)
    (ITEMS_DIR / "ejections.json").write_text(json.dumps(ejections, indent=1))
    print(f"[gen] done; {len(ejections)} ejection(s) recorded", flush=True)


if __name__ == "__main__":
    main()
