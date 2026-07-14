"""Import Exp 1's FROZEN probe module unchanged (design doc §5: "the signature
library is imported from experiments/exp1/signatures/ unchanged; any change to it
for Exp 2 needs is a new function, never an edit").

Loaded via importlib under the alias `exp1_signatures` — NOT by sys.path
insertion: exp1 has top-level packages (`models`, `configs`) whose names collide
with Exp 2's own modules, and a path insert shadows them for every subsequent
import in the process (this bit the first campaign launch, 2026-07-14: exp1's
`models` package hijacked `from models import PROBE_SIZES`). The alias keeps the
frozen package's internal relative imports working while leaving Exp 2's
namespace untouched.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SIG_DIR = Path(__file__).resolve().parent.parent / "exp1" / "signatures"
_ALIAS = "exp1_signatures"

if _ALIAS not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        _ALIAS, _SIG_DIR / "__init__.py",
        submodule_search_locations=[str(_SIG_DIR)])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[_ALIAS] = pkg
    spec.loader.exec_module(pkg)

_probe = importlib.import_module(f"{_ALIAS}.probe")
_schema = importlib.import_module(f"{_ALIAS}.schema")

probe_below_threshold = _probe.probe_below_threshold
ProbeResult = _schema.ProbeResult

__all__ = ["probe_below_threshold", "ProbeResult"]
