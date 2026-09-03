# experiments/exp2m/analyze_2m.py
"""STUB (Task 2): only `_endpoint_seal_paths_2m`; Task 3 replaces this
file with the real analyzer and keeps the function byte-identical."""
from __future__ import annotations

import sys
from pathlib import Path

EXP2M = Path(__file__).resolve().parent
if str(EXP2M.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2M.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402


def _endpoint_seal_paths_2m(root) -> list:
    paths = [bm.rung_set_path(root), bm.power_path(root)]
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            paths.append(bm.endpoint_record_path(root, which, r))
    return paths
