# experiments/exp6/tests/test_power_6.py
"""The power record: the tree-level arithmetic, the declarations
re-derived from their own numbers, and the REAL producer's record
accepted by the analyzer's own check."""
import copy
import itertools

import numpy as np
import pytest

from experiments.exp2i import power_2i as pw
from experiments.exp6 import families_6 as fm
from experiments.exp6 import power_6 as p6w
from experiments.exp6.tests import _world_6 as W


def test_poisson_binomial_against_enumeration():
    ps = [0.9, 0.4, 0.75, 0.1]
    for k in range(6):
        want = sum(np.prod([p if b else 1 - p for p, b in zip(ps, bits)])
                   for bits in itertools.product([0, 1], repeat=4) if sum(bits) >= k)
        assert p6w.poisson_binomial_at_least(ps, k) == pytest.approx(want)
    assert p6w.poisson_binomial_at_least([], 0) == 1.0
    assert p6w.poisson_binomial_at_least([], 1) == 0.0
    assert p6w.poisson_binomial_at_least([1, 1, 1, 0], 3) == 1.0


def test_frechet_bounds():
    assert p6w.frechet(0.9, 0.8) == pytest.approx([0.7, 0.8])
    assert p6w.frechet(0.3, 0.4) == pytest.approx([0.0, 0.3])
    assert p6w.frechet(1.0, 1.0) == [1.0, 1.0]
    for p, q in ((0.2, 0.9), (0.5, 0.5), (0.0, 1.0)):
        lo, hi = p6w.frechet(p, q)
        assert 0 <= lo <= p * q <= hi <= min(p, q) + 1e-12   # independence lies inside


def _inputs(n_rungs=4, seed=0, constant=()):
    rng = np.random.default_rng(seed)
    rungs = [f"r{i}" for i in range(n_rungs)]
    out = {}
    for t, f in p6w.TESTS_6:
        x = {r: (np.zeros(500, dtype=int) if (t, r) in constant
                 else rng.integers(0, 40, size=500)).tolist() for r in rungs}
        out[(t, f)] = {"x": x, "strata": {r: {"strata": [str(i % 4) for i in range(500)]}
                                          for r in rungs},
                       "n_pos": {r: 250 for r in rungs}, "rungs": list(rungs),
                       "n_steps": len(fm.grid(f))}
    return out


def _record(inputs, p15=0.9, **over):
    tests = {}
    for t, f in p6w.TESTS_6:
        name = p6w.test_name(t, f)
        rec = W.fake_power_test(inputs[(t, f)], p15=over.get(name, p15))
        rec.update({"test": t, "family": f})
        tests[name] = rec
    return {"tests": tests, "tree": p6w.tree_level(tests)}


def test_tree_level_when_every_test_is_powered():
    rec = _record(_inputs())
    tree = rec["tree"]
    want = p6w.poisson_binomial_at_least([0.9] * 4, 3)
    assert tree["predictors"]["A"]["p_holds"]["0.15"] == pytest.approx(want)
    assert tree["p_general"]["0.15"] == pytest.approx(p6w.frechet(want, want))
    null_h = p6w.poisson_binomial_at_least([0.01] * 4, 3)
    assert tree["predictors"]["B"]["p_holds"]["null"] == pytest.approx(null_h)
    assert null_h < 1e-5
    fails = 1 - p6w.poisson_binomial_at_least([0.01] * 4, 2)
    assert tree["p_battery_bound"]["null"] == pytest.approx(p6w.frechet(fails, fails))
    assert tree["holds_at"] == 3 and "independent" in tree["independence_note"]


def test_a_predictor_with_two_evaluable_families_cannot_hold():
    inputs = _inputs(constant={("A", "r0"), ("A", "r1")})    # A reads two rungs: THIN
    rec = _record(inputs)
    a = rec["tree"]["predictors"]["A"]
    assert a["evaluable"] == [] and a["status_if_nothing_else"] == "U"
    assert set(a["p_holds"]) == {"0.1", "0.15", "0.2", "null"}
    assert set(a["p_holds"].values()) == set(a["p_fails"].values()) == {0.0}
    assert rec["tests"]["A:olmo7b"]["declared_status"] == "POWERED"
    assert rec["tests"]["A:olmo7b"]["thin"] is True
    assert rec["tree"]["p_general"]["0.15"] == [0.0, 0.0]
    assert p6w.claim_failures(rec, inputs) == []


