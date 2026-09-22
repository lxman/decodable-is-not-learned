# experiments/exp5/tests/test_determinism_5.py
"""The cross-process determinism fixture: one MATCHED world analysed
twice, in two SEPARATE interpreters, must give a byte-identical
`verdict.json` once the one volatile key (`git_sha`, nested under
`"meta"` — Task 6's change to `verdict_5`, see `analyze_5.verdict_5`'s
own docstring) is dropped. A multi-threaded BLAS reduction is not
bit-reproducible across processes, which is what `experiments/exp5/
_threads_5.py` pins before numpy is imported; this test is what would
catch that pin going missing.

The world's slice (`fakes_5.small_slice()`) is deterministic and I/O-
free, so each subprocess builds its own copy rather than being handed
the parent process's live numpy-array dict (not JSON-representable as
an argv literal)."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5.tests import full_shape_5 as fs

pytestmark = pytest.mark.slow

_SCRIPT = '''
import json, sys
import pytest
sys.path.insert(0, {repo!r})
from experiments.exp5 import analyze_5 as an
from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5.tests import fakes_5 as fk
from experiments.exp5.tests import full_shape_5 as fs
fs.apply_shrink(pytest.MonkeyPatch())   # a one-shot process: SIZES_5/etc. shrunk, never undone
v = an.run(root=sys.argv[1], write=False, n_sample=200, n_boot=100,
          manifest={manifest!r}, sl=fk.small_slice(),
          tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r),
          blobs_bound=lambda t, p, **k: [],
          projection_commit="p1", is_ancestor=lambda a, b: True, seal_tag_commit="s1",
          power_gate="full")
print(json.dumps(v, sort_keys=True, allow_nan=False))
'''


@pytest.fixture(scope="module")
def _world(tmp_path_factory):
    """`write_world_5` needs a `monkeypatch` object but the built-in
    fixture is function-scoped; `pytest.MonkeyPatch()` used directly
    (not as a fixture) gives the same API at module scope. Never
    undone — this module never needs it reverted, and the process
    exits with the test run."""
    root = tmp_path_factory.mktemp("world_determinism_5")
    mp = pytest.MonkeyPatch()
    w = fs.write_world_5(root, "MATCHED", monkeypatch=mp)
    return root, w


def test_two_processes_agree(_world):
    root, w = _world
    script = root / "_det_5.py"
    script.write_text(_SCRIPT.format(repo=str(b5.REPO), manifest=w["manifest"]))
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    outs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, str(script), str(root)],
                           cwd=str(b5.REPO), capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr[-4000:]
        outs.append(json.loads(r.stdout))

    def strip(v):
        v = dict(v)
        v.pop("meta", None)
        return v

    a, b = strip(outs[0]), strip(outs[1])
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["verdict"] == "MATCHED", a
    # confirms the strip is doing real work, not a no-op
    assert "meta" in outs[0] and "git_sha" in outs[0]["meta"]
