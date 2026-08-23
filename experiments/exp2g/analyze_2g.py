# experiments/exp2g/analyze_2g.py
"""Exp 2g frozen analysis (design §4–§6): the sealed item-grain
forecast. Every input re-asserted against a pin; every loader refusal
COLLECTED and delivered as INSUFFICIENT_DATA with the reason verbatim
(lesson 8); the verdict tree mechanical (§6.3); the secondaries
printed, non-gating (§6.4).

Tree: INSUFFICIENT_DATA → FORECAST (p_strat < .01 ∧ T ≥ .10 ∧ p_twin
≥ .05) → SURFACE (… ∧ p_twin < .05) → DIFFICULTY-ONLY (p_raw < .01 ∧
p_strat ≥ .01) → NO-FORECAST (everything else; 'inverted' and
'detected below the effect bar' named inside it)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import labels_2g as lb  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import stats_2d as st2d  # noqa: E402

EXP2D = a2d.EXP2D
RESULTS = EXP2G / "results"
REFERENTS_PATH = EXP2G / "referents_2g.json"
CHECKPOINTS_SHA256 = "b4c50031e25f861f85609892b75f0b4bfe2ed9c4440cca7dce6ba940d950defe"
REFERENTS_FILE_SHA256 = None          # pinned in Task 13
WORLDS = ("INSUFFICIENT_DATA", "FORECAST", "SURFACE", "DIFFICULTY-ONLY",
          "NO-FORECAST")
ALPHA, ALPHA_TWIN, T_BAR = st.ALPHA, st.ALPHA_TWIN, st.T_BAR
N_PERM, N_BOOT = st.N_PERM, st.N_BOOT
DIGIT_RUNGS = ("add_base8", "sub_base8", "add3_mid", "sub3_mid", "sub4_mid",
               "arith_next")

KNOWN_INPUTS_CAVEAT_2G = (
    "Known to the designer before any checkpoint loaded: 2c's committed m4 "
    "counts at 2.8b/6.9b/12b final weights (which fix the rung sets and "
    "bound each rung's number of positive-outcome items from below); 2d's "
    "committed per-item generator records at 410m/1b (argmax continuations, "
    "64 draws per item), which supply two named secondaries; 2c's and 2f's "
    "committed probe records. Not known to anyone: any quantity at any "
    "intermediate checkpoint — the per-item verify bits, the trajectories, "
    "the first-clear steps. The predictor table was committed and tagged "
    "(exp2g-predictor-sealed) before the first checkpoint loaded.")

LICENSED = {
    "FORECAST": ("a per-item probe reading at 1b, fixed before any checkpoint "
                 "was loaded, forecast the order in which 2.8b's training made "
                 "2c's rising items emittable, beyond each rung's structural "
                 "difficulty covariate, on seven rungs in five families"),
    "SURFACE": ("the item ordering is readable from the prompt by a random "
                "network: the probe's item-level reading at 1b does not separate "
                "from surface statistics on this battery"),
    "DIFFICULTY-ONLY": ("structural difficulty orders emergence; the "
                        "representation adds nothing detectable beyond it"),
    "NO-FORECAST": "not detected at this resolution; blind region stated",
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}


def pythia_sha(size: str) -> str:
    from models import PYTHIA_SHAS
    return PYTHIA_SHAS[size]


def collect(thunk, label):
    try:
        return thunk(), []
    except (ValueError, FileNotFoundError, KeyError, RuntimeError) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


# -------------------------------------------------------------- gate 1

def gate1_failures(rec: dict, size: str) -> list:
    """Re-derived from the recorded quantities; `pass` is ignored."""
    bad = []
    rungs = bg.sweep_rungs(size)
    if rec.get("size") != size:
        bad.append(f"gate 1 {size}: record is for {rec.get('size')!r}")
    if list(rec.get("rungs", [])) != list(rungs):
        bad.append(f"gate 1 {size}: rung list is not the sweep set")
    if rec.get("model_sha") != pythia_sha(size):
        bad.append(f"gate 1 {size}: model_sha is not 2c's pinned main")
    counts = rec.get("counts_2c_path", {})
    for r in rungs:
        if r not in counts:
            bad.append(f"gate 1 {size}: no count for {r}")
        elif counts[r] != bg.FINAL_COUNT_PIN[size][r]:
            bad.append(f"gate 1 {size}/{r}: 2c's loader gives {counts[r]}, m4 "
                       f"committed {bg.FINAL_COUNT_PIN[size][r]} — the stack drifted")
    da, db = rec.get("digest_2c_path"), rec.get("digest_2g_path")
    if not da or not db or da != db:
        bad.append(f"gate 1 {size}: tensor digest through 2g's loader ({db}) ≠ "
                   f"through 2c's ({da}) — the checkpoint loader path is not "
                   f"the production path")
    cd = rec.get("continuation_diffs_2g_path", {})
    for r in rungs:
        if cd.get(r) != 0:
            bad.append(f"gate 1 {size}/{r}: {cd.get(r)} continuation diffs between "
                       f"the two loader paths")
    if not rec.get("seal", {}).get("sha256"):
        bad.append(f"gate 1 {size}: no seal recorded")
    return bad


# ------------------------------------------------------- step records

def step_record_failures(rec: dict, *, size, step, rung, cap, entry, verify_fn,
                         seal_sha) -> list:
    bad = []
    want_commit = pythia_sha(size) if step == bg.FINAL_STEP else entry["commit"]
    for k, v in (("rung", rung), ("size", size), ("step", int(step)),
                 ("n", bg.N_ITEMS), ("seal_tag", bg.SEAL_TAG)):
        if rec.get(k) != v:
            bad.append(f"{size}/step{step}/{rung}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("commit") != want_commit:
        bad.append(f"{size}/step{step}/{rung}: commit {rec.get('commit')} is not the "
                   f"manifest's {want_commit}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{size}/step{step}/{rung}: items_sha256 is not the pinned item file")
    if rec.get("predictor_sha") != seal_sha:
        bad.append(f"{size}/step{step}/{rung}: predictor_sha {rec.get('predictor_sha')} "
                   f"is not the seal {seal_sha}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bg.N_ITEMS or len(conts) != bg.N_ITEMS:
        bad.append(f"{size}/step{step}/{rung}: bits/continuations are not "
                   f"{bg.N_ITEMS} long")
        return bad
    if rec.get("correct") != sum(bits):
        bad.append(f"{size}/step{step}/{rung}: correct {rec.get('correct')} ≠ "
                   f"sum(bits) {sum(bits)}")
    re = [int(bool(verify_fn(c, it["answer"], cap["answer_type"])))
          for c, it in zip(conts, cap["eval_items"])]
    if re != [int(b) for b in bits]:
        n = sum(1 for a, b in zip(re, bits) if a != int(b))
        bad.append(f"{size}/step{step}/{rung}: re-verification of the continuations "
                   f"disagrees with the stored bits on {n} item(s)")
    return bad


def load_sweep(root, size, battery, verify_fn, *, manifest, seal_sha, steps=None) -> dict:
    steps = tuple(steps) if steps is not None else bg.GRID[size]
    out = {}
    for step in steps:
        entry = (ck.entry_for(manifest, size, step) if step != 0 or str(0) in
                 manifest[size]["entries"] else None)
        if entry is None:
            raise ValueError(f"{size} step {step} has no manifest entry")
        out[step] = {}
        for rung in bg.sweep_rungs(size):
            p = bg.record_path(root, size, step, rung)
            if not p.is_file():
                raise FileNotFoundError(f"sweep record missing: {p}")
            rec = json.loads(p.read_text())
            bad = step_record_failures(rec, size=size, step=step, rung=rung,
                                       cap=battery[rung], entry=entry,
                                       verify_fn=verify_fn, seal_sha=seal_sha)
            if bad:
                raise ValueError("; ".join(bad))
            out[step][rung] = rec
        if step != bg.FINAL_STEP:
            cp = bg.checkpoint_record_path(root, size, step)
            if not cp.is_file():
                raise FileNotFoundError(f"checkpoint record missing: {cp}")
            crec = json.loads(cp.read_text())
            for name, want in entry["lfs_sha256"].items():
                if crec.get("sha256", {}).get(name) != want:
                    raise ValueError(f"{size}/step{step}: downloaded {name} sha "
                                     f"{crec.get('sha256', {}).get(name)} ≠ manifest {want}")
            if crec.get("loading_info", {}) != {"missing_keys": 0, "unexpected_keys": 0,
                                                 "mismatched_keys": 0}:
                raise ValueError(f"{size}/step{step}: loading info not empty")
    return out


# ------------------------------------------------------------ outcomes

def outcomes(sweep: dict, size: str, *, rungs=None) -> dict:
    steps = bg.trained_steps(size)
    rungs = tuple(rungs) if rungs is not None else bg.sweep_rungs(size)
    out = {}
    for rung in rungs:
        bits = {s: [int(b) for b in sweep[s][rung]["bits"]] for s in sweep}
        y, first, last, stab = [], [], [], []
        for i in range(bg.N_ITEMS):
            hits = [s for s in steps if bits[s][i]]
            y.append(len(hits))
            first.append(hits[0] if hits else None)
            last.append(hits[-1] if hits else None)
            st_ = None
            for k, s in enumerate(steps):
                if all(bits[t][i] for t in steps[k:]):
                    st_ = s
                    break
            stab.append(st_)
        out[rung] = {"y": y, "first": first, "last": last, "stab": stab,
                     "n_pos": int(sum(1 for v in y if v > 0)),
                     "counts_by_step": {int(s): int(sweep[s][rung]["correct"])
                                        for s in sweep}}
    return out


def rung_level(out: dict, size: str, floors: dict, *, rungs=None) -> dict:
    steps = bg.trained_steps(size)
    rungs = tuple(rungs) if rungs is not None else tuple(out)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in steps
                  if st2d.binomial_bar(c[s], bg.N_ITEMS, floors[rung])["significant"]]
        final = bg.FINAL_STEP in clears
        res[rung] = {"s_star": clears[0] if clears else None,
                     "clears": clears, "final_clears": final,
                     "transient_clears": ([] if final else clears)}
    return res


# ------------------------------------------------------------- primary

def cells_for(pred: dict, out: dict, strata: dict, *, rungs, size_pred, mode,
              rule="cv", one_stratum=False, y_key="y", min_pos=bg.ELIGIBILITY_MIN_POS,
              keep=None) -> tuple:
    cells, thin = [], []
    for rung in rungs:
        y = np.asarray(out[rung][y_key], dtype=np.float64)
        x = pr.cell_scores(pred, rung, size_pred, mode, rule=rule)
        s = ["0"] * len(y) if one_stratum else list(strata[rung]["strata"])
        if keep is not None:
            m = np.asarray(keep[rung], dtype=bool)
            x, y, s = x[m], y[m], [v for v, k in zip(s, m) if k]
        if int((y > 0).sum()) < min_pos:
            thin.append(rung)
            continue
        cells.append({"rung": rung, "x": x, "y": y, "strata": s})
    return cells, thin


def primary(pred: dict, out: dict, strata: dict, *, size_pred, rungs, n_perm=N_PERM,
            seed=st.PERM_SEED, n_boot=N_BOOT, rule="cv", y_key="y", keep=None) -> dict:
    cells, thin = cells_for(pred, out, strata, rungs=rungs, size_pred=size_pred,
                            mode="trained", rule=rule, y_key=y_key, keep=keep)
    if not cells:
        raise ValueError("primary: no eligible rung")
    strat = st.perm_test(cells, n_perm=n_perm, seed=seed)
    raw_cells, _ = cells_for(pred, out, strata, rungs=rungs, size_pred=size_pred,
                             mode="trained", rule=rule, one_stratum=True, y_key=y_key,
                             keep=keep)
    raw = st.perm_test(raw_cells, n_perm=n_perm, seed=seed)
    tw_cells, _ = cells_for(pred, out, strata, rungs=rungs, size_pred=size_pred,
                            mode="untrained", rule=rule, y_key=y_key, keep=keep)
    twin = st.perm_test(tw_cells, n_perm=n_perm, seed=seed)
    per_rung = {}
    for c in cells:
        per_rung[c["rung"]] = {**strat["per_rung"][c["rung"]],
                               "ci": st.bootstrap_d(c["x"], c["y"], c["strata"],
                                                    n_boot=n_boot),
                               "raw_d": raw["per_rung"][c["rung"]]["d"],
                               "twin_d": twin["per_rung"][c["rung"]]["d"]}
    return {"stratified": strat, "raw": raw, "twin": twin,
            "pooled_d": st.pooled_d(cells), "per_rung": per_rung,
            "eligible": [c["rung"] for c in cells], "thin": thin,
            "size_pred": size_pred, "rule": rule, "y_key": y_key,
            "alpha": ALPHA, "alpha_twin": ALPHA_TWIN, "t_bar": T_BAR}


def verdict_tree_2g(failures, prim) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader failure(s): "
                          f"{list(failures)[:5]}"}
    T, p = prim["stratified"]["T"], prim["stratified"]["p"]
    p_raw, p_tw = prim["raw"]["p"], prim["twin"]["p"]
    if p < ALPHA and T >= T_BAR:
        if p_tw >= ALPHA_TWIN:
            return {"verdict": "FORECAST",
                    "reason": f"T = {T:.4f} ≥ {T_BAR}, p = {p:.4g} < {ALPHA}; twin "
                              f"p = {p_tw:.3g} ≥ {ALPHA_TWIN}"}
        return {"verdict": "SURFACE",
                "reason": f"T = {T:.4f}, p = {p:.4g}, but the twin's stratified "
                          f"forecast p = {p_tw:.3g} < {ALPHA_TWIN}"}
    if p_raw < ALPHA and p >= ALPHA:
        return {"verdict": "DIFFICULTY-ONLY",
                "reason": f"raw p = {p_raw:.4g} < {ALPHA}; stratified p = {p:.4g}"}
    notes = []
    if p < ALPHA and T < T_BAR:
        notes.append(f"detected below the effect bar (T = {T:.4f} < {T_BAR}, p = {p:.4g})")
    if T < 0:
        hi = prim["stratified"].get("n_perm", 0)
        p_inv = (1 + hi - prim["stratified"].get("n_ge", 0)) / (1 + hi) if hi else None
        notes.append(f"inverted (T = {T:.4f}; one-sided p for T_perm ≤ T_obs ≈ {p_inv})")
    return {"verdict": "NO-FORECAST",
            "reason": (f"stratified p = {p:.4g}, raw p = {p_raw:.4g}, T = {T:.4f}"
                       + ("; " + "; ".join(notes) if notes else ""))}


# ----------------------------------------------- 2d-derived secondaries

def sampler_counts_1b(d2_root, battery, verify_fn, rungs) -> dict:
    spec = a2d.TIERS["main"]
    out = {}
    for rung in rungs:
        cap = battery[rung]
        rows = a2d.read_rows(a2d.tier_draws_path(d2_root, "main", "1b", rung),
                             seed=spec["seed"], dps=spec["draws_per_seed"])
        counts = [0] * bg.N_ITEMS
        for row in rows:
            ans = cap["eval_items"][row["item"]]["answer"]
            counts[row["item"]] = sum(1 for d in row["draws"][str(spec["seed"])]
                                      if verify_fn(d, ans, cap["answer_type"]))
        out[rung] = counts
    return out


def performable_1b(d2_root, battery, verify_fn, rungs) -> dict:
    out = {}
    for rung in rungs:
        cap = battery[rung]
        rec = json.loads(a2d.argmax_record_path(d2_root, "1b", rung).read_text())
        conts = rec["continuations"]
        bits = [int(bool(verify_fn(c, it["answer"], cap["answer_type"])))
                for c, it in zip(conts, cap["eval_items"])]
        if sum(bits) != rec["correct"]:
            raise ValueError(f"2d argmax 1b/{rung}: re-verified {sum(bits)} ≠ stored "
                             f"{rec['correct']}")
        out[rung] = bits
    return out


# ----------------------------------------------------------------- run

def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                          capture_output=True, text=True).stdout.strip()


def _tree_of(prim):
    return verdict_tree_2g([], prim)


def run(root=EXP2G, *, write=False, n_perm=N_PERM, n_boot=N_BOOT, probe_root=None,
        d2_root=EXP2D, tag_exists=None, blob_sha=None, manifest_sha=CHECKPOINTS_SHA256,
        referents_sha=REFERENTS_FILE_SHA256, with_2d_secondaries=True,
        out_path=None) -> dict:
    failures = []
    bg.check_frozen_imports_2g()
    manifest, f = collect(lambda: ck.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=manifest_sha),
                          "checkpoint manifest")
    failures += f
    if referents_sha is not None:
        from experiments.exp2g import make_referents_2g as mk
        mf, f = collect(lambda: mk.check_referents(REFERENTS_PATH, sha_pin=referents_sha),
                        "referent manifest")
        failures += f + (mf or [])
    battery = bg.load_battery()
    floors = bg.load_floors()
    gates = {}
    g, f = collect(lambda: bg.check_rung_sets(floors), "rung sets")
    failures += f
    g, f = collect(lambda: lb.check_label_gates({r: battery[r] for r in bg.PREDICTOR_RUNGS}),
                   "label gates")
    failures += f
    gates["labels"] = g
    seal, f = collect(lambda: pr.require_seal(root, tag_exists=tag_exists, blob_sha=blob_sha),
                      "seal")
    failures += f
    pred, f = collect(lambda: pr.load_predictor(bg.predictor_path(root),
                                                sha_pin=seal["sha256"] if seal else None),
                      "predictor")
    failures += f
    strata = sg.from_json(pred["strata"]) if pred else None
    if pred:
        gates["strata"] = sg.check_strata_pins(strata)
        gates["predictor_gates"] = pred.get("gates", {})
    verify_fn = a2d.load_verify()
    seal_sha = seal["sha256"] if seal else None

    # gate 1 and the sweep, adjudicating size
    size = bg.ADJUDICATING
    g1p = bg.gate1_path(root, size)
    if bg.halt_marker_path(root, size).exists():
        failures.append(f"gate 1 {size}: the runner halted "
                        f"({bg.halt_marker_path(root, size).read_text().strip()[:200]})")
    if not g1p.is_file():
        failures.append(f"gate 1 {size}: record missing ({g1p})")
        gate1 = None
    else:
        gate1, f = collect(lambda: json.loads(g1p.read_text()), f"gate 1 {size} record")
        failures += f
        if gate1 is not None:
            failures += gate1_failures(gate1, size)
    sweep, f = collect(lambda: load_sweep(root, size, battery, verify_fn, manifest=manifest,
                                          seal_sha=seal_sha) if manifest and seal_sha else
                       (_ for _ in ()).throw(ValueError("manifest or seal missing")),
                       f"sweep {size}")
    failures += f

    referents = {"failures": list(failures), "gates": gates,
                 "manifest_sha256": manifest_sha, "frozen_imports": len(bg.FROZEN_IMPORT_SHA256_2G),
                 "seal": seal, "gate1": {k: v for k, v in (gate1 or {}).items()
                                         if k not in ("timing",)}}
    if failures:
        tree = verdict_tree_2g(failures, None)
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2G,
             "licensed_sentence": LICENSED["INSUFFICIENT_DATA"], "referents": referents,
             "primary": None, "secondaries": None, "git_sha": _git_sha()}
    else:
        out = outcomes(sweep, size)
        rl = rung_level(out, size, floors)
        prim = primary(pred, out, strata, size_pred=bg.PRIMARY_SIZE, rungs=bg.R_28,
                       n_perm=n_perm, n_boot=n_boot)
        tree = verdict_tree_2g([], prim)
        lbf = lb.floor_table({r: battery[r] for r in bg.PREDICTOR_RUNGS})
        sec = {}
        sec["replication_410m"] = primary(pred, out, strata, size_pred=bg.REPLICATION_SIZE,
                                          rungs=bg.R_28, n_perm=n_perm, n_boot=n_boot)
        sec["replication_410m"]["tree"] = _tree_of(sec["replication_410m"])
        sec["eval_site_rule"] = primary(pred, out, strata, size_pred=bg.PRIMARY_SIZE,
                                        rungs=bg.R_28, n_perm=n_perm, n_boot=n_boot, rule="eval")
        sec["eval_site_rule"]["tree"] = _tree_of(sec["eval_site_rule"])
        first = {r: {"y": [0 if v is None else (max(bg.trained_steps(size)) + 1 - v)
                           for v in out[r]["first"]], "n_pos": out[r]["n_pos"]}
                 for r in bg.R_28}
        sec["first_correct_outcome"] = primary(pred, first, strata, size_pred=bg.PRIMARY_SIZE,
                                               rungs=bg.R_28, n_perm=n_perm, n_boot=n_boot)
        sec["first_correct_outcome"]["note"] = ("y = (last trained step + 1 − first-correct "
                                               "step), 0 for never; monotone in earliness")
        lx = {}
        for r in bg.R_28:
            lab = lb.eval_labels(battery[r], r)
            lx[r] = {"strata": [f"{s}|{l}" for s, l in zip(strata[r]["strata"], lab)]}
        sec["label_x_covariate_strata"] = primary(pred, out, lx, size_pred=bg.PRIMARY_SIZE,
                                                  rungs=bg.R_28, n_perm=n_perm, n_boot=n_boot)
        sec["rung_level"] = {
            "note": "descriptive by design: seven rungs in five family blocks",
            "table": {r: {"s_star": rl[r]["s_star"],
                          "probe_margin_1b": (pred["cells"][r]["1b"]["trained"]["eval_acc"]
                                              - lbf[r]["floor"]),
                          "counts_by_step": out[r]["counts_by_step"]} for r in bg.R_28}}
        xs = [sec["rung_level"]["table"][r]["probe_margin_1b"] for r in bg.R_28]
        ys = [sec["rung_level"]["table"][r]["s_star"] or 10 ** 9 for r in bg.R_28]
        from scipy.stats import spearmanr
        sec["rung_level"]["spearman_point"] = float(spearmanr(xs, ys).statistic)
        sec["flat_rungs"] = {r: {"s_star": rl[r]["s_star"], "transient_clears": rl[r]["transient_clears"],
                                 "counts_by_step": out[r]["counts_by_step"]}
                             for r in bg.sweep_rungs(size) if r not in bg.R_28}
        sec["step0_counts"] = {r: out[r]["counts_by_step"].get(0) for r in bg.sweep_rungs(size)}
        sec["descriptive_item_level"] = {}
        for r in ("median5", "sub4_mid", "count_div13", "odd6"):
            c, thin = cells_for(pred, out, strata, rungs=(r,), size_pred=bg.PRIMARY_SIZE,
                                mode="trained")
            sec["descriptive_item_level"][r] = ({"thin": True, "n_pos": out[r]["n_pos"]} if thin
                                                else {**st.somers_d_within(c[0]["x"], c[0]["y"],
                                                                            c[0]["strata"])})
        if with_2d_secondaries:
            samp = sampler_counts_1b(d2_root, battery, verify_fn, bg.R_28)
            sp = {"cells": {r: {"1b": {"trained": {"scores": [float(v) for v in samp[r]],
                                                   "eval_rule": {"scores": [float(v) for v in samp[r]]}},
                                       "untrained": pred["cells"][r]["1b"]["untrained"]}}
                            for r in bg.R_28}}
            sec["sampler_competitor"] = primary(sp, out, strata, size_pred="1b", rungs=bg.R_28,
                                                n_perm=n_perm, n_boot=n_boot)
            sec["sampler_competitor"]["tree"] = _tree_of(sec["sampler_competitor"])
            sx = {r: {"strata": [f"{s}|{int(v > 0)}" for s, v in zip(strata[r]["strata"], samp[r])]}
                  for r in bg.R_28}
            sec["probe_beyond_sampler"] = primary(pred, out, sx, size_pred=bg.PRIMARY_SIZE,
                                                  rungs=bg.R_28, n_perm=n_perm, n_boot=n_boot)
            perf = performable_1b(d2_root, battery, verify_fn, bg.R_28)
            keep = {r: [1 - b for b in perf[r]] for r in bg.R_28}
            sec["exclude_1b_performable"] = primary(pred, out, strata, size_pred=bg.PRIMARY_SIZE,
                                                    rungs=bg.R_28, n_perm=n_perm, n_boot=n_boot,
                                                    keep=keep)
            sec["exclude_1b_performable"]["n_removed"] = {r: int(sum(perf[r])) for r in bg.R_28}
        # 12b replication, non-gating
        s12 = bg.REPLICATING
        rep = {"gate1": None, "failures": []}
        g1 = bg.gate1_path(root, s12)
        if g1.is_file():
            rep["gate1"], f = collect(lambda: json.loads(g1.read_text()), f"gate 1 {s12} record")
            rep["failures"] += f
            if rep["gate1"] is not None:
                rep["failures"] += gate1_failures(rep["gate1"], s12)
        else:
            rep["failures"].append(f"gate 1 {s12}: record missing")
        sw12, f = collect(lambda: load_sweep(root, s12, battery, verify_fn, manifest=manifest,
                                             seal_sha=seal_sha), f"sweep {s12}")
        rep["failures"] += f
        if not rep["failures"]:
            o12 = outcomes(sw12, s12)
            rep["primary"] = primary(pred, o12, strata, size_pred=bg.PRIMARY_SIZE,
                                     rungs=bg.R_12B, n_perm=n_perm, n_boot=n_boot)
            rep["tree"] = _tree_of(rep["primary"])
            rep["rung_level"] = rung_level(o12, s12, floors, rungs=bg.sweep_rungs(s12))
        sec["replication_12b"] = rep
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2G,
             "licensed_sentence": LICENSED[tree["verdict"]], "referents": referents,
             "primary": prim, "rung_level": rl, "secondaries": sec,
             "n_perm": n_perm, "git_sha": _git_sha()}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(v, indent=1, default=_jsonable))
    return v


def _jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason")}, indent=1))
    if v["primary"]:
        print(json.dumps({"T": v["primary"]["stratified"]["T"], "p": v["primary"]["stratified"]["p"],
                          "raw_p": v["primary"]["raw"]["p"], "twin_p": v["primary"]["twin"]["p"],
                          "per_rung": {r: d["d"] for r, d in v["primary"]["per_rung"].items()}},
                         indent=1))
