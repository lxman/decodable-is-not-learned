"""Import Exp 1's FROZEN probe module unchanged (design doc §5: "the signature
library is imported from experiments/exp1/signatures/ unchanged; any change to it
for Exp 2 needs is a new function, never an edit").

This shim adds experiments/exp1 to sys.path and re-exports. Nothing else. If Exp 2
ever needs different probe behavior, it gets a new function HERE, and the ledger
says why — signatures/probe.py is never edited.
"""

from __future__ import annotations

import sys
from pathlib import Path

EXP1_DIR = str(Path(__file__).resolve().parent.parent / "exp1")
if EXP1_DIR not in sys.path:
    sys.path.insert(0, EXP1_DIR)

from signatures.probe import probe_below_threshold  # noqa: E402
from signatures.schema import ProbeResult  # noqa: E402

__all__ = ["probe_below_threshold", "ProbeResult"]
