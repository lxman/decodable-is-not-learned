import json, pytest
from experiments.exp4c import battery_4c as b
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg


def test_grids_are_the_literals():
    assert b.GRID_4C["pythia_6.9b"] == (1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000,
        40000, 50000, 60000, 64000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000, 143000)
    assert b.GRID_4C["olmo2_13b"] == (1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 192000,
        256000, 320000, 384000, 448000, 512000, 576000, 596057)
    assert b.ENDPOINT_STEP_4C == {"pythia_6.9b": 143000, "olmo2_13b": 596057}
    assert b.FIRST_STEP_4C == {"pythia_6.9b": 1000, "olmo2_13b": 1000} and b.INIT_STEP_4C == 0


def test_site_count_pin_reproduces():
    from experiments.exp4 import metric_4
    for n_hidden, want in b.SITE_COUNT_PIN_4C.items():
        assert len(metric_4.sites_4(n_hidden)) == want
    assert metric_4.sites_4(41) == [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 40]


def test_refs_exclude_own_family():
    assert b.REFS_FOR_4C["pythia_6.9b"] == ("ref_olmo2_7b", "ref_smollm3_3b", "ref_comma_7b")
    assert b.REFS_FOR_4C["olmo2_13b"] == ("ref_pythia_12b", "ref_smollm3_3b", "ref_comma_7b")


@pytest.mark.slow
def test_manifests_load_at_their_pins_and_reproduce_the_grids():
    m = b.manifests_4c()
    assert tuple(m["pythia_6.9b"]["trained_steps"]) == b.GRID_4C["pythia_6.9b"]
    assert tuple(m["olmo2_13b"]["grid_13b"]) == b.GRID_4C["olmo2_13b"]


@pytest.mark.slow
def test_outcomes_reproduce_the_design_pins():
    floors, battery = bg.load_floors(), bt.load_battery()
    for traj in b.TRAJECTORIES_4C:
        oc = b.load_outcome_4c(traj, battery=battery)
        assert oc["steps"] == list(b.GRID_4C[traj])
        rs = b.rung_sets_4c(oc, floors)
        assert b.check_rung_set_pins_4c(traj, rs, oc["steps"]) == []
    assert b.CLEAR_INDEX_PIN_4C["pythia_6.9b"]["arith_next"] == 5
    assert b.CLEAR_INDEX_PIN_4C["olmo2_13b"]["count_div13"] == 15
    assert len(b.RUNG_SET_PIN_4C["pythia_6.9b"]["flat"]) == 24 and len(b.RUNG_SET_PIN_4C["olmo2_13b"]["flat"]) == 15
    assert set(b.RUNG_SET_PIN_4C["olmo2_13b"]["flat"]) <= set(b.RUNG_SET_PIN_4C["pythia_6.9b"]["flat"])


@pytest.mark.slow
def test_step0_digests_are_readable_and_distinct_from_endpoints():
    for traj in b.TRAJECTORIES_4C:
        d0 = b.committed_step_digest_4c(traj, 0); de = b.committed_step_digest_4c(traj, b.ENDPOINT_STEP_4C[traj])
        assert len(d0) == 64 and len(de) == 64 and d0 != de


def _write_valid_outcome_step(root, traj, step, battery, *, render_override=None,
                              dtype_override=None):
    """A minimal, fully valid `load_outcome_4c` step directory — one
    `_checkpoint.json` plus all 34 rung records, real `bt.load_battery()`
    item hashes/shot counts (no model contact), so the ONLY thing off
    from a real committed step is whatever `_override` sets."""
    d = root / f"step{int(step)}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "_checkpoint.json").write_text(json.dumps({"digest": "d" * 64}))
    fam = b.FAMILY_OF_TRAJ_4C[traj]
    render = render_override if render_override is not None else b.RENDER_4C[fam]
    dtype = dtype_override if dtype_override is not None else b.DTYPE_4C
    for rung in b.RUNGS:
        rec = {"rung": rung, "step": int(step), "n": b.N_ITEMS, "bits": [0] * b.N_ITEMS,
               "items_sha256": battery[rung]["items_sha256"], "render": render, "dtype": dtype,
               "n_shots": len(battery[rung]["shots"]), "correct": 0}
        (d / f"{rung}.json").write_text(json.dumps(rec))


def _shrunk_outcome_env(monkeypatch, tmp_path, traj, step=1000):
    root = tmp_path / "sweep"
    monkeypatch.setattr(b, "GRID_4C", {traj: (step,)})
    monkeypatch.setattr(b, "SWEEP_ROOT_4C", {traj: root})
    return root


