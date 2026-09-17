# experiments/exp4b/tests/full_shape_4b.py
"""Builds a synthetic exp4-shaped tree (`experiments/exp4/tests/
full_shape.build_world`) and runs `analyze_4.run(write=True, ...)` on
it with `test_full_shape_4.py`'s own stand-ins, so the returned root
carries a real, self-consistent `verdict.json`/`eligibility_4.json`/
`power_4.json` -- exp4b's `analyze_4b.run(root4=<that root>, ...)` can
then be gated/calibrated against it exactly as it would the real
closed tree, with zero real-tree contact. `stage="full"` sweeps the
real 92-point grid regardless of `mode` (`full_shape.build_world`'s
own docstring: "structurally complete, behaviourally restricted"),
~11-13 minutes per call."""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4.tests import full_shape as fs  # noqa: E402


def blob_sha_4b(tag, rel):
    """`test_full_shape_4.py`'s own fake: the 'tag-bound' sha IS the
    file's own sha, so `require_prereg_4`'s equality check passes
    without a real git tag -- exp4b's own `battery_4b.require_prereg_4b`
    equality check has the identical shape, so this same fake covers
    both."""
    p = battery_4.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def exp4_run_kwargs_4b():
    """The stand-ins `analyze_4.run()` needs to accept a world tree
    without a real git tag (`test_full_shape_4.py`'s own
    `_run_kwargs()`)."""
    return dict(tag_exists=lambda t: True, blob_sha=blob_sha_4b,
               blobs_bound=lambda tag, paths, repo_root=None: [],
               referents_sha=False, imports_pinned=False,
               expected_n_sim=fs.WORLD_POWER_N_SIM_4)


def build_world_4b(root, mode: str, *, seed=0) -> Path:
    """`full_shape.build_world(root, mode, seed=seed, stage='full')`
    then `analyze_4.run(root=root, write=True, n_boot=200, ...)` with
    the stand-ins above, so the returned root carries a real
    `verdict.json`/`eligibility_4.json`/`power_4.json` exp4b's own
    loaders can read. Returns `(root, v4)`.

    Task 6 (mutation-confirmation infrastructure): when the
    `EXP4B_WORLD_CACHE` environment variable names a scratch directory,
    a build for a given `(mode, seed)` is written there ONCE (a
    `_BUILD_COMPLETE` marker file gates a genuine completion) and every
    later call for the SAME `(mode, seed)` `shutil.copytree`s the
    cached tree into `root` instead of re-running `full_shape.
    build_world`'s ~11-13 minute sweep generation, reading `v4` back
    off the copy's own `verdict.json` rather than re-running `analyze_
    4.run()` too (both already committed to the cache by the first,
    genuine build). Never used when the env var is unset -- every
    existing caller (the test suite's own fixtures) is unaffected. The
    cache directory itself is scratch and must never be committed."""
    root = Path(root)
    cache_root = os.environ.get("EXP4B_WORLD_CACHE")
    if not cache_root:
        fs.build_world(root, mode, seed=seed, stage="full")
        v4 = an.run(root=root, write=True, n_boot=200, **exp4_run_kwargs_4b())
        return root, v4

    cache_dir = Path(cache_root) / f"{mode}_seed{seed}"
    marker = cache_dir / "_BUILD_COMPLETE"
    if marker.is_file():
        shutil.copytree(cache_dir, root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("_BUILD_COMPLETE"))
        v4 = json.loads(battery_4.verdict_path(root).read_text())
        return root, v4

    fs.build_world(root, mode, seed=seed, stage="full")
    v4 = an.run(root=root, write=True, n_boot=200, **exp4_run_kwargs_4b())
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root, cache_dir, dirs_exist_ok=True)
    marker.touch()
    return root, v4
