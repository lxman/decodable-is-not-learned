"""Fixture suite for the frozen Exp 1b analysis. One synthetic case per
preregistered provision (design §5). No test reads real records.

Amended 2026-08-12 for the floor-corrected S1 (1b's one pre-committed change,
ruled by Michael after the untrained row measured grokking 9/10). Two provisions
changed shape and are tested in their new form:

  - S1-present now additionally requires accuracy > the cell's OWN untrained
    twin's accuracy. Pairing is per (system, size, seed).
  - The untrained row is no longer a verdict-touching bar. It cannot be one
    under the corrected criterion: an untrained cell cannot exceed its own
    accuracy, so the bar would be unfailable, and §6 forbids a gate no
    baseline can fail. It is reported as a diagnostic instead.
"""
import pytest
from experiments.exp1b import analyze_1b as a


def cells(system, present_by_size, acc=0.50):
    """present_by_size: {"1M": n_present, "10M": n_present}, 5 seeds each."""
    out = []
    for size, k in present_by_size.items():
        for seed in range(5):
            out.append({"system": system, "size_bucket": size,
                        "seed": 100 + seed, "present": seed < k,
                        "accuracy": acc})
    return out


def matrix(grok=(5, 4), above=(5, 5), below=(0, 0), untrained_present=0,
           trained_acc=0.50, twin_acc=0.10, below_acc=None):
    """below_acc defaults to trained_acc; set it to vary the absent row's
    accuracy without demoting the present rows along with it."""
    trained = (cells("grokking", dict(zip(a.SIZES, grok)), trained_acc)
               + cells("lubana_above", dict(zip(a.SIZES, above)), trained_acc)
               + cells("lubana_below", dict(zip(a.SIZES, below)),
                       trained_acc if below_acc is None else below_acc))
    untrained = []
    for system in a.TRAINED_ROWS:
        for size in a.SIZES:
            for seed in range(5):
                untrained.append({"system": system, "size_bucket": size,
                                  "seed": 100 + seed, "present": False,
                                  "accuracy": twin_acc})
    for i in range(untrained_present):
        untrained[i]["present"] = True
    return trained, untrained


def twin(untrained, system, size, seed):
    return next(c for c in untrained if c["system"] == system
                and c["size_bucket"] == size and c["seed"] == seed)


# --------------------------------------------------------------- the bars

def test_passes_on_the_expected_matrix():
    out = a.verdict(*matrix())
    assert out["verdict"] == "PASS"
    assert out["failures"] == []


def test_pools_counts_across_sizes():
    out = a.verdict(*matrix(grok=(5, 4)))
    assert out["rows"]["grokking"]["present"] == 9
    assert out["rows"]["grokking"]["n"] == 10
    assert out["rows"]["grokking"]["per_size"] == {"1M": 5, "10M": 4}


def test_present_row_below_the_bar_fails():
    out = a.verdict(*matrix(grok=(4, 3)))          # 7/10 < 8
    assert out["verdict"] == "FAIL"
    assert any("grokking" in f for f in out["failures"])


def test_a_single_fire_on_the_absent_row_fails():
    out = a.verdict(*matrix(below=(1, 0)))
    assert out["verdict"] == "FAIL"
    assert any("lubana_below" in f for f in out["failures"])


def test_pooling_tolerates_a_five_three_split_and_says_so():
    """Preregistered consequence of pooling: >=8/10 admits a split that a
    per-size >=4/5 bar would reject. Per-size counts stay visible."""
    out = a.verdict(*matrix(grok=(5, 3)))
    assert out["verdict"] == "PASS"
    assert out["rows"]["grokking"]["per_size"] == {"1M": 5, "10M": 3}


def test_zero_rows_carry_a_clopper_pearson_bound():
    out = a.verdict(*matrix())
    lo, hi = out["rows"]["lubana_below"]["cp95"]
    assert lo == 0.0
    assert 0.25 < hi < 0.35            # 0/10
    lo_u, hi_u = out["rows"]["untrained"]["cp95"]
    assert hi_u < 0.15                 # 0/30 is a much tighter bound


# ------------------------------------------------- the floor correction

def test_a_cell_that_does_not_beat_its_twin_is_not_present():
    """The correction. Raw S1 fires on every grokking cell, but none exceeds
    its untrained twin, so the corrected row is empty and the bar fails."""
    out = a.verdict(*matrix(grok=(5, 5), trained_acc=0.10, twin_acc=0.10))
    assert out["rows"]["grokking"]["present"] == 0
    assert out["rows"]["grokking"]["present_raw"] == 10
    assert out["verdict"] == "FAIL"


