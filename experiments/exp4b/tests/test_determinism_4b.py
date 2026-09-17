# experiments/exp4b/tests/test_determinism_4b.py
"""Cross-process determinism (Task 6 brief's Step 4, carried item (b)):
two SEPARATE processes run `analyze_4b.run(write=True, B=200,
n_sim_ext=10)` against the SAME exp4-shaped tree and must write
byte-identical `verdict.json`/`placebo_4b.json`/`power_ext_4b.json`.

Uses the FOLLOWS world (`conftest.py`'s session-scoped `_follows_
world_4b`), not "leads": "leads" hits the design §4 feasibility floor
and never draws a placebo battery, so it never writes `placebo_4b.
json`/`power_ext_4b.json` at all -- there would be nothing there to
compare. "follows" clears the floor and completes the pipeline
(`test_full_shape_4b.py::test_follows_world_reaches_not_
distinguishable_or_marginal`), so all three files exist on every run.

`root4` (the shared follows-world tree) is read-only here -- `analyze_
4b.run()` never writes into `root4`, only into `root4b` -- so both
subprocesses point at the SAME `root4` directory (no `fresh_copy_4b`
needed) with two DIFFERENT `root4b` tmp directories, one per
subprocess. `_threads_4`'s BLAS-thread pinning (imported before numpy
in every exp4b module) is what makes a multi-threaded reduction
bit-reproducible across processes in the first place -- the same
reason `experiments/exp4/tests/test_full_shape_4.py`'s own
`test_determinism_fixture_two_processes` exists."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402

_DET_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, {repo!r})
from experiments.exp2g import battery_2g as bg
from experiments.exp4 import battery_4
from experiments.exp4.tests import full_shape as fs
from experiments.exp4b import analyze_4b as an4b

def blob_sha(tag, rel):
    p = battery_4.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None

root4 = Path(sys.argv[1])
root4b = Path(sys.argv[2])
v = an4b.run(root4b=root4b, root4=root4, write=True, B=200, n_sim_ext=10, power_gate="full",
            tag_exists=lambda t: True, blob_sha=blob_sha, referents_sha=False,
            imports_pinned=False, frozen_check=lambda: None,
            expected_n_sim=fs.WORLD_POWER_N_SIM_4)
# run()'s own gate-4 block prints a wall-clock timing line to stdout
# (`4b gate 4: power record reproduction took {{seconds}}s ...`) --
# non-deterministic by construction, so the verdict is marked with a
# distinguishing prefix and read off the LAST matching line rather
# than compared as the whole of stdout.
print("DETERMINISM_VERDICT=" + v["verdict"])
"""


@pytest.mark.slow
def test_determinism_two_processes_same_follows_world(_follows_world_4b, tmp_path):
    root4, v4 = _follows_world_4b
    assert v4["verdict"] == "FOLLOWS", v4["reason"]

    script = tmp_path / "_det4b.py"
    script.write_text(_DET_SCRIPT.format(repo=str(battery_4.REPO)))

    roots4b = [tmp_path / "run0" / "4b", tmp_path / "run1" / "4b"]
    verdicts = []
    for root4b in roots4b:
        r = subprocess.run([sys.executable, str(script), str(root4), str(root4b)],
                           cwd=str(battery_4.REPO), capture_output=True, text=True, check=True)
        # run()'s own gate-4 block prints a wall-clock timing line to
        # stdout ahead of the script's own verdict line -- non-
        # deterministic by construction (the two subprocesses' power
        # record reproduction takes very slightly different wall time),
        # so only the marked verdict line is read, never the whole of
        # stdout.
        marked = [ln for ln in r.stdout.splitlines() if ln.startswith("DETERMINISM_VERDICT=")]
        assert marked, r.stdout
        verdicts.append(marked[-1][len("DETERMINISM_VERDICT="):])

    assert verdicts[0] == verdicts[1]
    assert verdicts[0] != "INSUFFICIENT_DATA", verdicts

    v_path_0 = battery_4b.verdict_path_4b(roots4b[0])
    v_path_1 = battery_4b.verdict_path_4b(roots4b[1])
    p_path_0 = battery_4b.placebo_record_path_4b(roots4b[0])
    p_path_1 = battery_4b.placebo_record_path_4b(roots4b[1])
    pe_path_0 = battery_4b.power_ext_path_4b(roots4b[0])
    pe_path_1 = battery_4b.power_ext_path_4b(roots4b[1])

    for p in (v_path_0, v_path_1, p_path_0, p_path_1, pe_path_0, pe_path_1):
        assert p.is_file(), p

    # Raw file bytes, no normalization: `git_sha` is stable across
    # these two calls (same repo state, no commit happens in between),
    # so nothing needs stripping for the files to be byte-identical --
    # unlike exp4's own determinism fixture, which only ever compared
    # the RETURNED dict (re-serialized, `git_sha` popped defensively)
    # and never the files on disk, this asserts the committed FILES
    # themselves are identical, per the brief.
    v0, v1 = v_path_0.read_bytes(), v_path_1.read_bytes()
    if v0 != v1:
        a, b = json.loads(v0), json.loads(v1)
        assert a.get("git_sha") == b.get("git_sha"), "git_sha itself differed between runs"
        raise AssertionError("verdict.json differs between the two processes")
    assert p_path_0.read_bytes() == p_path_1.read_bytes()
    assert pe_path_0.read_bytes() == pe_path_1.read_bytes()
