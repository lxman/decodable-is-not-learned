# experiments/exp2m/tests/full_shape.py
"""Synthetic 2m worlds. The predictors are never synthesized (REAL 2k
tier, REAL 2i x_B); only the SmolLM3 trees under `root` are: three
endpoint whichs, the 26-point sweep, the twin, gate 1, the rung set
and the power record. Modes drive the four worlds; `missing` drives
the refusals.

The latent (dial b, Tests A and B UNCONDITIONED on the base strata):
2i disclosed x_A and x_B correlated within base strata (rho .06–.32),
so a latent built from one predictor's rank alone leaks into the OTHER
test. Each single-predictor mode therefore uses the predictor's rank
RESIDUALIZED on the other predictor's rank inside every base stratum
(`_resid_given`): `pythia_only` = resid(x_A | x_B) → A fires, B ≈ 0;
`olmo_only` = resid(x_B | x_A) → B fires, A ≈ 0; `shared` = the sum of
the two residuals → both fire; `independent`/`inverted` → NEITHER."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

EXP2M = Path(__file__).resolve().parents[1]
if str(EXP2M.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2M.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2m import analyze_2m as an  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402

RUNGS_PRIMARY = tuple(sorted(bm.R_CAP_2K))
N_POS_FIRING = 200
_CACHE = {}


def _cached(name, fn):
    if name not in _CACHE:
        _CACHE[name] = fn()
    return _CACHE[name]


def battery():
    return _cached("battery", bg.load_battery)


def manifest():
    return _cached("manifest", lambda: bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256))


def verify_fn():
    return _cached("verify", a2d.load_verify)


def floors():
    return _cached("floors", bg.load_floors)


def strata():
    return _cached("strata", lambda: sg.from_json(
        pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)["strata"]))


def x_a256_real():
    return _cached("x_a256", lambda: {r: list(json.loads(bk.seal_path(bk.EXP2K).read_text())["counts"]["1b"][r])
                                      for r in RUNGS_PRIMARY})


def x_b_real():
    return _cached("x_b", lambda: bi.sampler_counts_olmo(RUNGS_PRIMARY, root=bi.EXP2I, battery=battery(),
                                                         verify_fn=verify_fn()))


def s8_cached():
    """The four committed outcomes loaded ONCE per process (≈ 2–4 min);
    `run_world` injects them so nineteen worlds do not re-read the
    2g/2h/2i/2l trees nineteen times. The production path (no
    injection) is exercised by the cold battery's item 13 and by
    `test_full_shape_2m.test_s8_production_loader_once`."""
    return _cached("s8", lambda: an.load_committed_outcomes_2m(battery(), verify_fn()))


def _w(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _resid_given(x_target, x_other, strata_r):
    """rank(x_target) residualized on rank(x_other) by least squares
    inside each base stratum (a stratum with fewer than three items, or
    a constant rank(x_other) within it, falls back to demeaning),
    standardized to unit variance over the rung."""
    n = len(x_target)
    rt, ro = rankdata(x_target, method="average"), rankdata(x_other, method="average")
    resid = np.zeros(n, dtype=np.float64)
    groups = {}
    for i, s in enumerate(strata_r):
        groups.setdefault(s, []).append(i)
    for idxs in groups.values():
        idxs = np.asarray(idxs)
        t_g, o_g = rt[idxs], ro[idxs]
        if len(idxs) < 3 or np.std(o_g) == 0:
            resid[idxs] = t_g - t_g.mean()
        else:
            design = np.vstack([o_g, np.ones(len(o_g))]).T
            beta, *_ = np.linalg.lstsq(design, t_g, rcond=None)
            resid[idxs] = t_g - design @ beta
    sd = resid.std(ddof=0)
    return resid / sd if sd > 0 else np.zeros(n)


def _latent(rng, x_a, x_b, strata_r, mode):
    n = len(x_a)
    tie = rng.normal(size=n) * 0.01
    xa, xb = np.asarray(x_a, dtype=np.float64), np.asarray(x_b, dtype=np.float64)
    resid_A = _resid_given(xa, xb, strata_r)
    resid_B = _resid_given(xb, xa, strata_r)
    if mode == "pythia_only":
        return resid_A + tie
    if mode == "olmo_only":
        return resid_B + tie
    if mode == "shared":
        return resid_A + resid_B + tie
    if mode == "independent":
        return rng.normal(size=n)
    if mode == "inverted":
        return -(resid_A + resid_B) + tie
    raise ValueError(mode)


def _ckpt(entry, digest="D"):
    return {"revision": entry["revision"], "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry.get("files", [])), "weight_sha256": digest, "config_source": "cs",
            "tokenizer_source": "ts"}


def _twin_ckpt(entry, digest="T"):
    return {"revision": bm.TWIN, "commit": None, "kind": "from_config", "files": [], "weight_sha256": digest,
            "config_source": f"{bm.REPO_CKPT}@{entry['config_commit']}",
            "tokenizer_source": f"{bm.REPO_CKPT}@{entry['config_commit']}"}


def write_world_2m(root, *, mode="pythia_only", seed=0, missing=None, power_status_a="POWERED",
                   power_status_b="POWERED", drifted_seal=None, halt=False, gate1_diff=False,
                   gate1_attested_mismatch=False, n_pos_cap=None, zero_rungs=(), all_fire=(),
                   expect_primary=None, mixed_digest_which=None) -> dict:
    # `mixed_digest_which` (freeze F-2): the LAST rung of that which is
    # written with a different tensor digest AT WRITE TIME, so the rung
    # set's own sha table and the 104-file composite are both computed
    # over the mixed tree and agree with it — the shape a resumed
    # endpoint stage leaves, not a post-hoc edit.
    root = Path(root)
    rng = np.random.default_rng(seed)
    bat, man, verify, strata0 = battery(), manifest(), verify_fn(), strata()
    x_a, x_b = x_a256_real(), x_b_real()
    steps = bm.trained_steps_3b()
    n_steps = len(steps)
    n_pos_cap, zero_rungs, all_fire = dict(n_pos_cap or {}), set(zero_rungs), set(all_fire)
    first = {}
    for r in bt.RUNGS:
        if r in RUNGS_PRIMARY and r not in zero_rungs:
            w = _latent(rng, x_a[r], x_b[r], strata0[r]["strata"], mode)
            order = np.argsort(-w)
            n_fire = max(int(n_pos_cap.get(r, N_POS_FIRING)), 1)
            first[r] = {int(i): steps[int(rank * n_steps / n_fire)] for rank, i in enumerate(order[:n_fire])}
        else:
            first[r] = {}
    entries = {w: bm.entry_which_3b(man, w) for w in bm.ENDPOINT_WHICH_2M}
    seal_ep = {"tag": bm.PREDICTOR_TAGS_2M, "sha256": bm.PREDICTOR_SHA_2M}

    def _bits_at(r, step):
        if r in all_fire:
            return [1] * bt.N_ITEMS
        return [int(i in first[r] and step >= first[r][i]) for i in range(bt.N_ITEMS)]

    # ---- the endpoint stage: stage1_final == the sweep's endpoint step; stage3_final/base all-zero
    stage1_correct, stage1_recs = {}, {}
    for r in bt.RUNGS:
        cap = bat[r]
        bits = _bits_at(r, bm.ENDPOINT_STEP_2M)
        conts = [f" {it['answer']}" if b else " zzz" for b, it in zip(bits, cap["eval_items"])]
        if gate1_diff and r == bt.RUNGS[0]:
            bits[0] = 1 - bits[0]
            conts[0] = f" {cap['eval_items'][0]['answer']}" if bits[0] else " zzz"
        ev = {"bits": bits, "correct": sum(bits), "continuations": conts}
        stage1_correct[r] = ev["correct"]
        _dg1 = "OTHER" if (mixed_digest_which == "stage1_final" and r == bt.RUNGS[-1]) else "D"
        rec = bm.endpoint_item_record_2m(rung=r, cap=cap, ev=ev,
                                         ckpt=_ckpt(entries["stage1_final"], _dg1),
                                         which="stage1_final", seal=seal_ep, t_s=0.0)
        stage1_recs[r] = rec
        _w(bm.endpoint_record_path(root, "stage1_final", r), rec)
        ev0 = {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}
        for which in ("stage3_final", "base"):
            _dg = "OTHER" if (mixed_digest_which == which and r == bt.RUNGS[-1]) else "D"
            _w(bm.endpoint_record_path(root, which, r),
               bm.endpoint_item_record_2m(rung=r, cap=cap, ev=ev0, ckpt=_ckpt(entries[which], _dg),
                                          which=which, seal=seal_ep, t_s=0.0))
    rs = bm.rung_set_from_counts_2m(stage1_correct, floors())
    want_primary = tuple(expect_primary) if expect_primary is not None else RUNGS_PRIMARY
    if tuple(rs["R_PRIMARY"]) != want_primary:
        raise AssertionError(f"world builder: R_PRIMARY {rs['R_PRIMARY']} != {list(want_primary)}")
    endpoint_shas = {}
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            p = bm.endpoint_record_path(root, which, r)
            endpoint_shas[str(p.relative_to(root))] = bg.sha256_file(p)
    _w(bm.rung_set_path(root), {**rs, "endpoint_file_sha256": endpoint_shas})
    r_primary = tuple(rs["R_PRIMARY"])
    # ---- the power record: literal statuses; re-derivable claims computed for real, B on BASE strata
    n_pos = {r: int(stage1_correct[r]) for r in r_primary}

    def _block(status, x):
        dropped = list(an2i._degenerate_rungs(x, strata0, r_primary))
        keep = [r for r in r_primary if r not in dropped]
        return {"declared_status": status, "declaration": "x", "rungs": list(r_primary),
                "n_trained_steps": bm.n_trained_3b(), "dropped_degenerate": dropped, "rungs_simulated": keep,
                "n_pos_lower_bound": n_pos, "t_bar": an.T_BAR, "alpha": an.ALPHA, "thin": len(keep) < 3}
    power = {"A": _block(power_status_a, x_a), "B": _block(power_status_b, x_b),
             "block_sd_A": {"n_sim": 1, "mean_block_sd_at_declare": 0.01, "mean_block_sd_null": 0.005,
                            "per_block_mean_T_at_declare": [0.1] * 4, "blocks": 4,
                            "rungs": [r for r in r_primary if r not in an2i._degenerate_rungs(x_a, strata0, r_primary)]},
             "r_primary": list(r_primary), "primary_is_the_nine": bool(rs["primary_is_the_nine"]),
             "predictor_sha256": bm.PREDICTOR_SHA_2M, "calibration_note": "x", "shape_note": "x", "note": "x"}
    if missing == "power_claims":
        power["A"] = dict(power["A"], declared_status="POWERED", dropped_degenerate=list(r_primary), rungs_simulated=[],
                          n_pos_lower_bound={r: 0 for r in r_primary}, t_bar=0.0, alpha=1.0, thin=True)
    if missing == "power_sha":
        power["predictor_sha256"] = "0" * 64
    _w(bm.power_path(root), power)
    esha = bm.endpoint_sha256(root)

    # ---- the sweep: 26 grid points + the twin (all-zero), checkpoint records, gate 1
    for step in steps:
        entry = bm.entry_3b(man, step)
        lfs = dict(entry.get("lfs_sha256", {}))
        _w(bm.checkpoint_record_path(root, step),
           {"family": bm.FAMILY, "size": bm.SIZE_OUT, "step": step, "repo": entry["repo"], "revision": entry["revision"],
            "commit": entry["commit"], "sha256": {n: lfs.get(n, f"non-lfs:{n}") for n in entry["files"]},
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}, "digest": "D",
            "download_seconds": 0.0})
        for r in bt.RUNGS:
            cap = bat[r]
            if step == bm.ENDPOINT_STEP_2M:
                src = stage1_recs[r]
                bits, conts = list(src["bits"]), list(src["continuations"])
                if gate1_diff and r == bt.RUNGS[0]:      # the sweep side keeps the un-flipped bytes
                    bits[0] = 1 - bits[0]
                    conts[0] = f" {cap['eval_items'][0]['answer']}" if bits[0] else " zzz"
            else:
                bits = _bits_at(r, step)
                conts = [f" {it['answer']}" if b else " zzz" for b, it in zip(bits, cap["eval_items"])]
            ev = {"bits": bits, "correct": sum(bits), "continuations": conts}
            _w(bm.record_path(root, step, r), bm.item_record_2m(rung=r, cap=cap, ev=ev, ckpt=_ckpt(entry), step=step,
                                                                 endpoint_sha=esha, t_s=0.0))
    te = bm.entry_3b(man, bm.TWIN)
    for r in bt.RUNGS:
        ev0 = {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}
        _w(bm.record_path(root, bm.TWIN, r), bm.item_record_2m(rung=r, cap=bat[r], ev=ev0, ckpt=_twin_ckpt(te),
                                                                step=bm.TWIN, endpoint_sha=esha, t_s=0.0))
    _w(bm.checkpoint_record_path(root, bm.TWIN),
       bm.twin_checkpoint_record_2m(info={"repo": bm.REPO_CKPT, "revision": bm.TWIN, "seed": bm.TWIN_SEED,
                                          "config_source": f"{bm.REPO_CKPT}@{te['config_commit']}", "tensor_digest": "T"}))
    e1 = entries["stage1_final"]
    g = {"rungs": list(bt.RUNGS),
         "bit_diffs": {r: (1 if gate1_attested_mismatch and r == bt.RUNGS[0] else 0) for r in bt.RUNGS},
         "continuation_diffs": {r: 0 for r in bt.RUNGS}, "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
         "digest_sweep": "D", "digest_endpoint": "D", "commit_sweep": e1["commit"], "commit_endpoint": e1["commit"],
         "prereg_tag": bm.PREREG_TAG_2M}
    _w(bm.gate1_path(root), g)
    if halt:
        bm.halt_marker_path(root).write_text("synthetic halt\n")
    if missing == "endpoint_record":
        bm.endpoint_record_path(root, "stage1_final", bt.RUNGS[0]).unlink()
    if missing == "base_record":
        bm.endpoint_record_path(root, "base", bt.RUNGS[0]).unlink()
    if missing == "sweep_record":
        bm.record_path(root, 600000, "antonym").unlink()
    if missing == "twin_record":
        bm.record_path(root, bm.TWIN, "antonym").unlink()
    if missing == "checkpoint_record":
        bm.checkpoint_record_path(root, bm.TWIN).unlink()
    if missing == "power":
        bm.power_path(root).unlink()
    if missing == "endpoint_sha":
        p = bm.endpoint_record_path(root, "base", "odd6")
        rec = json.loads(p.read_text())
        rec["seconds"] = 999.0
        p.write_text(json.dumps(rec))
    if missing == "dtype":
        p = bm.record_path(root, 600000, "odd6")
        rec = json.loads(p.read_text())
        rec["dtype"] = "bfloat16"
        p.write_text(json.dumps(rec))

    tags_2m = (bm.PREREG_TAG_2M, bm.ENDPOINT_SEAL_TAG_2M)

    def tag_exists(t):
        return True if t in tags_2m else pr.git_tag_exists(t)

    def blobs_bound(tag, paths, repo_root=None):
        if tag in tags_2m:
            return ["drifted"] if drifted_seal == tag else []
        return bi.blobs_bound(tag, paths, repo_root=repo_root if repo_root is not None else bi.REPO)

    def blob_sha(tag, rel):
        p = bm.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    return {"tag_exists": tag_exists, "blob_sha": blob_sha, "blobs_bound": blobs_bound}


def run_world(root, seal, *, n_perm=200, n_boot=20) -> dict:
    # referents_sha=False stays: a synthetic world root is not the real
    # tree, so the pre-campaign manifest cannot check against it. The
    # import pin (imports_pinned) and the frozen-module pin (frozen_check)
    # both now run for real (Task 5 pinned IMPORTED_SHA256_2M and
    # FROZEN_SHA256_2M and dropped both bypasses here).
    return an.run(root_2m=root, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=n_perm, n_boot=n_boot,
                  referents_sha=False, s8_loader=s8_cached, **seal)


def world_specs() -> list:
    return [
        ("W1 PYTHIA-ONLY", dict(mode="pythia_only"), "PYTHIA-ONLY"),
        ("W2 OLMO-ONLY", dict(mode="olmo_only"), "OLMO-ONLY"),
        ("W3 SHARED", dict(mode="shared"), "SHARED"),
        ("W4 NEITHER independent", dict(mode="independent"), "NEITHER"),
        ("W5 NEITHER inverted", dict(mode="inverted"), "NEITHER"),
        ("W6 PYTHIA-ONLY underpowered B disclosed", dict(mode="pythia_only", power_status_b="DECLARED UNDERPOWERED IN ADVANCE"), "PYTHIA-ONLY"),
        ("W7 INSUFFICIENT missing endpoint record", dict(mode="pythia_only", missing="endpoint_record"), "INSUFFICIENT_DATA"),
        ("W8 INSUFFICIENT drifted endpoint seal", dict(mode="pythia_only", drifted_seal=bm.ENDPOINT_SEAL_TAG_2M), "INSUFFICIENT_DATA"),
        ("W9 INSUFFICIENT halted", dict(mode="pythia_only", halt=True), "INSUFFICIENT_DATA"),
        ("W10 INSUFFICIENT gate-1 diff (real bytes, attestation blind, no marker)", dict(mode="pythia_only", gate1_diff=True), "INSUFFICIENT_DATA"),
        ("W11 INSUFFICIENT gate-1 attested mismatch", dict(mode="pythia_only", gate1_attested_mismatch=True), "INSUFFICIENT_DATA"),
        ("W12 INSUFFICIENT missing sweep record", dict(mode="pythia_only", missing="sweep_record"), "INSUFFICIENT_DATA"),
        ("W13 INSUFFICIENT missing twin checkpoint record", dict(mode="pythia_only", missing="checkpoint_record"), "INSUFFICIENT_DATA"),
        ("W14 INSUFFICIENT missing power", dict(mode="pythia_only", missing="power"), "INSUFFICIENT_DATA"),
        ("W15 INSUFFICIENT power sha", dict(mode="pythia_only", missing="power_sha"), "INSUFFICIENT_DATA"),
        ("W16 INSUFFICIENT power claims", dict(mode="pythia_only", missing="power_claims"), "INSUFFICIENT_DATA"),
        ("W17 INSUFFICIENT endpoint file edited after the sweep stamped its sha", dict(mode="pythia_only", missing="endpoint_sha"), "INSUFFICIENT_DATA"),
        ("W18 PYTHIA-ONLY extra rungs with an undefined D", dict(mode="pythia_only", all_fire=("count_div13", "caesar")), "PYTHIA-ONLY"),
        ("W19 thin eligible set (2l F-4)",
         dict(mode="pythia_only", zero_rungs=("antonym", "antonym6", "odd6", "sub_base8", "arith_next"),
              n_pos_cap={"add3_mid": 12, "sub3_mid": 18, "sub4_mid": 12},
              expect_primary=("add3_mid", "add_base8", "sub3_mid", "sub4_mid")), None),
        ("W20 INSUFFICIENT missing base record", dict(mode="pythia_only", missing="base_record"), "INSUFFICIENT_DATA"),
        ("W21 INSUFFICIENT missing twin record", dict(mode="pythia_only", missing="twin_record"), "INSUFFICIENT_DATA"),
        ("W22 INSUFFICIENT a record at another precision", dict(mode="pythia_only", missing="dtype"), "INSUFFICIENT_DATA"),
        ("W23 OLMO-ONLY underpowered A disclosed", dict(mode="olmo_only", power_status_a="DECLARED UNDERPOWERED IN ADVANCE"), "OLMO-ONLY"),
        # Freeze F-1: `add3_mid` clears 2d's endpoint bar at k = 9, so a
        # 12-positive rung is in R_PRIMARY and out of BOTH tests as
        # n_pos-thin; eligible = 8 >= 3, so 2l F-4's guard stays silent.
        ("W24 PYTHIA-ONLY partial eligible set disclosed (freeze F-1)",
         dict(mode="pythia_only", n_pos_cap={"add3_mid": 12}), "PYTHIA-ONLY"),
        # Freeze F-2: a `which` assembled from two loads. stage3_final is
        # chosen deliberately — gate 1 never looks at it and the rung
        # set's sha table agrees with the mixed bytes, so the ONLY thing
        # that can refuse is the new which-coherence check.
        ("W25 INSUFFICIENT a which assembled from two loads (freeze F-2)",
         dict(mode="pythia_only", mixed_digest_which="stage3_final"), "INSUFFICIENT_DATA"),
    ]
