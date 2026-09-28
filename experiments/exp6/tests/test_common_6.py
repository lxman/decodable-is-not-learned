# experiments/exp6/tests/test_common_6.py
"""What every runner shares: the host record and its pin."""
import pytest

from experiments.exp6.run import _common_6 as cm
from experiments.exp6.tests import _world_6 as W


def test_the_stack_pin_is_exp5s():
    from experiments.exp5 import battery_5 as b5      # imports torch; the analyzer does not
    assert cm.STACK_PIN_6 == b5.STACK_PIN_5 and cm.PYTHON_PIN_6 == b5.PYTHON_PIN_5
    good = W.host()
    assert cm.stack_pin_failures(good) == b5.stack_pin_failures_5(good) == []
    for k in cm.STACK_PIN_6:
        bad = dict(good, stack=dict(good["stack"], **{k: "0.0.1"}))
        assert len(cm.stack_pin_failures(bad)) == len(b5.stack_pin_failures_5(bad)) == 1
    assert len(cm.stack_pin_failures(dict(good, python="3.12.1"))) == 1
    cu = dict(good, stack=dict(good["stack"], torch="2.12.1+cu130"))
    assert cm.stack_pin_failures(cu) == []            # a build suffix is not a version


def test_a_host_record_is_named_by_what_identifies_the_host(tmp_path):
    a, b = W.host("box-1"), W.host("box-1")
    assert a["sha256"] == b["sha256"] == cm.host_key(a)   # the clock is not in the key
    assert W.host("box-2")["sha256"] != a["sha256"]
    assert cm.host_failures(a) == []
    assert any("sha256" in m for m in cm.host_failures(dict(a, node="other")))
    assert any("gpu" in m for m in cm.host_failures(dict(a, gpu="")))
    rec = cm.ensure_host(tmp_path, "cuda", stack_=dict(W.STACK), gpu="A100",
                         cuda="13.0", node="n", python="3.11.9", platform_="Linux",
                         nvidia_smi="x")
    p = cm.hosts_dir(tmp_path) / f"{rec['sha256'][:12]}.json"
    assert p.is_file()
    again = cm.ensure_host(tmp_path, "cuda", stack_=dict(W.STACK), gpu="A100",
                           cuda="13.0", node="n", python="3.11.9", platform_="Linux",
                           nvidia_smi="x")
    assert again == rec                                # written once, re-read after
    p.write_text(p.read_text().replace('"n"', '"m"'))
    with pytest.raises(RuntimeError, match="does not hash to its own name"):
        cm.ensure_host(tmp_path, "cuda", stack_=dict(W.STACK), gpu="A100", cuda="13.0",
                       node="n", python="3.11.9", platform_="Linux", nvidia_smi="x")


def test_a_runner_refuses_over_a_halt_marker(tmp_path):
    from experiments.exp6 import records_6 as r6
    cm.refuse_if_halted(tmp_path)
    r6.sweep_halt_path(tmp_path, "olmo7b").parent.mkdir(parents=True)
    r6.sweep_halt_path(tmp_path, "olmo7b").write_text("x")
    with pytest.raises(RuntimeError, match="halt marker"):
        cm.refuse_if_halted(tmp_path)


def test_the_exit_gate(tmp_path):
    """A runner checks again when its work is done: what it imported
    lazily was not on the surface at entry. A failure leaves the stage's
    halt marker and raises."""
    from experiments.exp6 import pins_6 as p6
    from experiments.exp6 import records_6 as r6
    marker = r6.sweep_halt_path(tmp_path, "olmo7b")
    cm.exit_gate(marker, frozen_check=lambda: None)
    assert not marker.exists() and r6.halt_markers(tmp_path) == []

    def boom():
        raise RuntimeError("imported module drifted: experiments/exp3/sampler.py")
    with pytest.raises(RuntimeError, match="EXIT GATE FIRED: imported module drifted"):
        cm.exit_gate(marker, frozen_check=boom)
    assert "exit gate: RuntimeError: imported module drifted" in marker.read_text()
    assert r6.halt_markers(tmp_path) == [marker]
    # with nothing injected it is the real pins that are checked
    if not p6.FROZEN_SHA256_6:
        with pytest.raises(RuntimeError, match="EXIT GATE FIRED: .*not pinned"):
            cm.exit_gate(r6.predictor_halt_path(tmp_path))
        assert r6.predictor_halt_path(tmp_path) in r6.halt_markers(tmp_path)
    seen = []

    def both():                       # the frozen modules AND the import surface
        seen.append("frozen")
    cm.exit_gate(marker, frozen_check=both)
    assert seen == ["frozen"]


def test_the_gates_every_runner_passes(monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        cm.gates(tag_exists=lambda t: False, blob_sha=W.blob_sha,
                 frozen_check=lambda: None)
    cm.gates(**W.INJECT)

    def boom():
        raise RuntimeError("frozen module drifted")
    with pytest.raises(RuntimeError, match="drifted"):
        cm.gates(tag_exists=W.tag_exists, blob_sha=W.blob_sha, frozen_check=boom)


def test_the_predictor_stage_binds_its_real_loader_and_sampler(monkeypatch):
    """No model is loaded: the frozen loaders are replaced by recorders
    and the calls `predict_6` makes are bound against the frozen
    signatures, so a keyword the frozen function does not take is found
    here and not at the first model contact."""
    import inspect

    from experiments.exp2i import battery_2i as bi
    from experiments.exp3 import sampler
    from experiments.exp3.run import run_cell
    from experiments.exp6 import records_6 as r6
    from experiments.exp6 import referents_6 as rf
    from experiments.exp6.run import predict_6 as pr

    seen = []

    def recorder(real, out):
        def call(*a, **k):
            inspect.signature(real).bind(*a, **k)       # TypeError if it cannot
            seen.append((real.__name__, a, k))
            return out
        return call
    monkeypatch.setattr(run_cell, "_assert_module_provenance", lambda: None)
    monkeypatch.setattr(run_cell, "_load_model",
                        recorder(run_cell._load_model, ("T", "M", "sha-of-the-revision")))
    monkeypatch.setattr(bi, "load_thin",
                        recorder(bi.load_thin, ("M", "T", {"commit": "c",
                                                            "tensor_digest": "d"})))
    tok, model, rec = pr.real_loader("pythia_1b", "untrained", "mps")
    assert (tok, model) == ("T", "M") and rec["model_sha"] == "sha-of-the-revision"
    assert seen[-1] == ("_load_model", ("1b", "untrained", r6.SAMPLING_DTYPE), {})
    tok, model, rec = pr.real_loader("olmo2_1b", "trained", "mps")
    assert (tok, model) == ("T", "M") and rec == {
        "repo": bi.REPO_1B, "commit": "c", "model_sha": "d"}
    name, a, k = seen[-1]
    assert name == "load_thin" and a == (bi.REPO_1B, rf.model_pin("olmo2_1b")["commit"])
    assert k == {"device": "mps", "dtype": r6.SAMPLING_DTYPE}
    with pytest.raises(ValueError, match="no untrained twin"):
        pr.real_loader("olmo2_1b", "untrained", "mps")
    # the sampler, as `run_unit` calls it
    assert pr.real_sampler() is sampler.sample_item
    inspect.signature(sampler.sample_item).bind(
        "model", "tok", "prompt", rung="lcs", size="olmo1b", mode="trained", item_idx=0,
        seeds=(0,), draws_per_seed=64, max_new_tokens=8, terminal_ids=(0,))
