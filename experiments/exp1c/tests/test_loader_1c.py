"""Fixture suite for 1c's loader, cell assembly and Stage A gate.

These exist as tests because 1b froze `analyze_1b.py` with a `verdict()` and
NO record loader, and the gap surfaced at analysis time — `run_analysis_1b.py`
had to be written and committed after the campaign had already run. Design §9
makes the loader part of the frozen artifact. A frozen verdict function that
cannot be fed from disk is not a frozen analysis.
"""
import pytest

from experiments.exp1c import analyze_1c as a
from experiments.exp1c import records as r


# ------------------------------------------------------------------ builders

def sites(acc_by_layer, null_p=0.0001, with_null=True):
    return [r.SiteResult(layer=l, token=t, accuracy=acc_by_layer[l],
                         null_p_raw=null_p if with_null else None,
                         null_mean=0.1 if with_null else None)
            for l in (0, 1, 2, 3) for t in (1, -1)]


def profile(density, size, seed, trained, acc_by_layer, system="sweep",
            arm="fixed", null_p=0.0001, capability=0.09):
    return r.ProfileRecord(
        system=system, arm=arm, density=density, size_bucket=size, seed=seed,
        trained=trained, sites=sites(acc_by_layer, null_p, arm == "fixed"),
        n_rows=400, n_val=100, per_class=40 if arm == "fixed" else None,
        capability_metric=capability if trained else None,
        git_sha="abc1234")


def sweep_profiles(depth_at_085=0.0, flat_acc=0.10):
    """Trained + twin profiles for the full 40-cell sweep."""
    out = []
    for d in a.DENSITIES:
        lift = depth_at_085 * (d - 0.25) / 0.60
        for size in a.SIZES:
            for seed in a.SEEDS:
                out.append(profile(d, size, seed, True,
                                   {0: flat_acc, 1: flat_acc + lift,
                                    2: flat_acc + lift, 3: flat_acc + lift}))
                out.append(profile(d, size, seed, False,
                                   {0: flat_acc, 1: flat_acc, 2: flat_acc,
                                    3: flat_acc}))
    return out


# ------------------------------------------------------------- the loader

def test_the_loader_reads_what_the_runner_wrote(tmp_path):
    p = profile(0.45, "1M", 100, True, {0: .1, 1: .2, 2: .3, 3: .4})
    p.save(r.record_path(tmp_path, "sweep", "fixed", 0.45, "1M", 100, True))
    got = a.load_profiles(tmp_path)
    assert len(got) == 1
    assert got[0].density == 0.45 and got[0].trained is True


def test_the_loader_separates_the_two_arms(tmp_path):
    for arm in ("fixed", "natural"):
        pr = profile(0.45, "1M", 100, True, {0: .1, 1: .2, 2: .3, 3: .4},
                     arm=arm)
        pr.save(r.record_path(tmp_path, "sweep", arm, 0.45, "1M", 100, True))
    assert len(a.load_profiles(tmp_path)) == 2
    assert len(a.load_profiles(tmp_path, arm="fixed")) == 1
    assert a.load_profiles(tmp_path, arm="natural")[0].arm == "natural"


def test_the_loader_returns_empty_rather_than_failing_on_a_missing_tree(tmp_path):
    assert a.load_profiles(tmp_path / "nothing-here") == []


# --------------------------------------------------------- cell assembly

def test_assembly_pairs_each_trained_cell_with_its_own_twin():
    cells = a.assemble_cells(sweep_profiles(depth_at_085=0.12))
    assert len(cells) == 40
    at85 = [c for c in cells if c["density"] == 0.85]
    assert all(c["depth_margin"] == pytest.approx(0.12) for c in at85)
    assert all(c["l0_margin"] == pytest.approx(0.0) for c in at85)


def test_assembly_refuses_a_trained_cell_with_no_twin():
    profs = [p for p in sweep_profiles() if p.trained]
    with pytest.raises(ValueError, match="twin"):
        a.assemble_cells(profs)


def test_assembly_refuses_two_twins_for_one_cell():
    profs = sweep_profiles()
    profs.append(profs[1])
    with pytest.raises(ValueError, match="duplicate"):
        a.assemble_cells(profs)


def test_assembly_attaches_the_capability_metric_from_the_trained_cell():
    """'Structure accumulates while capability stays flat' is a measured
    conjunction — design §4 — so the metric must ride along with the margin."""
    cells = a.assemble_cells(sweep_profiles())
    assert all(c["capability_metric"] == pytest.approx(0.09) for c in cells)


def test_assembly_output_feeds_the_verdict_directly():
    """The loop 1b could not close: records on disk -> verdict, no glue."""
    cells = a.assemble_cells(sweep_profiles(depth_at_085=0.12))
    out = a.verdict({"pass": True, "failures": []}, cells, below_silent=True,
                    n_draw=2000, seed=1)
    assert out["verdict"] == "PASS"
    assert out["n_blocks"] == 10


