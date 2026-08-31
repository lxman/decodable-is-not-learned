# experiments/exp2l/tests/full_shape.py
"""Synthetic 2l worlds (see the Task 4 header for the construction).
The predictors are never synthesized; only the 13B trees under `root`
are. Modes drive the four worlds; `missing` drives the refusals."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

EXP2L = Path(__file__).resolve().parents[1]
if str(EXP2L.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2L.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import analyze_2h as an2h  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i import power_2i as pw  # noqa: E402
from experiments.exp2i.run import endpoint_2i as ep2i  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import analyze_2l as an  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402

RUNGS_PRIMARY = tuple(sorted(bl.R_CAP_2K))
N_POS_FIRING = 200
_CACHE = {}


def _cached(name, fn):
    if name not in _CACHE:
        _CACHE[name] = fn()
    return _CACHE[name]


def battery():
    return _cached("battery", bg.load_battery)


def manifest():
    return _cached("manifest", lambda: bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256))


def verify_fn():
    return _cached("verify", a2d.load_verify)


def floors():
    return _cached("floors", bg.load_floors)


def strata():
    return _cached("strata", lambda: sg.from_json(
        pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)["strata"]))


def x_a256_real():
    """From the committed seal (the analyzer re-derives the same counts
    from the tier; 2k's seal check guarantees agreement)."""
    return _cached("x_a256", lambda: {r: list(json.loads(bk.seal_path(bk.EXP2K).read_text())["counts"]["1b"][r])
                                      for r in RUNGS_PRIMARY})


def x_b_real():
    return _cached("x_b", lambda: bi.sampler_counts_olmo(RUNGS_PRIMARY, root=bi.EXP2I, battery=battery(),
                                                         verify_fn=verify_fn()))


def _w(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _resid_b_given_a(x_a, x_b, strata_r):
    """The piece `b_only`/`both`/`inverted` need: within each BASE
    stratum, the residual of rank(x_b) after least-squares regression
    on rank(x_a) inside that stratum (a stratum with fewer than three
    items, or a constant rank(x_a) within it, falls back to demeaning
    rank(x_b) alone — there is nothing to regress against), standardized
    to unit variance over the whole rung."""
    n = len(x_a)
    ra, rb = rankdata(x_a, method="average"), rankdata(x_b, method="average")
    resid = np.zeros(n, dtype=np.float64)
    groups = {}
    for i, s in enumerate(strata_r):
        groups.setdefault(s, []).append(i)
    for idxs in groups.values():
        idxs = np.asarray(idxs)
        a_g, b_g = ra[idxs], rb[idxs]
        if len(idxs) < 3 or np.std(a_g) == 0:
            resid[idxs] = b_g - b_g.mean()
        else:
            design = np.vstack([a_g, np.ones(len(a_g))]).T
            beta, *_ = np.linalg.lstsq(design, b_g, rcond=None)
            resid[idxs] = b_g - design @ beta
    sd = resid.std(ddof=0)
    return resid / sd if sd > 0 else np.zeros(n)


# 2l's predictors are REAL (x_A^(256) from 2k, x_B from 2i), and 2i
# disclosed them correlated within base strata (rho .06-.32) — unlike
# 2i's own worlds, whose `_latent` mixed a SYNTHETIC x_B independent of
# x_A by construction. A latent built from x_A's raw rank alone still
# leaks into Test B (which conditions on x_A's own median bucket, so an
# x_A-driven outcome is still tracked inside each bucket by the
# correlated x_B), and symmetrically for x_B into Test A — both W1 and
# W2 landed BOTH instead of SHARED/LINEAGE. Orthogonalizing each mode's
# latent against the OTHER predictor under the analyzer's OWN
# conditioning (x_A's median bucket for Test B; the base stratum alone
# for Test A) removes that leak: `bucket_A` is exactly the split Test B
# forms its composite cells from, and `resid_B` is x_B's rank with
# x_A's linear signal removed inside every base stratum Test A reads.
def _latent(rng, x_a, x_b, strata_r, mode):
    n = len(x_a)
    tie = rng.normal(size=n) * 0.01
    xa, xb = np.asarray(x_a, dtype=np.float64), np.asarray(x_b, dtype=np.float64)
    bucket_A = np.asarray(an2h._median_bucket(xa), dtype=np.float64)
    resid_B = _resid_b_given_a(xa, xb, strata_r)
    if mode == "a_only":
        return bucket_A + tie
    if mode == "b_only":
        return resid_B + tie
    if mode == "both":
        return bucket_A + resid_B + tie
    if mode == "independent":
        return rng.normal(size=n)
    if mode == "inverted":
        return -(bucket_A + resid_B) + tie
    raise ValueError(mode)


def _ckpt(entry, digest="D"):
    return {"revision": entry["revision"], "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry.get("files", [])), "weight_sha256": digest, "config_source": "cs",
            "tokenizer_source": "ts"}


def write_world_2l(root, *, mode="a_only", seed=0, missing=None, power_status_a="POWERED",
                   power_status_b="POWERED", drifted_seal=None, halt=False, gate1_diff=False,
                   gate1_attested_mismatch=False) -> dict:
    root = Path(root)
    rng = np.random.default_rng(seed)
    bat, man, verify, strata0 = battery(), manifest(), verify_fn(), strata()
    x_a, x_b = x_a256_real(), x_b_real()
    steps = bl.trained_steps_13b()
    n_steps = len(steps)
    first = {}
    for r in bt.RUNGS:
        if r in RUNGS_PRIMARY:
            w = _latent(rng, x_a[r], x_b[r], strata0[r]["strata"], mode)
            order = np.argsort(-w)
            first[r] = {int(i): steps[int(rank * n_steps / N_POS_FIRING)]
                        for rank, i in enumerate(order[:N_POS_FIRING])}
        else:
            first[r] = {}
    entry_stage1, entry_main = bl.entry_13b(man, bl.ENDPOINT_STEP_13B), bl.entry_main_13b(man)

    # ---- the endpoint stage (stage1_final == the sweep's endpoint step; main all-zero)
    stage1_correct, stage1_recs = {}, {}
    for r in bt.RUNGS:
        cap = bat[r]
        bits = [int(i in first[r] and bl.ENDPOINT_STEP_13B >= first[r][i]) for i in range(bt.N_ITEMS)]
        conts = [f" {it['answer']}" if b else " zzz" for b, it in zip(bits, cap["eval_items"])]
        if gate1_diff and r == bt.RUNGS[0]:
            bits[0] = 1 - bits[0]
            conts[0] = f" {cap['eval_items'][0]['answer']}" if bits[0] else " zzz"
        ev = {"bits": bits, "correct": sum(bits), "continuations": conts}
        stage1_correct[r] = ev["correct"]
        rec = ep2i.item_record_2i(rung=r, family=bl.FAMILY, size=bl.SIZE_OUT, which="stage1_final", cap=cap, ev=ev,
                                  ckpt=_ckpt(entry_stage1), seal={"tag": bl.PREDICTOR_TAGS_2L, "sha256": bl.PREDICTOR_SHA_2L},
                                  t_s=0.0)
        stage1_recs[r] = rec
        _w(bl.endpoint_record_path(root, "stage1_final", r), rec)
        ev0 = {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}
        _w(bl.endpoint_record_path(root, "main", r),
           ep2i.item_record_2i(rung=r, family=bl.FAMILY, size=bl.SIZE_OUT, which="main", cap=cap, ev=ev0,
                               ckpt=_ckpt(entry_main), seal={"tag": bl.PREDICTOR_TAGS_2L, "sha256": bl.PREDICTOR_SHA_2L},
                               t_s=0.0))
    rs = bl.rung_set_from_counts_2l(stage1_correct, floors())
    if tuple(rs["R_PRIMARY"]) != RUNGS_PRIMARY:
        raise AssertionError(f"world builder: R_PRIMARY {rs['R_PRIMARY']} != the nine")
    _w(bl.rung_set_path(root), {**rs, "endpoint_file_sha256": {}})
    r_primary = tuple(rs["R_PRIMARY"])
    # ---- the power record: literal statuses, re-derivable claims computed for real (2k F-2)
    strata_b = an2i._composite_strata_median(strata0, x_a, r_primary)
    n_pos = {r: int(stage1_correct[r]) for r in r_primary}

    def _block(status, x, s):
        dropped = list(an2i._degenerate_rungs(x, s, r_primary))
        keep = [r for r in r_primary if r not in dropped]
        return {"declared_status": status, "declaration": "x", "rungs": list(r_primary),
                "n_trained_steps": bl.n_trained_13b(), "dropped_degenerate": dropped, "rungs_simulated": keep,
                "n_pos_lower_bound": n_pos, "t_bar": an.T_BAR, "alpha": an.ALPHA, "thin": len(keep) < 3}
    power = {"A": _block(power_status_a, x_a, strata0), "B": _block(power_status_b, x_b, strata_b),
             "block_sd_A": {"n_sim": 1, "mean_block_sd_at_declare": 0.01, "mean_block_sd_null": 0.005,
                            "per_block_mean_T_at_declare": [0.1] * 4, "blocks": 4},
             "predictor_sha256": bl.PREDICTOR_SHA_2L, "calibration_note": "x", "shape_note": "x", "note": "x"}
    if missing == "power_claims":
        power["A"] = dict(power["A"], declared_status="POWERED", dropped_degenerate=list(r_primary),
                          rungs_simulated=[], n_pos_lower_bound={r: 0 for r in r_primary}, t_bar=0.0, alpha=1.0, thin=True)
    if missing == "power_sha":
        power["predictor_sha256"] = "0" * 64
    _w(bl.power_path(root), power)
    esha = bl.endpoint_sha256(root)

    # ---- the sweep: 16 grid points + step 0 (all-zero), checkpoint records, gate 1
    for step in steps + (bl.STEP0,):
        entry = bl.entry_13b(man, step)
        _w(bl.checkpoint_record_path(root, step),
           {"family": bl.FAMILY, "size": bl.SIZE_OUT, "step": step, "revision": entry["revision"], "commit": entry["commit"],
            "sha256": dict(entry.get("lfs_sha256", {})),
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}, "digest": "D",
            "download_seconds": 0.0})
        for r in bt.RUNGS:
            cap = bat[r]
            if step == bl.ENDPOINT_STEP_13B:
                src = stage1_recs[r]
                bits, conts = list(src["bits"]), list(src["continuations"])
                if gate1_diff and r == bt.RUNGS[0]:      # the sweep side keeps the un-flipped bytes
                    bits[0] = 1 - bits[0]
                    conts[0] = f" {cap['eval_items'][0]['answer']}" if bits[0] else " zzz"
            elif step == bl.STEP0:
                bits, conts = [0] * bt.N_ITEMS, [" zzz"] * bt.N_ITEMS
            else:
                bits = [int(i in first[r] and step >= first[r][i]) for i in range(bt.N_ITEMS)]
                conts = [f" {it['answer']}" if b else " zzz" for b, it in zip(bits, cap["eval_items"])]
            ev = {"bits": bits, "correct": sum(bits), "continuations": conts}
            _w(bl.record_path(root, step, r), bl.item_record_2l(rung=r, cap=cap, ev=ev, ckpt=_ckpt(entry), step=step,
                                                                 endpoint_sha=esha, t_s=0.0))
    g = {"rungs": list(bt.RUNGS),
         "bit_diffs": {r: (1 if gate1_attested_mismatch and r == bt.RUNGS[0] else 0) for r in bt.RUNGS},
         "continuation_diffs": {r: 0 for r in bt.RUNGS}, "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
         "digest_sweep": "D", "digest_endpoint": "D", "commit_sweep": entry_stage1["commit"],
         "commit_endpoint": entry_stage1["commit"], "prereg_tag": bl.PREREG_TAG_2L}
    _w(bl.gate1_path(root), g)
    if halt:
        bl.halt_marker_path(root).write_text("synthetic halt\n")
    if missing == "endpoint_record":
        bl.endpoint_record_path(root, "stage1_final", bt.RUNGS[0]).unlink()
    if missing == "sweep_record":
        bl.record_path(root, 64000, "antonym").unlink()
    if missing == "checkpoint_record":
        bl.checkpoint_record_path(root, bl.STEP0).unlink()
    if missing == "power":
        bl.power_path(root).unlink()
    if missing == "endpoint_sha":            # a post-seal edit to an endpoint file
        p = bl.endpoint_record_path(root, "main", "odd6")
        rec = json.loads(p.read_text())
        rec["seconds"] = 999.0
        p.write_text(json.dumps(rec))

    tags_2l = (bl.PREREG_TAG_2L, bl.ENDPOINT_SEAL_TAG_2L)

    def tag_exists(t):
        return True if t in tags_2l else pr.git_tag_exists(t)

    def blobs_bound(tag, paths, repo_root=None):
        if tag in tags_2l:
            return ["drifted"] if drifted_seal == tag else []
        return bi.blobs_bound(tag, paths, repo_root=repo_root if repo_root is not None else bi.REPO)

    def blob_sha(tag, rel):
        p = bl.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    return {"tag_exists": tag_exists, "blob_sha": blob_sha, "blobs_bound": blobs_bound}


def run_world(root, seal, *, n_perm=200, n_boot=20) -> dict:
    # referents_sha=False stays: a synthetic world root is not the real
    # tree, so the pre-campaign manifest cannot check against it. The
    # import pin (imports_pinned) and the frozen-module pin (frozen_check)
    # both now run for real (Task 5 pinned IMPORTED_SHA256_2L and
    # FROZEN_SHA256_2L and dropped both bypasses here).
    return an.run(root_2l=root, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=n_perm, n_boot=n_boot,
                  referents_sha=False, **seal)


def world_specs() -> list:
    return [
        ("W1 SHARED", dict(mode="a_only"), "SHARED"),
        ("W2 LINEAGE", dict(mode="b_only"), "LINEAGE"),
        ("W3 BOTH", dict(mode="both"), "BOTH"),
        ("W4 NEITHER independent", dict(mode="independent"), "NEITHER"),
        ("W5 NEITHER inverted", dict(mode="inverted"), "NEITHER"),
        ("W6 SHARED underpowered B disclosed", dict(mode="a_only", power_status_b="DECLARED UNDERPOWERED IN ADVANCE"), "SHARED"),
        ("W7 INSUFFICIENT missing endpoint record", dict(mode="a_only", missing="endpoint_record"), "INSUFFICIENT_DATA"),
        ("W8 INSUFFICIENT drifted endpoint seal", dict(mode="a_only", drifted_seal=bl.ENDPOINT_SEAL_TAG_2L), "INSUFFICIENT_DATA"),
        ("W9 INSUFFICIENT halted", dict(mode="a_only", halt=True), "INSUFFICIENT_DATA"),
        ("W10 INSUFFICIENT gate-1 diff (real bytes, attestation blind, no marker)", dict(mode="a_only", gate1_diff=True), "INSUFFICIENT_DATA"),
        ("W11 INSUFFICIENT gate-1 attested mismatch", dict(mode="a_only", gate1_attested_mismatch=True), "INSUFFICIENT_DATA"),
        ("W12 INSUFFICIENT missing sweep record", dict(mode="a_only", missing="sweep_record"), "INSUFFICIENT_DATA"),
        ("W13 INSUFFICIENT missing step-0 checkpoint record", dict(mode="a_only", missing="checkpoint_record"), "INSUFFICIENT_DATA"),
        ("W14 INSUFFICIENT missing power", dict(mode="a_only", missing="power"), "INSUFFICIENT_DATA"),
        ("W15 INSUFFICIENT power sha", dict(mode="a_only", missing="power_sha"), "INSUFFICIENT_DATA"),
        ("W16 INSUFFICIENT power claims", dict(mode="a_only", missing="power_claims"), "INSUFFICIENT_DATA"),
        ("W17 INSUFFICIENT endpoint file edited after the sweep stamped its sha", dict(mode="a_only", missing="endpoint_sha"), "INSUFFICIENT_DATA"),
    ]
