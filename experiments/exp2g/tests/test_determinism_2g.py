# experiments/exp2g/tests/test_determinism_2g.py
"""I-6: the frozen analyzer is deterministic across a PROCESS boundary,
not just within one interpreter. Build one FORECAST world on disk, run
analyze_2g.run() in two independent subprocesses against it, and
compare the written verdicts byte-for-byte. The seal lambdas
(tag_exists/blob_sha) can't cross a process boundary, so the driver
re-derives them from the world's own predictor_sha256.txt."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from experiments.exp2g.tests import full_shape as fs

REPO = fs.EXP2G.parent.parent

_DRIVER = """
import json, sys
from pathlib import Path
sys.path.insert(0, {repo!r})
from experiments.exp2g import analyze_2g as an
from experiments.exp2g import battery_2g as bg

root = Path({root!r})
sha = (root / "results" / "predictor" / "predictor_sha256.txt").read_text().split()[0]
v = an.run(root=root, n_perm=200, n_boot=50, referents_sha=None,
          with_2d_secondaries=False, tag_exists=lambda t: t == bg.SEAL_TAG,
          blob_sha=lambda t, rel: sha)
Path({out!r}).write_text(json.dumps(v, indent=1, default=an._jsonable))
"""


def _run_once(root: Path, out_path: Path) -> None:
    code = _DRIVER.format(repo=str(REPO), root=str(root), out=str(out_path))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-c", code], cwd=str(REPO),
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"driver subprocess failed: {r.stderr[-4000:]}")


def test_two_process_runs_are_byte_identical(tmp_path):
    root = tmp_path / "world"
    fs.write_world(root, assoc=0.8)      # a W1-shaped FORECAST world
    out1, out2 = tmp_path / "v1.json", tmp_path / "v2.json"
    t0 = time.time()
    _run_once(root, out1)
    _run_once(root, out2)
    elapsed = time.time() - t0
    print(f"[determinism] two subprocess analyzer runs: {elapsed:.1f}s")
    b1, b2 = out1.read_bytes(), out2.read_bytes()
    assert b1 == b2, "two independent processes produced different verdict bytes"
    v1 = json.loads(b1)
    assert v1["verdict"] == "FORECAST"
