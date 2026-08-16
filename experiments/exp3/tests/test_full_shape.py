"""Pytest face of the full-shape rule (design §2 item 1, §8, Open item
4): every terminal branch of the frozen verdict tree, reached end to
end through the frozen loaders on complete synthetic worlds — plus the
malformed-battery hard errors that must fire BEFORE any gate.
"""
import pytest

from experiments.exp3 import analyze_3 as a
from experiments.exp3.tests import full_shape as fs


@pytest.mark.parametrize("name", sorted(fs.BATTERIES))
def test_battery_reaches_its_terminal(tmp_path, name):
    spec = fs.BATTERIES[name]
    root = fs.write_world(tmp_path, **spec.get("world", {}))
    out = fs.run_battery(root)
    assert out["verdict"] == spec["expect"], out.get("reason")
    assert spec.get("expect_reason", "") in out["reason"]
    assert out["contaminated"] == spec.get("expect_contaminated", [])
    for i, chk in enumerate(spec.get("check", [])):
        assert chk(out), f"{name} provision check {i} failed"


def test_every_verdict_terminal_is_reachable():
    """The battery set must span the §6 terminals: all four worlds,
    PARTIAL, and every INSUFFICIENT_DATA route."""
    expected = {fs.BATTERIES[n]["expect"] for n in fs.BATTERIES}
    assert expected == {"ELICITABLE", "BULK-ONLY", "TAIL-ONLY", "WALL",
                        "PARTIAL", "INSUFFICIENT_DATA"}


def test_verdict_refuses_a_short_battery(tmp_path):
    """A missing cell is a malformed battery and a hard error, never a
    verdict: INSUFFICIENT_DATA is a statement about the world, and a
    half-copied directory is not the world."""
    root = fs.write_world(tmp_path)
    mass = a.load_mass_cells(root)
    sampling = a.load_sampling_cells(root)
    redecode = a.load_redecode_cells(root)
    refs = a.load_gate2_referents(root / "gate2")
    floors, margins = a.load_floors(), a.load_probe_margins()
    del sampling[("rev_string7", "410m", "trained")]
    with pytest.raises(ValueError, match="16"):
        a.verdict(mass, sampling, redecode, refs, floors, margins)


def test_verdict_refuses_a_sha_pin_mismatch(tmp_path):
    """Reading 7: a cell not carrying the rung's single §4 item-file
    pin is not a cell of this experiment."""
    root = fs.write_world(tmp_path)
    mass = a.load_mass_cells(root)
    sampling = a.load_sampling_cells(root)
    redecode = a.load_redecode_cells(root)
    refs = a.load_gate2_referents(root / "gate2")
    floors, margins = a.load_floors(), a.load_probe_margins()
    mass[("rev_string7", "410m", "trained")]["items_sha256"] = "DRIFTED"
    with pytest.raises(ValueError, match="items_sha256"):
        a.verdict(mass, sampling, redecode, refs, floors, margins)


def test_verdict_refuses_answer_drift_against_the_referent(tmp_path):
    """Reading 7's second arm: answers must equal the 3b referent's."""
    root = fs.write_world(tmp_path)
    mass = a.load_mass_cells(root)
    sampling = a.load_sampling_cells(root)
    redecode = a.load_redecode_cells(root)
    refs = a.load_gate2_referents(root / "gate2")
    floors, margins = a.load_floors(), a.load_probe_margins()
    cell = sampling[("rev_string7", "410m", "trained")]
    cell["answers"] = list(cell["answers"])
    cell["answers"][0] = "zrevq0"
    with pytest.raises(ValueError, match="answers"):
        a.verdict(mass, sampling, redecode, refs, floors, margins)


def test_run_on_an_empty_results_tree_hard_errors(tmp_path):
    """The freeze checklist's own line: no silent verdict on a missing
    battery."""
    with pytest.raises(FileNotFoundError):
        a.run(tmp_path)
