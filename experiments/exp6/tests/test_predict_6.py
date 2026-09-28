# experiments/exp6/tests/test_predict_6.py
"""The predictor stage's own rules, each on the smallest tree that shows
it: nothing here samples, and no world is built."""
import pytest

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import records_6 as r6
from experiments.exp6 import referents_6 as rf
from experiments.exp6.run import predict_6 as pr
from experiments.exp6.run import seal_predictor_6 as sp
from experiments.exp6.tests import _world_6 as W


def _no_sampler(*a, **k):
    raise AssertionError("sampled")


def _files(root):
    return [p for p in root.rglob("*") if p.is_file()]


@pytest.mark.parametrize("predictor", sorted(r6.PREDICTORS_6))
def test_the_gated_units_run_first(predictor):
    """A unit that regenerates a committed stream runs before any unit
    that samples something new: a stack that has drifted halts on its
    first gated item, with nothing new on disk."""
    trained, twin = pr.unit_order(predictor)
    gated = [(t, r) for p, t, r in rf.gated_units() if p == predictor]
    assert gated and trained[:len(gated)] == gated
    rest = trained[len(gated):]
    assert not set(gated) & set(rest)
    assert [t for t, _ in rest] == sorted((t for t, _ in rest),
                                          key=("pilot", "main").index)
    assert all(t == "twin" for t, _ in twin)
    assert sorted(trained + twin) == sorted(
        (t, r) for p, t, r in r6.predictor_units() if p == predictor)


def test_a_torn_unit_is_not_resumed(tmp_path):
    """The draws are written before the record; a kill between the two
    leaves draws without a record. Neither half alone is a unit, and a
    resume refuses rather than sample over it."""
    p = "pythia_1b"
    t, r = pr.unit_order(p)[0][0]
    assert pr.unit_complete(tmp_path, p, t, r) is False
    rec = r6.tier_record_path(tmp_path, p, t, r)
    dr = r6.tier_draws_path(tmp_path, p, t, r)
    for half in (rec, dr):
        half.parent.mkdir(parents=True, exist_ok=True)
        half.write_bytes(b"{}")
        with pytest.raises(RuntimeError, match="torn record"):
            pr.unit_complete(tmp_path, p, t, r)

        def loader(*a):
            raise AssertionError("loaded")
        with pytest.raises(RuntimeError, match="torn record"):
            pr.run(p, root=tmp_path, loader=loader, sampler=_no_sampler, **W.INJECT)
        half.unlink()
    assert pr.unit_complete(tmp_path, p, t, r) is False


@pytest.mark.parametrize("field", ["commit", "model_sha"])
def test_a_loader_off_its_pin_samples_nothing(tmp_path, field):
    def loader(predictor, mode, device):
        tok, model, rec = W.fake_predictor_loader(predictor, mode, device)
        return tok, model, dict(rec, **{field: "0" * 40})
    with pytest.raises(RuntimeError, match="against the pin"):
        pr.run("pythia_1b", root=tmp_path, loader=loader, sampler=_no_sampler,
               **W.INJECT)
    assert _files(tmp_path) == []


def test_the_predictor_seal_refuses_a_tree_with_failures(tmp_path):
    with pytest.raises(RuntimeError, match="cannot seal: "):
        sp.seal(tmp_path, **W.INJECT)
    assert _files(tmp_path) == []


def test_gate_1p_counts_its_coverage(tmp_path):
    """A re-derivation that compared fewer draws than the committed
    stream holds is not a pass, though nothing it compared differs (3d,
    2h F-2)."""
    p, t, r = rf.gated_units()[0]
    rows = rf.committed_rows(p, t, r)
    name = f"6 gate 1-P {p}/{t}/{r}:"
    bad, out = sp.gate1p(tmp_path, {(p, t, r): {"rows": rows}})
    assert not any(m.startswith(name) for m in bad)
    k = r6.tier_shape(p, t)["k"]
    assert out[f"{p}/{t}/{r}"] == dict(
        out[f"{p}/{t}/{r}"], items_compared=b6.N_ITEMS, draws_compared=b6.N_ITEMS * k,
        n_diffs=0)
    bad, out = sp.gate1p(tmp_path, {(p, t, r): {"rows": rows[:-1]}})
    assert out[f"{p}/{t}/{r}"]["n_diffs"] == 0
    assert [m for m in bad if m.startswith(name)] == [
        f"{name} 0 diffs over {(b6.N_ITEMS - 1) * k} of {b6.N_ITEMS * k} draws"]
    # every other gated unit is missing, and says so
    assert len(bad) == len(rf.gated_units())


def test_the_predictor_is_sealed_once_and_nothing_is_sampled_after(tmp_path):
    seal = r6.seal_path(tmp_path)
    seal.parent.mkdir(parents=True)
    seal.write_text("{}")
    with pytest.raises(RuntimeError, match="already sealed"):
        sp.seal(tmp_path, **W.INJECT)
    assert seal.read_text() == "{}"

    def loader(*a):
        raise AssertionError("loaded")
    with pytest.raises(RuntimeError, match="nothing may be sampled after"):
        pr.run("pythia_1b", root=tmp_path, loader=loader, sampler=_no_sampler,
               **W.INJECT)
    assert _files(tmp_path) == [seal]


def test_the_predictor_seal_refuses_over_a_halt_marker(tmp_path):
    for marker in (r6.predictor_halt_path(tmp_path),
                   r6.tier_halt_path(tmp_path, "pythia_1b", "main", "sub_base8")):
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("x")
        with pytest.raises(RuntimeError, match="halt marker"):
            sp.seal(tmp_path, **W.INJECT)
        assert not r6.seal_path(tmp_path).exists()
        marker.unlink()


def test_a_loader_that_is_handed_in_is_the_one_used(tmp_path, monkeypatch):
    """What a caller hands in is used, falsy or not (see the same test of
    the endpoint stage and the sweep)."""
    W.no_real_loaders(monkeypatch)
    with pytest.raises(AssertionError, match="reached its loader$"):
        pr.run("pythia_1b", root=tmp_path, loader=W.Unreached(),
               sampler=W.Unreached(), **W.INJECT)
    with pytest.raises(AssertionError, match="^sampled$"):
        pr.run("pythia_1b", root=tmp_path, loader=W.fake_predictor_loader,
               sampler=_FalsySampler(), **W.INJECT)


class _FalsySampler:
    def __bool__(self):
        return False

    def __call__(self, *a, **k):
        raise AssertionError("sampled")
