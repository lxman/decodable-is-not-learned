"""battery_2d: pins, order, floors — against the committed trees."""
import json

import pytest

from experiments.exp2d import battery_2d as bt


def test_order_pins_against_2c():
    r = bt.check_order_against_2c()
    assert r["n_rungs"] == 34 and r["n_families"] == 16
    assert tuple(r["family_sizes"]) == bt.FAMILY_SIZES
    assert sum(bt.FAMILY_SIZES) == 34


def test_rung_order_is_family_contiguous():
    seen, last = [], None
    for _, f in bt.RUNG_ORDER_2D:
        if f != last:
            assert f not in seen, f"{f} appears in two blocks"
            seen.append(f)
            last = f


def test_every_item_file_loads_and_pins():
    b = bt.load_battery()
    assert len(b) == 34
    for r, cap in b.items():
        assert cap["answer_type"] == bt.ANSWER_TYPE_PIN[r]
        assert len(cap["eval_items"]) == 500
        assert cap["items_sha256"] == bt.ITEMS_SHA_PIN[r]
    assert {c["answer_type"] for c in b.values()} == {"number", "word"}


def test_token_budgets_are_2cs():
    h = bt.harness_2c()
    for r in bt.RUNGS:
        assert bt.max_new_tokens(r) == h.MAX_NEW_TOKENS[bt.ANSWER_TYPE_PIN[r]]
    assert bt.max_new_tokens("reverse_string") == 12
    assert bt.max_new_tokens("sub3_mid") == 8


def test_floors_match_doc_and_are_model_free():
    t = bt.floor_table()
    bt.check_floors_against_doc(t)
    assert t["hamming12"]["floor"] == pytest.approx(0.226)
    assert t["reverse_string"]["floor"] == pytest.approx(0.002)
    assert t["reverse_string"]["n_distinct_answers"] == 500
    assert t["mod13"]["majority_answer"] == "11"
    for r, f in t.items():
        assert f["floor"] >= 1 / 500
        assert f["majority_count"] == round(f["floor"] * 500)


def test_floor_uses_2c_normalization(tmp_path):
    """A number answer written with a comma/sign and a word answer
    with case/punctuation collapse under 2c's normalize before the
    majority is counted."""
    cap = {"answer_type": "number", "eval_items": [
        {"answer": "1,000"}, {"answer": "1000"}, {"answer": "7"}]}
    f = bt.majority_floor(cap)
    assert f["majority_answer"] == "1000" and f["majority_count"] == 2
    cap = {"answer_type": "word", "eval_items": [
        {"answer": "Cat."}, {"answer": "cat"}, {"answer": "dog"}]}
    f = bt.majority_floor(cap)
    assert f["majority_answer"] == "cat" and f["floor"] == pytest.approx(2 / 3)


def test_sha_mismatch_refused(tmp_path, monkeypatch):
    p = tmp_path / "reverse_string.json"
    p.write_text(json.dumps({"name": "reverse_string", "answer_type": "word",
                             "eval_items": [], "shots": []}))
    monkeypatch.setattr(bt, "items_path", lambda r: p)
    with pytest.raises(ValueError, match="sha256"):
        bt.load_item_file("reverse_string")


def test_unknown_rung_refused():
    with pytest.raises(ValueError):
        bt.items_path("base12")   # 2c's screen-ejected candidate


def test_option_copy_descriptive_names_the_six_option_listing_rungs():
    """Build finding (PROGRESS.md): six rungs list the answer among
    options in the question; this descriptive enters no verdict."""
    oc = bt.option_copy_table()
    assert set(oc) == {"antonym6", "antonym", "median5", "median7", "odd6",
                       "odd_one_out"}
    assert oc["median7"]["n_options"] == 7
    assert oc["antonym"]["floor"] == pytest.approx(0.25)
    assert all(v["share_listed"] >= 0.99 for v in oc.values())


def test_answer_type_pin_asserted_against_registry(monkeypatch):
    monkeypatch.setitem(bt.ANSWER_TYPE_PIN, "antonym", "number")
    with pytest.raises(ValueError, match="answer_type"):
        bt.load_item_file("antonym")


def test_probe_order_and_manifest_checks_fire(tmp_path):
    probe = json.loads((bt.EXP2C / "results" / "probe_scores.json").read_text())
    probe["rungs"] = probe["rungs"][::-1]
    bad_probe = tmp_path / "probe.json"
    bad_probe.write_text(json.dumps(probe))
    with pytest.raises(ValueError, match="probe_scores"):
        bt.check_order_against_2c(probe_path=bad_probe)
    man = json.loads((bt.EXP2C / "results" / "reuse_manifest.json").read_text())
    man["survivors"]["mod13"]["item_file"]["sha256"] = "00" * 32
    bad_man = tmp_path / "manifest.json"
    bad_man.write_text(json.dumps(man))
    with pytest.raises(ValueError, match="manifest sha"):
        bt.check_order_against_2c(manifest_path=bad_man)
