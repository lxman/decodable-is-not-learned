"""Run provenance: git SHA and library versions stamped into every RunRecord.

Uses the Homebrew git explicitly -- on the Mac, /usr/bin/git is a broken Xcode shim
(see environment.md). Falls back to "unknown" rather than raising, so a run in a
detached/dirty state still records SOMETHING traceable instead of crashing.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_GIT = "/opt/homebrew/bin/git"


def git_sha(repo_dir: str | Path | None = None) -> str:
    repo_dir = Path(repo_dir) if repo_dir else Path(__file__).resolve().parent
    try:
        out = subprocess.run(
            [_GIT, "rev-parse", "--short", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True, timeout=10,
        )
        sha = out.stdout.strip()
        if out.returncode == 0 and sha:
            dirty = subprocess.run(
                [_GIT, "status", "--porcelain"],
                cwd=repo_dir, capture_output=True, text=True, timeout=10,
            ).stdout.strip()
            return f"{sha}-dirty" if dirty else sha
    except Exception:
        pass
    return "unknown"


def lib_versions() -> tuple[str, str]:
    import torch
    import transformers
    return torch.__version__, transformers.__version__
