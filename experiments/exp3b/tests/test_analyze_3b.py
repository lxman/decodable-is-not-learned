"""Fixture suite for the frozen Exp 3b analysis (design §5, §6, §11).

One synthetic case per preregistered provision, in both directions: every
gate has a case where it must fire and a case where it must not. The
experiment adjudicates a claim already in print; every provision that could
soften an unwelcome outcome — or manufacture a dramatic one — is pinned.

The committed-record fixtures at the bottom read real referent files
(inclusion counts, floors, m3 margins, 3a record STRUCTURE). None of them
computes a first-character quantity on real continuations: that number does
not exist until after the exp3b-preregistered tag.
"""
import json
from pathlib import Path

import pytest

from experiments.exp3b import analyze_3b as a

REV = a.REVERSAL_RUNGS
FLOOR = {"rev_string7": 0.056, "reverse_string": 0.054, "ctrl_copy": 0.052,
         "clock24_d999": 0.496}
SYNTH_FLOORS = {r: {"primary": f} for r, f in FLOOR.items()}
MARGINS = {"rev_string7": {"410m": 0.6263, "1b": 0.7725},
           "reverse_string": {"410m": 0.5731, "1b": 0.6749}}
LABELS = {"rev_string7": "r", "reverse_string": "s", "ctrl_copy": "c",
          "clock24_d999": "8"}
INCLUSION = {}
for _r in a.RUNGS:
    for _s in a.PROBE_SIZES:
        INCLUSION[(_r, _s, "trained")] = 0
        INCLUSION[(_r, _s, "untrained")] = 0
INCLUSION[("ctrl_copy", "410m", "trained")] = 480
INCLUSION[("ctrl_copy", "1b", "trained")] = 490
INCLUSION[("clock24_d999", "410m", "trained")] = 18
INCLUSION[("clock24_d999", "1b", "trained")] = 24

N = 500
AT_FLOOR = {"rev_string7": 28, "reverse_string": 27, "ctrl_copy": 26,
            "clock24_d999": 240}


# ------------------------------------------------------------------ floors

def items(first_chars, input_firsts=None):
    ifs = input_firsts or ["z"] * len(first_chars)
    return [{"answer": c + "xxxxxx",
             "question": f"Spell the string '{i}bcdefg' backwards.",
             "probe_label": c} for c, i in zip(first_chars, ifs)]


def test_floor_is_the_max_of_three_and_names_them():
    f = a.chance_floors(items(["a"] * 60 + ["b"] * 40))
    assert f["uniform"] == pytest.approx(1 / 26)
    assert f["marginal"] == pytest.approx(0.60)
    assert f["primary"] == pytest.approx(0.60)
    assert f["primary_source"] == "marginal"


def test_copy_first_floor_catches_a_model_that_echoes_the_input():
    f = a.chance_floors(items(list("abcdefghij") * 10, list("abcdefghij") * 10))
    assert f["copy_first"] == pytest.approx(1.0)
    assert f["primary"] == pytest.approx(1.0)
    assert f["primary_source"] == "copy_first"


def copy_items(n=52):
    """A COPY task: the answer IS the input, so echoing scores 1.0."""
    out = []
    for i in range(n):
        w = "abcdefghijklmnopqrstuvwxyz"[i % 26] + "qrst"
        out.append({"answer": w, "question": f"Repeat the string '{w}'.",
                    "probe_label": w[0]})
    return out


def test_copy_first_is_excluded_when_copying_IS_the_task():
    """ctrl_copy's copy_first floor is 1.0 by construction; taking the max
    would make the positive-control gate fire unconditionally and leave
    INSUFFICIENT_DATA as the only reachable verdict (3a's freeze catch)."""
    f = a.chance_floors(copy_items())
    assert f["copy_is_the_task"] is True
    assert f["primary"] != pytest.approx(1.0)
    assert f["primary_source"] != "copy_first"


def test_copy_first_still_applies_where_copying_is_wrong():
    f = a.chance_floors(items(list("abcdefghij") * 5, list("abcdefghij") * 5))
    assert f["copy_is_the_task"] is False
    assert f["primary_source"] == "copy_first"


def test_copy_is_the_task_is_derived_from_items_not_declared():
    assert a.chance_floors(copy_items())["copy_is_the_task"] is True
    assert a.chance_floors(items(["a"] * 40))["copy_is_the_task"] is False


# ------------------------------------------------------- first-char scoring

