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
    loaders can read. Returns `root` (a `Path`)."""
    root = Path(root)
    fs.build_world(root, mode, seed=seed, stage="full")
    v4 = an.run(root=root, write=True, n_boot=200, **exp4_run_kwargs_4b())
    return root, v4
