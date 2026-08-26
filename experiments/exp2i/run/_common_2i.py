# experiments/exp2i/run/_common_2i.py
"""Shared runner helpers for exp2i's stage modules (`sample_2i.py`,
`endpoint_2i.py`, `preflight_2i.py`) — process/git introspection and
provenance/lifecycle checks with no experiment-specific logic, factored
out here because they were byte-identical across the three (Task 2
review finding 1). `write_draws` stays copied verbatim in `sample_2i
.py` (ruling 6) — that one is deliberately NOT shared, and is
drift-tested against its exp3 source instead.

`ckpt_of`/`checkpoint_record` (Task 4 review finding 2) factor out the
`ckpt` dict and the on-disk checkpoint-record dict that were
byte-for-byte duplicated between `sweep_2i.py`'s `run_gate1`/`run_step`
and (for `ckpt_of` only) `endpoint_2i.py`'s per-`which` loop.
`ckpt_of` reconciles the two loader-info shapes it's fed: `battery_2i
.load_checkpoint`'s (which always carries its own `config_source`) and
`load_thin`'s (which does not — `endpoint_2i.py` built `config_source`
by hand from `commit`; the fallback here reproduces that construction
exactly rather than assuming the field is always present). Every
field's value is unchanged from what each caller computed before this
factor — verified caller by caller, not merely by shape. The
from_config TWIN's `ckpt`/checkpoint-record construction in `sweep_2i
.run_twin` stays bespoke (not routed through either helper): its shape
genuinely differs (`commit=None`, `kind="from_config"`, a tokenizer
source keyed by `config_commit` not `commit`, no `sha256`/
`loading_info`/`download_seconds`), and the review's finding named
only `run_gate1`/`run_step` as the duplicated pair.

Whole-branch review fix wave (2026-08-25): `ckpt_of`'s `repo` is a
REQUIRED keyword argument, not a `bi.REPO_7B` default — every real
caller happens to load OLMo-2 7B today, but the fallback
`config_source`/`tokenizer_source` strings it builds would silently
mislabel a future OLMo-2 1B caller if the repo stayed hardcoded, so
every caller threads its own `repo=` through explicitly."""

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


def ckpt_of(entry: dict, info: dict, *, repo, revision_fallback=None) -> dict:
    """The `ckpt` dict `item_record_2i` consumes, built identically to
    what `sweep_2i.run_gate1`/`run_step` and `endpoint_2i.run`'s
    per-`which` loop each built inline before this factor. `commit` is
    read from `info` (present and equal to `entry["commit"]` on every
    real loader path) falling back to `entry` itself; `config_source`
    prefers `info`'s own (`load_checkpoint`'s candidate-file path
    always sets one) and otherwise reconstructs `endpoint_2i.py`'s
    exact `f"{repo}@{commit}"` fallback (`load_thin`'s path never sets
    one). `repo` is REQUIRED rather than defaulted to `bi.REPO_7B`:
    every real caller in this build (`sweep_2i.py`'s two call sites,
    `endpoint_2i.py`'s per-`which` loop) happens to load OLMo-2 7B, but
    hardcoding that into the fallback string construction would
    silently mislabel a future OLMo-2 1B caller — so callers thread
    their own repo through explicitly instead. `revision_fallback`
    reproduces `endpoint_2i.py`'s own defensive `entry.get("revision",
    which)` default for a manifest entry that happens to omit
    `revision`; `sweep_2i.py`'s callers never pass it (their entries
    always carry one)."""
    commit = info.get("commit", entry.get("commit"))
    config_source = info.get("config_source") or f"{repo}@{commit}"
    return {"revision": entry.get("revision", revision_fallback), "commit": commit,
           "kind": entry.get("kind", "thin-loader"),
           "files": list(entry.get("files", [])),
           "weight_sha256": info.get("tensor_digest"),
           "config_source": config_source,
           "tokenizer_source": f"{repo}@{commit}"}


def checkpoint_record(*, step_or_which, ckpt: dict, info: dict, seconds: float) -> dict:
    """The on-disk `checkpoint_record_path` payload — the shape
    `sweep_2i.run_gate1`/`run_step` each wrote inline before this
    factor (`run_twin`'s own checkpoint record stays bespoke — see the
    module docstring). `step_or_which` is stored verbatim under
    `"step"`; the caller owns any int()/`bi.TWIN` normalization."""
    return {"family": bi.FAMILY, "size": bi.SIZE_OUT, "step": step_or_which,
           "revision": ckpt["revision"], "commit": ckpt["commit"],
           "sha256": dict(info.get("sha256", {})), "loading_info": info.get("loading_info"),
           "digest": ckpt["weight_sha256"], "download_seconds": round(seconds, 1)}
