# experiments/exp6/tests/test_referents_6.py
"""The committed records Exp 6 measures itself against, and the known
answers they give: Exp 6's criterion, run on the committed streams,
reproduces every committed tally exactly."""
import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import make_referents_6 as mkr
from experiments.exp6 import records_6 as r6
from experiments.exp6 import referents_6 as rf

# (predictor, tier, rung) -> verified draws in the committed stream
COMMITTED_TALLY = {
    ("pythia_1b", "main", "add_base8"): 644,
    ("pythia_1b", "main", "sub_base8"): 2799,
    ("pythia_1b", "control", "ctrl_copy"): 13460,
    ("pythia_410m", "main", "add_base8"): 964,
    ("pythia_410m", "main", "sub_base8"): 2689,
    ("pythia_410m", "control", "ctrl_copy"): 12787,
    ("olmo2_1b", "main", "add_base8"): 1554,
    ("olmo2_1b", "main", "sub_base8"): 4124,
}


def test_the_gated_units_are_the_eight():
    assert sorted(rf.gated_units()) == sorted(COMMITTED_TALLY)
    with pytest.raises(ValueError):
        rf.committed_draws_path("olmo2_1b", "control", "ctrl_copy")
    with pytest.raises(ValueError):
        rf.committed_draws_path("pythia_1b", "main", "lcs")


@pytest.mark.parametrize("unit", sorted(COMMITTED_TALLY))
def test_verify_6_reproduces_every_committed_tally(unit):
    """The known-answer gate on the criterion: 2c's normalizer is
    imported, not copied, so the anchors and the control score as they
    were committed — to the draw."""
    p, t, r = unit
    shape = r6.tier_shape(p, t)
    rows = rf.committed_rows(p, t, r)
    cap = b6.load_item_file_6(r)
    bits = r6.bits_of(rows, cap, seeds=shape["seeds"])
    assert sum(map(sum, bits)) == COMMITTED_TALLY[unit]
    assert len(rows) == 500 and all(len(b) == shape["k"] for b in bits)
    rec = r6.read_json(rf.committed_record_path(p, t, r))
    assert rec["items_sha256"] == cap["items_sha256"]


def test_the_model_pins():
    from experiments.exp6 import verify_6 as v6
    v6.harness_2c()                        # puts 2b on the path
    from models import PYTHIA_SHAS         # imports torch; the analyzer does not
    assert rf.PYTHIA_COMMIT_6 == {k: PYTHIA_SHAS[k] for k in ("410m", "1b")}
    for p in r6.PREDICTORS_6:
        pin = rf.model_pin(p)
        assert len(pin["commit"]) == 40 and pin["model_sha"] and pin["repo"]
    assert rf.model_pin("pythia_1b")["repo"] == "EleutherAI/pythia-1b"
    assert rf.model_pin("pythia_1b")["model_sha"] == rf.model_pin("pythia_1b")["commit"]
    o = rf.model_pin("olmo2_1b")
    assert o["model_sha"] != o["commit"]             # a tensor digest, measured


def test_anchor_tolerance():
    assert rf.TOL_PER_RUNG_6 == 15 and rf.D_TOLERANCE_6 == 0.03
    ref = {"add_base8": 100, "sub_base8": 200}
    assert rf.anchor_tolerance({"add_base8": 115, "sub_base8": 185}, ref, label="x") == []
    bad = rf.anchor_tolerance({"add_base8": 116, "sub_base8": 200}, ref, label="x")
    assert len(bad) == 1 and "add_base8" in bad[0] and "16 > 15" in bad[0]
    assert len(rf.anchor_tolerance({"add_base8": 100}, ref, label="x")) == 1


def test_gate1b_is_one_function_of_the_counts():
    counts = {f: {"stage1_final": {r: rf.mac_endpoint_count(f, r) for r in b6.ANCHORS_6},
                  "init": {r: rf.mac_count(f, fm.INIT, r) for r in b6.ANCHORS_6}}
              for f in fm.FAMILIES_6}
    g = rf.gate1b_record(counts)
    assert g["pass"] and g["failures"] == [] and set(g["families"]) == set(fm.FAMILIES_6)
    counts["olmo13b"]["init"]["sub_base8"] += 16
    g = rf.gate1b_record(counts)
    assert not g["pass"] and len(g["failures"]) == 1 and "olmo13b/init" in g["failures"][0]
    assert list(rf.gate1b_record({"olmo7b": counts["olmo7b"]})["families"]) == ["olmo7b"]


def test_the_committed_tests_of_2cs_battery():
    want = {("A", "olmo7b"): 0.1548, ("A", "olmo13b"): 0.1261,
            ("A", "smollm3_3b"): 0.1696, ("A", "comma_7b"): 0.1599,
            ("B", "olmo7b"): 0.2204, ("B", "olmo13b"): 0.2045,
            ("B", "smollm3_3b"): 0.2514, ("B", "comma_7b"): 0.2097}
    for (t, f), T in want.items():
        c = rf.committed_test(t, f)
        assert round(c["T"], 4) == T and len(c["eligible"]) == 9
        assert set(b6.ANCHORS_6) <= set(c["per_rung_d"])
        assert "unconditioned" in c["conditioning"]


def test_the_referent_manifest(tmp_path):
    files = rf.referent_files()
    assert len(files) == len(set(files)) == 219 and all(p.is_file() for p in files)
    rec = mkr.build()
    assert rec["n_files"] == 219
    import hashlib
    text = mkr.dumps(rec)
    p = tmp_path / "referents_6.json"
    p.write_text(text)
    pin = hashlib.sha256(text.encode()).hexdigest()
    assert mkr.check_referents(p, sha_pin=pin) == []
    assert any("pinned" in b for b in mkr.check_referents(p, sha_pin="0" * 64))
    rec["files"][next(iter(rec["files"]))] = "0" * 64
    text = mkr.dumps(rec)
    p.write_text(text)
    bad = mkr.check_referents(p, sha_pin=hashlib.sha256(text.encode()).hexdigest())
    assert len(bad) == 1 and "changed" in bad[0]
    del rec["files"][next(iter(rec["files"]))]
    text = mkr.dumps(rec)
    p.write_text(text)
    bad = mkr.check_referents(p, sha_pin=hashlib.sha256(text.encode()).hexdigest())
    assert any("file list" in b for b in bad)
