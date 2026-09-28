# experiments/exp6/tests/test_battery_6.py
import hashlib
import json

import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import floors_6 as f6
from experiments.exp6 import strata_6 as s6
from experiments.exp6 import verify_6 as v6
from experiments.exp6.battery import audit_bbkeys_6 as au
from experiments.exp6.battery import generate as gen
from experiments.exp6.battery import measure_tokens_6 as mt
from experiments.exp6.battery import spec as sp


@pytest.fixture(scope="module")
def battery():
    return b6.load_battery_6()


def test_rung_tables_agree():
    assert b6.RUNGS_6 == gen.RUNG_ORDER_6 and len(b6.RUNGS_6) == 17
    assert len(b6.ALL_RUNGS_6) == 20
    for table in (b6.TASK_OF, b6.WEI_CLASS_OF, b6.RUNG_TYPE_OF, b6.ANSWER_TYPE_OF,
                  b6.ITEMS_SHA_PIN_6, s6.COVARIATE_OF_6, s6.STRATA_COUNT_PIN_6,
                  f6.FLOOR_PIN_6):
        assert set(table) == set(b6.RUNGS_6)
    for r in b6.RUNGS_6:
        s = sp.SPECS_6[r]
        assert (s.task, s.wei_class, s.rung_type, s.answer_type, s.n_options) == \
            (b6.TASK_OF[r], b6.WEI_CLASS_OF[r], b6.RUNG_TYPE_OF[r],
             b6.ANSWER_TYPE_OF[r], b6.N_OPTIONS_OF.get(r))
    assert sorted(set(b6.TASK_OF.values())) == sorted(
        {"modified_arithmetic", "word_unscrambling", "word_sorting",
         "international_phonetic_alphabet_transliterate", "logical_deduction",
         "ascii_word_recognition", "geometric_shapes", "temporal_sequences",
         "cs_algorithms", "unit_interpretation"})
    assert sum(1 for r in b6.RUNGS_6 if b6.WEI_CLASS_OF[r] == "E.2") == 10


def test_committed_files_load_under_their_pins(battery):
    assert set(battery) == set(b6.ALL_RUNGS_6)
    for r in b6.RUNGS_6:
        cap = battery[r]
        assert cap["items_sha256"] == b6.ITEMS_SHA_PIN_6[r] and cap["battery"] == "6"
        assert set(cap["eval_items"][0]) == {"question", "answer", "bb_sha256", "meta"}
        assert cap["provenance"]["bigbench_commit"] == \
            "092b196c1f8f14a54bbc62f24759d43bde46dd3b"
        # the file was written behind the audited gate, and says which audit
        assert cap["provenance"]["bbkey_audit_sha256"] == au.AUDIT_6_SHA256
    for r in b6.ANCHORS_6 + (b6.CONTROL_6,):
        assert battery[r]["battery"] == "2c" and len(battery[r]["eval_items"]) == 500
    assert battery["ctrl_copy"]["items_sha256"] == b6.CONTROL_SHA256
    assert battery["add_base8"]["answer_type"] == "number"


def test_a_tampered_item_file_is_refused(tmp_path, monkeypatch):
    src = b6.items_path_6("sort3")
    d = json.loads(src.read_text(encoding="utf-8"))
    d["eval_items"][0]["answer"] = "zzz"
    (tmp_path / "sort3.json").write_text(gen.dumps(d), encoding="utf-8")
    monkeypatch.setattr(b6, "ITEMS_DIR", tmp_path)
    with pytest.raises(ValueError, match="not the committed items"):
        b6.load_item_file_6("sort3")


def test_a_file_whose_header_disagrees_with_the_tables_is_refused(tmp_path, monkeypatch):
    d = json.loads(b6.items_path_6("lcs").read_text(encoding="utf-8"))
    d["answer_type"] = "word"
    text = gen.dumps(d)
    (tmp_path / "lcs.json").write_text(text, encoding="utf-8")
    monkeypatch.setattr(b6, "ITEMS_DIR", tmp_path)
    monkeypatch.setitem(b6.ITEMS_SHA_PIN_6, "lcs",
                        hashlib.sha256(text.encode("utf-8")).hexdigest())
    with pytest.raises(ValueError, match="answer_type"):
        b6.load_item_file_6("lcs")


def test_unknown_rung_is_refused():
    with pytest.raises(ValueError):
        b6.items_path_6("logic_grid")
    with pytest.raises(ValueError):
        b6.items_path_6("add_base8")


