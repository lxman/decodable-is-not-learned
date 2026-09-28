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
from experiments.exp6.battery import overlap_6 as ov
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
        keys = {"question", "answer", "bb_sha256", "meta"}
        if cap["task"] == "modified_arithmetic":
            keys |= {"bb_extra_sha256"}               # the query line's own key
        assert all(set(it) == keys for it in cap["eval_items"])
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
    assert table["modarith_mul1"]["counts"] == {"1": 10, "2": 19, "3": 129, "4": 342}
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
    for it, lv in zip(battery["ipa_word"]["eval_items"], st["ipa_word"]["structure"]):
        assert lv == ("marked" if ("ˈ" in it["answer"] or "ˌ" in it["answer"])
                      else "plain")
    assert 250 < st["ipa_word"]["structure_counts"]["marked"] < 400
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
    # lcs: the answer follows the lengths as it does in BIG-bench's own 320
    # items, where the same three rules, cross-fitted the same way, score
    # .27 (shorter), .17 (longer) and .21 (total); here .23, .18 and .23
    assert set(h["lcs"]["heuristics"]) == {f6.LENGTH_MIN, f6.LENGTH_MAX, f6.LENGTH_SUM}
    assert max(h["lcs"]["heuristics"].values()) <= 165       # it was 235 (.47)
    for r in ("unit_interp1", "unit_interp2"):
        g = h[r]["heuristics"]
        assert set(g) == {f6.LIST_POSITION, f6.SIZE_RANK, f6.ABSENT, f6.DIVISIBLE,
                          f6.SHARES}
        assert g[f6.SIZE_RANK] <= 120                        # it was 224 and 186
        assert g[f6.LIST_POSITION] <= 105
        # on BIG-bench's 25 items a level: .28 and .20 (lv1), .08 and .28 (lv2)
        assert g[f6.DIVISIBLE] <= 125 and g[f6.SHARES] <= 160
    for r in ("deduction3", "deduction5", "shapes"):
        assert h[r]["heuristics"][f6.ABSENT] == 0
    for r in b6.RUNGS_6:
        if b6.N_OPTIONS_OF.get(r) is None and r != "lcs":
            assert h[r]["heuristic"] is None and h[r]["heuristic_floor"] is None
        else:
            assert set(h[r]["heuristics"]) <= set(f6.GUESSERS_6)
    # independently, from the text: the option the schedule never mentions
    for it in battery["temporal"]["eval_items"]:
        body, opts = it["question"].split("\nOptions: ")
        assert [o for o in opts.split(", ") if f" {o}." not in body] == [it["answer"]]