def test_the_claims_are_rederived(monkeypatch):
    inputs = _inputs()
    rec = _record(inputs)
    assert p6w.claim_failures(rec, inputs) == []

    def broken(path, value):
        r = copy.deepcopy(rec)
        node = r
        for k in path[:-1]:
            node = node[k]
        node[path[-1]] = value
        return p6w.claim_failures(r, inputs)
    t = ("tests", "B:comma_7b")
    assert any("rungs are not R_f" in b for b in broken(t + ("rungs",), ["r0"]))
    assert any("n_pos_lower_bound" in b for b in broken(
        t + ("n_pos_lower_bound",), {"r0": 1}))
    assert any("grid's length" in b for b in broken(t + ("n_trained_steps",), 21))
    assert any("dropped_degenerate" in b for b in broken(
        t + ("dropped_degenerate",), ["r0"]))
    assert any("rungs_simulated" in b for b in broken(
        t + ("rungs_simulated",), ["r0", "r1", "r2"]))
    assert any("t_bar" in b for b in broken(t + ("t_bar",), 0.05))
    assert any("declared" in b for b in broken(
        t + ("declared_status",), "DECLARED UNDERPOWERED IN ADVANCE"))
    assert any("declared_status" in b for b in broken(t + ("declared_status",), "FINE"))
    assert any("n_sim" in b for b in broken(t + ("n_sim",), 3))
    assert any("tree-level" in b for b in broken(
        ("tree", "p_general", "0.15"), [0.0, 1.0]))
    r = copy.deepcopy(rec)
    del r["tests"]["A:olmo7b"]
    assert any("not the eight" in b for b in p6w.claim_failures(r, inputs))
    # a declaration ATTESTED against its own number (Exp 4 F-4)
    r = copy.deepcopy(rec)
    r["tests"]["A:olmo7b"]["targets"]["0.15"]["p_fires"] = 0.5
    assert any("declared POWERED against" in b for b in p6w.claim_failures(r, inputs))


def test_the_declaration_at_the_bar():
    """P(fires) equal to the bar is POWERED: the rule is >=."""
    inputs = _inputs()
    rec = _record(inputs, p15=pw.BAR)
    assert {t["declared_status"] for t in rec["tests"].values()} == {"POWERED"}
    assert p6w.claim_failures(rec, inputs) == []
    rec = _record(inputs, p15=pw.BAR - 1e-9)
    assert {t["declared_status"] for t in rec["tests"].values()} == \
        {"DECLARED UNDERPOWERED IN ADVANCE"}
    # the producer's rule and the checker's are one rule
    name = p6w.test_name("A", "olmo7b")
    test = dict(_record(inputs, p15=pw.BAR)["tests"][name],
                declared_status="DECLARED UNDERPOWERED IN ADVANCE")
    assert any("declared" in m for m in p6w.declaration_failures(name, test))


def _sealed_predictor(root):
    """The least a root needs for `power_6.main` to reach its own
    refusals: a predictor seal that describes the (empty) stage."""
    from experiments.exp6 import records_6 as r6
    from experiments.exp6.run import seal_predictor_6 as sp
    (r6.results(root) / "predictor").mkdir(parents=True)
    files = sp.file_table(root)
    r6.write_json(r6.seal_path(root), {"files": files,
                                       "sha256": r6.composite_sha(files)})


def test_the_power_record_is_written_once_and_after_the_rung_sets(tmp_path):
    from experiments.exp6 import records_6 as r6
    _sealed_predictor(tmp_path)
    with pytest.raises(RuntimeError, match="the rung sets are missing"):
        p6w.main([], root=tmp_path, **W.INJECT_SEAL)
    assert not r6.power_path(tmp_path).exists()
    r6.write_json(r6.power_path(tmp_path), {"written": "before"})
    with pytest.raises(RuntimeError, match="written ONCE"):
        p6w.main([], root=tmp_path, **W.INJECT_SEAL)
    assert r6.read_json(r6.power_path(tmp_path)) == {"written": "before"}
    with pytest.raises(RuntimeError, match="does not exist"):
        p6w.main([], root=tmp_path, **dict(W.INJECT_SEAL, tag_exists=lambda t: False))


def test_an_underpowered_test_is_declared(monkeypatch):
    inputs = _inputs()
    rec = _record(inputs, **{"A:olmo13b": 0.4})
    assert rec["tests"]["A:olmo13b"]["declared_status"] == \
        "DECLARED UNDERPOWERED IN ADVANCE"
    assert p6w.claim_failures(rec, inputs) == []
    ps = [0.9, 0.9, 0.4, 0.9]
    assert rec["tree"]["predictors"]["A"]["p_holds"]["0.15"] == pytest.approx(
        p6w.poisson_binomial_at_least(ps, 3))


@pytest.mark.slow
def test_the_real_producer_writes_a_record_the_analyzer_accepts(monkeypatch):
    """2d F-1's standard applied to power: the record the REAL producer
    leaves — 2i's simulation, shrunk — passes the analyzer's own check,
    serial and in a pool alike."""
    monkeypatch.setattr(pw, "N_SIM", 6)
    monkeypatch.setattr(pw, "N_PERM_POWER", 20)
    inputs = _inputs(n_rungs=3)
    rec = p6w.compute(inputs, jobs=1)
    assert p6w.claim_failures(rec, inputs) == []
    assert set(rec["tests"]) == {p6w.test_name(t, f) for t, f in p6w.TESTS_6}
    for r in rec["tests"].values():
        assert r["n_sim"] == 6 and set(r["targets"]) == {"0.1", "0.15", "0.2"}
        assert r["declared_status"] in p6w.STATUSES_6
    again = p6w.compute(inputs, jobs=1)
    assert again["tests"]["A:olmo7b"]["targets"] == rec["tests"]["A:olmo7b"]["targets"]
