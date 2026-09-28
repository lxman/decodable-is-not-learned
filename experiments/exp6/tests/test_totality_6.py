# experiments/exp6/tests/test_totality_6.py
"""Totality of the tree (2d F-1, 2h F-1, 2i F-2): whatever a killed
runner, a full disk, a bad sync or a hand can leave in place of a record,
`analyze_6.run` RETURNS — INSUFFICIENT_DATA, with the reason — and never
raises. One file of every kind the analyzer reads, every shape."""
import gzip
import json

import pytest

from experiments.exp6 import analyze_6 as an
from experiments.exp6 import families_6 as fm
from experiments.exp6 import records_6 as r6
from experiments.exp6.run import _common_6 as cm
from experiments.exp6.tests import _world_6 as W
from experiments.exp6.tests.test_worlds_6 import base, battery  # noqa: F401

pytestmark = pytest.mark.slow


def _host(root):
    return json.loads(r6.checkpoint_path(root, "olmo7b", fm.grid("olmo7b")[0])
                      .read_text())["host_sha256"]


KINDS = {
    "predictor record": lambda r: r6.tier_record_path(r, "pythia_1b", "main", "sort3"),
    "predictor seal": r6.seal_path,
    "gate 1-P record": r6.gate1p_path,
    "endpoint record": lambda r: r6.endpoint_record_path(r, "olmo7b", "stage1_final",
                                                          "lcs"),
    "endpoint load record": lambda r: r6.endpoint_load_path(r, "comma_7b", "init"),
    "gate 1(b) record": r6.gate1b_path,
    "rung sets": r6.rung_sets_path,
    "power record": r6.power_path,
    "host record": lambda r: sorted(cm.hosts_dir(r).glob("*.json"))[0],
    "sweep record": lambda r: r6.sweep_record_path(r, "olmo13b", fm.grid("olmo13b")[3],
                                                   "temporal"),
    "checkpoint record": lambda r: r6.checkpoint_path(r, "smollm3_3b",
                                                      fm.grid("smollm3_3b")[5]),
    "gate 1 record": lambda r: r6.gate1_path(r, "olmo7b", _host(r)),
    "gate read record": lambda r: r6.gate_record_path(r, "olmo7b", _host(r),
                                                      r6.SWEEP_CAND, "shapes"),
    "gate load record": lambda r: r6.gate_load_path(r, "olmo7b", _host(r),
                                                    r6.SWEEP_THIN),
}
JSON_SHAPES = {
    "empty": b"", "torn": b'{"rung": "lc', "a list": b"[]", "a full list": b"[1, 2]",
    "null": b"null", "an empty object": b"{}", "a string": b'"x"', "a number": b"7",
    "not utf-8": b"\xff\xfe\x00{", "a directory": None,
}
GZ_SHAPES = {
    "empty": b"", "not gzip": b"plain text\n", "a directory": None,
    "gzip of a torn line": gzip.compress(b'{"item": 0, "draws": {"0": ["a"'),
    "gzip of a list": gzip.compress(b"[1, 2, 3]\n"),
    "gzip of nothing": gzip.compress(b""),
}


def _put(path, raw):
    if raw is None:
        path.unlink()
        path.mkdir()
    else:
        path.write_bytes(raw)


def _refused(root):
    v = an.run(root, n_perm=20, n_boot=5, **W.ANALYZE)     # must not raise
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["referents"]["failures"] and v["tests"] is None
    json.dumps(an.an2i._json_safe(v), default=an.an2i._jsonable, allow_nan=False)
    return v


@pytest.mark.parametrize("kind", sorted(KINDS))
@pytest.mark.parametrize("shape", sorted(JSON_SHAPES))
def test_a_record_in_any_shape_is_a_refusal(base, tmp_path, kind, shape):  # noqa: F811
    root = W.clone(base, tmp_path / "w")
    _put(KINDS[kind](root), JSON_SHAPES[shape])
    _refused(root)


@pytest.mark.parametrize("shape", sorted(GZ_SHAPES))
@pytest.mark.parametrize("unit", [("pythia_1b", "main", "lcs"),
                                  ("olmo2_1b", "main", "add_base8")])
def test_a_draws_file_in_any_shape_is_a_refusal(base, tmp_path, unit, shape):  # noqa: F811
    root = W.clone(base, tmp_path / "w")
    _put(r6.tier_draws_path(root, *unit), GZ_SHAPES[shape])
    _refused(root)


def test_a_truncated_draws_file_at_every_cut(base, tmp_path):  # noqa: F811
    root = W.clone(base, tmp_path / "w")
    p = r6.tier_draws_path(root, "pythia_410m", "main", "sort5")
    raw = p.read_bytes()
    for frac in (0.01, 0.5, 0.99):
        p.write_bytes(raw[:int(len(raw) * frac)])
        _refused(root)


@pytest.mark.parametrize("what", ["results", "results/predictor", "results/endpoint",
                                  "results/sweep", "results/sweep/olmo7b",
                                  "results/hosts"])
def test_a_missing_directory_is_a_refusal(base, tmp_path, what):  # noqa: F811
    import shutil
    root = W.clone(base, tmp_path / "w")
    shutil.rmtree(root / what)
    _refused(root)


def test_an_empty_tree_is_a_refusal(tmp_path):
    _refused(tmp_path)
    (tmp_path / "results").mkdir()
    _refused(tmp_path)


def test_a_file_where_a_directory_belongs(base, tmp_path):  # noqa: F811
    import shutil
    root = W.clone(base, tmp_path / "w")
    d = r6.step_dir(root, "olmo7b", fm.grid("olmo7b")[2])
    shutil.rmtree(d)
    d.write_text("not a directory\n")
    _refused(root)
    h = cm.hosts_dir(root)
    shutil.rmtree(h)
    h.write_text("x")
    _refused(root)
