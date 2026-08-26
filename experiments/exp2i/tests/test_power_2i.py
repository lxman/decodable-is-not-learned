# experiments/exp2i/tests/test_power_2i.py
"""power_2i: the simulated cells respect n_pos and use the REAL
committed x_A/2g strata; calibration is monotone; power_at runs
through analyze_2i's own firing rule (fires_2i — one implementation,
shared with the analyzer); main() writes once, refuses without
rung_set_2i.json/predictor_2i.json, and declares per test at tiny N."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2g import strata_2g as sg
from experiments.exp2h import battery_2h as bh
from experiments.exp2i import analyze_2i as an
from experiments.exp2i import battery_2i as bi
from experiments.exp2i import power_2i as pw
from experiments.exp2i.run import endpoint_2i as ep

R_SMALL = ("antonym", "antonym6")   # two of the eleven strata rungs


def _setup():
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    x_real = bi.sampler_counts_pythia("1b", R_SMALL)
    n_pos = {r: 60 for r in R_SMALL}
    return strata, x_real, n_pos


def test_simulated_cells_respect_n_pos_and_use_real_x():
    strata, x_real, n_pos = _setup()
    rng = np.random.default_rng(0)
    n_steps = bi.n_trained_7b()
    cells = pw.simulate_cells_2i(rng, 0.5, strata, x_real, n_pos, R_SMALL, n_steps=n_steps)
    by = {c["rung"]: c for c in cells}
    assert n_steps == 21
    for r in R_SMALL:
        assert int((np.asarray(by[r]["y"]) > 0).sum()) == n_pos[r]
        assert by[r]["strata"] == strata[r]["strata"]
        assert list(by[r]["x"]) == list(x_real[r])
        assert max(by[r]["y"]) <= 21


def test_calibration_is_monotone():
    strata, x_real, n_pos = _setup()
    n_steps = bi.n_trained_7b()
    lo = pw.calibrate_rho(0.10, strata, x_real, n_pos, R_SMALL, n_steps=n_steps, seed=0, n_cal=5)
    hi = pw.calibrate_rho(0.20, strata, x_real, n_pos, R_SMALL, n_steps=n_steps, seed=0, n_cal=5)
    assert 0 <= lo < hi < 1


def test_power_at_runs_through_fires_2i():
    strata, x_real, n_pos = _setup()
    n_steps = bi.n_trained_7b()
    # n_perm must clear the permutation p-value floor 1/(n_perm+1) < ALPHA
    # (.01) for a fire to be reachable at all; 200 floors at ~.005.
    r = pw.power_at(0.9, strata, x_real, n_pos, R_SMALL, n_steps=n_steps, n_sim=5,
                    n_perm=200, seed=0)
    assert set(r) >= {"p_fires", "p_detect", "mean_T", "n_sim", "rho"}
    assert r["p_fires"] > 0.5


def test_one_calls_the_shared_fires_2i(monkeypatch):
    """Ruling 9: one firing-rule implementation. A spy on `an.fires_2i`
    (the name `pw._one` calls through, `power_2i.an` being the same
    `analyze_2i` module object) proves `_one` delegates rather than
    re-deriving its own close-but-not-identical boundary check —
    numerically-close boundary mutants of the local re-derivation are
    otherwise nearly unreachable at random-simulation N."""
    calls = []

    def spy(prim):
        calls.append(prim)
        return True

    monkeypatch.setattr(pw.an, "fires_2i", spy)
    strata, x_real, n_pos = _setup()
    n_steps = bi.n_trained_7b()
    rng = np.random.default_rng(0)
    fires, strat = pw._one(rng, 0.5, strata, x_real, n_pos, R_SMALL, n_perm=50,
                           n_steps=n_steps)
    assert calls == [{"stratified": strat}]
    assert fires is True


def test_declared_status_boundary_is_inclusive(monkeypatch):
    """`declared_status` must read POWERED at `declare_p == BAR` exactly
    (`>=`, not `>`) — a boundary random simulation essentially never
    lands on, so it is pinned directly via a fixed `power_at`/
    `calibrate_rho` stand-in rather than hoped for from N simulated
    draws."""
    strata, x_real, n_pos = _setup()
    n_steps = bi.n_trained_7b()
    monkeypatch.setattr(pw, "D_TARGETS", (pw.DECLARE_AT,))
    monkeypatch.setattr(pw, "calibrate_rho", lambda *a, **k: 0.5)
    monkeypatch.setattr(pw, "power_at", lambda *a, **k: {
        "p_fires": pw.BAR, "p_detect": 0.0, "mean_T": 0.0, "sd_T": 0.0,
        "n_sim": 1, "n_perm": 1, "rho": 0.5, "Ts": [0.0]})
    rec = pw._one_test_power(strata, x_real, n_pos, R_SMALL, n_steps=n_steps)
    assert rec["declared_status"] == "POWERED"


def test_rank_to_count_direction():
    c = pw._ranks_to_counts([10, 20, 30, 40], 21)
    assert c[10] == 21
    assert c[40] >= 1
    assert c[10] >= c[20] >= c[30] >= c[40]


def test_rankz_handles_zero_variance():
    z = pw._rankz(np.zeros(5))
    assert np.allclose(z, 0.0)


# --------------------------------------------------------------- main()

def _write_rung_set(root, rungs):
    p = bi.rung_set_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"R_OLMO": list(rungs), "R_CAP": list(rungs), "R_EXTRA": [],
                             "per_rung": {}, "endpoint_file_sha256": {}}))


def _write_predictor_seal(root, sha="PSEAL0"):
    p = bi.predictor_seal_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"files": {}, "counts": {}, "sha256": sha,
                             "tag": bi.PREDICTOR_SEAL_TAG, "sampling": {}}))
    return sha


def _write_x_b_draws(root, rungs, battery, hit_fraction):
    """Real battery items, exp3-format draws — the same shape
    `sample_2i.py` writes — so `bi.sampler_counts_olmo` reproduces x_B."""
    from experiments.exp2i.run.sample_2i import write_draws
    for rung in rungs:
        cap = battery[rung]
        n_hit = int(round(hit_fraction * len(cap["eval_items"])))
        rows = []
        for i, it in enumerate(cap["eval_items"]):
            text = str(it["answer"]) if i < n_hit else "zzz"
            rows.append({"item": i, "draws": {"0": [text] * bi.DRAWS_PER_ITEM}})
        write_draws(bi.predictor_draws_path(root, rung), rows)
        rec_path = bi.predictor_record_path(root, rung)
        rec_path.write_text(json.dumps({"rung": rung}))


def _write_stage1_final(root, rungs, battery, verify_fn, entry, predictor_sha,
                        hit_fraction):
    for rung in rungs:
        cap = battery[rung]
        n = bt.N_ITEMS
        n_hit = int(round(hit_fraction * n))
        conts = [f" {it['answer']}" if i < n_hit else " zzz"
                for i, it in enumerate(cap["eval_items"])]
        bits = [int(verify_fn(c, it["answer"], cap["answer_type"]))
               for c, it in zip(conts, cap["eval_items"])]
        ckpt = {"revision": entry["revision"], "commit": entry["commit"], "kind": entry["kind"],
               "files": list(entry.get("files", [])), "weight_sha256": "D",
               "config_source": "cs", "tokenizer_source": "ts"}
        ev = {"bits": bits, "correct": sum(bits), "continuations": conts}
        rec = ep.item_record_2i(rung=rung, family=bi.FAMILY, size=bi.SIZE_OUT,
                                which="stage1_final", cap=cap, ev=ev, ckpt=ckpt,
                                seal={"tag": bi.PREDICTOR_SEAL_TAG, "sha256": predictor_sha},
                                t_s=0.0)
        p = bi.endpoint_record_path(root, "stage1_final", rung)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec, indent=1))


def test_main_refuses_without_rung_set(tmp_path):
    with pytest.raises(FileNotFoundError):
        pw.main(root=tmp_path)


def test_main_refuses_without_predictor_seal(tmp_path):
    _write_rung_set(tmp_path, R_SMALL)
    with pytest.raises(FileNotFoundError):
        pw.main(root=tmp_path)


def test_main_writes_once_and_declares_at_tiny_n(tmp_path, monkeypatch):
    monkeypatch.setattr(pw, "N_SIM", 3)
    monkeypatch.setattr(pw, "N_PERM_POWER", 20)
    monkeypatch.setattr(pw, "D_TARGETS", (0.15,))

    # `an.load_endpoint_which` (reused by power_2i.main) reads all 34
    # rungs' stage1_final records, matching the real production
    # precondition (the endpoint stage always writes all 34 before
    # R_CAP is even known) — only R_SMALL needs a realistic hit
    # fraction, the rest can be trivial all-miss records.
    battery = bg.load_battery(bt.RUNGS)
    verify_fn = a2d.load_verify()
    manifest = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    entry = bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B)

    _write_rung_set(tmp_path, R_SMALL)
    psha = _write_predictor_seal(tmp_path)
    _write_x_b_draws(tmp_path, R_SMALL, battery, hit_fraction=0.3)
    other_rungs = tuple(r for r in bt.RUNGS if r not in R_SMALL)
    _write_stage1_final(tmp_path, R_SMALL, battery, verify_fn, entry, psha,
                        hit_fraction=0.4)
    _write_stage1_final(tmp_path, other_rungs, battery, verify_fn, entry, psha,
                        hit_fraction=0.0)

    rec = pw.main(root=tmp_path)
    for test in ("A", "B"):
        assert rec[test]["declared_status"] in ("POWERED",
                                                 "DECLARED UNDERPOWERED IN ADVANCE")
        assert rec[test]["thin"] is True   # R_SMALL has 2 rungs, < 3 (design §4)
        assert rec[test]["n_sim"] == 3
        assert "declaration" in rec[test]
    assert bi.power_path(tmp_path).is_file()

    with pytest.raises(RuntimeError, match="written ONCE"):
        pw.main(root=tmp_path)