@pytest.mark.parametrize("cont,label,want", [
    (" rcnnbgv", "r", True),
    ("rcnnbgv", "r", True),
    ("\n\n  R", "r", True),          # case-folded
    (" xcnnbgv", "r", False),
    ("", "r", False),               # empty is a failure to emit, not a drop
    ("   ", "r", False),
    ("7abc", "r", False),           # non-matching non-alphabetic first char
])
def test_first_char_scoring(cont, label, want):
    assert a.score_first_char(cont, label) is want


def test_digit_labels_score_correctly():
    """clock24_d999's probe label is a DIGIT. 3a's isalpha() guard zeroed
    the matched control at every cell and looked like a finding."""
    assert a.score_first_char("8", "8") is True
    assert a.score_first_char(" 7 o'clock", "7") is True
    assert a.score_first_char("8", "7") is False


def test_label_case_is_folded_on_both_sides():
    assert a.score_first_char("r", "R") is True
    assert a.score_first_char("R", "r") is True


def test_scoring_never_silently_drops_an_item():
    got = a.score_cell([" r", "", "   ", "7x", " R"], ["r"] * 5)
    assert got["n"] == 5 and got["correct"] == 2


def test_a_length_mismatch_is_an_error_not_a_truncation():
    with pytest.raises(ValueError, match="dropped"):
        a.score_cell([" r", " x"], ["r"])


# ------------------------------------------------------------ significance

def test_the_test_is_one_sided():
    """45/500 against floor .056: p = .00137, p*8 = .011 fails at .01; a
    halved (two-sided) p would pass at .0055."""
    assert a.significant(correct=45, n=500, floor=0.056, n_tests=8) is False


def test_bonferroni_separates_one_from_eight():
    """43/500 against .056: p = .00394 — clears alpha alone, fails /8.
    This is also why an untrained twin at 43 contaminates (n_tests=1)
    while a trained cell at 43 does not adjudicate as present."""
    assert a.significant(correct=43, n=500, floor=0.056, n_tests=1) is True
    assert a.significant(correct=43, n=500, floor=0.056, n_tests=8) is False


def test_bonferroni_separates_eight_from_twenty():
    """46/500 against .056: p = .000781 — clears .01/8, fails .01/20. An
    implementation that counted ALL trained cells (20, eval sizes included)
    instead of the preregistered 8 probe-size cells flips here."""
    assert a.significant(correct=46, n=500, floor=0.056, n_tests=8) is True
    assert a.significant(correct=46, n=500, floor=0.056, n_tests=20) is False


def test_critical_counts_match_the_committed_power_table():
    """power.json's critical counts are the verdict's actual thresholds:
    46 at floor .056, 44 at .054 (design §7)."""
    assert a.significant(correct=46, n=500, floor=0.056, n_tests=8) is True
    assert a.significant(correct=45, n=500, floor=0.056, n_tests=8) is False
    assert a.significant(correct=44, n=500, floor=0.054, n_tests=8) is True
    assert a.significant(correct=43, n=500, floor=0.054, n_tests=8) is False


# -------------------------------------------------------- Clopper–Pearson

def test_clopper_pearson_known_values():
    lo, hi = a.clopper_pearson(0, 500)
    assert lo == 0.0 and hi == pytest.approx(0.0073506, abs=1e-6)
    lo, hi = a.clopper_pearson(480, 500)
    assert lo == pytest.approx(0.938897, abs=1e-5)
    assert hi == pytest.approx(0.975399, abs=1e-5)


def test_cp_overlap_tolerates_8_of_500_against_a_zero_referent():
    """Design §6's own arithmetic: ≤8/500 is compatible with a committed 0,
    9/500 is not."""
    assert a.cp_overlap(8, 500, 0, 500) is True
    assert a.cp_overlap(9, 500, 0, 500) is False


def test_cp_overlap_brackets_the_ctrl_copy_referent():
    assert a.cp_overlap(460, 500, 480, 500) is True
    assert a.cp_overlap(455, 500, 480, 500) is False
    assert a.cp_overlap(495, 500, 480, 500) is False


def test_cp_overlap_is_symmetric():
    assert a.cp_overlap(9, 500, 0, 500) == a.cp_overlap(0, 500, 9, 500)
    assert a.cp_overlap(460, 500, 480, 500) == a.cp_overlap(480, 500, 460, 500)


# --------------------------------------------------------- battery builder

