# experiments/exp5b/tests/test_freeze_5b.py
"""The adversarial freeze's executable record (Task 7 step 1): one test per
finding and per named surface (i)-(x) that needs a synthetic world. Every
world is `full_shape_5b.write_world_5b` in a `tmp_path`; nothing here
touches the real tree. See `experiments/exp5b/FREEZE_CHECKLIST.md`."""
from __future__ import annotations

import json
import math
import shutil

import pytest

from experiments.exp5 import battery_5 as b5
from experiments.exp5 import stats_5 as ss
from experiments.exp5.tests import fakes_5 as fk
from experiments.exp5.tests import full_shape_5 as fs
from experiments.exp5b import analyze_5b as an
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b import power_5b as pw5b
from experiments.exp5b.run import units_5b as un
from experiments.exp5b.tests import full_shape_5b as fs5b

pytestmark = pytest.mark.slow

FINAL = b5.FINAL_STEP_5
M0, M1, M2 = fs5b.WINDOW_W


def _move(src, dest):
    shutil.move(str(src), str(dest))


def _refused(v, needle):
    assert v["verdict"] == "INSUFFICIENT_DATA", (v["verdict"], v["tree"], v["sides"])
    assert v["primary"] is None and v["cells"] == [] and v["secondaries"] == {}
    assert any(needle in f for f in v["failures"]), v["failures"][:6]


def test_f1_an_incomplete_campaign_never_delivers_a_verdict(tmp_path, monkeypatch):
    """F-1 (the class defect): a unit the campaign never wrote was read as an
    ABSENT member, a side it never reached as EXCLUDED, and a campaign killed
    after the host record as UNDETERMINED — each a verdict with every gate
    passing. After the closure every one is INSUFFICIENT_DATA at
    '5b window completeness'."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    r5b = w["root5b"]
    v0 = fs5b.run_5b(w)
    assert (v0["verdict"], v0["tree"]["cell"]) == ("SURVIVES", "CALIBRATED"), v0["failures"][:3]

    # (a) one member never written (the runner killed while loading 29000)
    d = b5b.unit_dir_5b(r5b, "1b", M2)
    _move(d, tmp_path / "held_a")
    _refused(fs5b.run_5b(w), "5b window completeness")
    _move(tmp_path / "held_a", d)

    # (b) a side never started (the campaign stopped at an earlier size)
    d = b5b.units_root_5b(r5b) / "2.8b"
    _move(d, tmp_path / "held_b")
    _refused(fs5b.run_5b(w), "5b window completeness")
    _move(tmp_path / "held_b", d)

    # (c) the campaign killed after the host record, before any unit directory
    d = b5b.units_root_5b(r5b)
    _move(d, tmp_path / "held_c")
    _refused(fs5b.run_5b(w), "5b window completeness")
    _move(tmp_path / "held_c", d)

    # (d) a directory under units/ that is not a small side (nothing else loaded)
    stray = b5b.units_root_5b(r5b) / "12b"
    stray.mkdir()
    _refused(fs5b.run_5b(w), "5b window completeness")
    stray.rmdir()

    v1 = fs5b.run_5b(w)
    assert (v1["verdict"], v1["tree"]["cell"]) == ("SURVIVES", "CALIBRATED")


def test_c1_gate1_coverage_is_measured(tmp_path, monkeypatch):
    """C-1: the runner's gate-1 attestation must cover exactly the re-read
    units re-derived — an attestation written before the last side (keys 10
    of 12, pass true) refuses; a side missing its re-read step refuses in
    the re-derivation itself."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    r5b = w["root5b"]
    g1 = b5b.gate1_path_5b(r5b)
    raw = g1.read_bytes()
    rec = json.loads(raw)
    assert len(rec["per_unit"]) == 2 * len(b5.SMALL_SIDES_5) and rec["pass"] is True
    for key in [k for k in rec["per_unit"] if k.startswith("1b/")]:
        del rec["per_unit"][key]
    g1.write_text(json.dumps(rec))
    _refused(fs5b.run_5b(w), "gate 1")
    g1.write_bytes(raw)

    # the re-derivation itself, on a side dict whose re-read member is missing
    side = {"steps": [FINAL, M1, M2], "rereads": {}}
    rec2, failures = an.gate1_rederive_5b(r5b, w["root5"], {"1b": side})
    assert any("1b/step31000" in f and "not on disk" in f for f in failures), failures
    assert rec2["pass"] is False