@pytest.mark.slow
def test_regeneration_is_byte_identical():
    ctx = gen.context()
    for r in b6.RUNGS_6:
        text = gen.dumps(gen.payload(r, ctx))
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == \
            b6.ITEMS_SHA_PIN_6[r], r
        assert text.encode("utf-8") == b6.items_path_6(r).read_bytes(), r


def test_every_answer_verifies_against_itself_and_is_read_whole(battery):
    for r in b6.RUNGS_6:
        at = battery[r]["answer_type"]
        for it in battery[r]["eval_items"]:
            assert v6.verify_6(" " + it["answer"] + "\n\nQ: next", it["answer"], at)
            assert v6.exact_under_criterion(it["answer"], at)
        for q, a in battery[r]["shots"]:
            assert v6.exact_under_criterion(a, at)
            assert q not in {it["question"] for it in battery[r]["eval_items"]}


def test_budgets(battery):
    want = {"modarith_add1": 8, "lcs": 8, "unit_interp2": 8, "unscramble_long": 12,
            "shapes": 12, "deduction5": 12, "temporal": 12, "sort3": 16,
            "sort5": 16, "ipa_word": 24, "add_base8": 8, "sub_base8": 8,
            "ctrl_copy": 12}
    assert {r: b6.max_new_tokens_6(r) for r in want} == want


def test_token_record_binds_the_items_and_clears_the_budgets(battery):
    rec = json.loads(mt.OUT.read_text())
    assert set(rec["rungs"]) == set(b6.ALL_RUNGS_6)
    assert set(rec["tokenizers"]) == {"pythia_1b", "pythia_410m", "olmo2_1b",
                                      "olmo2_7b", "olmo2_13b", "smollm3_3b",
                                      "comma_7b"}
    assert rec["tokenizers"] == mt.tokenizer_revisions()
    for r, t in rec["rungs"].items():
        assert t["items_sha256"] == battery[r]["items_sha256"], r
        assert t["budget"] == b6.max_new_tokens_6(r), r
        assert set(t["answer_tokens_max"]) == set(rec["tokenizers"])
        assert max(t["answer_tokens_max"].values()) + 2 <= t["budget"], r
        assert max(t["prompt_tokens_max"].values()) + t["budget"] <= 2048, r


# ---------------------------------------------------------------- floors
def test_floors(battery):
    table = f6.floor_table_6(battery)
    assert f6.check_floor_pins_6(table) == {r: "PASS" for r in b6.RUNGS_6}
    want = {"deduction3": 1 / 3, "deduction5": .2, "shapes": .1, "temporal": .25,
            "unit_interp1": .2, "unit_interp2": .2, "lcs": .1,
            "unscramble_short": .002, "sort5": .002}
    for r, f in want.items():
        assert table[r]["floor"] == pytest.approx(f)
    assert table["add_base8"]["floor"] == pytest.approx(.028)   # 2d's committed floors
    assert table["sub_base8"]["floor"] == pytest.approx(.056)
    assert all(0 < t["floor"] < 1 for t in table.values())


def test_floor_refuses_tampered_options(battery):
    cap = json.loads(json.dumps(battery["deduction3"]))
    q = cap["eval_items"][3]["question"]
    cap["eval_items"][3]["question"] = q.rsplit(", ", 1)[0]       # one option lost
    with pytest.raises(ValueError, match="options"):
        f6.rung_floor_6(cap)
    cap = json.loads(json.dumps(battery["sort3"]))
    cap["eval_items"][0]["question"] += "\nOptions: a, b, c"
    with pytest.raises(ValueError, match="free-form"):
        f6.rung_floor_6(cap)


def test_the_bar_is_2ds(battery):
    assert f6.clears(60, 500, .1)["significant"] is False          # p ≈ .08
    assert f6.clears(80, 500, .1)["significant"] is True
    assert f6.clears(9, 500, .002)["significant"] is True


# ---------------------------------------------------------------- strata
def test_strata(battery):
    table = s6.build_table_6(battery)
    assert set(table) == set(b6.RUNGS_6) | set(b6.ANCHORS_6)
    done = s6.check_strata_pins_6(table)
    assert set(done) == set(table) and set(done.values()) == {"PASS"}
    for r, t in table.items():
        assert len(t["strata"]) == 500 and sum(t["counts"].values()) == 500
        assert min(t["counts"].values()) >= s6.MIN_STRATUM
        assert all(isinstance(s, str) for s in t["strata"])
    assert table["modarith_mul1"]["counts"] == {"1": 10, "2": 21, "3": 136, "4": 333}
    assert set(table["shapes"]["counts"].values()) == {50}
    json.dumps(table)                                           # serialisable


