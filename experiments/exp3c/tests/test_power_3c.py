"""§7 tables (doc Open item 5): the committed power_3c.json must be
exactly what the frozen code produces (the freeze re-runs this cold),
and the doc-quote cross-check must disagree on EXACTLY the three
ledgered slips — no silent absorption in either direction.
"""
import json

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import compute_power_3c as pw

EXPECTED_DISAGREEMENTS = {"luck_floor_26^-4_quoted_1.5e-6",
                          "luck_gap_factor_quoted_13x",
                          "lone_draw_one_in_three_at_1e-6"}


def test_committed_tables_equal_the_frozen_codes_output():
    committed = pw.OUT.read_text()
    rebuilt = json.dumps(pw.build(), indent=1, sort_keys=True) + "\n"
    assert committed == rebuilt


def test_doc_quotes_disagree_on_exactly_the_ledgered_slips():
    q = pw.build()["doc_quotes_check"]
    bad = {k for k, v in q.items() if not v["agrees"]}
    assert bad == EXPECTED_DISAGREEMENTS
    for k in EXPECTED_DISAGREEMENTS:
        assert "note" in q[k]


def test_detection_at_the_exp3_point_rate():
    t = pw.build()["sampling"]
    d = t["detection_new_by_rate"][f"{1.0 / 128000:.6e}"]
    assert abs(d - 0.9502) < 5e-4
    assert t["n_new_per_cell"] == 384_000
    assert t["n_pooled_per_cell"] == 512_000


def test_zero_bounds_are_cp_upper_read_from_the_other_side():
    t = pw.build()["sampling"]["zero_bounds_cp95"]
    assert abs(t["pooled_cell"] - a3.cp_upper(0, 512_000)) < 1e-15
    assert abs(t["exp3_cell"] - a3.cp_upper(0, 128_000)) < 1e-15
    assert abs(t["new_cell"] - a3.cp_upper(0, 384_000)) < 1e-15


def test_strata_counts_are_the_committed_batterys():
    s = pw.build()["strata"]
    assert {L: v["n_items"] for L, v in s["reverse_string"].items()} \
        == {"4": 194, "5": 155, "6": 151}
    assert s["rev_string7"]["7"]["n_items"] == 500
    assert s["reverse_string"]["4"]["n_new"] == 148_992


def test_luck_floors_from_code():
    lf = pw.build()["luck_floors"]
    assert abs(lf["4"] - 26.0 ** -4) < 1e-18
    assert abs(lf["4"] - 2.1883e-6) < 1e-9
    assert lf["7"] < 1e-9