def test_a_table_guesser_is_scored_on_items_it_has_not_seen():
    # the key determines the answer: learned on one half, right on the other
    keys = [i % 7 for i in range(500)]
    assert f6._cross_fit(keys, [str(k) for k in keys]) == 500
    # the key is the item itself: nothing carries over, and the fallback
    # (the commonest answer of the other half) is all that scores
    assert f6._cross_fit(list(range(500)), ["a"] * 300 + ["b"] * 200) == 300
    # no key at all: the commonest answer of the OTHER half
    ans = ["x"] * 260 + ["y"] * 240
    assert f6._cross_fit([0] * 500, ans) in (240, 260)
    # the two halves are blocks of ten slots, so a cycle of ten is in both
    halves = [(i // f6.HALF_BLOCK) % 2 for i in range(500)]
    assert sum(halves) == 250
    assert {i % 10 for i, h in enumerate(halves) if h} == set(range(10))


def test_the_two_new_pin_checks_refuse(battery):
    h = f6.heuristic_table_6(battery)
    h["lcs"] = dict(h["lcs"], heuristic_count=h["lcs"]["heuristic_count"] + 1)
    with pytest.raises(ValueError, match="lcs: heuristic floor"):
        f6.check_heuristic_pins_6(h)
    table = s6.build_table_6(battery)
    st = s6.structure_table_6(battery, table)
    st["sort3"] = dict(st["sort3"], structure_counts={"1": 1})
    with pytest.raises(ValueError, match="sort3: structure counts"):
        s6.check_structure_pins_6(st)
    st = s6.structure_table_6(battery, table)
    st["sort3"] = dict(st["sort3"], strata=st["sort3"]["strata"][:-1])
    with pytest.raises(ValueError, match="sort3: 499 labels"):
        s6.check_structure_pins_6(st)


@pytest.mark.parametrize("change,match", [
    (lambda c: c.__setitem__("name", "sort5"), "names"),
    (lambda c: c.__setitem__("n_options", 3), "n_options"),
    (lambda c: c["eval_items"].pop(), "499 items"),
    (lambda c: c["shots"].pop(), "1 shots"),
    (lambda c: c["shot_records"].pop(), "1 shot records"),
    (lambda c: c.pop("shot_records"), "0 shot records"),
    (lambda c: c.__setitem__("rung_type", "choice"), "rung_type"),
])
def test_the_loader_refuses_every_header_it_checks(tmp_path, monkeypatch, change, match):
    """Past the sha: a file that hashes to its pin and says the wrong
    thing about itself."""
    cap = json.loads((b6.ITEMS_DIR / "sort3.json").read_text())
    change(cap)
    raw = gen.dumps(cap)
    (tmp_path / "sort3.json").write_text(raw, encoding="utf-8")
    monkeypatch.setattr(b6, "ITEMS_DIR", tmp_path)
    monkeypatch.setitem(b6.ITEMS_SHA_PIN_6, "sort3",
                        hashlib.sha256(raw.encode("utf-8")).hexdigest())
    with pytest.raises(ValueError, match=match):
        b6.load_item_file_6("sort3")


def test_a_floor_outside_the_unit_interval_is_refused(battery):
    floors = f6.floor_table_6(battery)
    floors["shapes"] = dict(floors["shapes"], floor=1.0)
    with pytest.raises(ValueError, match="shapes: floor"):
        f6.check_floor_pins_6(floors)


# ------------------------------------------------------- content overlap
def test_the_content_overlap_record(monkeypatch):
    """What the collision gate does not establish, as counted: the record
    is the pinned one, of the index and the items now pinned."""
    rec = ov.load_record()
    assert tuple(rec["rungs"]) == tuple(sorted(ov.RUNGS)) and rec["n_items"] == 500
    n = {r: row["items"] for r, row in rec["rungs"].items()}
    for r in ov.MODARITH_FILE:
        # the gate's two keys: the prompt, and the pair asked
        assert n[r]["asks a pair BIG-bench asks"] == 0
        assert n[r]["asks a pair BIG-bench prints on any line"] == 0
    shows = "shows a worked pair BIG-bench prints on any line"
    assert [n[r][shows] for r in ov.MODARITH_FILE] == [15, 13, 473]
    assert n["unscramble_short"] == {"the answer is a BIG-bench target word": 491}
    assert n["unscramble_long"] == {"the answer is a BIG-bench target word": 497}
    assert n["ipa_word"] == {"the word occurs in a BIG-bench sentence": 95}
    assert n["sort3"] == {"a word of the list is in a BIG-bench list": 369,
                          "every word of the list is in a BIG-bench list": 22}
    assert n["sort5"] == {"a word of the list is in a BIG-bench list": 434,
                          "every word of the list is in a BIG-bench list": 2}
    assert n["lcs"] == {"one of the two strings is a BIG-bench string": 0}
    monkeypatch.setitem(b6.ITEMS_SHA_PIN_6, "lcs", "0" * 64)
    with pytest.raises(ValueError, match=r"of other items: \['lcs'\]"):
        ov.load_record()
    monkeypatch.undo()
    monkeypatch.setattr(ov.c6, "INDEX_6_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="of another index"):
        ov.load_record()
    monkeypatch.undo()
    monkeypatch.setattr(ov, "OVERLAP_6_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="pinned"):
        ov.load_record()


def test_the_overlap_is_counted_from_the_text(monkeypatch, tmp_path):
    files = {
        "modified_arithmetic/three_digit_addition_plus_one":
            [{"input": "h\n1 + 2 -> 4\n3 + 4 ->"}],
        "modified_arithmetic/three_digit_subtraction_plus_one":
            [{"input": "h\n1 - 2 -> 0\n3 - 4 ->"}],
        "modified_arithmetic/two_digit_multiplication_plus_one":
            [{"input": "h\n1 * 2 -> 3\n3 * 4 ->"}],
        "word_unscrambling": [{"input": "x", "target": ["pear", "reap"]}],
        ov.IPA_FILE: [{"input": "English: A pear, a fig."},
                      {"input": "IPA: ə pɛr", "target": "A pear"}],
        "word_sorting": [{"input": "pear fig"}],
        "cs_algorithms/lcs": [{"input": "ABC DEF"}],
    }
    monkeypatch.setattr(ov, "_examples", lambda src, task, path: files[path])

    def arith(sym, worked, asked):
        return {"question": f"h\n{worked[0]} {sym} {worked[1]} -> 0\n"
                            f"{asked[0]} {sym} {asked[1]} ->"}
    battery = {
        "modarith_add1": [arith("+", (9, 9), (3, 4)), arith("+", (3, 4), (1, 2)),
                          arith("+", (1, 2), (8, 8))],
        "modarith_sub1": [arith("-", (9, 9), (8, 8))],
        "modarith_mul1": [arith("*", (1, 2), (3, 4))],
        "unscramble_short": [{"answer": "pear"}, {"answer": "plum"}],
        "unscramble_long": [{"answer": "reap"}],
        "ipa_word": [{"meta": {"word": "fig"}}, {"meta": {"word": "a"}},
                     {"meta": {"word": "plum"}}],
        "sort3": [{"meta": {"words": ["pear", "fig"]}}, {"meta": {"words": ["pear", "kiwi"]}},
                  {"meta": {"words": ["plum", "kiwi"]}}],
        "sort5": [{"meta": {"words": ["plum"]}}],
        "lcs": [{"meta": {"a": "ABC", "b": "XYZ"}}, {"meta": {"a": "XYZ", "b": "DEF"}},
                {"meta": {"a": "AB", "b": "DE"}}],
    }
    battery = {r: {"eval_items": v, "items_sha256": r} for r, v in battery.items()}
    got = {r: row["items"] for r, row in ov.overlap(tmp_path, battery)["rungs"].items()}
    assert got["modarith_add1"] == {
        "asks a pair BIG-bench asks": 1,
        "asks a pair BIG-bench prints on any line": 2,
        "shows a worked pair BIG-bench prints on any line": 2}
    assert set(got["modarith_sub1"].values()) == {0}
    assert got["modarith_mul1"] == {
        "asks a pair BIG-bench asks": 1,
        "asks a pair BIG-bench prints on any line": 1,
        "shows a worked pair BIG-bench prints on any line": 1}
    assert got["unscramble_short"] == {"the answer is a BIG-bench target word": 1}
    assert got["unscramble_long"] == {"the answer is a BIG-bench target word": 1}
    assert got["ipa_word"] == {"the word occurs in a BIG-bench sentence": 2}
    assert got["sort3"] == {"a word of the list is in a BIG-bench list": 2,
                            "every word of the list is in a BIG-bench list": 1}
    assert got["sort5"] == {"a word of the list is in a BIG-bench list": 0,
                            "every word of the list is in a BIG-bench list": 0}
    assert got["lcs"] == {"one of the two strings is a BIG-bench string": 2}


def test_the_overlap_tool_reads_only_the_files_of_the_index(tmp_path):
    p = tmp_path / ov.local_name("word_sorting")
    p.write_text(json.dumps({"examples": [{"input": "pear fig"}]}))
    with pytest.raises(ValueError, match="not the file the index was built from"):
        ov._examples(tmp_path, "word_sorting", "word_sorting")