# --------------------------------------------------------- the Stage A gate

def pairs(margins, l0=0.0):
    """One (trained, twin) profile pair per margin value."""
    out = []
    for i, m in enumerate(margins):
        size = a.SIZES[i % 2]
        out.append(profile(10.0, size, 100 + i // 2, True,
                           {0: 0.10 + l0, 1: 0.10 + m, 2: 0.10 + m,
                            3: 0.10 + m}, system="lubana_above"))
        out.append(profile(10.0, size, 100 + i // 2, False,
                           {0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10},
                           system="lubana_above"))
    return out


def below_pairs(margins):
    out = []
    for i, m in enumerate(margins):
        size = a.SIZES[i % 2]
        out.append(profile(0.50, size, 100 + i // 2, True,
                           {0: 0.10, 1: 0.10 + m, 2: 0.10 + m, 3: 0.10 + m},
                           system="lubana_below"))
        out.append(profile(0.50, size, 100 + i // 2, False,
                           {0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10},
                           system="lubana_below"))
    return out


# The absent row scatters around zero rather than sitting at a constant. These
# are 1b's OWN measured paired margins for lubana_below (argmax statistic):
# 6/10 positive, mean +.0123, sign-flip p = .099. The gate is calibrated
# against real data rather than against a fixture invented to pass it.
BELOW_1B = [-0.0108, 0.0155, 0.0105, -0.0220, 0.0107,
            0.0591, -0.0206, 0.0421, 0.0385, 0.0000]


def test_stage_a_passes_when_the_known_answers_reproduce():
    out = a.stage_a_gate(pairs([0.20] * 10), below_pairs(BELOW_1B), seed=1)
    assert out["pass"] is True
    assert out["failures"] == []
    assert out["below_p"] > 0.05


def test_stage_a_fails_when_the_present_row_is_mostly_silent():
    out = a.stage_a_gate(pairs([0.20] * 3 + [-0.01] * 7),
                         below_pairs(BELOW_1B), seed=1)
    assert out["pass"] is False
    assert any("lubana_above" in f for f in out["failures"])


def test_a_small_but_perfectly_consistent_bias_trips_the_absent_row():
    """A margin of +0.001 in all ten cells is tiny but not chance: under sign
    exchangeability only 1 of 1024 relabelings matches it. The gate must catch
    a systematic floor error even when its magnitude looks negligible — 2c's
    chance-floor defect was exactly a small consistent bias."""
    out = a.stage_a_gate(pairs([0.20] * 10), below_pairs([0.001] * 10), seed=1)
    assert out["pass"] is False
    assert any("lubana_below" in f for f in out["failures"])


def test_stage_a_fails_when_the_absent_row_shows_structure():
    """If the new measure reads structure where 1b's closed record found none,
    it is the measure that is wrong."""
    out = a.stage_a_gate(pairs([0.20] * 10), below_pairs([0.20] * 10), seed=1)
    assert out["pass"] is False
    assert any("lubana_below" in f for f in out["failures"])


def test_stage_a_measures_the_variance_the_power_table_needs():
    """Design §5: sd is not guessed, it is measured here and the power table
    is finalized against it BEFORE Stage B runs."""
    out = a.stage_a_gate(pairs([0.20] * 10),
                         below_pairs([0.00, 0.02, 0.04, 0.01, 0.03,
                                      0.02, 0.01, 0.03, 0.02, 0.02]), seed=1)
    # sample sd (ddof=1) of those ten margins is sqrt(12/9)/100. Pinned tightly
    # on purpose: at abs=5e-4 the population sd (0.010954) also passes, and a
    # variance that silently means n rather than n-1 is exactly the kind of
    # quiet units error that killed Exp 1.
    assert out["sd_depth_margin"] == pytest.approx(0.011547, abs=1e-5)


def test_stage_a_requires_ten_cells_per_row():
    with pytest.raises(ValueError, match="10"):
        a.stage_a_gate(pairs([0.20] * 8), below_pairs([0.001] * 10), seed=1)


# ---------------------------------------------------- statistical calibration

def test_the_permutation_null_holds_its_type_one_rate():
    """A frozen statistic whose false-positive rate is not measured is not
    frozen, it is merely fixed. 2c's power table assumed structure the
    realized data did not have; this one is checked."""
    import numpy as np
    rng = np.random.default_rng(11)
    rejects = 0
    n_sim = 400
    for i in range(n_sim):
        blocks = [dict(zip(a.DENSITIES, rng.normal(0, 0.02, 4)))
                  for _ in range(10)]
        if a.slope_and_p(blocks, n_draw=500, seed=int(rng.integers(1e6)))["p"] < 0.01:
            rejects += 1
    assert rejects / n_sim <= 0.035     # ~5 sd above 0.01 at n=400
