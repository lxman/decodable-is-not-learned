# experiments/exp6/tests/test_data_6.py
import json
from collections import Counter

import pytest

from experiments.exp6.battery import collisions_6 as c6
from experiments.exp6.battery import make_bigbench_index_6 as mk
from experiments.exp6.battery import make_data_6 as md
from experiments.exp6.battery import words_6 as w6
from experiments.exp6.battery.spec import RungSpec


def test_word_table_is_pinned_and_well_formed():
    rows = w6.load_words()
    assert len(rows) == 21_540
    assert all(w.isascii() and w.isalpha() and w.islower() and len(w) >= 3
               for _, w, _, _ in rows)
    assert all(1 <= r <= md.TOP_N for r, _, _, _ in rows)
    assert all(c > 0 for _, _, c, _ in rows)
    assert all((" " not in ipa) and not ipa.endswith("*") for _, _, _, ipa in rows)


def test_a_tampered_word_table_is_refused(tmp_path, monkeypatch):
    p = tmp_path / "words_6.tsv"
    p.write_bytes(w6.WORDS_PATH.read_bytes() + b"99999\tzzz\t1\t\n")
    monkeypatch.setattr(w6, "WORDS_PATH", p)
    w6.load_words.cache_clear()
    with pytest.raises(ValueError, match="pinned"):
        w6.load_words()
    monkeypatch.undo()
    w6.load_words.cache_clear()


def test_vocab_properties():
    v = w6.vocab()
    rows = w6.load_words()
    sig = Counter(w6.signature(w) for _, w, _, _ in rows)
    assert len(v["v10"]) == 9_128
    assert all(v["rank"][w] <= w6.TOP_V10 for w in v["v10"])
    assert all(sig[w6.signature(w)] == 1 for w in v["unique_anagram"])
    assert all(v["ipa"][w] for w in v["ipa"]) and len(v["ipa"]) == 7_649
    assert w6.ipa_len("ˈfoʊˌtoʊz") == 7
    assert w6.by_length(("abc", "abcd", "abcde"), 4, 5) == {4: ["abcd"], 5: ["abcde"]}


def test_make_data_refuses_the_wrong_source(tmp_path):
    src = tmp_path / "count_1w.txt"
    src.write_text("the\t1\n")
    with pytest.raises(ValueError, match="pinned"):
        md.build(src, tmp_path / "out.tsv")
    assert not (tmp_path / "out.tsv").exists()


def test_index_is_pinned_and_covers_every_task():
    idx = c6.load_index()
    assert idx["commit"] == mk.BIGBENCH_COMMIT == c6.BIGBENCH_COMMIT
    assert set(idx["tasks"]) == set(mk.SOURCES)
    want = {"modified_arithmetic": 3000, "word_unscrambling": 8917,
            "word_sorting": 1900,
            "international_phonetic_alphabet_transliterate": 1003,
            "logical_deduction": 200, "ascii_word_recognition": 1000,
            "geometric_shapes": 359, "temporal_sequences": 1000,
            "cs_algorithms": 320, "unit_interpretation": 50}
    assert {t: v["n_keys"] for t, v in idx["tasks"].items()} == want
    assert all(v["kind"] == mk.SOURCES[t][0] for t, v in idx["tasks"].items())


def test_index_builder_hashes_inputs_or_targets(tmp_path):
    for _, paths in mk.SOURCES.values():
        for path in paths:
            ex = [{"input": f"{path} in", "target": ["t1", "t2"]}]
            (tmp_path / mk.local_name(path)).write_text(json.dumps({"examples": ex}))
    out = tmp_path / "index.json"
    mk.build(tmp_path, out)
    rec = json.loads(out.read_text())
    assert rec["tasks"]["word_sorting"]["keys"] == [mk._sha("word_sorting in")]
    assert set(rec["tasks"]["ascii_word_recognition"]["keys"]) == \
        {mk._sha("t1"), mk._sha("t2")}
    assert rec["tasks"]["logical_deduction"]["n_keys"] == 2


def test_for_spec_checks_the_kind():
    ok = RungSpec(name="x", task="word_sorting", wei_class="E.2",
                  rung_type="string", answer_type="sequence", description="d",
                  seed=1, draw=lambda *a: None)
    assert len(c6.for_spec(ok)) == 1900
    bad = RungSpec(name="x", task="word_sorting", wei_class="E.2",
                   rung_type="string", answer_type="sequence", description="d",
                   seed=1, draw=lambda *a: None, collision_kind="target")
    with pytest.raises(ValueError, match="collision kind"):
        c6.for_spec(bad)
    none = RungSpec(name="x", task="nonesuch", wei_class="E.2",
                    rung_type="string", answer_type="word", description="d",
                    seed=1, draw=lambda *a: None)
    with pytest.raises(ValueError, match="no index entry"):
        c6.for_spec(none)
