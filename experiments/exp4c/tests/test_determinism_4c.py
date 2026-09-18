# experiments/exp4c/tests/test_determinism_4c.py
"""The cross-process determinism fixture: one world analysed twice, in
two SEPARATE interpreters, must give a byte-identical `verdict.json`
once the three wall-clock/commit fields are dropped. A multi-threaded
BLAS reduction is not bit-reproducible across processes, which is what
`experiments/exp4/_threads_4.py` pins before numpy is imported; this
test is what would catch that pin going missing."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from experiments.exp4c import battery_4c as bc
from experiments.exp4c.tests import full_shape_4c as fs4c

pytestmark = pytest.mark.slow

_SCRIPT = '''
import json, sys
sys.path.insert(0, {repo!r})
from experiments.exp4c import battery_4c as bc
from experiments.exp4c.tests import full_shape_4c as fs4c
from experiments.exp4c import analyze_4c as an
bc.INSTRUMENT_BLOBS_4C = fs4c.existing_instrument_blobs_4c()
v = an.run(root=sys.argv[1], root4=sys.argv[2], **fs4c.world_run_kwargs_4c())
print(json.dumps(v, sort_keys=True, allow_nan=False))
'''


@pytest.fixture(scope="module")
def _world(tmp_path_factory):
    root = tmp_path_factory.mktemp("world_determinism")
    return fs4c.build_world(root / "root4c", root / "root4", "replicates", seed=0)


def test_two_processes_agree(_world, tmp_path):
    script = tmp_path / "_det_4c.py"
    script.write_text(_SCRIPT.format(repo=str(bc.REPO)))
    outs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, str(script), str(_world["root4c"]),
                            str(_world["root4"])],
                           cwd=str(bc.REPO), capture_output=True, text=True, check=True)
        outs.append(json.loads(r.stdout))

    def strip(v):
        v = dict(v)
        for k in ("git_sha", "seconds", "elapsed"):
            v.pop(k, None)
        return v

    a, b = strip(outs[0]), strip(outs[1])
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["verdict"] == "REPLICATES"