def test_a_small_ordinal_level_merges_into_its_neighbour():
    items = ([{"answer": "2", "meta": {"a": 1, "b": 1}}] * 5
             + [{"answer": "26", "meta": {"a": 5, "b": 5}}] * 95
             + [{"answer": "2501", "meta": {"a": 50, "b": 50}}] * 400)
    t = s6.strata_for_6({"name": "modarith_mul1", "eval_items": items})
    assert t["counts"] == {"1+2": 100, "4": 400}
    assert t["levels_raw"] == {"1": 5, "2": 95, "4": 400}
    assert t["strata"][0] == t["strata"][5] == "1+2"


def test_anchor_strata_are_2gs_committed_rows(battery):
    committed = json.loads((b6.EXPERIMENTS / "exp2g" / "results" / "predictor" /
                            "strata.json").read_text())
    table = s6.build_table_6(battery)
    for r in b6.ANCHORS_6:
        assert table[r]["strata"] == committed[r]["strata"]
        assert table[r]["counts"] == committed[r]["counts"]


def test_frequency_terciles_are_exact():
    items = [{"meta": {"rank": r}} for r in (50, 10, 40, 20, 30, 60, 5, 7, 9)]
    groups = ["a"] * 6 + ["b"] * 3
    assert s6.frequency_terciles(items, groups) == [2, 0, 1, 0, 1, 2, 0, 1, 2]


def test_a_thin_stratum_is_refused(battery):
    cap = json.loads(json.dumps(battery["shapes"]))
    for it in cap["eval_items"][:45]:                 # leave 5 circles
        if it["answer"] == "circle":
            it["answer"] = "line"
    n = 0
    for it in cap["eval_items"]:
        if it["answer"] == "circle":
            n += 1
            if n > 5:
                it["answer"] = "line"
    with pytest.raises(ValueError, match="strata below"):
        s6.strata_for_6(cap)


# ------------------------------------------------- refusals (each one run)
def test_the_pin_checks_refuse_a_table_that_moved(battery):
    floors = f6.floor_table_6(battery)
    floors["lcs"] = dict(floors["lcs"], majority_count=49, floor=0.098)
    with pytest.raises(ValueError, match="lcs: floor"):
        f6.check_floor_pins_6(floors)
    table = s6.build_table_6(battery)
    table["sort3"] = dict(table["sort3"], counts={"0": 166, "1": 167, "2": 167})
    with pytest.raises(ValueError, match="sort3: strata counts"):
        s6.check_strata_pins_6(table)
    table = s6.build_table_6(battery)
    table["sort3"] = dict(table["sort3"], strata=table["sort3"]["strata"][:-1])
    with pytest.raises(ValueError, match="sort3: 499 labels"):
        s6.check_strata_pins_6(table)


def test_floor_refuses_options_that_omit_the_answer(battery):
    cap = json.loads(json.dumps(battery["temporal"]))
    it = cap["eval_items"][3]
    body, opts = it["question"].split(sp.OPTIONS_PREFIX)
    opts = ["1am to 2am" if o == it["answer"] else o for o in opts.split(", ")]
    it["question"] = body + sp.OPTIONS_PREFIX + ", ".join(opts)
    with pytest.raises(ValueError, match="temporal item 3"):
        f6.rung_floor_6(cap)


def test_a_tampered_control_is_refused(tmp_path, monkeypatch):
    raw = b6.CONTROL_PATH.read_bytes()
    bad = tmp_path / "ctrl_copy.json"
    bad.write_bytes(raw.replace(b"ctrl_copy", b"ctrl_copz", 1))
    monkeypatch.setattr(b6, "CONTROL_PATH", bad)
    with pytest.raises(ValueError, match="against the pin"):
        b6.load_item_file_6("ctrl_copy")