def test_c2_a_nonfinite_reread_member_refuses_at_gate1_and_b4_is_unreachable(tmp_path, monkeypatch):
    """C-2 and surface (x): the re-read member's non-finite loss is an
    identity failure (gate 1), not an ABSENT member; so a side whose three
    members are all non-finite refuses too — B-4's measured exclusion is
    unreachable from the runner (§F slip)."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch, nonfinite_at=[("1b", M0)])
    v = fs5b.run_5b(w)
    _refused(v, "gate 1 1b/step31000")
    w = fs5b.write_world_5b(tmp_path / "x", "SURVIVES", monkeypatch=monkeypatch,
                            nonfinite_at=[("1.4b", s) for s in fs5b.WINDOW_W])
    v = fs5b.run_5b(w)
    _refused(v, "gate 1 1.4b/step31000")
    # a non-final, non-re-read member alone non-finite is ABSENT (the design's rule)
    w = fs5b.write_world_5b(tmp_path / "y", "SURVIVES", monkeypatch=monkeypatch,
                            nonfinite_at=[("1.4b", M1), ("1.4b", M2)])
    v = fs5b.run_5b(w)
    assert v["failures"] == [] and v["sides"]["excluded"] == []
    assert v["sides"]["members_absent"] == {"1.4b": {str(M1): "non-finite loss", str(M2): "non-finite loss"}}


def test_a_nonfinite_final_halts_the_size_and_refuses(tmp_path, monkeypatch):
    """Design §3.2/§3.6 say a non-finite final EXCLUDES the side; Experiment
    5's writer halts on a non-finite 'final' (HALT_ON_NONFINITE_WHY_5), so
    the 5b runner halts the size and the analyzer refuses (§F slip)."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    r5b = w["root5b"]
    shutil.rmtree(b5b.units_root_5b(r5b) / "1b")
    exp5_cf = fs.count_fn_for(fs5b.MODES_5B["SURVIVES"][0])
    loaders, _ = fk.make_loaders(w["battery"], loss_fn=fs.loss_w,
                                 count_fn=fs5b.member_count_fn_5b(exp5_cf, 6),
                                 nonfinite_at=[("1b", FINAL)])
    with pytest.raises(SystemExit):
        un.run(size="1b", root=r5b, exp5_root=w["root5"], cache_root=r5b, device="cuda", loaders=loaders,
               manifest=w["manifest"], sl=w["sl"], host_meta=fk.fake_host(), git_sha="g2", verdict_sha=False,
               projection_commit="p2", is_ancestor=lambda a, b: True, power_present=True, **fs5b._inj())
    assert b5b.halt_marker_path_5b(r5b, "1b").is_file()
    _refused(fs5b.run_5b(w), "halt")


@pytest.mark.parametrize("kw,needle", [({"reread_delta": {"antonym": 16}}, "antonym"),
                                       ({"loss_delta_final": 2e-4}, "|Δℓ|")])
def test_v_the_reread_comparison_at_the_boundary(tmp_path, monkeypatch, kw, needle):
    """(v): digest equal, one rung's count off by 16 (the per-rung tolerance
    is 15) — the runner records it, the analyzer refuses; counts equal, the
    loss off by 2e-4 (tolerance 1e-4) — refuses."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch, **kw)
    rr = json.loads(b5b.unit5b_record_path_5b(w["root5b"], "1b", FINAL).read_text())["reread_record"]
    assert rr["digest_equal"] is True
    if "reread_delta" in kw:
        assert rr["tolerance_failures"] and rr["count_abs_diff_max"] == 16
    else:
        assert rr["loss_within_tol"] is False and rr["count_abs_diff_sum"] == 0
    _refused(fs5b.run_5b(w), needle)


def test_vi_an_attestation_contradicting_the_rederivation_refuses(tmp_path, monkeypatch):
    """(vi): the runner's `_unit_5b.json` says digest_equal true (and
    gate1_5b.json pass true) where the re-derivation finds the digest
    differs — the attestation mismatch is named."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch, halt_on_digest=False,
                            digest_fn_b=lambda s, st: __import__("hashlib").sha256(
                                (f"other-{s}-{st}" if s == "1b" else f"d-{s}-{st}").encode()).hexdigest())
    r5b = w["root5b"]
    for step in b5b.reread_steps_5b():
        p = b5b.unit5b_record_path_5b(r5b, "1b", step)
        rec = json.loads(p.read_text())
        rec["reread_record"]["digest_equal"] = True
        p.write_text(json.dumps(rec))
    g1 = json.loads(b5b.gate1_path_5b(r5b).read_text())
    g1["pass"] = True
    for k in g1["per_unit"]:
        g1["per_unit"][k]["digest_equal"] = True
    b5b.gate1_path_5b(r5b).write_text(json.dumps(g1))
    v = fs5b.run_5b(w)
    _refused(v, "attested digest_equal True != re-derived False")