def batt(fc_overrides=None, full_overrides=None):
    """An in-memory full-shape battery: the DISSOCIATION world unless
    edited. Returns (cells, floors, inclusion, byte_ref)."""
    fc = {}
    for r in a.RUNGS:
        for s in a.SIZES:
            fc[(r, s, "trained")] = AT_FLOOR[r]
            fc[(r, s, "untrained")] = 20
    for s in a.PROBE_SIZES:
        fc[("ctrl_copy", s, "trained")] = 480
    fc.update(fc_overrides or {})
    full_overrides = full_overrides or {}

    cells = []
    for (r, s, m), k in fc.items():
        label = LABELS[r]
        conts = [f" {label}x{i}" if i < k else f" z{i}" for i in range(N)]
        full = full_overrides.get((r, s, m), INCLUSION.get((r, s, m), 0))
        rec = {"rung": r, "size": s, "mode": m, "n_items": N,
               "continuations": conts, "probe_labels": [label] * N,
               "full_string_correct": int(full)}
        cells.append({**rec, **a.score_cell(conts, rec["probe_labels"]),
                      "mean_continuation_len": 4.0})
    byte_ref = {(r, s, m): list(c["continuations"])
                for c in cells
                for (r, s, m) in [a.cell_key(c)] if s in a.EVAL_SIZES}
    inclusion = {k: {"correct": v, "n": N} for k, v in INCLUSION.items()}
    return cells, SYNTH_FLOORS, inclusion, byte_ref


def vd(cells, floors, inclusion, byte_ref):
    return a.verdict(cells, floors, inclusion, byte_ref, MARGINS)


def cell_of(cells, r, s, m):
    return next(c for c in cells if a.cell_key(c) == (r, s, m))


# --------------------------------------------------------- the verdict tree

def test_positive_control_failure_precedes_everything():
    out = vd(*batt(fc_overrides={("ctrl_copy", "410m", "trained"): 26,
                                 ("ctrl_copy", "1b", "trained"): 26}))
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "ctrl_copy" in out["reason"]


def test_gate1_requires_both_probe_sizes_not_either():
    """One blind size already invalidates the instrument: 'both' is both."""
    out = vd(*batt(fc_overrides={("ctrl_copy", "1b", "trained"): 30}))
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "ctrl_copy" in out["reason"]


def test_replication_failure_names_every_incompatible_cell():
    out = vd(*batt(full_overrides={("ctrl_copy", "410m", "trained"): 100,
                                   ("clock24_d999", "1b", "trained"): 200}))
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "replication" in out["reason"]
    assert "ctrl_copy/410m/trained" in out["reason"]
    assert "clock24_d999/1b/trained" in out["reason"]


def test_replication_tolerates_cp_overlap():
    """8/500 against a committed 0 is compatible (design §6); the gate must
    not fire on sampling noise the referent's own interval allows."""
    out = vd(*batt(full_overrides={("rev_string7", "410m", "trained"): 8}))
    assert out["verdict"] == "DISSOCIATION"


def test_replication_checks_untrained_cells_too():
    """The 16 gate-2 cells include the twins: an untrained model suddenly
    emitting full strings is stack drift, not data."""
    out = vd(*batt(full_overrides={("rev_string7", "410m", "untrained"): 20}))
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "rev_string7/410m/untrained" in out["reason"]


def test_byte_gate_fires_above_tolerance():
    cells, fl, inc, br = batt()
    k = ("rev_string7", "2.8b", "trained")
    for i in range(3):
        br[k][N - 1 - i] = br[k][N - 1 - i] + " DRIFT"
    out = vd(cells, fl, inc, br)
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "byte gate" in out["reason"]
    assert "rev_string7/2.8b/trained (3 items)" in out["reason"]


def test_byte_gate_tolerates_two_and_discloses_them_verbatim():
    """≤2 differing items — the exact-tie argmax allowance — must not kill
    the experiment, and must still be disclosed item by item."""
    cells, fl, inc, br = batt()
    k = ("rev_string7", "2.8b", "trained")
    br[k][0] = "SOMETHING ELSE"
    br[k][1] = "ANOTHER"
    out = vd(cells, fl, inc, br)
    assert out["verdict"] == "DISSOCIATION"
    diffs = out["byte_diffs"]["rev_string7/2.8b/trained"]
    assert [d["item"] for d in diffs] == [0, 1]
    assert diffs[0]["referent"] == "SOMETHING ELSE"
    assert diffs[0]["got"] == cell_of(cells, *k)["continuations"][0]


def test_no_byte_diffs_reports_empty_not_missing():
    out = vd(*batt())
    assert out["byte_diffs"] == {}


