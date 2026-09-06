# experiments/exp2n/analyze_2n.py
"""STUB (Task 2): only `_endpoint_seal_paths_2n`; Task 3 replaces this
file with the real analyzer and keeps the function byte-identical."""
from __future__ import annotations

import sys
from pathlib import Path

EXP2N = Path(__file__).resolve().parent
if str(EXP2N.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2N.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402


def _endpoint_seal_paths_2n(root) -> list:
    paths = [bn.rung_set_path(root), bn.power_path(root)]
    for which in bn.ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            paths.append(bn.endpoint_record_path(root, which, r))
    return paths
