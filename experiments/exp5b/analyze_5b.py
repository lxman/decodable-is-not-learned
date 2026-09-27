# experiments/exp5b/analyze_5b.py
"""Exp 5b frozen analysis (design §3.2–§3.7, §5, §6): gates 0–7, with
Experiment 5's whole analyzer run in-process on Experiment 5's tree as
gate 2 (the re-derived verdict must equal the committed one exactly,
minus `meta`/`pins_active`; its `cells` supply R, P, a, b⁻, b⁺, f_A),
the 5b units under Experiment 5's contracts plus 5b's attestation, the
twelve re-reads re-derived, the power record re-derived byte-for-byte,
the projection's ancestry, the cells, the matched-placebo primary, σ̂_s
and the calibration read, the nine-cell tree, S1–S12 and the licence
block. Every loader refusal is COLLECTED and delivered as
INSUFFICIENT_DATA (lesson 8); the primary is a function of bytes that
exist only after the campaign (design §2)."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
import numpy as np  # noqa: E402

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp5 import analyze_5 as an5  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402
from experiments.exp5b import collect_5b as c5b  # noqa: E402
from experiments.exp5b import power_5b as pw5b  # noqa: E402
from experiments.exp5b import stats_5b as st  # noqa: E402

REFERENTS_PATH_5B = EXP5B / "referents_5b.json"
REFERENTS_5B_SHA256 = "ae5261d3d781e0d5a501aff8ee9a909eccd3bd69ba1727fcfd4369b28e1db32c"  # Task 6
_LITERAL = object()

CAVEAT_5B = ("one family, one battery of 34 synthetic tasks, sizes to 12b, loss matched on a 2M-token "
             "validation slice; the small side's wobble read at three neighbours at 1,000-step spacing "
             "at the anneal's end")

_LICENCE_BODY_5B = {
    "SURVIVES-CALIBRATED": (
        "the third disclosure is retired: with each smaller model read at its three preceding checkpoints "
        "as well and both sides' wobble subtracted, the excess is {t_items} items per 500 (p = {p}), "
        "{outside_items} items outside the 2.8B row; the essay states the excess net of both wobbles "
        "(the number replaces 27); the rule's realized false-positive rate at the measured wobble "
        "(sigma_hat {sigma_hat} items) is {alpha}"),
    "SURVIVES-INFLATED": (
        "as CALIBRATED — the excess is {t_items} items per 500 (p = {p}), {outside_items} items outside the "
        "2.8B row — and the sentence adds: the preregistered rule's own false-positive rate under the "
        "measured wobble (sigma_hat {sigma_hat} items) is {alpha}, so the reading rests on the size of the "
        "excess more than on the test"),
    "SURVIVES-OFF-GRID": (
        "the licence is NOT claimed: the excess survives the rung-block null at {t_items} items per 500 "
        "(p = {p}; {outside_items} items outside the 2.8B row), but the small side's wobble ({sigma_hat} items "
        "per read) lies above the range the sealed calibration covered, so the rule's false-positive rate there "
        "is unmeasured; a calibration successor is named; the disclosure is not retired"),
    "NOT-SURVIVED-INSIDE": (
        "Experiment 5's excess is DEMOTED: with both sides' wobble subtracted the excess is {t_items} items "
        "per 500 against a bar of five at p {p} — inside the two sides' combined wobble at this resolution; "
        "Prediction 3's 'partly no' becomes 'not distinguishable from the wobble at this resolution, on "
        "this battery, to 12B'; not licensed: 'Prediction 3 holds'"),
    "NOT-SURVIVED-SIGN-ONLY": (
        "the excess is real in sign and smaller than five items: {t_items} items per 500 (p = {p}), below "
        "the preregistered bar; the disclosure is replaced by the measured number; no 'partly no'"),
    "NOT-SURVIVED-SIZE-ONLY": (
        "the excess of {t_items} items per 500 does not reject across tasks once both wobbles are "
        "subtracted (p = {p}); the essay names the row and rungs that carry it from S1 and makes no "
        "across-task claim; the scoreboard's p is replaced by the new p with the reason"),
    "UNDETERMINED": "the battery did not supply the cells; nothing in the essay changes; the reason is ledgered",
    "INSUFFICIENT_DATA": "nothing; the record states which gate failed, verbatim",
}


def collect_total_5b(thunk, label):
    if not isinstance(label, str) or not label.startswith("5b "):
        raise ValueError(f"collect_total_5b: label {label!r} must start with the '5b ' prefix")
    try:
        return an2i.collect_total(thunk, label)
    except (zipfile.BadZipFile, KeyError, OSError, ImportError, EOFError) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


# ---------------------------------------------------------------- sides

def _steps_on_disk(root, size) -> set:
    d = b5b.units_root_5b(root) / size
    if not d.exists():
        return set()
    return {int(p.name[4:]) for p in d.iterdir()
            if p.is_dir() and p.name.startswith("step") and p.name[4:].isdigit()}


def load_side_5b(root, size, *, manifest, battery, verify_fn, host, slice_sha, n_scored) -> dict:
    """`None` only when the side's directory is absent — since freeze F-1
    that absence is refused outright by the caller's window-completeness
    site (a campaign that did not finish, never an exclusion), and `None`
    is returned solely so that site has something to report; otherwise
    gate 3 through Experiment 5's loader (the final required), the 5b
    attestation on every unit, nothing else loaded, no torn directory;
    members = the finite window steps present."""
    root = Path(root)
    d = b5b.units_root_5b(root) / size
    if not d.exists():
        return None
    on_disk = _steps_on_disk(root, size)
    u = an5.load_units_5(root, size, manifest=manifest, battery=battery, verify_fn=verify_fn, host=host,
                         slice_sha=slice_sha, n_scored=n_scored)
    torn = sorted(s for s in on_disk if not b5.unit_complete_5(root, size, s))
    if torn:
        raise ValueError(f"{size}: step{torn[0]} is on disk but is not a complete unit (torn)")
    extra = sorted(on_disk - set(b5b.unit_steps_5b()))
    if extra:
        raise ValueError(f"gate 4 {size}: step{extra[0]} on disk but never requested (nothing else loaded)")
    rereads = {}
    for step in u["steps"]:
        p = b5b.unit5b_record_path_5b(root, size, step)
        if not p.is_file():
            raise ValueError(f"{size}/step{step}: _unit_5b.json missing (a unit without 5b's attestation)")
        rec = json.loads(p.read_text())
        bad = b5b.unit5b_record_failures_5b(rec, size=size, step=step, host=host)
        if bad:
            raise ValueError(f"{size}/step{step}: {bad[:4]}")
        if rec["reread"]:
            rereads[step] = rec["reread_record"]
    members_present = [s for s in b5b.WINDOW_STEPS_5B if s in u["steps"] and s not in u["nonfinite"]]
    members_absent = {}
    for s in b5b.WINDOW_STEPS_5B:
        if s not in u["steps"]:
            members_absent[str(s)] = "not loaded"
        elif s in u["nonfinite"]:
            members_absent[str(s)] = "non-finite loss"
    counts = {step: u["counts"][step] for step in [b5.FINAL_STEP_5] + members_present}
    return {"steps": u["steps"], "counts": counts, "losses": u["losses"], "nonfinite": u["nonfinite"],
            "digests": u["digests"], "git_shas": u["git_shas"], "whys": u["whys"], "rereads": rereads,
            "members_present": members_present, "members_absent": members_absent,
            "final_loss": u["losses"].get(b5.FINAL_STEP_5)}


def window_completeness_failures_5b(root) -> list:
    """Freeze F-1 (the class defect; 2d F-1's lineage): gate 4's window
    completeness MEASURED from the tree, not inferred from what loaded.
    The runner writes every one of the 24 units — a non-finite member is
    written whole and marked (Experiment 5's slip 9), a non-finite final
    halts the size with a marker — so a unit NOT on disk is a campaign that
    did not finish, never an ABSENT member (design §3.2's ABSENT is the
    measured non-finite rule), and a side directory NOT on disk is a size
    the campaign never reached, never an exclusion. Before this check both
    were read as §3.2's shorter window / exclusion and a verdict was
    delivered over whatever the kill left. Also: nothing but the six small
    sides under results/units/ (nothing else loaded)."""
    root = Path(root)
    bad = []
    ur = b5b.units_root_5b(root)
    if ur.is_dir():
        stray = sorted(p.name for p in ur.iterdir() if p.is_dir() and p.name not in b5b.small_sides_5b())
        if stray:
            bad.append(f"gate 4: {stray} under results/units/ is not a small side (nothing else loaded)")
    for size in b5b.small_sides_5b():
        missing = [int(s) for s in b5b.unit_steps_5b() if not b5b.unit_complete_5b(root, size, s)]
        if missing:
            bad.append(f"gate 4 {size}: step(s) {missing} not on disk as complete 5b units — the campaign "
                       f"did not finish this side (an ABSENT member is a written unit whose loss is "
                       f"not finite, never an unwritten one)")
    return bad


# --------------------------------------------------------------- gate 1

def gate1_rederive_5b(root, exp5_root, sides: dict) -> tuple:
    per_unit, failures = {}, []
    for size, side in sides.items():
        if side is None:
            continue
        for step in b5b.reread_steps_5b():
            if step not in side["steps"]:
                # Freeze C-1 (3d's gate 1 / 2h F-2): a re-read unit missing is a refusal, never a skip
                failures.append(f"gate 1 {size}/step{int(step)}: the re-read unit is not on disk — gate 1 "
                                f"compares all {len(b5b.reread_steps_5b())} re-reads of every side")
                continue
            rr = c5b.reread_compare_5b(root, size, step, exp5_root=exp5_root)
            key = f"{size}/step{int(step)}"
            per_unit[key] = rr
            if not rr["digest_equal"]:
                failures.append(f"gate 1 {key}: tensor digest {rr['digest_here'][:12]} is not Experiment 5's "
                                f"{rr['digest_committed'][:12]}")
            if not rr["loss_within_tol"]:
                failures.append(f"gate 1 {key}: |Δℓ| {rr['loss_delta']:.3e} > {b5b.LOSS_TOL_5B}")
            failures += rr["tolerance_failures"]
            att = side["rereads"].get(step) or {}
            for k in ("digest_equal", "loss_within_tol", "tolerance_failures", "byte_identical"):
                if att.get(k) != rr[k]:
                    failures.append(f"gate 1 {key}: the runner's attested {k} {att.get(k)!r} != re-derived {rr[k]!r}")
    return {"per_unit": per_unit, "pass": not failures, "n_units": len(per_unit)}, failures


# ------------------------------------------------------- power / projection

def power_failures_5b(rec: dict, *, cells5_live, floors, closed, power_gate="full") -> list:
    bad = []
    if rec.get("prereg_tag") != b5b.PREREG_TAG_5B:
        bad.append(f"power record: prereg_tag {rec.get('prereg_tag')!r} != {b5b.PREREG_TAG_5B!r}")
    if rec.get("exp5_closed_tag") != b5b.EXP5_CLOSED_TAG_5B:
        bad.append("power record: exp5_closed_tag is not exp5-closed")
    if rec.get("n_sim") != pw5b.N_SIM_5B or rec.get("seed") != pw5b.SEED_5B:
        bad.append(f"power record: n_sim/seed {rec.get('n_sim')}/{rec.get('seed')} != power_5b's "
                   f"{pw5b.N_SIM_5B}/{pw5b.SEED_5B} — provenance is measured, not attested")
    if closed and closed.get("verdict_sha256") is not None and \
            rec.get("exp5_verdict_sha256") != closed["verdict_sha256"]:
        bad.append("power record: exp5_verdict_sha256 is not the committed verdict's")
    want_struct = pw5b.structure_sha256_5b(pw5b.structure_5b(cells5_live))
    if rec.get("structure_sha256") != want_struct:
        bad.append("power record: structure_sha256 is not the sha of the structure built from the re-derived cells")
    if rec.get("declaration") not in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE"):
        bad.append(f"power record: declaration {rec.get('declaration')!r} is not one of the two literals")
    for k in ("sigma_hat_axis", "alpha_5b_axis", "null_mean_5b_axis", "alpha_exp5_axis", "alpha_naive_axis",
              "null_mean_exp5_axis", "null_mean_naive_axis"):
        if len(rec.get(k) or []) != len(b5b.SIGMA_GRID_5B):
            bad.append(f"power record: {k} does not cover the grid")
    # Freeze F-3: numpy.interp returns a number for ANY axis; the calibration read is defined
    # only on a strictly increasing one
    ax = rec.get("sigma_hat_axis") or []
    if len(ax) == len(b5b.SIGMA_GRID_5B) and not all(float(b) > float(a) for a, b in zip(ax, ax[1:])):
        bad.append("power record: sigma_hat_axis is not strictly increasing — the calibration read "
                   "(numpy.interp on the simulated axis) is undefined on it")
    if power_gate == "full" and not bad:
        recomputed = pw5b.compute_5b(cells5_live, floors, n_sim=rec["n_sim"], seed=rec["seed"])
        recomputed["exp5_verdict_sha256"] = rec.get("exp5_verdict_sha256")
        if json.dumps(recomputed, sort_keys=True) != json.dumps(rec, sort_keys=True):
            bad.append("power record: the recomputed record differs byte-for-byte from the committed one")
    return bad


def projection_failures_5b(sides: dict, *, projection_commit, prereg_commit, is_ancestor, edits=()) -> list:
    bad = list(edits)
    if not projection_commit:
        bad.append("projection: no projection commit found (experiments/exp5b/projection.md was never added)")
        return bad
    if not prereg_commit:
        bad.append("projection: no exp5b-preregistered tag commit to check ancestry against")
        return bad
    if not is_ancestor(prereg_commit, projection_commit):
        bad.append(f"projection: the tag commit ({prereg_commit}) is not an ancestor of the projection "
                   f"commit ({projection_commit})")
    for size, side in sides.items():
        if side is None:
            continue
        for step, sha in (side.get("git_shas") or {}).items():
            if not is_ancestor(projection_commit, sha):
                bad.append(f"projection: {size}/step{step} was built at {sha}, not a descendant of the "
                           f"projection commit ({projection_commit})")
    return bad


def _prereg_tag_commit():
    return b5b.prereg_tag_commit_5b()


# -------------------------------------------------------------- licence

def licence_block_5b(tree, *, primary, calibration, s1, sigma_hat) -> dict:
    world, cell = tree["verdict"], tree.get("cell")
    key = f"{world}-{cell}" if cell else world
    T = (primary or {}).get("T")
    p = ((primary or {}).get("rung_block") or {}).get("p")
    out_T = ((s1 or {}).get("outside_2p8b") or {}).get("T")
    fields = {"t_items": (f"{T * b5.N_ITEMS:.1f}" if T is not None else "?"),
              "p": (f"{p:.4g}" if p is not None else "?"),
              "outside_items": (f"{out_T * b5.N_ITEMS:.1f}" if out_T is not None else "?"),
              "sigma_hat": (f"{(sigma_hat or {}).get('pooled'):.1f}" if (sigma_hat or {}).get("pooled") is not None else "?"),
              "alpha": (f"{(calibration or {}).get('alpha_realized'):.3f}"
                        if (calibration or {}).get("alpha_realized") is not None else "?")}
    sentence = _LICENCE_BODY_5B.get(key, _LICENCE_BODY_5B["INSUFFICIENT_DATA"]).format(**fields)
    return {"world": world, "cell": cell, "key": key, "sentence": sentence, "caveat": CAVEAT_5B,
            "claimed": world == "SURVIVES" and cell == "CALIBRATED",
            "T_items": fields["t_items"], "outside_2p8b_items": fields["outside_items"],
            "sigma_hat": (sigma_hat or {}).get("pooled"), "alpha_realized": (calibration or {}).get("alpha_realized"),
            "T_star": (calibration or {}).get("T_star")}


# ----------------------------------------------------------- secondaries

def secondaries_5b(cells, *, cells5_all, v5, sides, power_rec, sigma_hat, calibration, gate1_rec, floors,
                   exp5_root, n_sample, seed) -> tuple:
    out, fails = {}, {}

    def _do(key, fn):
        try:
            out[key] = fn()
        except Exception as e:  # noqa: BLE001 — a secondary never touches `failures`
            fails[key] = f"{type(e).__name__}: {e}"

    counts_by_side = {s: side["counts"] for s, side in sides.items() if side is not None and side["members_present"]}
    _do("S1", lambda: st.s1_rows_5b(cells, n_sample=n_sample, seed=seed))

    def _s2():
        base = st.s2_swaps_5b(cells, n_sample=n_sample, seed=seed)
        disp = {}
        for s, side in sides.items():
            if side is None:
                continue
            fa = float(json.loads(b5.loss_record_path_5(exp5_root, s, b5.FINAL_STEP_5).read_text())["loss"])
            disp[s] = {str(step): (side["losses"][step] - fa) for step in side["steps"] if step in side["losses"]}
        return {**base, "loss_mismatch_per_side": disp}
    _do("S2", _s2)

    def _s3():
        live = st.analysed_5b(cells)
        q = [c["Q"] for c in live if c["Q"] is not None]
        pv = [float(c["P"]) for c in live]
        disp = {}
        for s, side in sides.items():
            if side is None:
                continue
            disp[s] = {str(step): (side["losses"][step] - side["final_loss"]) for step in side["steps"]
                       if step in side["losses"] and side["final_loss"] is not None}
        return {"Q": {"mean": float(np.mean(q)) if q else None, "sd": float(np.std(q)) if q else None, "n": len(q)},
                "P": {"mean": float(np.mean(pv)) if pv else None, "sd": float(np.std(pv)) if pv else None},
                "sigma_hat": sigma_hat, "small_side_loss_displacements": disp,
                "large_side_residuals": {f"{c['small']}→{c['large']}": [c["residual_lo"], c["residual_hi"]] for c in live},
                "referents": {"P_mean_items": b5b.EXP5_REFERENTS_5B["P_mean_items"], "P_sd_items": b5b.EXP5_REFERENTS_5B["P_sd_items"]}}
    _do("S3", _s3)

    def _s4():
        sh = (sigma_hat or {}).get("pooled")
        axis = power_rec["sigma_hat_axis"]
        x = min(max(sh, axis[0]), axis[-1]) if sh is not None else None
        T5 = (v5.get("primary") or {}).get("T")
        Tsym = st.primary_5b(cells, n_sample=n_sample, seed=seed)["T"] if cells else None
        def at(k):
            return float(np.interp(x, axis, power_rec[k])) if x is not None else None
        return {"sigma_hat": sh, "off_grid": bool(sh is not None and sh > axis[-1]),
                "exp5_rule": {"alpha_at_sigma_hat": at("alpha_exp5_axis"), "null_mean_at_sigma_hat": at("null_mean_exp5_axis"),
                              "T": T5, "T_star": (T5 - at("null_mean_exp5_axis")) if (T5 is not None and x is not None) else None,
                              "alpha_axis": power_rec["alpha_exp5_axis"]},
                "naive_rule": {"alpha_at_sigma_hat": at("alpha_naive_axis"), "null_mean_at_sigma_hat": at("null_mean_naive_axis"),
                               "alpha_axis": power_rec["alpha_naive_axis"]},
                "rule_5b": {"alpha_at_sigma_hat": at("alpha_5b_axis"), "null_mean_at_sigma_hat": at("null_mean_5b_axis"),
                            "T": Tsym, "T_star": (calibration or {}).get("T_star"), "alpha_axis": power_rec["alpha_5b_axis"]},
                "grid": list(b5b.SIGMA_GRID_5B), "sigma_hat_axis": axis}
    _do("S4", _s4)
    _do("S5", lambda: {"modifier": st.modifier_5b(cells), "exp5_signed_offset": v5.get("signed_offset")})
    _do("S6", lambda: {**st.s6_ledger_5b(cells),
                       "count_div13_1p4b": {str(k): v.get("count_div13") for k, v in
                                            ((sides.get("1.4b") or {}).get("counts") or {}).items()}})
    _do("S7", lambda: st.s7_by_type_5b(cells, n_sample=n_sample, seed=seed))
    _do("S8", lambda: st.s8_one_member_5b(cells, ((v5.get("secondaries") or {}).get("S11") or {}).get("per_small_side") or {},
                                          n_sample=n_sample, seed=seed))
    _do("S9", lambda: st.s9_spike_5b(cells, n_sample=n_sample, seed=seed))

    def _s10():
        forms = st.s10_forms_5b(cells, n_sample=n_sample, seed=seed)
        sh = (sigma_hat or {}).get("pooled")
        axis = power_rec["sigma_hat_axis"]
        x = min(max(sh, axis[0]), axis[-1]) if sh is not None else None
        forms["c_naive"]["null_mean_at_sigma_hat"] = float(np.interp(x, axis, power_rec["null_mean_naive_axis"])) if x is not None else None
        forms["null_mean_5b_at_sigma_hat"] = float(np.interp(x, axis, power_rec["null_mean_5b_axis"])) if x is not None else None
        return forms
    _do("S10", _s10)
    _do("S11", lambda: gate1_rec)
    dead = [c for c in cells5_all if not (c.get("live") and c.get("defined_P"))]
    _do("S12", lambda: st.s12_newly_live_5b(dead, counts_by_side, floors))
    return out, fails


# -------------------------------------------------------------- verdict

def verdict_5b(*, failures, tree, primary, calibration, sigma_hat, modifier, gate1, gate2, sides_block,
               secondaries, secondary_failures, licence, power, pins_active, git_sha, cells) -> dict:
    return {"verdict": tree["verdict"], "tree": tree, "primary": primary, "calibration": calibration,
            "sigma_hat": sigma_hat, "modifier": modifier, "gate1": gate1, "gate2": gate2, "sides": sides_block,
            "secondaries": secondaries, "failures": list(failures), "secondary_failures": secondary_failures,
            "licence": licence, "power": power, "pins_active": pins_active, "cells": list(cells or []),
            "meta": {"git_sha": git_sha}}


def write_verdict_txt_5b(v: dict) -> str:
    t = v["tree"]
    lines = [f"EXPERIMENT 5b VERDICT: {t['verdict']}" + (f" · {t['cell']}" if t.get("cell") else ""),
             f"reason: {t.get('reason', '')}", "", f"caveat: {v['licence'].get('caveat', '')}", "",
             f"licence: {v['licence'].get('sentence', '')}", ""]
    p = v.get("primary") or {}
    rb = p.get("rung_block") or {}
    T = p.get("T")
    lines.append(f"primary: T_sym={T} ({(T or 0) * b5.N_ITEMS:.1f} items per 500) n_cells={p.get('n_cells')} "
                 f"n_rungs={p.get('n_rungs')} rung-block p={rb.get('p')} method={rb.get('method')} "
                 f"n_blocks={rb.get('n_blocks')} p_min_attainable={p.get('p_min_attainable')}")
    lines.append(f"  family-block p={(p.get('family_block') or {}).get('p')}  cell-level p={(p.get('cell_level') or {}).get('p')}")
    c = v.get("calibration") or {}
    sh = v.get("sigma_hat") or {}
    lines.append(f"calibration: sigma_hat={sh.get('pooled')} per_side={sh.get('per_side')} in_grid={c.get('in_grid')} "
                 f"alpha_realized={c.get('alpha_realized')} null_mean_T={c.get('null_mean_T')} T_star={c.get('T_star')} "
                 f"cell={c.get('cell')}")
    pw_rec = v.get("power") or {}
    lines.append(f"power: {pw_rec.get('declaration')}  P(plugin, sigma_s 15)={((pw_rec.get('deciding') or {}).get('P_fire_5b'))}  "
                 f"min_detectable_T_5b={pw_rec.get('min_detectable_T_5b')}")
    m = v.get("modifier") or {}
    lines.append(f"modifier (R > M): {m.get('modifier')} n={m.get('n')} n_pos={m.get('n_pos')} n_neg={m.get('n_neg')} p={m.get('p_two_sided')}")
    lines.append("")
    sec = v.get("secondaries") or {}
    for k in ("S1", "S2", "S3", "S4", "S6", "S7", "S8", "S9", "S10", "S12"):
        lines.append(f"{k}: " + json.dumps(sec.get(k)))
    lines.append("")
    g1 = v.get("gate1") or {}
    lines.append(f"gate 1: pass={g1.get('pass')} n_units={g1.get('n_units')}")
    for key, rr in (g1.get("per_unit") or {}).items():
        lines.append(f"  {key}: digest_equal={rr.get('digest_equal')} byte_identical={rr.get('byte_identical')} "
                     f"|Δℓ|={rr.get('loss_delta')} Σ|Δ|={rr.get('count_abs_diff_sum')} max|Δ|={rr.get('count_abs_diff_max')} "
                     f"cont_diffs={rr.get('continuation_diffs_sum')} per_doc_diffs={rr.get('per_doc_diffs')}")
    g2 = v.get("gate2") or {}
    lines.append(f"gate 2: exp5 verdict {g2.get('exp5_verdict')} T={g2.get('exp5_T')} equal={g2.get('exp5_verdict_equal')} "
                 f"pins_active={g2.get('exp5_pins_active')}")
    lines.append(f"sides: {json.dumps(v.get('sides'))}")
    lines.append("")
    lines.append(f"failures: {v.get('failures')}")
    lines.append(f"secondary_failures: {v.get('secondary_failures')}")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ run

def run(root=None, *, exp5_root=None, write=False, n_sample=None, n_boot=None, manifest=None, sl=None,
        tag_exists=None, blob_sha=None, verdict_sha=None, exp5_kwargs=None, projection_commit=None,
        prereg_commit=None, is_ancestor=None, referents_sha=_LITERAL, imports_pinned=_LITERAL,
        frozen_check=None, power_gate="full", projection_edits=None) -> dict:
    root = Path(root) if root is not None else EXP5B
    exp5_root = Path(exp5_root) if exp5_root is not None else b5b.EXP5
    n_sample = b5.N_PERM_SAMPLED_5 if n_sample is None else n_sample
    # `n_boot` is accepted for signature parity with Experiment 5's analyzer only — 5b's
    # primary/calibration path takes no bootstrap; the kwarg is unused (Minor 6).
    exp5_kwargs = dict(exp5_kwargs or {})
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_5B_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = True
    failures = []

    def _halts():
        bad = [f"{s} is halted: {b5b.halt_marker_path_5b(root, s).read_text().strip()[:200]}"
               for s in b5b.small_sides_5b() if b5b.halt_marker_path_5b(root, s).exists()]
        if bad:
            raise ValueError(f"halt marker(s): {bad}")
        return True
    _, f = collect_total_5b(_halts, "5b halt marker"); failures += f
    _, f = collect_total_5b(frozen_check or b5b.check_frozen_5b, "5b frozen modules"); failures += f
    if imports_pinned is not False:
        _, f = collect_total_5b(b5b.check_imports_5b, "5b import surface (entry)"); failures += f
    prereg, f = collect_total_5b(lambda: b5b.require_prereg_5b(tag_exists=tag_exists, blob_sha=blob_sha), "5b prereg tag")
    failures += f
    closed, f = collect_total_5b(lambda: b5b.require_exp5_closed_5b(tag_exists=tag_exists, blob_sha=blob_sha,
                                                                     verdict_sha=verdict_sha, exp5_root=exp5_root),
                                 "5b exp5-closed"); failures += f
    manifest_injected = manifest is not None
    manifest, f = collect_total_5b(lambda: manifest if manifest_injected else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5),
                                   "5b manifest"); failures += f
    sl_injected = sl is not None
    sl, f = collect_total_5b(lambda: sl if sl_injected else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5), "5b slice")
    failures += f
    if referents_sha is not False:
        if referents_sha is None:
            failures.append("5b referents: not pinned (build incomplete)")
        else:
            def _refs():
                from experiments.exp5b import make_referents_5b as mkr
                return mkr.check_referents_5b(REFERENTS_PATH_5B, sha_pin=referents_sha)
            mf, f = collect_total_5b(_refs, "5b referents"); failures += f + (mf or [])
    battery, f = collect_total_5b(bt.load_battery, "5b battery"); failures += f
    floors, f = collect_total_5b(b5.load_floors_5, "5b floors"); failures += f
    verify_fn, f = collect_total_5b(a2d.load_verify, "5b verify"); failures += f

    # gate 2: Experiment 5's analyzer on Experiment 5's tree, in-process (plan B-3/B-10)
    def _exp5():
        kw5 = {"imports_pinned": False, **exp5_kwargs}          # B-10: 5b's check covers the union
        v5 = an5.run(root=exp5_root, write=False, **kw5)
        if v5["failures"]:
            raise ValueError("exp5: " + "; ".join(f"{x}" for x in v5["failures"][:3]))
        committed = json.loads((exp5_root / "results" / "verdict.json").read_text())
        bad = b5b.exp5_verdict_equal_failures_5b(v5, committed) + b5b.exp5_verdict_pin_failures_5b(v5)
        if bad:
            raise ValueError("; ".join(bad))
        return v5
    v5, f = collect_total_5b(_exp5, "5b exp5"); failures += f
    cells5_live = [c for c in (v5 or {}).get("cells", []) if c.get("live") and c.get("defined_P")] if v5 else None
    gate2 = {"exp5_verdict": (v5 or {}).get("verdict"), "exp5_T": ((v5 or {}).get("primary") or {}).get("T"),
             "exp5_verdict_equal": v5 is not None, "exp5_failures": f, "n_cells5_live": len(cells5_live or []),
             "exp5_pins_active": (v5 or {}).get("pins_active")}

    def _host():
        p = b5b.host_record_path_5b(root)
        if not p.is_file():
            raise ValueError("host record missing")
        rec = json.loads(p.read_text())
        bad = b5.host_record_failures_5(rec)
        if bad:
            raise ValueError(f"host record: {bad}")
        return rec
    host, f = collect_total_5b(_host, "5b host record"); failures += f

    ready = all(x is not None for x in (manifest, sl, battery, verify_fn, host))
    sides = {}
    for size in b5b.small_sides_5b():
        def _side(size=size):
            if not ready:
                raise ValueError("manifest, slice, battery, verify criterion or host record missing")
            return load_side_5b(root, size, manifest=manifest, battery=battery, verify_fn=verify_fn, host=host,
                                slice_sha=sl["sha256"], n_scored=sl["meta"]["n_scored"])
        side, f = collect_total_5b(_side, f"5b units {size}"); failures += f
        sides[size] = side if not f else None
    def _window():
        bad = window_completeness_failures_5b(root)
        if bad:
            raise ValueError("; ".join(bad[:6]))
        return True
    _, f = collect_total_5b(_window, "5b window completeness"); failures += f
    excluded = sorted(s for s, side in sides.items() if side is None or not side["members_present"])
    members_absent = {s: side["members_absent"] for s, side in sides.items() if side is not None and side["members_absent"]}

    def _gate1():
        rec, bad = gate1_rederive_5b(root, exp5_root, sides)
        att_p = b5b.gate1_path_5b(root)
        if not att_p.is_file():
            bad.append("gate 1: results/gate1_5b.json (the runner's attestation) missing")
        else:
            att = json.loads(att_p.read_text())
            if att.get("pass") != rec["pass"]:
                bad.append("gate 1: the runner's attested pass flag != the re-derived one")
            # Freeze C-1: coverage measured — the attestation's units == the re-derived units
            att_keys, got_keys = set(att.get("per_unit") or {}), set(rec["per_unit"])
            if att_keys != got_keys:
                bad.append(f"gate 1: the runner's attestation covers {len(att_keys)} unit(s), the "
                           f"re-derivation {len(got_keys)}: attested-only {sorted(att_keys - got_keys)[:4]}, "
                           f"re-derived-only {sorted(got_keys - att_keys)[:4]}")
        if bad:
            raise ValueError("; ".join(bad[:6]))
        return rec
    gate1_rec, f = collect_total_5b(_gate1, "5b gate 1"); failures += f

    def _power():
        p = b5b.power_path_5b(root)
        if not p.is_file():
            raise ValueError("power_5b.json missing")
        rec = json.loads(p.read_text())
        if cells5_live is None or floors is None:
            raise ValueError("power record: cannot check — the re-derived cells or floors are missing")
        bad = power_failures_5b(rec, cells5_live=cells5_live, floors=floors, closed=closed, power_gate=power_gate)
        if bad:
            raise ValueError(f"power record: {bad}")
        return rec
    power_rec, f = collect_total_5b(_power, "5b power record"); failures += f

    resolved_pc = projection_commit if projection_commit is not None else b5b.projection_commit_5b()
    resolved_tag = prereg_commit if prereg_commit is not None else _prereg_tag_commit()
    anc = is_ancestor or b5b.is_ancestor_5b

    def _projection():
        if projection_edits is not None:
            edits = list(projection_edits)
        elif projection_commit is None and resolved_pc:
            edits = b5b.projection_edits_5b(resolved_pc)
        else:
            edits = []
        bad = projection_failures_5b(sides, projection_commit=resolved_pc, prereg_commit=resolved_tag,
                                     is_ancestor=anc, edits=edits)
        if bad:
            raise ValueError(f"projection: {bad}")
        return True
    _, f = collect_total_5b(_projection, "5b projection"); failures += f

    cells, primary, sigma_hat, calibration, modifier = [], None, None, None, None
    # Since freeze F-1 an incomplete side refuses at "5b window completeness" above before a
    # verdict is reached, so `excluded`/`cells_dropped` are always empty on any tree that gets
    # this far — they are attested for the record, not a live exclusion mechanism.
    sides_block = {"present": sorted(s for s in sides if sides[s] is not None and sides[s]["members_present"]),
                   "excluded": excluded, "members_absent": members_absent, "cells_dropped": 0}
    if not failures and cells5_live is not None:
        counts_by_side = {s: side["counts"] for s, side in sides.items()
                          if side is not None and side["members_present"]}
        kept5 = [c for c in cells5_live if c["small"] in counts_by_side]
        sides_block["cells_dropped"] = len(cells5_live) - len(kept5)
        cells, f = collect_total_5b(lambda: st.cells_5b(kept5, counts_by_side, floors), "5b cells"); failures += f
        cells = cells or []
        primary, f = collect_total_5b(lambda: st.primary_5b(cells, n_sample=n_sample, seed=b5.PERM_SEED_5), "5b primary")
        failures += f
        sigma_hat, f = collect_total_5b(lambda: st.sigma_hat_5b(cells), "5b sigma hat"); failures += f
        calibration, f = collect_total_5b(
            lambda: st.calibration_read_5b(power_rec, (sigma_hat or {}).get("pooled"), T_sym=(primary or {}).get("T")),
            "5b calibration"); failures += f
        modifier, f = collect_total_5b(lambda: st.modifier_5b(cells), "5b modifier"); failures += f
    if imports_pinned is not False:
        _, f = collect_total_5b(b5b.check_imports_5b, "5b import surface (exit)"); failures += f

    tree = st.tree_5b(failures=failures, primary=primary or {}, calibration=calibration or {"cell": None})
    secondaries, secondary_failures = ({}, {})
    if not failures:
        secondaries, secondary_failures = secondaries_5b(
            cells, cells5_all=(v5 or {}).get("cells", []), v5=v5 or {}, sides=sides, power_rec=power_rec,
            sigma_hat=sigma_hat, calibration=calibration, gate1_rec=gate1_rec, floors=floors, exp5_root=exp5_root,
            n_sample=n_sample, seed=b5.PERM_SEED_5)
    licence = licence_block_5b(tree, primary=primary, calibration=calibration, s1=secondaries.get("S1"),
                               sigma_hat=sigma_hat)
    pins_active = {"frozen_modules": frozen_check is None, "import_surface": bool(imports_pinned),
                   "referents_sha": referents_sha, "prereg_binding": tag_exists is None and blob_sha is None,
                   "exp5_verdict_sha": verdict_sha is None, "power_gate": power_gate,
                   "slice_injected": sl_injected, "manifest_injected": manifest_injected,
                   "exp5_kwargs_injected": bool(exp5_kwargs),
                   "projection_edits_measured": projection_edits is None and projection_commit is None,
                   # Final review Important 1: every live injection recorded, not only some —
                   # an injected `is_ancestor`/`prereg_commit` bypasses the projection's real
                   # ancestry check while `projection_edits_measured` alone still read True; an
                   # injected `n_sample` moves every block/cell p-value with no flag showing it;
                   # `root`/`exp5_root` left un-recorded meant a non-default tree could not be
                   # told apart from the real campaign's in this dict alone.
                   "ancestry_injected": is_ancestor is not None or prereg_commit is not None,
                   "n_sample": n_sample,
                   "roots_default": root == EXP5B and exp5_root == b5b.EXP5}
    v = verdict_5b(failures=failures, tree=tree, primary=primary, calibration=calibration, sigma_hat=sigma_hat,
                   modifier=modifier, gate1=gate1_rec, gate2=gate2, sides_block=sides_block, secondaries=secondaries,
                   secondary_failures=secondary_failures, licence=licence, power=power_rec, pins_active=pins_active,
                   git_sha=b5b.git_sha_5b(), cells=cells)
    v = an5._json_safe_5(v)
    if write:
        def _w():
            out_v = root / "results" / "verdict.json"
            out_v.parent.mkdir(parents=True, exist_ok=True)
            out_v.write_text(json.dumps(v, indent=1, allow_nan=False))
            (root / "results" / "VERDICT.txt").write_text(write_verdict_txt_5b(v))
            return True
        _, f = collect_total_5b(_w, "5b verdict write")
        if f:
            v["write_failure"] = f[0]
    return v


if __name__ == "__main__":
    result = run(write="--write" in sys.argv)
    print(json.dumps({"verdict": result["verdict"], "cell": result["tree"].get("cell"),
                      "git_sha": result["meta"]["git_sha"]}, indent=1))