def test_untrained_fire_marks_contamination_without_halting():
    out = vd(*batt(fc_overrides={("clock24_d999", "410m", "untrained"): 400}))
    assert out["contaminated"] == ["clock24_d999"]
    assert out["verdict"] in ("UNITS_ARTIFACT", "DISSOCIATION", "PARTIAL")


def test_untrained_twins_test_at_n1_not_n8():
    """43/500 fires as contamination (n_tests=1) while the same count on a
    trained cell adjudicates as absent (n_tests=8) — the asymmetry is the
    design's, and softening it in either direction is a defect."""
    out = vd(*batt(fc_overrides={("rev_string7", "410m", "untrained"): 43,
                                 ("rev_string7", "410m", "trained"): 43}))
    assert out["contaminated"] == ["rev_string7"]
    assert "rev_string7/410m" not in out["significant_cells"]


def test_eval_size_twin_fire_is_not_contamination():
    """Design §6: eval-size cells take no significance tests. A 12b twin
    emitting loudly is a descriptive fact, not a contamination flag."""
    out = vd(*batt(fc_overrides={("rev_string7", "12b", "untrained"): 400}))
    assert out["contaminated"] == []
    assert out["verdict"] == "DISSOCIATION"


def test_eval_size_cells_take_no_significance_tests():
    out = vd(*batt())
    for row in out["cells"]:
        if row["size"] in a.EVAL_SIZES:
            assert row["significant"] is None
        else:
            assert isinstance(row["significant"], bool)


def test_contaminated_rung_is_excluded_from_step5_quantifiers():
    """rev_string7's twin fires; reverse_string fires everywhere. With the
    exclusion honored the verdict is UNITS_ARTIFACT over the surviving
    rung; an implementation that ignores contamination sees rev_string7 at
    floor and says PARTIAL."""
    out = vd(*batt(fc_overrides={
        ("rev_string7", "410m", "untrained"): 400,
        ("reverse_string", "410m", "trained"): 300,
        ("reverse_string", "1b", "trained"): 300}))
    assert out["contaminated"] == ["rev_string7"]
    assert out["verdict"] == "UNITS_ARTIFACT"


def test_both_rungs_contaminated_is_insufficient_data():
    """A universal quantifier over zero cells decides nothing: with both
    reversal twins firing, all([]) must not be allowed to read as
    UNITS_ARTIFACT (or DISSOCIATION)."""
    out = vd(*batt(fc_overrides={
        ("rev_string7", "410m", "untrained"): 400,
        ("reverse_string", "1b", "untrained"): 400,
        ("rev_string7", "410m", "trained"): 300,
        ("rev_string7", "1b", "trained"): 300,
        ("reverse_string", "410m", "trained"): 300,
        ("reverse_string", "1b", "trained"): 300}))
    assert out["verdict"] == "INSUFFICIENT_DATA"
    assert "contamination" in out["reason"]
    assert out["contaminated"] == ["rev_string7", "reverse_string"]


def test_reversal_above_floor_everywhere_is_a_units_artifact():
    out = vd(*batt(fc_overrides={(r, s, "trained"): 300
                                 for r in REV for s in a.PROBE_SIZES}))
    assert out["verdict"] == "UNITS_ARTIFACT"


def test_reversal_at_floor_everywhere_is_a_dissociation():
    out = vd(*batt())
    assert out["verdict"] == "DISSOCIATION"


def test_dissociation_reason_quotes_per_size_margins():
    out = vd(*batt())
    assert "0.7725" in out["reason"] and "0.6263" in out["reason"]
    assert "0.6749" in out["reason"] and "0.5731" in out["reason"]


def test_mixed_is_reported_as_partial_with_the_cells_named():
    out = vd(*batt(fc_overrides={("rev_string7", "1b", "trained"): 300}))
    assert out["verdict"] == "PARTIAL"
    assert "rev_string7/1b" in out["reason"]


def test_the_critical_count_adjudicates_at_the_verdict_level():
    """All four reversal trained probe cells at exactly their critical
    counts (46 at .056, 44 at .054) → UNITS_ARTIFACT; one below → PARTIAL."""
    crit = {"rev_string7": 46, "reverse_string": 44}
    out = vd(*batt(fc_overrides={(r, s, "trained"): crit[r]
                                 for r in REV for s in a.PROBE_SIZES}))
    assert out["verdict"] == "UNITS_ARTIFACT"
    below = {(r, s, "trained"): crit[r] for r in REV for s in a.PROBE_SIZES}
    below[("rev_string7", "410m", "trained")] = 45
    out = vd(*batt(fc_overrides=below))
    assert out["verdict"] == "PARTIAL"


