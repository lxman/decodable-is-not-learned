# experiments/exp6/tests/test_run_6.py
"""`analyze_6.run` at its own door, on a tree that holds nothing: what
each check does when it fails and when it RAISES. A check that raises is
a refusal with its reason, never a crash (2d F-1, 2h F-1)."""
import pytest

from experiments.exp6 import analyze_6 as an
from experiments.exp6 import pins_6 as p6
from experiments.exp6 import records_6 as r6
from experiments.exp6.tests import _world_6 as W


def _boom(*a, **k):
    raise RuntimeError("the check itself failed")


def run(root, **over):
    kw = dict(W.ANALYZE, n_perm=20, n_boot=5)
    kw.update(over)
    v = an.run(root, **kw)                                  # must not raise
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["tests"] is None and v["secondaries"] is None and v["statuses"] is None
    assert v["licensed_sentence"] == an.LICENSED_6["INSUFFICIENT_DATA"]
    return " || ".join(v["referents"]["failures"])


def test_an_empty_tree_is_refused_for_what_it_lacks(tmp_path):
    text = run(tmp_path)
    assert "6 predictor seal" in text and "6 power record" in text
    assert "6 endpoint seal binding: rung sets missing" in text
    for label in ("6 halt", "6 frozen modules", "6 import surface",
                  "6 referent manifest", "6 prereg tag"):
        assert label not in text, label
    assert not [p for p in tmp_path.rglob("*")]             # and nothing is written


@pytest.mark.parametrize("label,patch,over", [
    ("6 halt scan", (r6, "halt_markers"), {}),
    ("6 frozen modules", None, {"frozen_check": _boom}),
    ("6 import surface (entry)", (p6, "check_imports_6"), {"imports_pinned": True}),
    ("6 prereg tag", None, {"tag_exists": _boom}),
    ("6 referent manifest", (an.mkr, "check_referents"), {"referents_sha": "0" * 64}),
    ("6 sealed stages", (an, "load_sealed_stages"), {}),
])
def test_a_check_that_raises_at_the_door_is_a_refusal(tmp_path, monkeypatch, label,
                                                     patch, over):
    if patch is not None:
        monkeypatch.setattr(*patch, _boom)
    text = run(tmp_path, **over)
    assert f"{label}: RuntimeError: the check itself failed" in text


def test_a_build_whose_pins_are_not_filled_is_refused(tmp_path):
    text = run(tmp_path, imports_pinned=None, referents_sha=None)
    assert "6 import surface: not pinned (build incomplete)" in text
    assert "6 referent manifest: not pinned (build incomplete)" in text
    text = run(tmp_path)                                    # the test-only injections
    assert "not pinned" not in text


def test_a_halt_marker_is_a_refusal(tmp_path):
    m = r6.predictor_halt_path(tmp_path)
    m.parent.mkdir(parents=True)
    m.write_text("gate 1-P fired\n")
    assert "6 halt marker: results/predictor/HALTED — a runner halted" in run(tmp_path)


def test_which_pins_ran_is_on_the_record(tmp_path):
    v = an.run(tmp_path, n_perm=20, n_boot=5, **W.ANALYZE)
    assert v["referents"]["pins_active"] == {
        "frozen_modules": False, "import_surface": False, "referent_manifest": False,
        "prereg_tag": False, "seal_tags": False}
    assert v["referents"]["failures"] and v["referents"]["power"] is None
