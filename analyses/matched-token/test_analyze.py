"""Synthetic-only tests. No production loader, statistics or bootstrap run."""
from contextlib import nullcontext
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


a = module("matched_token_analysis", "analyze.py")
v = module("matched_token_checker", "verify_outputs.py")


def test_fixed_scope_and_independent_battery_map():
    from experiments.exp2d import battery_2d as bt
    from experiments.exp5 import battery_5 as b5
    assert a.SIZES == tuple(v.EXPECTED["sizes"])
    assert a.STEPS == tuple(v.EXPECTED["steps"])
    assert v.FROZEN_RUNGS == list(bt.RUNG_ORDER_2D)
    assert {r for r, _ in v.FROZEN_RUNGS if b5.RUNG_TYPE_5[r] == "option"} == v.OPTION
    assert {r for r, _ in v.FROZEN_RUNGS if b5.RUNG_TYPE_5[r] == "string"} == v.STRING


@pytest.fixture
def data():
    # Four rungs, three families: the first family deliberately has two rungs.
    bits = np.array([
        [[1, 1, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
        [[0, 1, 1, 0], [1, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
        [[1, 0, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
    ], dtype=np.uint8)
    return a.Data(
        sizes=("small", "middle", "large"), steps=(1000, 5000, 143000),
        rungs=("a", "b", "c", "d"), family_of={"a": "A", "b": "A", "c": "B", "d": "C"},
        type_of={"a": "arithmetic", "b": "arithmetic", "c": "option", "d": "string"},
        params=(100, 200, 800), floors={r: .1 for r in "abcd"},
        thresholds={r: 2 for r in "abcd"}, bits=np.stack([bits, bits[:, :, ::-1], bits]),
    )


@pytest.fixture
def draws():
    return np.array([[0, 0, 1], [0, 1, 2], [2, 2, 2], [1, 1, 0]], dtype=np.int64)


def test_paired_and_texture(data):
    pair = a.paired_counts(data.bits[0, 0, 0], data.bits[0, 1, 0])
    assert pair == {"n00": 1, "n01": 1, "n10": 1, "n11": 1}
    tex = a.texture(data.bits[0, :, 0], data.params)
    assert tex["ever_correct"] == 4
    assert tex["any_loss"] == 2  # item 0 loses then regains; item 1 later loses
    assert tex["loss_fraction_all"] == .5
    assert tex["loss_fraction_ever"] == .5
    assert tex["adjacent_decreases"] == 0  # counts conceal item churn
    assert tex["nondecreasing"] is True
    assert tex["slope_accuracy_per_doubling"] == pytest.approx(5 / 56)
    assert tex["spearman"] == pytest.approx(np.sqrt(.75))
    assert sum(tex["size_pattern_counts"]) == 4


def test_constant_and_decreasing_texture():
    for bit in [0, 1]:
        row = a.texture(np.full((3, 4), bit), [1, 2, 4])
        assert row["spearman"] is None
        assert row["slope_accuracy_per_doubling"] == 0
        assert row["any_loss"] == 0
        assert row["loss_fraction_ever"] == (None if bit == 0 else 0)
    row = a.texture(np.array([[1, 1], [1, 0], [0, 0]]), [1, 2, 4])
    assert row["adjacent_decreases"] == 2
    assert not row["nondecreasing"]
    assert row["spearman"] == -1
    assert row["loss_fraction_ever"] == 1


def test_uneven_family_bootstrap():
    # Draw A,A,B retains BOTH A rungs on BOTH occurrences (5 rungs).
    result = a.bootstrap_means(np.array([0., 1., 3.]), ["A", "A", "B"],
                               np.array([[0, 0], [0, 1], [1, 1]]))
    np.testing.assert_allclose(result["all_rung"], [.5, 4 / 3, 3])
    np.testing.assert_allclose(result["equal_family"], [.5, 1.75, 3])


def test_complete_tables_and_shared_draws(data, draws):
    summary, tables = a.summarize(data, draws)
    assert {k: len(rows) for k, rows in tables.items()} == {
        "counts": 36, "accuracy": 9, "contrasts": 9, "transitions": 36,
        "texture": 12, "time_averages": 6,
    }
    for row in tables["transitions"]:
        assert sum(row[k] for k in ("n00", "n01", "n10", "n11")) == 4
        assert row["n01"] - row["n10"] == row["correct_difference"]
    for row in tables["time_averages"]:
        assert row["n_checkpoints"] == (3 if row["grid"] == "all_steps" else 2)
    # Every condition has the same family values, so paired intervals must match.
    for pair in [("small", "middle"), ("small", "large"), ("middle", "large")]:
        rows = [r for r in tables["contrasts"] if (r["smaller"], r["larger"]) == pair]
        assert len({(r["all_rung_ci_low_pp"], r["all_rung_ci_high_pp"]) for r in rows}) == 1
    assert summary["scope"]["n_items_per_rung"] == 4


def test_time_average_pairs_whole_conditions(data, draws):
    data.bits[1] = 0  # synthetic search-added checkpoint has no size difference
    _, tables = a.summarize(data, draws)
    rows = {(r["grid"], r["smaller"], r["larger"]): r for r in tables["time_averages"]}
    for smaller, larger in [("small", "middle"), ("small", "large"), ("middle", "large")]:
        full, spine = (rows[g, smaller, larger] for g in ("all_steps", "shared_spine"))
        for key in ("all_rung_pp", "equal_family_pp", "all_rung_ci_low_pp", "all_rung_ci_high_pp",
                    "equal_family_ci_low_pp", "equal_family_ci_high_pp"):
            assert full[key] == pytest.approx((2 / 3) * spine[key])


def test_validate_only_cannot_reach_statistics(tmp_path, monkeypatch, capsys, data):
    fake_pin = SimpleNamespace(bind=lambda _: None, recheck=lambda: None, files={}, commit="fixture")
    monkeypatch.setattr(a, "HERE", tmp_path)
    monkeypatch.setattr(a, "Bindings", lambda *_: fake_pin)
    monkeypatch.setattr(a, "check_imported", lambda *_: None)
    monkeypatch.setattr(a, "pinned_imports", lambda *_: nullcontext())
    monkeypatch.setattr(a, "load_selected", lambda _: (data, {}))
    def forbidden(*args, **kwargs):
        pytest.fail("validate-only reached production statistics/output")
    for name in ("summarize", "frozen_thresholds", "write_outputs", "reserve_output"):
        monkeypatch.setattr(a, name, forbidden)
    monkeypatch.setattr(a.np.random, "default_rng", forbidden)
    assert a.main(["--validate-only"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["state"] == "validated"
    assert set(output) == {"state", "units", "rung_records", "rederived_bits", "bound_source_files", "bound_launch_files"}
    assert not (tmp_path / "results").exists()


def test_write_once(tmp_path):
    dest = tmp_path / "results"
    a.reserve_output(dest)
    with pytest.raises(a.Refusal, match="exists"):
        a.reserve_output(dest)
    (dest / "valuable").write_text("keep")
    with pytest.raises(a.Refusal):
        a.reserve_output(dest)
    assert (dest / "valuable").read_text() == "keep"


def git(root, *args):
    return subprocess.check_output([a.GIT, "-C", str(root), *args]).decode().strip()


def test_binding_tamper_and_exit_recheck(tmp_path):
    git(tmp_path, "init", "-q")
    p = tmp_path / "payload.json"
    p.write_text('{"value": 1}')
    git(tmp_path, "add", "payload.json")
    git(tmp_path, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "synthetic source")
    pin = a.Bindings(tmp_path, git(tmp_path, "rev-parse", "HEAD"))
    assert pin.bind(p)["sha256"] == a.sha256(p.read_bytes())
    p.write_text('{"value": 2}')
    with pytest.raises(a.Refusal, match="binding"):
        pin.recheck()
    with pytest.raises(a.Refusal, match="binding"):
        pin.bind(p)
    (tmp_path / "untracked.py").write_text("x=1")
    with pytest.raises(a.Refusal):
        pin.bind(tmp_path / "untracked.py")


def test_import_refuses_before_execution(tmp_path):
    git(tmp_path, "init", "-q")
    p = tmp_path / "synthetic_bound_module.py"
    p.write_text("x = 1\n")
    git(tmp_path, "add", p.name)
    git(tmp_path, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "synthetic module")
    pin = a.Bindings(tmp_path, git(tmp_path, "rev-parse", "HEAD"))
    p.write_text("raise AssertionError('executed tampered module')\n")
    sys.path.insert(0, str(tmp_path))
    try:
        with a.pinned_imports(pin):
            with pytest.raises(a.Refusal, match="binding"):
                __import__(p.stem)
    finally:
        sys.path.remove(str(tmp_path))


def test_rung_tamper_reverification():
    # Actual frozen contract, entirely synthetic capability and record.
    from experiments.exp5 import battery_5 as b5
    cap = {"answer_type": "number", "items_sha256": "fixture",
           "eval_items": [{"answer": "1"}] * 500}
    host = {"stack": {"fixture": "1"}, "device": "cuda", "sha256": "host"}
    record = dict(rung="add4_mid", size="fixture", step=1000, n=500, commit="commit",
                  dtype="float16", n_shots=2, batch_size=16, prereg_tag="exp5-preregistered",
                  answer_type="number", items_sha256="fixture", max_new_tokens=8,
                  bits=[1] * 500, continuations=["1"] * 500, correct=500,
                  stack=host["stack"], device="cuda", host_sha256="host")
    kwargs = dict(size="fixture", step=1000, rung="add4_mid", cap=cap,
                  entry={"commit": "commit"}, verify_fn=lambda c, answer, _: c == answer, host=host)
    assert b5.rung_record_failures_5(record, **kwargs) == []
    record["continuations"][3] = "0"
    with pytest.raises(a.Refusal, match="re-verification"):
        a.require_clean(b5.rung_record_failures_5(record, **kwargs))
    record["bits"][0] = .5
    with pytest.raises(a.Refusal, match="binary"):
        a.require_binary_record(record, 500)


def test_measured_nonfinite_refusal():
    from experiments.exp5 import battery_5 as b5
    rec = {"loss": float("nan"), "finite": True, "per_set": {}}
    assert not b5.loss_is_finite_5(rec)
    with pytest.raises(a.Refusal, match="finite"):
        a.require_clean(b5.loss_record_failures_5(
            rec, size="fixture", step=1000, host={}, slice_sha="synthetic"))


@pytest.fixture
def synthetic_unit(tmp_path):
    from experiments.exp5 import battery_5 as b5
    from experiments.exp2d import battery_2d as bt
    size, step = "410m", 1000
    host = {"stack": b5.STACK_PIN_5, "device": "cuda", "sha256": "host", "gpu": "synthetic"}
    common = dict(size=size, step=step, stack=host["stack"], device="cuda",
                  host_sha256="host", git_sha="a" * 40)
    entry = dict(revision="step1000", commit="b" * 40, kind="safetensors",
                 files=["model.safetensors", "model.safetensors.index.json"],
                 lfs_sha256={"model.safetensors": "c" * 64})
    payload_hashes = {**entry["lfs_sha256"], "model.safetensors.index.json": "f" * 64}
    config = f"{b5.REPO_OF_5[size]}@{b5.MAIN_SHA_5[size]}"
    ck = dict(common, revision=entry["revision"], commit=entry["commit"], kind=entry["kind"],
              files=entry["files"], sha256=payload_hashes, config_source=config, tokenizer_source=config,
              loading_info=dict(missing_keys=0, unexpected_keys=0, mismatched_keys=0),
              digest="d" * 64, n_params=100, dtype="float16", dtype_measured="float16", why="spine")
    loss = dict(common, loss=1., finite=True, n_nonfinite=0, n_scored=b5.SLICE_N_SCORED_5,
                n_docs=1, per_doc_loss=[1.], per_set={"synthetic": dict(loss=1., n_tokens=b5.SLICE_N_SCORED_5)},
                slice_sha256=b5.SLICE_SHA256_5, batch_size=8, pad_id=0,
                logits_dtype="float16", log_softmax_dtype="float32")
    battery = {r: dict(answer_type=bt.ANSWER_TYPE_PIN[r], items_sha256="items",
                       eval_items=[{"answer": "synthetic"}] * 500) for r in bt.RUNGS}
    records = {"_checkpoint.json": ck, "_loss.json": loss}
    for r in bt.RUNGS:
        records[r + ".json"] = dict(common, rung=r, revision=entry["revision"], commit=entry["commit"],
            kind=entry["kind"], files=entry["files"], weight_sha256=payload_hashes,
            config_source=config, tokenizer_source=config, gpu="synthetic", n=500,
            dtype="float16", n_shots=2, batch_size=16, prereg_tag=b5.PREREG_TAG_5,
            answer_type=battery[r]["answer_type"], items_sha256="items", max_new_tokens=bt.max_new_tokens(r),
            correct=500, bits=[1] * 500, continuations=["synthetic"] * 500,
            verify="2c normalize + exact match under 3c's total wrapper")
    records["_unit.json"] = dict(common, why="spine", digest=ck["digest"], loss=1., finite=True,
                                 n_nonfinite=0, prereg_tag=b5.PREREG_TAG_5, files={})
    def write():
        for name in b5.unit_files_5():
            raw = json.dumps(records[name]).encode()
            (tmp_path / name).write_bytes(raw)
            records["_unit.json"]["files"][name] = a.sha256(raw)
        (tmp_path / "_unit.json").write_text(json.dumps(records["_unit.json"]))
    write()
    kwargs = dict(size=size, step=step, entry=entry, battery=battery, host=host,
                  verify=lambda cont, answer, _: cont == answer)
    return records, tmp_path, kwargs, write


def test_whole_synthetic_unit_and_payload_hash(synthetic_unit):
    records, directory, kwargs, _ = synthetic_unit
    result = a.validate_unit(records, directory, **kwargs)
    assert np.array(result).shape == (34, 500)
    p = directory / "add4_mid.json"
    p.write_text(p.read_text() + "\n")
    with pytest.raises(a.Refusal, match="sha"):
        a.validate_unit(records, directory, **kwargs)


@pytest.mark.parametrize("filename,key,value,reason", [
    ("_unit.json", "host_sha256", "other", "host"),
    ("_unit.json", "digest", "e" * 64, "digest"),
    ("_loss.json", "loss", float("nan"), "finite"),
    ("_loss.json", "per_doc_loss", [float("inf")], "nonfinite"),
    ("_loss.json", "git_sha", "e" * 40, "git SHA"),
    ("_checkpoint.json", "n_params", True, "parameter"),
    ("_checkpoint.json", "dtype_measured", "float32", "dtype"),
    ("add4_mid.json", "weight_sha256", {}, "weight"),
    ("add4_mid.json", "revision", "main", "revision"),
    ("add4_mid.json", "continuations", ["wrong"] * 500, "re-verification"),
])
def test_consistent_hashes_do_not_hide_bad_records(synthetic_unit, filename, key, value, reason):
    records, directory, kwargs, write = synthetic_unit
    records[filename][key] = value
    write()  # update unit hashes: deeper measured/provenance checks still must refuse
    with pytest.raises(a.Refusal, match=reason):
        a.validate_unit(records, directory, **kwargs)


def test_saved_checker_and_tampering(tmp_path, data, draws):
    summary, tables = a.summarize(data, draws)
    summary["provenance"] = {"source_commit": "a" * 40, "launch_commit": "b" * 40}
    dest = tmp_path / "saved"
    a.reserve_output(dest)
    a.write_outputs(dest, summary, tables, {"fixture": True})
    expected = dict(sizes=list(data.sizes), steps=list(data.steps), n_rungs=4,
                    n_families=3, n_items_per_rung=4)
    assert v.verify_saved(dest, expected=expected)["state"] == "verified"
    # Bypass the output checksum deliberately: the arithmetic checker must catch it.
    text = (dest / "transitions.csv").read_text()
    lines = text.splitlines()
    header = lines[0].split(",")
    row = lines[1].split(",")
    row[header.index("n01")] = str(int(row[header.index("n01")]) + 1)
    lines[1] = ",".join(row)
    (dest / "transitions.csv").write_text("\n".join(lines) + "\n")
    manifest = json.loads((dest / "provenance.json").read_text())
    manifest["outputs_sha256"]["transitions.csv"] = a.sha256((dest / "transitions.csv").read_bytes())
    (dest / "provenance.json").write_text(json.dumps(manifest))
    with pytest.raises(v.InvalidOutput):
        v.verify_saved(dest, expected=expected)


def test_report_number_tampering(tmp_path, data, draws):
    summary, tables = a.summarize(data, draws)
    summary["provenance"] = {"source_commit": "a" * 40, "launch_commit": "b" * 40}
    a.reserve_output(tmp_path / "saved")
    a.write_outputs(tmp_path / "saved", summary, tables, {})
    p = tmp_path / "saved" / "REPORT.md"
    p.write_text(p.read_text().replace("| 1000 |", "| 999 |", 1))
    manifest_path = p.with_name("provenance.json")
    manifest = json.loads(manifest_path.read_text())
    manifest["outputs_sha256"][p.name] = a.sha256(p.read_bytes())
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(v.InvalidOutput):
        v.verify_saved(p.parent, expected=dict(sizes=list(data.sizes), steps=list(data.steps),
                       n_rungs=4, n_families=3, n_items_per_rung=4))