def test_vii_the_power_record_at_another_n_sim_or_from_62_cells_refuses(tmp_path, monkeypatch):
    """(vii): a record genuinely recomputed at n_sim != N_SIM_5B, and one
    whose structure (and structure_sha256) came from 62 of the cells —
    both refuse at '5b power record'. (In the worlds N_SIM_5B is 30, so
    the analogue of the brief's 999 is 29.)"""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    p = b5b.power_path_5b(w["root5b"])
    raw = p.read_bytes()
    cells5 = [c for c in w["v5"]["cells"] if c["live"] and c["defined_P"]]
    floors = b5.load_floors_5()
    rec_sha = json.loads(raw)["exp5_verdict_sha256"]
    for rec in (pw5b.compute_5b(cells5, floors, n_sim=pw5b.N_SIM_5B - 1, seed=pw5b.SEED_5B),
                pw5b.compute_5b(cells5[:-1], floors, n_sim=pw5b.N_SIM_5B, seed=pw5b.SEED_5B)):
        rec["exp5_verdict_sha256"] = rec_sha
        p.write_text(json.dumps(rec, indent=1, sort_keys=True))
        _refused(fs5b.run_5b(w), "5b power record")
    p.write_bytes(raw)
    assert fs5b.run_5b(w)["failures"] == []


def test_f3_a_non_monotone_sigma_hat_axis_refuses(tmp_path, monkeypatch):
    """F-3: `numpy.interp` needs an increasing axis and returns a number for
    any axis; a non-increasing `sigma_hat_axis` must refuse, not read."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    p = b5b.power_path_5b(w["root5b"])
    rec = json.loads(p.read_text())
    ax = list(rec["sigma_hat_axis"])
    ax[2], ax[3] = ax[3], ax[2]
    p.write_text(json.dumps(dict(rec, sigma_hat_axis=ax), indent=1, sort_keys=True))
    _refused(fs5b.run_5b(w, power_gate="skip"), "sigma_hat_axis is not strictly increasing")


def test_iv_off_grid_is_not_claimed(tmp_path, monkeypatch):
    """(iv): a doctored power record whose simulated axis tops below the
    observed sigma-hat → OFF-GRID, claimed false, 'NOT claimed' in the
    sentence, never CALIBRATED."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch)
    p = b5b.power_path_5b(w["root5b"])
    rec = json.loads(p.read_text())
    v0 = fs5b.run_5b(w)
    sh = v0["sigma_hat"]["pooled"]
    assert sh > 0
    top = sh * 0.99
    p.write_text(json.dumps(dict(rec, sigma_hat_axis=[top * k / 6 for k in range(1, 7)],
                                 alpha_5b_axis=[0.001] * 6), indent=1, sort_keys=True))
    v = fs5b.run_5b(w, power_gate="skip")
    assert (v["verdict"], v["tree"]["cell"]) == ("SURVIVES", "OFF-GRID")
    assert v["licence"]["claimed"] is False and "NOT claimed" in v["licence"]["sentence"]
    assert v["calibration"]["in_grid"] is False


def test_ix_a_noiseless_small_side_gives_R_minus_P_over_root2(tmp_path, monkeypatch):
    """(ix): every member equal to the final (wobble 0; the re-read member
    mirrors the final in the world) → T_sym == mean((R - P/√2)/500) over
    the world's Experiment 5 cells, and the rung-block p equals the flip
    on the hand-built per-rung sums."""
    w = fs5b.write_world_5b(tmp_path, "SURVIVES", monkeypatch=monkeypatch, wobble=0)
    v = fs5b.run_5b(w)
    assert v["failures"] == [], v["failures"][:3]
    for c in v["cells"]:
        assert all(n == c["f_B"] for n in c["members"].values()) and c["f_B"] == c["f"]
    live = [c for c in w["v5"]["cells"] if c["live"] and c["defined_P"]]
    hand = [(float(c["R"]) - float(c["P"]) / math.sqrt(2.0)) / b5.N_ITEMS for c in live]
    T_hand = sum(hand) / len(hand)
    assert v["primary"]["n_cells"] == len(live)
    assert abs(v["primary"]["T"] - T_hand) < 1e-12, (v["primary"]["T"], T_hand)
    sums = {}
    for c, x in zip(live, hand):
        sums[c["rung"]] = sums.get(c["rung"], 0.0) + x
    p_hand = ss.sign_flip_p_5(list(sums.values()), len(hand), n_sample=200, seed=b5.PERM_SEED_5)["p"]
    assert v["primary"]["rung_block"]["p"] == p_hand
