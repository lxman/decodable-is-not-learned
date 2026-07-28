"""Exp 2c uses Exp 2b's frozen instrument verbatim (design §3: carried
frozen, certified by 2b gate-review ruling (a)). This module is the ONLY
sanctioned access path: it puts experiments/exp2b on sys.path exactly the
way exp2b's own runners do and re-exports the frozen callables. Never
copy, never edit."""

import sys
from pathlib import Path

EXP2B = Path(__file__).resolve().parent.parent / "exp2b"
if str(EXP2B) not in sys.path:
    sys.path.insert(0, str(EXP2B))

from probe_starved import probe_starved  # noqa: E402
import splits  # noqa: E402,F401  (starving-split machinery, frozen)

FLOORS = {"410m": 18 / 2501, "1b": 14 / 2501}
N_PERM_FULL = 2500
N_PERM_SCREEN = 500
SEEDS_FULL = range(5)
SEEDS_SCREEN = range(2)
SIZES = ("410m", "1b")