def test_n_tests_is_the_preregistered_eight():
    out = vd(*batt())
    assert out["n_tests"] == 8


def test_zero_cells_carry_cp_upper_bounds():
    out = vd(*batt(fc_overrides={("rev_string7", "410m", "trained"): 0}))
    row = next(r for r in out["cells"] if r["rung"] == "rev_string7"
               and r["size"] == "410m" and r["mode"] == "trained")
    assert row["correct"] == 0
    assert row["cp95"][0] == 0.0
    assert row["cp95"][1] == pytest.approx(0.0073506, abs=1e-6)


def test_behavioural_margin_formula():
    """m_b = (acc − floor) / (1 − floor), design §5."""
    out = vd(*batt(fc_overrides={("rev_string7", "410m", "trained"): 300}))
    row = next(r for r in out["cells"] if r["rung"] == "rev_string7"
               and r["size"] == "410m" and r["mode"] == "trained")
    assert row["m_b"] == pytest.approx((0.6 - 0.056) / (1 - 0.056))


# ------------------------------------------------------------ shape errors

def test_verdict_refuses_a_missing_cell():
    cells, fl, inc, br = batt()
    cells = [c for c in cells
             if a.cell_key(c) != ("rev_string7", "12b", "untrained")]
    with pytest.raises(ValueError, match="missing"):
        vd(cells, fl, inc, br)


def test_verdict_refuses_a_duplicate_cell():
    cells, fl, inc, br = batt()
    with pytest.raises(ValueError, match="duplicate"):
        vd(cells + [cells[0]], fl, inc, br)


def test_verdict_refuses_a_cell_without_full_string_correct():
    cells, fl, inc, br = batt()
    bad = dict(cell_of(cells, "ctrl_copy", "410m", "trained"))
    del bad["full_string_correct"]
    cells = [bad if a.cell_key(c) == ("ctrl_copy", "410m", "trained") else c
             for c in cells]
    with pytest.raises(ValueError, match="full_string_correct"):
        vd(cells, fl, inc, br)


def test_verdict_refuses_incomplete_inclusion_referents():
    cells, fl, inc, br = batt()
    del inc[("ctrl_copy", "410m", "trained")]
    with pytest.raises(ValueError, match="inclusion"):
        vd(cells, fl, inc, br)


def test_verdict_refuses_byte_referent_length_mismatch():
    cells, fl, inc, br = batt()
    br[("rev_string7", "2.8b", "trained")] = \
        br[("rev_string7", "2.8b", "trained")][:499]
    with pytest.raises(ValueError, match="byte referent"):
        vd(cells, fl, inc, br)


# ------------------------------------------------------------- the loaders

def write_cell(root, rung, size, mode, **edits):
    label = LABELS[rung]
    rec = {"rung": rung, "size": size, "mode": mode, "n_items": 3,
           "continuations": [" " + label, " z", ""],
           "probe_labels": [label] * 3, "answers": [label + "x"] * 3,
           "full_string_correct": 1, "full_string_acc": 1 / 3,
           "max_new_tokens": 12, "n_shots": 2, "untrained_seed": None,
           "model_sha": "synthetic", "items_sha256": "synthetic"}
    rec.update(edits)
    p = Path(root) / "results" / f"{size}_{mode}" / f"{rung}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec))
    return p


def test_load_cells_scores_and_keeps_continuations(tmp_path):
    write_cell(tmp_path, "rev_string7", "410m", "trained")
    (c,) = a.load_cells(tmp_path)
    assert c["n"] == 3 and c["correct"] == 1 and "continuations" in c
    assert c["mean_continuation_len"] == pytest.approx((2 + 2 + 0) / 3)


def test_load_cells_never_ingests_top_level_artifacts(tmp_path):
    """A verdict record written at results/ top level must not become data
    on the next load (the loader reads only the canonical cell dirs)."""
    write_cell(tmp_path, "rev_string7", "410m", "trained")
    (tmp_path / "results" / "verdict_record.json").write_text(
        json.dumps({"verdict": "DISSOCIATION"}))
    assert len(a.load_cells(tmp_path)) == 1


def test_load_cells_refuses_a_non_cell_json_inside_a_cell_dir(tmp_path):
    write_cell(tmp_path, "rev_string7", "410m", "trained")
    (tmp_path / "results" / "410m_trained" / "notes.json").write_text("{}")
    with pytest.raises(ValueError, match="not a cell record"):
        a.load_cells(tmp_path)


