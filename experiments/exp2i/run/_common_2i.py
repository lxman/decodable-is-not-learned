# experiments/exp2i/run/_common_2i.py
"""Shared runner helpers for exp2i's stage modules (`sample_2i.py`,
`endpoint_2i.py`, `preflight_2i.py`) — process/git introspection and
provenance/lifecycle checks with no experiment-specific logic, factored
out here because they were byte-identical across the three (Task 2
review finding 1). `write_draws` stays copied verbatim in `sample_2i
.py` (ruling 6) — that one is deliberately NOT shared, and is
drift-tested against its exp3 source instead."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXP2I = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2i import battery_2i as bi  # noqa: E402


def stack() -> dict:
    try:
        import torch
        import transformers
        return {"torch": torch.__version__, "transformers": transformers.__version__}
    except ImportError:                     # fakes in tests
        return {"torch": "n/a", "transformers": "n/a"}


def git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()


def assert_provenance() -> None:
    import harness
    got = Path(sys.modules["harness"].__file__).resolve()
    if bi.EXP2C.resolve() not in got.parents:
        raise ImportError(f"harness resolved to {got}, not under {bi.EXP2C}")


def release(model) -> None:
    if model is None:      # a load failure can leave the caller's slot empty
        return
    try:
        import torch
        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:      # noqa: BLE001 — fakes
        pass