def test_load_outcome_4c_accepts_a_well_formed_synthetic_step(tmp_path, monkeypatch):
    battery = bt.load_battery()
    traj = "pythia_6.9b"
    root = _shrunk_outcome_env(monkeypatch, tmp_path, traj)
    _write_valid_outcome_step(root, traj, 1000, battery)
    oc = b.load_outcome_4c(traj, battery=battery)
    assert oc["steps"] == [1000]
    assert set(oc["per_step"][1000]["rungs"]) == set(b.RUNGS)


def test_load_outcome_4c_refuses_the_wrong_render(tmp_path, monkeypatch):
    battery = bt.load_battery()
    traj = "pythia_6.9b"
    root = _shrunk_outcome_env(monkeypatch, tmp_path, traj)
    _write_valid_outcome_step(root, traj, 1000, battery, render_override="chat")
    with pytest.raises(ValueError, match="render"):
        b.load_outcome_4c(traj, battery=battery)


def test_load_outcome_4c_refuses_the_wrong_dtype(tmp_path, monkeypatch):
    battery = bt.load_battery()
    traj = "pythia_6.9b"
    root = _shrunk_outcome_env(monkeypatch, tmp_path, traj)
    _write_valid_outcome_step(root, traj, 1000, battery, dtype_override="float32")
    with pytest.raises(ValueError, match="dtype"):
        b.load_outcome_4c(traj, battery=battery)


def test_expected_fields_for_step0_and_thin_endpoint(monkeypatch):
    monkeypatch.setattr(b, "committed_step_digest_4c", lambda traj, step: f"d:{traj}:{step}")
    e = b.expected_fields_4c(("olmo2_13b", 0))
    assert e == dict(family="olmo2", render="plain", batch=16, refs=b.REFS_FOR_4C["olmo2_13b"],
                     n_hidden=41, committed_digest="d:olmo2_13b:0")
    t = b.expected_fields_4c(b.THIN_ENDPOINT_KEY_4C)
    assert t["committed_digest"] == "d:olmo2_13b:596057" and t["n_hidden"] == 41 and t["batch"] == 16
    with pytest.raises(ValueError):
        b.expected_fields_4c("ladder_pythia_6.9b")


def test_record_failures_requires_the_4c_tag_and_measured_digest(tmp_path, monkeypatch):
    monkeypatch.setattr(b, "committed_step_digest_4c", lambda traj, step: "dd")
    rec = {"family": "pythia", "render": "plain", "batch_size": 16, "committed_digest": "dd",
           "tensor_digest": "dd", "refs": list(b.REFS_FOR_4C["pythia_6.9b"]), "prereg_tag": b.PREREG_TAG_4C,
           "commit": "c", "revision": "r", "repo": "p", "kind": "candidate", "config_source": "s",
           "n_hidden": 33, "loading_info": {}, "sets_sha256": {}, "attested_sha256": {"x": "y"},
           "activation_sha256": {"x": None}}
    assert b.load_record_failures_4c(rec, key=("pythia_6.9b", 1000), root=tmp_path) == []
    bad = dict(rec, prereg_tag="exp4-preregistered"); assert any("prereg_tag" in m for m in b.load_record_failures_4c(bad, key=("pythia_6.9b", 1000), root=tmp_path))
    bad = dict(rec, tensor_digest="other"); assert any("tensor_digest" in m for m in b.load_record_failures_4c(bad, key=("pythia_6.9b", 1000), root=tmp_path))


def test_gate1_failures_reads_every_field():
    g1 = {"traj": "olmo2_13b", "rungs": list(bt.RUNGS), "sets_equal": {r: True for r in bt.RUNGS},
          "attested_sha_equal": {r: True for r in bt.RUNGS}, "digest_equal": True, "n_rungs": 34,
          "reference_key": "endpoint_olmo2_13b", "reference_root": "exp4c", "prereg_tag": b.PREREG_TAG_4C}
    assert b.gate1_failures_4c(g1, traj="olmo2_13b") == []
    assert b.gate1_failures_4c(dict(g1, rungs=list(bt.RUNGS)[:33]), traj="olmo2_13b")
    assert b.gate1_failures_4c(dict(g1, n_rungs=33), traj="olmo2_13b")
    assert b.gate1_failures_4c(dict(g1, reference_key="ladder_pythia_6.9b"), traj="olmo2_13b")


def test_exp4_closed_pins_hold():
    b.check_exp4_closed_4c()   # raises on drift


def test_exp4_reference_paths_count(tmp_path):
    assert len(b.exp4_reference_paths_4c(tmp_path)) == 5 * 37