def test_load_cells_refuses_path_content_disagreement(tmp_path):
    p = write_cell(tmp_path, "rev_string7", "410m", "trained")
    rec = json.loads(p.read_text())
    rec["size"] = "1b"
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="disagree"):
        a.load_cells(tmp_path)


def test_load_cells_refuses_an_n_items_mismatch(tmp_path):
    write_cell(tmp_path, "rev_string7", "410m", "trained", n_items=5)
    with pytest.raises(ValueError, match="n_items"):
        a.load_cells(tmp_path)


# ------------------------------------- committed referents, read not scored

def test_load_floors_real_tree_is_the_design_table():
    """sha pin + recompute-assert against the real committed artifacts, and
    the primaries are the design doc's: .056/.054/.052/.496, all marginal."""
    floors = a.load_floors()
    assert {r: floors[r]["primary"] for r in a.RUNGS} == {
        "rev_string7": 0.056, "reverse_string": 0.054,
        "ctrl_copy": 0.052, "clock24_d999": 0.496}
    assert all(floors[r]["primary_source"] == "marginal" for r in a.RUNGS)


def test_load_floors_rejects_a_tampered_file(tmp_path):
    raw = a.FLOORS_PATH.read_text().replace("0.056", "0.055")
    p = tmp_path / "chance_floors.json"
    p.write_text(raw)
    with pytest.raises(ValueError, match="sha256"):
        a.load_floors(p)


def test_load_floors_rejects_drifted_items():
    def fake_items(rung):
        return items(["a"] * 40)
    with pytest.raises(ValueError, match="recompute mismatch"):
        a.load_floors(items_loader=fake_items)


def test_load_inclusion_real_trees_match_the_design_table():
    refs = a.load_inclusion_referents()
    assert set(refs) == {(r, s, m) for r in a.RUNGS for s in a.PROBE_SIZES
                        for m in a.MODES}
    for k, ref in refs.items():
        assert ref["n"] == 500
        assert ref["correct"] == INCLUSION[k], k


def test_load_inclusion_refuses_a_missing_record(tmp_path):
    with pytest.raises(FileNotFoundError, match="no inclusion referent"):
        a.load_inclusion_referents(tmp_path, tmp_path)


def test_load_inclusion_refuses_a_valueless_record(tmp_path):
    for rung in a.RUNGS:
        tree = "2b" if rung in a.RUNGS_2B else "2c"
        for s in a.PROBE_SIZES:
            for m in a.MODES:
                p = tmp_path / tree / f"{s}_{m}" / f"{rung}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({"correct": 0, "n": 500}))
    p = tmp_path / "2c" / "410m_trained" / "ctrl_copy.json"
    p.write_text(json.dumps({"correct": None, "n": 500}))
    with pytest.raises(ValueError, match="no usable value"):
        a.load_inclusion_referents(tmp_path / "2c", tmp_path / "2b")


def test_load_byte_referents_real_tree_shape_only():
    """3a's 24 records load as byte referents: 500 continuations each.
    STRUCTURE ONLY — nothing here scores a real continuation."""
    refs = a.load_byte_referents()
    assert set(refs) == {(r, s, m) for r in a.RUNGS for s in a.EVAL_SIZES
                        for m in a.MODES}
    assert all(len(v) == 500 for v in refs.values())


def test_load_byte_referents_refuses_a_missing_record(tmp_path):
    with pytest.raises(FileNotFoundError, match="no byte referent"):
        a.load_byte_referents(tmp_path)


def test_load_probe_margins_committed_values():
    m = a.load_probe_margins()
    assert m["rev_string7"]["410m"] == pytest.approx(0.6263, abs=5e-5)
    assert m["rev_string7"]["1b"] == pytest.approx(0.7725, abs=5e-5)
    assert m["reverse_string"]["410m"] == pytest.approx(0.5731, abs=5e-5)
    assert m["reverse_string"]["1b"] == pytest.approx(0.6749, abs=5e-5)


def test_pooled_margins_appear_nowhere():
    """The paper's pooled .699/.624 was part of the original confound
    (design §3) and must not appear in this experiment's code or margins."""
    src = Path(a.__file__).read_text()
    assert "0.699" not in src and "0.624" not in src
    committed = a.MARGINS_PATH.read_text()
    assert "pooled" not in committed
    assert "0.699" not in committed and "0.624" not in committed
