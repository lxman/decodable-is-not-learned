"""The committed power tables must be exactly what the frozen code
produces (design §7, Open item 6; freeze checklist re-runs this cold),
and the inversion must agree with the adjudication convention in both
directions at the critical count.
"""
import json

import pytest

from experiments.exp3 import analyze_3 as a
from experiments.exp3 import compute_power as cp


def test_critical_count_is_the_significance_boundary():
    """K* fires the frozen test and K* − 1 does not — the inversion is
    of the same function the verdict adjudicates through."""
    k = cp.critical_count(500)
    _, sig_at = a.sign_test_significance(k, 500, n_tests=a.N_ADJ_TESTS)
    _, sig_below = a.sign_test_significance(k - 1, 500,
                                            n_tests=a.N_ADJ_TESTS)
    assert sig_at is True and sig_below is False


def test_control_critical_count_is_lower_at_n_tests_1():
    assert cp.critical_count(500, n_tests=1) < cp.critical_count(500)


def test_power_is_monotone_in_theta_and_n():
    assert cp.sign_test_power(0.60, 500) > cp.sign_test_power(0.55, 500)
    assert cp.sign_test_power(0.60, 500) > cp.sign_test_power(0.60, 300)


def test_detection_closed_form():
    """1 − (1−p)^k, and the .95-detectable rate equals cp_upper(0, k) —
    the same bound read from both sides."""
    assert cp.detection(2.3405e-5, 128_000) == pytest.approx(0.95,
                                                             abs=1e-3)
    assert cp.build()["sampling"]["rate_detectable_at_95"]["128000"] == \
        pytest.approx(a.cp_upper(0, 128_000), abs=1e-15)


def test_committed_power_json_matches_the_frozen_code():
    """Byte-for-value lock between power.json and build(): the freeze
    re-runs this comparison cold, and a drifted table cannot hide."""
    committed = json.loads(cp.OUT.read_text())
    rebuilt = json.loads(json.dumps(cp.build(), sort_keys=True))
    assert committed == rebuilt


def test_doc_quotes_agree_or_are_flagged():
    """§7's quoted numbers, cross-checked; a disagreement must surface
    as agrees=False (ledger material), never silently."""
    q = cp.build()["doc_quotes_check"]
    assert all("quoted" in v and "computed" in v and "agrees" in v
               for v in q.values())
    disagreements = {k: v for k, v in q.items() if not v["agrees"]}
    assert disagreements == {}, disagreements