# ---------------------------------------------------- structure levels
def test_structure_levels_are_what_they_say(battery):
    table = s6.build_table_6(battery)
    st = s6.structure_table_6(battery, table)
    assert s6.check_structure_pins_6(st) == {r: "PASS" for r in b6.RUNGS_6}
    assert set(s6.STRUCTURE_OF_6) == set(b6.RUNGS_6)
    for r in b6.RUNGS_6:
        items, lv = battery[r]["eval_items"], st[r]["structure"]
        if s6.STRUCTURE_OF_6[r] is None:
            assert lv == [] and st[r]["strata"] == table[r]["strata"]
            continue
        assert len(lv) == 500 and sum(st[r]["structure_counts"].values()) == 500
        assert st[r]["strata"] == [f"{a}|{b}" for a, b in zip(table[r]["strata"], lv)]
    # each level recomputed from the item's TEXT, not from the module
    for it, lv in zip(battery["unscramble_long"]["eval_items"],
                      st["unscramble_long"]["structure"]):
        s = it["question"].split(" ")[2]
        assert lv == str(min(sum(a == b for a, b in zip(it["answer"], s)), 2))
    for it, lv in zip(battery["sort3"]["eval_items"], st["sort3"]["structure"]):
        w = it["question"].split(": ")[1].split(" ")
        assert lv == str(sum(w[i] > w[j] for i in range(3) for j in range(i + 1, 3)))
        assert lv != "0"                                    # never already sorted
    for it, lv in zip(battery["modarith_add1"]["eval_items"],
                      st["modarith_add1"]["structure"]):
        a, b = it["meta"]["a"], it["meta"]["b"]
        assert lv == str(int((a + b) // 10 != (a + b + 1) // 10))
    for it, lv in zip(battery["temporal"]["eval_items"], st["temporal"]["structure"]):
        lines = it["question"].split("\nOptions: ")[0].split("\n")
        wake = lines[2].rsplit(" ", 1)[1].rstrip(".")
        shut = lines[-2].rsplit(" ", 1)[1].rstrip(".")
        a, b = it["answer"].split(" to ")
        assert lv == ("first" if a == wake else "last" if b == shut else "middle")
    for it, lv in zip(battery["unit_interp2"]["eval_items"],
                      st["unit_interp2"]["structure"]):
        body = it["question"].split("\nOptions: ")[0]
        if " If " not in body:
            assert lv == "plain"
        else:
            assert lv == ("stated" if it["meta"]["answer_stated"] else "computed")
    lcs = battery["lcs"]["eval_items"]
    for a in "0123456789":
        tot = sorted(len(it["question"].split("Strings: ")[1]) - 1
                     for it in lcs if it["answer"] == a)
        med = tot[len(tot) // 2]
        for it, lv in zip(lcs, st["lcs"]["structure"]):
            if it["answer"] == a:
                t = len(it["question"].split("Strings: ")[1]) - 1
                assert lv == ("long" if t >= med else "short")
    assert s6.inversions(["b", "a", "c"]) == 1 and s6.inversions(list("edcba")) == 10


# ---------------------------------------------------- heuristic floors
def test_heuristic_floors(battery):
    """What a guesser that solves nothing can score, beside the rule's
    floor. `temporal`: the right interval is the only option the text
    does not mention, on every item — BIG-bench's own construction."""
    h = f6.heuristic_table_6(battery)
    assert f6.check_heuristic_pins_6(h) == {r: "PASS" for r in b6.RUNGS_6}
    assert h["temporal"]["heuristic"] == f6.ABSENT
    assert h["temporal"]["heuristic_count"] == 500
    assert h["lcs"]["heuristic"] == f6.LENGTH_RULE
    assert 190 <= h["lcs"]["heuristic_count"] <= 230        # BIG-bench's own: .40
    for r in ("unit_interp1", "unit_interp2"):
        assert h[r]["heuristics"][f6.SIZE_RANK] <= 120      # it was 224 and 186
        assert h[r]["heuristics"][f6.LIST_POSITION] <= 102
    for r in ("deduction3", "deduction5", "shapes"):
        assert h[r]["heuristics"][f6.ABSENT] == 0
    for r in b6.RUNGS_6:
        if b6.N_OPTIONS_OF.get(r) is None and r != "lcs":
            assert h[r]["heuristic"] is None and h[r]["heuristic_floor"] is None
    # independently, from the text: the option the schedule never mentions
    for it in battery["temporal"]["eval_items"]:
        body, opts = it["question"].split("\nOptions: ")
        assert [o for o in opts.split(", ") if f" {o}." not in body] == [it["answer"]]
