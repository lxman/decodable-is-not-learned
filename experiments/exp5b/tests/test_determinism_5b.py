# experiments/exp5b/tests/test_determinism_5b.py
"""The cross-process determinism fixture: one SURVIVES world analysed
twice, in two SEPARATE interpreters, must give a byte-identical
`verdict.json` once the one volatile key (`git_sha`, nested under
`"meta"`) is dropped. A multi-threaded BLAS reduction is not
bit-reproducible across processes, which is what `experiments/exp5/
_threads_5.py` pins before numpy is imported — this test is what would
catch that pin going missing.

Experiment 5's own `_SCRIPT` shape: the subprocess applies `full_shape_
5b.apply_shrink_5b(pytest.MonkeyPatch())` (a one-shot process, never
undone), patches `full_shape_5.count_fn_for`/`MODES` the same way
`write_world_5b` does at build time (harmless during a read-only
re-analysis — `analyze_5b.run()` never calls a count function — kept
for parity with the brief), rebuilds `fakes_5.small_slice()` (
deterministic, I/O-free) rather than pickling a live slice across the
process boundary, and calls `analyze_5b.run(...)` with the world's
manifest reconstructed as a Python literal and `exp5_kwargs`
reconstructed from literals (`tag_exists`/`blob_sha`/`is_ancestor`
lambdas re-created in the script, never pickled)."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from experiments.exp5b import battery_5b as b5b
from experiments.exp5b.tests import full_shape_5b as fs5b

pytestmark = pytest.mark.slow

_SCRIPT = '''
import json, sys
import pytest
sys.path.insert(0, {repo!r})
from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5.tests import fakes_5 as fk
from experiments.exp5.tests import full_shape_5 as fs
from experiments.exp5b import analyze_5b as an
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b.tests import full_shape_5b as fs5b
mp = pytest.MonkeyPatch()               # a one-shot process: SIZES_5/etc. shrunk, never undone
fs5b.apply_shrink_5b(mp)
orig_cf = fs.count_fn_for
mp.setattr(fs, "MODES", tuple(fs.MODES) + ("SIGN-ONLY", "CONCENTRATED"))
mp.setattr(fs, "count_fn_for", lambda m, amp_=6: fs5b.count_fn_5b_world(m, amp_, orig_cf))
# the REAL repo tree has no results/power_5b.json yet (no campaign has run) —
# require_prereg_5b's default blobs list names it, so this subprocess (a fresh
# interpreter, none of write_world_5b's in-process wrap) restricts blobs to
# what is actually present on the real disk, exactly as write_world_5b does.
orig_pre = b5b.require_prereg_5b
present = tuple(rel for rel in b5b.INSTRUMENT_BLOBS_5B if (b5b.REPO / rel).is_file())
mp.setattr(b5b, "require_prereg_5b",
          lambda *, tag_exists=None, blob_sha=None, blobs=present:
          orig_pre(tag_exists=tag_exists, blob_sha=blob_sha, blobs=blobs))
manifest = {manifest!r}
exp5_kwargs = dict(tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r),
                   blobs_bound=lambda t, p, **k: [], projection_commit="p1",
                   is_ancestor=lambda a, b: True, seal_tag_commit="s1", power_gate="full",
                   manifest=manifest, sl=fk.small_slice(), n_sample=200, n_boot=100)
v = an.run(root=sys.argv[1], exp5_root=sys.argv[2], write=False, n_sample=200, n_boot=100,
          manifest=manifest, sl=fk.small_slice(), verdict_sha=False, exp5_kwargs=exp5_kwargs,
          projection_commit="p2", prereg_commit="t2", is_ancestor=lambda a, b: True,
          power_gate="full", **fs5b._inj())
print(json.dumps(v, sort_keys=True, allow_nan=False))
'''


@pytest.fixture(scope="module")
def _world(tmp_path_factory, request):
    """`write_world_5b` needs a `monkeypatch` object but the built-in
    fixture is function-scoped; `pytest.MonkeyPatch()` used directly
    (not as a fixture) gives the same API at module scope.
    `request.addfinalizer` undoes it at module teardown regardless of
    how the suite is invoked (Experiment 5's own Review finding 2)."""
    root = tmp_path_factory.mktemp("world_determinism_5b")
    mp = pytest.MonkeyPatch()
    request.addfinalizer(mp.undo)
    w = fs5b.write_world_5b(root, "SURVIVES", monkeypatch=mp)
    return w


def test_two_processes_agree(_world):
    w = _world
    script = w["root5b"].parent / "_det_5b.py"
    script.write_text(_SCRIPT.format(repo=str(b5b.REPO), manifest=w["manifest"]))
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    outs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, str(script), str(w["root5b"]), str(w["root5"])],
                           cwd=str(b5b.REPO), capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr[-4000:]
        outs.append(json.loads(r.stdout))

    def strip(v):
        v = dict(v)
        v.pop("meta", None)
        return v

    a, b = strip(outs[0]), strip(outs[1])
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["verdict"] == "SURVIVES", a
    # confirms the strip is doing real work, not a no-op
    assert "meta" in outs[0] and "git_sha" in outs[0]["meta"]
