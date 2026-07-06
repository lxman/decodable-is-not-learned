"""Generate and commit the battery item files (design doc §2: the committed file is
the operationalization). Deterministic: fixed per-capability seeds derived from the
spec's position; regeneration reproduces the committed files byte-for-byte.

Usage:  python -m battery.gen_items          (from experiments/exp2)
"""

from __future__ import annotations

from .base import generate_items, save_items
from .generators import SPECS

BASE_SEED = 20260706  # date-stamped, fixed forever


def main():
    for i, spec in enumerate(SPECS):
        payload = generate_items(spec, seed=BASE_SEED + i)
        path = save_items(payload)
        n_e, n_p = len(payload["eval_items"]), len(payload["probe_items"])
        uniq = len({it["question"] for it in payload["eval_items"] + payload["probe_items"]})
        print(f"{spec.name:18} eval={n_e} probe={n_p} unique_q={uniq} -> {path.name}")


if __name__ == "__main__":
    main()