def test_the_correction_is_per_cell_paired_not_row_wide():
    """Raising ONE twin above its own trained cell demotes exactly that cell."""
    trained, untrained = matrix(grok=(5, 5))
    twin(untrained, "grokking", "1M", 100)["accuracy"] = 0.99
    out = a.verdict(trained, untrained)
    assert out["rows"]["grokking"]["present"] == 9
    assert out["rows"]["grokking"]["present_raw"] == 10
    assert out["rows"]["grokking"]["per_size"] == {"1M": 4, "10M": 5}


def test_the_correction_protects_the_absent_row_too():
    """A raw fire on lubana_below that does not beat its twin is not a fire.
    The absent row's bar is applied to the corrected count."""
    trained, untrained = matrix(below=(2, 0), below_acc=0.10, twin_acc=0.10)
    out = a.verdict(trained, untrained)
    assert out["rows"]["lubana_below"]["present_raw"] == 2
    assert out["rows"]["lubana_below"]["present"] == 0
    assert out["verdict"] == "PASS"


def test_equal_accuracy_does_not_count_as_beating_the_twin():
    """Strict inequality: a tie is not evidence training added anything."""
    out = a.verdict(*matrix(grok=(5, 5), trained_acc=0.25, twin_acc=0.25))
    assert out["rows"]["grokking"]["present"] == 0


def test_raw_and_corrected_counts_are_both_reported():
    """The correction's effect must be visible, not silently applied."""
    out = a.verdict(*matrix(grok=(5, 5), trained_acc=0.10, twin_acc=0.10))
    row = out["rows"]["grokking"]
    assert row["present_raw"] == 10 and row["present"] == 0
    assert row["per_size_raw"] == {"1M": 5, "10M": 5}
    assert row["per_size"] == {"1M": 0, "10M": 0}


# ------------------------------------------- the untrained row's new status

def test_untrained_fires_no_longer_fail_the_verdict():
    """Measured 2026-08-12: grokking twins fire 9/10. Under the corrected
    criterion that is calibration, not contamination, so it cannot fail the
    verdict — the correction already discounts it cell by cell."""
    out = a.verdict(*matrix(untrained_present=9))
    assert out["verdict"] == "PASS"
    assert out["rows"]["untrained"]["present"] == 9
    assert not any("untrained" in f for f in out["failures"])


def test_the_untrained_row_is_still_reported_with_its_rate():
    out = a.verdict(*matrix(untrained_present=9))
    row = out["rows"]["untrained"]
    assert row["n"] == 30
    assert row["present"] == 9
    assert row["cp95"][0] > 0.0        # a real rate, bounded away from zero
    assert row["verdict_touching"] is False


# --------------------------------------------------------- shape refusals

def test_missing_cells_are_refused_not_scored():
    trained, untrained = matrix()
    trained.pop()
    with pytest.raises(ValueError, match="incomplete"):
        a.verdict(trained, untrained)


def test_a_size_outside_the_matrix_is_refused():
    trained, untrained = matrix()
    trained.append({"system": "grokking", "size_bucket": "100M",
                    "seed": 100, "present": True, "accuracy": 0.5})
    with pytest.raises(ValueError, match="100M"):
        a.verdict(trained, untrained)


def test_a_trained_cell_without_a_twin_is_refused():
    """The corrected criterion is undefined without the twin; it must never
    silently fall back to theoretical chance."""
    trained, untrained = matrix()
    untrained.remove(twin(untrained, "grokking", "1M", 100))
    untrained.append({"system": "grokking", "size_bucket": "1M",
                      "seed": 199, "present": False, "accuracy": 0.1})
    with pytest.raises(ValueError, match="twin"):
        a.verdict(trained, untrained)


def test_duplicate_twins_are_refused():
    """Swap one twin for a copy of another: the count stays 10, so this tests
    duplicate detection rather than re-testing the shape check."""
    trained, untrained = matrix()
    untrained.remove(twin(untrained, "grokking", "1M", 101))
    untrained.append(dict(twin(untrained, "grokking", "1M", 100)))
    with pytest.raises(ValueError, match="duplicate"):
        a.verdict(trained, untrained)
