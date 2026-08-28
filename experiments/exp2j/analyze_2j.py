# experiments/exp2j/analyze_2j.py
"""Experiment 2j — the mechanism question, analysis-only (design
`experiment-2j-design.md`). Every loader is 2i's; the statistic is
2i's `_run_test`; 2j adds the functionals (functionals_2j), the
composite strata, the comparison gates against 2i/2g/2h's committed
verdicts (three-way: re-derived == on disk == literal), the primary,
the printed decompositions, A-1's density matching and the tree."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2J = Path(__file__).resolve().parent
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import analyze_2g as an2g  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck2g  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import analyze_2h as an2h  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402

RESULTS = EXP2J / "results"
REFERENTS_PATH_2J = EXP2J / "referents_2j.json"
REFERENTS_2J_SHA256 = None      # pinned in Task 4 after make_referents_2j builds it
PREREG_TAG_2J = "exp2j-preregistered"
INSTRUMENT_BLOBS_2J = ("experiments/exp2j/analyze_2j.py",
                       "experiments/exp2j/functionals_2j.py")
WORLDS_2J = ("INSUFFICIENT_DATA", "RESIDUAL", "ABSORBED")
ALPHA, T_BAR, N_PERM, N_BOOT = st.ALPHA, st.T_BAR, st.N_PERM, st.N_BOOT
collect_total = an2i.collect_total
_run_test = an2i._run_test

VERDICT_2I_PIN = {"B": 0.21533409065382436, "within_alone": 0.22041895894950217,
                  "A": 0.09491251078607414, "cross_beyond_within": 0.07006211800715849,
                  "reverse_2.8b": 0.2612016707857866, "reverse_6.9b": 0.297364446603449}
VERDICT_2G_PIN = {"sampler_competitor": 0.16722141085849532}
VERDICT_2H_PIN = {"primary": 0.20197097010795367}

# FROZEN_SHA256_2J: 2i's 22 pins carried verbatim + 2i's own instrument
# and battery + power_2j.py + make_referents_2j.py (Task 4 adds their
# final shas; power_2j.py does not exist yet at this task, so the
# computed pin below carries only the files that are actually on disk —
# 2i's 22 + analyze_2i.py + battery_2i.py + make_referents_2j.py = +3
# over `bi.FROZEN_SHA256`). Task 4 replaces this with the literal dict.
FROZEN_FILES_2J = tuple(bi.FROZEN_SHA256) + (
    bi.EXP2I / "analyze_2i.py", bi.EXP2I / "battery_2i.py",
    EXP2J / "power_2j.py", EXP2J / "make_referents_2j.py")


def _pin_frozen_now() -> dict:
    return {p: bg.sha256_file(p) for p in FROZEN_FILES_2J if Path(p).is_file()}


FROZEN_SHA256_2J = _pin_frozen_now()   # Task 4 replaces this with the literal dict


def check_frozen_2j() -> None:
    if not FROZEN_SHA256_2J:
        raise RuntimeError("FROZEN_SHA256_2J is empty — the build has not pinned it")
    for p, want in FROZEN_SHA256_2J.items():
        got = bg.sha256_file(p)
        if got != want:
            raise RuntimeError(f"frozen module drifted: {p} ({got[:12]} != {want[:12]})")


def require_prereg_2j(*, tag_exists=None, blob_sha=None) -> dict:
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_2J):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_2J} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_2J:
        p = bg.REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_2J, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_2J} does not bind {rel}: "
                               f"tag {str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_2J, "instrument_blobs": bound}


# --------------------------------------------------------- disclosure

KNOWN_INPUTS_CAVEAT_2J = (
    "Everything. 2i's outcome (OLMo-2 7B's 21-point emission order) was sealed until "
    "its sweep and is now known, with its verdict; 2g's and 2h's outcomes are known; "
    "x_A (Pythia-1b, 2d's main tier) and x_B (OLMo-2 1B, 2i's predictor stage) are "
    "known with their per-rung concordances in every direction. There is no sealed "
    "outcome left on this battery below 12b, and 2j does not pretend to one. It is "
    "2e's kind of experiment: mechanism attribution on committed bytes, where "
    "preregistration protects against exactly one thing — choosing the functional, "
    "the partition or the tree after seeing what they do to the concordance — and "
    "not against a design written with the concordances in view.")

_L = {
 "INSUFFICIENT_DATA": "no licence: a referent, provenance, gate or comparison failed",
 "RESIDUAL": ("the essay's lineage sentence gains its mechanism clause — what the count "
              "carries is not the answer's length, its repetitiveness, its overlap with "
              "the input, or the smaller model's habit of saying that answer anyway; "
              "holding all four fixed inside the difficulty strata, the forecast survives "
              "at the printed T — a claim bounded to 'not these four'"),
 "ABSORBED": ("the count's forecast is structural at this resolution — it reads which "
              "answers are cheap to say or to produce; the 2g/2h/2i finding is reframed as "
              "an item-property forecast that any small model's output reads, with the "
              "printed attribution naming which functional carried it"),
 "ABSORBED_UNDERPOWERED": ("not detected at this resolution: the primary was DECLARED "
                           "UNDERPOWERED IN ADVANCE on its composite strata, so ABSORBED "
                           "licenses nothing beyond one sentence that the mechanism split "
                           "was attempted and not resolved"),
 "ABSORBED_THIN": ("not resolved: fewer than three rungs survived the composite "
                   "partition (THIN); ABSORBED licenses nothing"),
 "ABSORBED_UNDEFINED": ("no licence: the primary was undefined (x_B constant inside "
                        "every composite stratum on every eligible rung) — the "
                        "residual is untested, not absent"),
}
LICENSED_2J = {k: f"{v}. Disclosure (design §2): {KNOWN_INPUTS_CAVEAT_2J}"
               for k, v in _L.items()}
A1_READINGS = ("DENSITY", "NOT-DENSITY", "MIXED")

# fix round 1 / Finding 1 (2i's I-4 standard, analyze_2i.py:797-806 +
# :1588-1590): a disclosure that rides on BOTH the reason string and the
# licensed sentence, not merely on the reason. Two cases the power
# record's `declared_status` alone cannot distinguish from a real
# POWERED-but-null result: the primary was UNDEFINED (every eligible
# rung degenerate inside the composite strata — `_run_test` short-
# circuits before calling `primary_2i` at all, Ruling 18), and the
# REALIZED eligible set is THIN (< 3 rungs survived composite
# degeneracy) even though the power record — computed before the
# composite strata were realized — declared POWERED.
DISCLOSURE_UNDEFINED_2J = ("the primary was undefined (x_B constant inside every "
                           "composite stratum on every eligible rung), so the "
                           "residual is untested, not absent")
DISCLOSURE_THIN_2J = ("fewer than three rungs survived the composite partition "
                      "(realized eligible set), so the primary is THIN regardless "
                      "of the power record")

# ---------------------------------------------------------------- pins

def pin_from_record_2i(v: dict) -> dict:
    s = v["secondaries"]
    return {"B": v["tests"]["B"]["stratified"]["T"],
            "within_alone": s["within_alone"]["stratified"]["T"],
            "A": v["tests"]["A"]["stratified"]["T"],
            "cross_beyond_within": s["cross_beyond_within"]["stratified"]["T"],
            "reverse_2.8b": s["reverse_direction"]["vs_2.8b"]["stratified"]["T"],
            "reverse_6.9b": s["reverse_direction"]["vs_6.9b"]["stratified"]["T"]}


def pin_from_record_2g(v: dict) -> dict:
    return {"sampler_competitor": v["secondaries"]["sampler_competitor"]["stratified"]["T"]}


def pin_from_record_2h(v: dict) -> dict:
    return {"primary": v["primary"]["stratified"]["T"]}


def check_pin(rederived: dict, on_disk: dict, literal: dict, label: str) -> list:
    bad = []
    for k in literal:
        if k not in rederived or rederived[k] != on_disk.get(k):
            bad.append(f"{label}: re-derived {k} {rederived.get(k)!r} != verdict.json "
                       f"{on_disk.get(k)!r}")
    if {k: on_disk.get(k) for k in literal} != literal:
        bad.append(f"{label}: verdict.json {on_disk} != the literal pin {literal}")
    return bad


def _T_of(res: dict):
    return res["stratified"]["T"]


# ------------------------------------------------------------- loaders

def load_pythia_outcomes(battery, verify_fn) -> dict:
    """2i's `_reverse_direction` loading, verbatim, but returning the
    OUTCOME dicts over the predecessors' full primary rung sets so the
    2g/2h comparison gates and the A-1 anchors can run on them."""
    man28 = ck2g.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=an2g.CHECKPOINTS_SHA256)
    sweep28 = an2g.load_sweep(bg.EXP2G, "2.8b", battery, verify_fn, manifest=man28,
                              seal_sha=bh.PREDICTOR_2G_SHA)
    out28 = an2g.outcomes(sweep28, "2.8b", rungs=tuple(bg.R_28))
    man69 = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=an2h.CHECKPOINTS_2H_SHA256)
    sweep69 = an2h.load_sweep_69(bh.EXP2H, battery, verify_fn, manifest=man69,
                                 seal_sha=bh.PREDICTOR_2G_SHA, rungs=tuple(bh.R_69))
    out69 = an2h.outcomes_69(sweep69, rungs=tuple(bh.R_69))
    return {"2.8b": out28, "6.9b": out69}


def rederive_2i(x_a, x_b, out, strata, r_cap, py, *, n_perm, n_boot) -> dict:
    r28 = tuple(r for r in r_cap if r in bg.R_28)
    r69 = tuple(r for r in r_cap if r in bh.R_69)
    kw = dict(n_perm=n_perm, n_boot=n_boot)
    return {
        "B": _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x_a, r_cap),
                       r_cap, **kw),
        "within_alone": _run_test(x_b, bi.SIZE_PRED, out, strata, r_cap, **kw),
        "A": _run_test(x_a, "1b", out, strata, r_cap, **kw),
        "cross_beyond_within": _run_test(
            x_a, "1b", out, an2i._composite_strata_median(strata, x_b, r_cap), r_cap, **kw),
        "reverse_2.8b": _run_test(x_b, bi.SIZE_PRED, py["2.8b"], strata, r28, **kw),
        "reverse_6.9b": _run_test(x_b, bi.SIZE_PRED, py["6.9b"], strata, r69, **kw)}


def rederive_2g2h(x_a_full, py, strata, *, n_perm, n_boot) -> dict:
    """x_a_full must cover R_28 ∪ R_69 (count_div13 included)."""
    kw = dict(n_perm=n_perm, n_boot=n_boot)
    return {"sampler_competitor": _run_test(x_a_full, "1b", py["2.8b"], strata,
                                            tuple(bg.R_28), **kw),
            "primary": _run_test(x_a_full, "1b", py["6.9b"], strata, tuple(bh.R_69), **kw)}


# ------------------------------------------------------------ statistic

def t_only(counts, size_label, out, strata, rungs) -> dict:
    """T without a permutation (A-1, design §5.4 / dial e): the same
    cells `_run_test` builds (degeneracy rule, eligibility, tie rule),
    the same per-rung D, the same unweighted mean. Equality with
    `_run_test`'s T is asserted bit-for-bit in the tests and at k = 64
    on the real tree (the block gate)."""
    dropped = list(an2i._degenerate_rungs(counts, strata, rungs))
    keep = [r for r in rungs if r not in dropped]
    if not keep:
        return {"T": None, "per_rung": {}, "eligible": [], "thin": list(rungs),
                "dropped_degenerate": dropped}
    pred = an2i._scores_predictor_2i(counts, size_label, keep)
    cells, thin = an2g.cells_for(pred, out, strata, rungs=tuple(keep), size_pred=size_label,
                                 mode="trained")
    per_rung = {}
    for c in cells:
        d = st.somers_d_within(c["x"], c["y"], c["strata"])["d"]
        if np.isfinite(d):
            per_rung[c["rung"]] = float(d)
    if not per_rung:
        return {"T": None, "per_rung": {}, "eligible": [], "thin": thin,
                "dropped_degenerate": dropped}
    return {"T": float(np.mean(list(per_rung.values()))), "per_rung": per_rung,
            "eligible": list(per_rung), "thin": thin, "dropped_degenerate": dropped}


def primary_2j(x_b, out, strata_comp, r_cap, *, n_perm, n_boot) -> dict:
    return _run_test(x_b, bi.SIZE_PRED, out, strata_comp, r_cap, n_perm=n_perm, n_boot=n_boot)


def decomposition(counts, size_label, out, base, tables, rungs, *, n_perm, n_boot,
                  bucket_fn=fn.bucket) -> dict:
    kw = dict(n_perm=n_perm, n_boot=n_boot)
    within = _run_test(counts, size_label, out, base, rungs, **kw)
    comp, report = fn.composite_strata(base, tables, rungs, bucket_fn=bucket_fn)
    beyond = _run_test(counts, size_label, out, comp, rungs, **kw)
    single, alone = {}, {}
    for f in fn.FUNCTIONALS:
        comp_f, _ = fn.composite_strata(base, tables, rungs, functionals=(f,), bucket_fn=bucket_fn)
        single[f] = _run_test(counts, size_label, out, comp_f, rungs, **kw)
        fx = {r: tables[r][f] for r in rungs}
        alone[f] = (_run_test(fx, f"{size_label}:{f}", out, base, rungs, **kw)
                    if any(report[r][f] not in ("dropped_constant", "dropped_after_fallback")
                           for r in rungs) else None)
    tw, tb = _T_of(within), _T_of(beyond)
    frac = (None if tw is None or tb is None or tw == 0 else float(1 - tb / tw))
    return {"within_alone": within, "beyond_all": beyond, "fraction_absorbed": frac,
            "beyond_single": single, "alone": alone, "composite_report": report}


def _block_reading(r, bits_side, k, n_blocks, size_label, out, strata) -> dict:
    """One rung's per-block within-stratum d's, over `n_blocks` blocks
    of width `k` cut from `bits_side` — computed exactly as `t_only`
    computes a per-rung d, but ONE rung at a time. A rung's d is
    invariant to whether other rungs share the `t_only` call (Somers'
    D and the degeneracy screen are both computed within a single rung,
    with no cross-rung term), so this is bit-identical to what a joint
    `t_only` call restricted to this rung would have produced — proven
    for k=64 by `test_ladder_k64_matches_t_only_bit_for_bit`. A `None`
    (degenerate/ineligible block) is dropped, not averaged in as zero
    (fix round 1 / Finding 2: `n_blocks_used` counts only the finite
    ones actually contributing to `mean`/`min`/`max`)."""
    ds = []
    for b in range(n_blocks):
        cnt_r = fn.thinned_counts(bits_side, k, b)
        d = t_only({r: cnt_r}, size_label, out, strata, (r,))["per_rung"].get(r)
        if d is not None:
            ds.append(d)
    return {"mean": float(np.mean(ds)) if ds else None,
            "min": min(ds) if ds else None, "max": max(ds) if ds else None,
            "n_blocks_used": len(ds)}


def a1_density(bits_a, bits_b, outcomes: dict, strata) -> dict:
    """outcomes = {label: (out, rungs, T_a64, T_b64)} — the two 64-draw
    anchors are computed by the caller through `_run_test`.

    fix round 1 / Finding 2: the matched and ladder readings are now
    PER RUNG — each rung gets its own block count (`64 // k` on the
    side being thinned, 1 at the full 64-draw count on the other) and
    its own mean/min/max over its own blocks, then T is the mean of
    the per-rung means. The prior version shared one `n_blocks =
    min(...)` across every thinned rung, so a single large-k rung
    (design §5.4's own table has odd6 k=57, sub3_mid k=40 — both give
    `64 // k == 1`) collapsed every OTHER rung's reading to one block
    too, discarding the spread §5.4 asks to be printed."""
    res = {}
    for label, (out, rungs, t_a64, t_b64) in outcomes.items():
        xa = {r: fn.counts_from_bits(bits_a[r]) for r in rungs}
        xb = {r: fn.counts_from_bits(bits_b[r]) for r in rungs}
        per_rung = {}
        for r in rungs:
            per_rung[r] = {**fn.matched_k(fn.mean_rate(xa[r]), fn.mean_rate(xb[r])),
                           "rate_A": fn.mean_rate(xa[r]), "rate_B": fn.mean_rate(xb[r]),
                           "zero_fraction_k": (fn.zero_fraction_k(bits_b[r], xa[r])
                                               if fn.mean_rate(xb[r]) > fn.mean_rate(xa[r])
                                               else fn.zero_fraction_k(bits_a[r], xb[r]))}

        # matched reading: thin `side` on every rung where it is the
        # denser predictor (design §5.4); a rung where the OTHER
        # predictor is denser keeps `side`'s full 64-draw count — one
        # block, k=64 (bit-identical to `thinned_counts(bits, 64, 0)`).
        def matched(side, use_zero_fraction=False):
            size_label = "A" if side == "A" else bi.SIZE_PRED
            per_rung_out = {}
            for r in rungs:
                bits_side = bits_a[r] if side == "A" else bits_b[r]
                if per_rung[r]["denser"] == side:
                    k = per_rung[r]["zero_fraction_k"] if use_zero_fraction else per_rung[r]["k"]
                    n_blocks = 1 if use_zero_fraction else (64 // k)
                else:
                    k, n_blocks = 64, 1
                per_rung_out[r] = _block_reading(r, bits_side, k, n_blocks, size_label,
                                                 out, strata)
            means = [v["mean"] for v in per_rung_out.values() if v["mean"] is not None]
            return {"T": float(np.mean(means)) if means else None, "per_rung": per_rung_out}
        matched_b = matched("B")
        matched_a = matched("A")
        gap = None
        if matched_b["T"] is not None and t_b64 is not None and t_a64 is not None \
                and t_b64 != t_a64:
            gap = float((t_b64 - matched_b["T"]) / (t_b64 - t_a64))

        # ladder: BOTH sides thinned to every k in fn.LADDER over ALL
        # `64 // k` blocks — the rate structure, not the matched
        # reading (design §5.4). At k=64 this reduces, rung by rung,
        # to exactly the joint `t_only` call's per-rung d.
        ladder = {}
        for k in fn.LADDER:
            row = {}
            n_blocks = 64 // k
            for side, bits in (("A", bits_a), ("B", bits_b)):
                size_label = "A" if side == "A" else bi.SIZE_PRED
                per_rung_out = {r: _block_reading(r, bits[r], k, n_blocks, size_label,
                                                  out, strata) for r in rungs}
                means = [v["mean"] for v in per_rung_out.values() if v["mean"] is not None]
                row[side] = {"T": float(np.mean(means)) if means else None,
                             "per_rung": per_rung_out, "n_blocks": n_blocks}
            ladder[str(k)] = row
        res[label] = {"per_rung": per_rung, "anchors": {"x_A_64": t_a64, "x_B_64": t_b64},
                      "thinned_B_matched": matched_b, "thinned_A_matched": matched_a,
                      "thinned_B_zero_fraction": matched("B", True),
                      "gap_fraction_closed": gap, "ladder": ladder}
    readings = [v["gap_fraction_closed"] for k, v in res.items() if k in ("2.8b", "6.9b")]
    if any(g is None for g in readings) or not readings:
        reading = "MIXED"
    elif all(g >= 0.5 for g in readings):
        reading = "DENSITY"
    elif all(g < 0.5 for g in readings):
        reading = "NOT-DENSITY"
    else:
        reading = "MIXED"
    return {"outcomes": res, "reading": reading,
            "note": "non-gating (dial e): T per block, no permutation p; readings per §6"}


# ---------------------------------------------------------------- tree

def verdict_tree_2j(failures, primary, power) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader/gate failure(s): "
                          f"{list(failures)[:5]}", "declared_status": None,
                "disclosures": []}
    status = power["declared_status"]
    T, p = primary["stratified"]["T"], primary["stratified"]["p"]
    if primary["fires"]:
        return {"verdict": "RESIDUAL", "declared_status": status,
                "reason": f"primary fires: T_beyond={an2i._fmt_T(T)}, p={p:.4g}; {status}",
                "disclosures": []}
    # fix round 1 / Finding 1: an undefined primary (2i's Ruling 18 —
    # `_run_test` short-circuits before `primary_2i` is even called
    # when every eligible rung is degenerate inside the COMPOSITE
    # strata, exactly the construction that can leave x_B constant in
    # every stratum) is not a positive null result, and a realized
    # eligible set under three rungs is THIN regardless of what the
    # power record (computed before the composite strata existed)
    # declared. Both are disclosed on the reason string AND — via
    # `_licensed` below — on the licensed sentence, 2i's I-4 standard.
    disclosures = []
    if an2i._is_undefined_2i(primary):
        disclosures.append(DISCLOSURE_UNDEFINED_2J)
    elif len(primary.get("eligible", [])) < 3:
        disclosures.append(DISCLOSURE_THIN_2J)
    reason = (f"primary does not fire: T_beyond={an2i._fmt_T(T)}, p={p:.4g}"
             f"{'; ' + primary['named_inside'] if primary.get('named_inside') else ''}"
             f"; {status}")
    if disclosures:
        reason = "; ".join([reason] + disclosures)
    return {"verdict": "ABSORBED", "declared_status": status, "reason": reason,
            "disclosures": disclosures}


def _licensed(tree) -> str:
    if tree["verdict"] != "ABSORBED":
        licensed = LICENSED_2J[tree["verdict"]]
    else:
        disclosures = tree.get("disclosures") or []
        if DISCLOSURE_UNDEFINED_2J in disclosures:
            licensed = LICENSED_2J["ABSORBED_UNDEFINED"]
        elif DISCLOSURE_THIN_2J in disclosures:
            licensed = LICENSED_2J["ABSORBED_THIN"]
        else:
            s = tree["declared_status"]
            if s == "POWERED":
                licensed = LICENSED_2J["ABSORBED"]
            elif s == "THIN":
                licensed = LICENSED_2J["ABSORBED_THIN"]
            else:
                licensed = LICENSED_2J["ABSORBED_UNDERPOWERED"]
    if tree.get("disclosures"):
        licensed = "; ".join([licensed] + list(tree["disclosures"]))
    return licensed


def _load_power_2j(root_2j, r_cap) -> dict:
    p = Path(root_2j) / "results" / "power_2j.json"
    rec = json.loads(p.read_text())
    if not isinstance(rec, dict) or "primary" not in rec:
        raise ValueError(f"{p}: not a 2j power record")
    prim = rec["primary"]
    if prim.get("declared_status") not in an2i.DECLARED_STATUSES_2I:
        raise ValueError(f"{p}: declared_status {prim.get('declared_status')!r}")
    if set(prim.get("rungs", [])) != set(r_cap):
        raise ValueError(f"{p}: power rungs {prim.get('rungs')} != R_CAP {list(r_cap)}")
    if prim.get("n_trained_steps") != len(bi.trained_steps_7b()):
        raise ValueError(f"{p}: n_trained_steps {prim.get('n_trained_steps')}")
    return rec


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


# ----------------------------------------------------------------- run

# 2i's sentinel convention: the DEFAULT is the current value of the
# module-level constant, read at CALL time (so a test can monkeypatch
# the constant and see it take effect) rather than baked into the
# signature at import time. A caller passes `referents_sha=False`
# (a distinct falsy, non-None value) to skip the manifest check
# entirely — worlds and the empty-root test use this. Passing
# `referents_sha=None` explicitly (or leaving the constant unpinned)
# is a refusal: "not pinned (build incomplete)".
_LITERAL = object()


def run(root_2i=bi.EXP2I, root_2j=EXP2J, *, write=False, n_perm=N_PERM, n_boot=N_BOOT,
        tag_exists=None, blob_sha=None, blobs_bound=None, referents_sha=_LITERAL,
        pins_2i=None, pins_2g=None, pins_2h=None, verdict_2i_path=None, out_path=None) -> dict:
    failures = []
    pins_2i = VERDICT_2I_PIN if pins_2i is None else pins_2i
    pins_2g = VERDICT_2G_PIN if pins_2g is None else pins_2g
    pins_2h = VERDICT_2H_PIN if pins_2h is None else pins_2h
    root_2i, root_2j = Path(root_2i), Path(root_2j)
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_2J_SHA256

    # ---- instrument pins (a failure here is a refusal, collected)
    for thunk, label in ((bg.check_frozen_imports_2g, "2g upstream frozen imports"),
                         (bi.check_frozen_2i, "2i frozen imports"),
                         (check_frozen_2j, "2j frozen imports"),
                         (bi.check_pythia_predictor_files, "x_A draws files pinned")):
        _, f = collect_total(thunk, label)
        failures += f
    prereg, f = collect_total(lambda: require_prereg_2j(tag_exists=tag_exists,
                                                        blob_sha=blob_sha), "2j prereg tag")
    failures += f
    if referents_sha is None:
        failures.append("referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        from experiments.exp2j import make_referents_2j as mkr
        mf, f = collect_total(lambda: mkr.check_referents(REFERENTS_PATH_2J, sha_pin=referents_sha),
                              "2j referent manifest")
        failures += f + (mf or [])

    # ---- battery, floors, verify, strata (2i's loads, 2i's labels re-used verbatim
    #      would collide with 2j's own — every label here is 2j-prefixed)
    battery, f = collect_total(bg.load_battery, "battery items");                failures += f
    floors, f = collect_total(bg.load_floors, "floors 2d");                       failures += f
    verify_fn, f = collect_total(a2d.load_verify, "verify criterion 3c");         failures += f
    pred2g, f = collect_total(
        lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA),
        "strata source 2g predictor");                                             failures += f
    strata = sg.from_json(pred2g["strata"]) if pred2g else None
    gates = {}
    if strata is not None:
        sgg, f = collect_total(lambda: sg.check_strata_pins(strata), "strata pins 2g")
        failures += f
        gates["strata"] = sgg

    # ---- 2i's tree: seals, predictor provenance, rung set, endpoint, sweep, gate 1
    manifest, f = collect_total(
        lambda: bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256),
        "2i checkpoint manifest");                                                 failures += f
    predictor_rec, f = collect_total(lambda: an2i._load_predictor_seal_content(root_2i),
                                     "2i predictor seal content");                failures += f
    psl = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(root_2i, predictor_rec),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2i predictor seal binding: {m}" for m in psl["failures"]]
    rung_set, f = collect_total(lambda: an2i._load_rung_set(root_2i), "2i rung set file");  failures += f
    esl = an2i.require_seal_2i(bi.ENDPOINT_SEAL_TAG, an2i._endpoint_seal_paths(root_2i),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2i endpoint seal binding: {m}" for m in esl["failures"]]
    entry_stage1 = entry_1b = None
    if manifest is not None:
        entry_stage1, f = collect_total(lambda: bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B),
                                        "2i 7B endpoint entry");                  failures += f
        entry_1b, f = collect_total(lambda: bi.entry_1b_endpoint(manifest),
                                    "2i 1B endpoint entry");                      failures += f
    _prec = battery is not None and entry_1b is not None
    predictor_records, f = collect_total(
        lambda: an2i.load_predictor_records_2i(root_2i, battery, entry_1b=entry_1b) if _prec
        else (_ for _ in ()).throw(ValueError("battery or 1B entry missing")),
        "2i predictor olmo1b records");                                            failures += f
    if predictor_rec is not None and predictor_records is not None:
        sbad, f = collect_total(lambda: an2i._check_predictor_seal_sampling(predictor_rec, predictor_records),
                                "2i predictor seal sampling block");               failures += f + (sbad or [])
    _st1 = (battery is not None and verify_fn is not None and predictor_rec is not None
            and entry_stage1 is not None)
    stage1_final, f = collect_total(
        lambda: an2i.load_endpoint_which(root_2i, "stage1_final", battery, verify_fn,
                                         entry=entry_stage1, predictor_sha=predictor_rec["sha256"])
        if _st1 else (_ for _ in ()).throw(ValueError("battery, verify, seal or entry missing")),
        "2i endpoint stage1_final");                                               failures += f
    if rung_set is not None and stage1_final is not None:
        rb, f = collect_total(lambda: an2i._check_rung_set_vs_endpoint(rung_set, stage1_final),
                              "2i rung set vs endpoint");                          failures += f + (rb or [])
        if floors is not None:
            rb2, f = collect_total(lambda: an2i._check_rung_set_derivation(rung_set, stage1_final, floors),
                                   "2i rung set re-derivation");                   failures += f + (rb2 or [])
    if bi.halt_marker_path(root_2i).exists():
        failures.append("2i sweep: HALTED marker present")
    g1p = bi.gate1_path(root_2i)
    gate1 = None
    if not g1p.is_file():
        failures.append(f"2i gate 1: record missing ({g1p})")
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()), "2i gate 1 record"); failures += f
    _sw = manifest is not None and battery is not None and verify_fn is not None and predictor_rec is not None
    sweep, f = collect_total(
        lambda: an2i.load_sweep_7b(root_2i, battery, verify_fn, manifest=manifest,
                                   predictor_sha=predictor_rec["sha256"]) if _sw
        else (_ for _ in ()).throw(ValueError("manifest, battery, verify or seal missing")),
        "2i sweep olmo7b");                                                        failures += f
    _g = sweep is not None and stage1_final is not None and gate1 is not None
    gb, f = collect_total(
        lambda: an2i.gate1_rederive_7b(sweep[bi.ENDPOINT_STEP_7B], stage1_final, gate1) if _g
        else (_ for _ in ()).throw(ValueError("sweep, endpoint or gate 1 record missing")),
        "2i gate 1 byte identity re-derived");                                     failures += f + (gb or [])

    # ---- predictors, bits, outcomes
    r_cap = tuple(rung_set["R_CAP"]) if rung_set else ()
    r_full = tuple(sorted(set(r_cap) | set(bg.R_28) | set(bh.R_69)))
    _pr = rung_set is not None and battery is not None and verify_fn is not None
    x_a, f = collect_total(lambda: bi.sampler_counts_pythia("1b", r_full) if _pr
                           else (_ for _ in ()).throw(ValueError("rung set/battery/verify missing")),
                           "x_A counts 1b");                                       failures += f
    x_a410, f = collect_total(lambda: bi.sampler_counts_pythia("410m", r_cap) if _pr
                              else (_ for _ in ()).throw(ValueError("rung set/battery/verify missing")),
                              "x_A counts 410m");                                  failures += f
    x_b, f = collect_total(lambda: bi.sampler_counts_olmo(r_full, root=root_2i, battery=battery,
                                                          verify_fn=verify_fn) if _pr
                           else (_ for _ in ()).throw(ValueError("rung set/battery/verify missing")),
                           "x_B counts olmo1b");                                   failures += f
    if predictor_rec is not None and predictor_records is not None and x_b is not None:
        cb, f = collect_total(lambda: an2i._check_predictor_counts_2i(predictor_rec, predictor_records, x_b),
                              "x_B counts vs the sealed attestation");             failures += f + (cb or [])

    def _bits(which):
        out = {}
        for r in r_full:
            rows = fn.draw_rows_2i(root_2i, r) if which == "B" else fn.draw_rows_2d("1b", r)
            out[r] = fn.verified_bits(rows, battery[r], verify_fn)
            if fn.counts_from_bits(out[r]) != (x_b if which == "B" else x_a)[r]:
                raise ValueError(f"verified bits do not reproduce the count on {r} ({which})")
        return out
    bits_b, f = collect_total(lambda: _bits("B") if _pr and x_b else
                              (_ for _ in ()).throw(ValueError("x_B missing")), "bits x_B"); failures += f
    bits_a, f = collect_total(lambda: _bits("A") if _pr and x_a else
                              (_ for _ in ()).throw(ValueError("x_A missing")), "bits x_A"); failures += f

    def _tables(which):
        return {r: fn.functional_table(battery[r], fn.draw_rows_2i(root_2i, r) if which == "B"
                                       else fn.draw_rows_2d("1b", r)) for r in r_full}
    tables_b, f = collect_total(lambda: _tables("B") if _pr else
                                (_ for _ in ()).throw(ValueError("inputs missing")), "functionals under x_B"); failures += f
    tables_a, f = collect_total(lambda: _tables("A") if _pr else
                                (_ for _ in ()).throw(ValueError("inputs missing")), "functionals under x_A (1b)"); failures += f
    tables_a410, f = collect_total(
        lambda: {r: fn.functional_table(battery[r], fn.draw_rows_2d("410m", r)) for r in r_cap} if _pr
        else (_ for _ in ()).throw(ValueError("inputs missing")), "functionals under x_A (410m)"); failures += f

    py, f = collect_total(lambda: load_pythia_outcomes(battery, verify_fn) if battery and verify_fn
                          else (_ for _ in ()).throw(ValueError("battery/verify missing")),
                          "pythia outcomes 2g 2h");                                failures += f
    power, f = collect_total(lambda: _load_power_2j(root_2j, r_cap) if r_cap
                             else (_ for _ in ()).throw(ValueError("rung set missing")),
                             "2j power record");                                   failures += f

    # ---- comparison gates (three-way), then the core — all behind refusals
    out = None
    comparison = None
    if not failures:
        out, f = collect_total(lambda: an2i.outcomes_7b(sweep, rungs=tuple(bt.RUNGS)),
                               "outcome olmo7b");                                 failures += f
    if not failures:
        def _cmp():
            v2i = json.loads((Path(verdict_2i_path) if verdict_2i_path
                              else root_2i / "results" / "verdict.json").read_text())
            v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
            v2h = json.loads((bh.EXP2H / "results" / "verdict.json").read_text())
            red_i = rederive_2i(x_a, x_b, out, strata, r_cap, py, n_perm=n_perm, n_boot=n_boot)
            red_gh = rederive_2g2h(x_a, py, strata, n_perm=n_perm, n_boot=n_boot)
            bad = (check_pin({k: _T_of(v) for k, v in red_i.items()}, pin_from_record_2i(v2i),
                             pins_2i, "comparison gate 2i")
                   + check_pin({"sampler_competitor": _T_of(red_gh["sampler_competitor"])},
                               pin_from_record_2g(v2g), pins_2g, "comparison gate 2g")
                   + check_pin({"primary": _T_of(red_gh["primary"])}, pin_from_record_2h(v2h),
                               pins_2h, "comparison gate 2h"))
            return {"rederived_2i": red_i, "rederived_2g2h": red_gh, "failures": bad}
        comparison, f = collect_total(_cmp, "comparison gate re-derivation");     failures += f
        if comparison:
            failures += comparison["failures"]

    core = None
    if not failures:
        def _core():
            comp, report = fn.composite_strata(strata, tables_b, r_cap)
            prim = primary_2j(x_b, out, comp, r_cap, n_perm=n_perm, n_boot=n_boot)
            # the block gate: k = 64, one block, must reproduce within-alone's T exactly
            t64 = t_only({r: fn.thinned_counts(bits_b[r], 64, 0) for r in r_cap}, bi.SIZE_PRED,
                         out, strata, r_cap)["T"]
            if t64 != _T_of(comparison["rederived_2i"]["within_alone"]):
                raise ValueError(f"block gate: k=64 T {t64!r} != within-alone "
                                 f"{_T_of(comparison['rederived_2i']['within_alone'])!r}")
            return prim, report, t64
        core, f = collect_total(_core, "primary A-2");                             failures += f

    referents = {"failures": list(failures), "gates": gates, "prereg": prereg,
                 "predictor_seal_2i": psl, "endpoint_seal_2i": esl,
                 "gate1_2i": {k: v for k, v in (gate1 if isinstance(gate1, dict) else {}).items()
                              if k != "timing"},
                 "comparison": None if comparison is None else
                     {"2i": {k: _T_of(v) for k, v in comparison["rederived_2i"].items()},
                      "2g": _T_of(comparison["rederived_2g2h"]["sampler_competitor"]),
                      "2h": _T_of(comparison["rederived_2g2h"]["primary"]),
                      "gate": "PASS" if not comparison["failures"] else "FAIL"},
                 "power": power, "rung_set": rung_set}
    if failures:
        tree = verdict_tree_2j(failures, None, None)
        v = {"verdict": tree["verdict"], "reason": tree["reason"], "declared_status": None,
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2J,
             "licensed_sentence": LICENSED_2J["INSUFFICIENT_DATA"], "referents": referents,
             "primary": None, "secondaries": None, "a1": None, "n_perm": n_perm,
             "git_sha": _git_sha(), "model_contact": "none"}
    else:
        prim, report, t64 = core
        tree = verdict_tree_2j([], prim, power["primary"])
        sec, sec_failures = {}, []

        def _sec(name, thunk):
            val, f = collect_total(thunk, name)
            if f:
                sec[name] = {"failed": f[0]}
                sec_failures.extend(f)
            else:
                sec[name] = val

        kw = dict(n_perm=n_perm, n_boot=n_boot)
        r28 = tuple(r for r in r_cap if r in bg.R_28)
        r69 = tuple(r for r in r_cap if r in bh.R_69)
        _sec("decomposition x_B to olmo7b",
             lambda: decomposition(x_b, bi.SIZE_PRED, out, strata, tables_b, r_cap, **kw))
        _sec("decomposition x_A to olmo7b",
             lambda: decomposition(x_a, "1b", out, strata, tables_a, r_cap, **kw))
        _sec("decomposition x_B to 2.8b",
             lambda: decomposition(x_b, bi.SIZE_PRED, py["2.8b"], strata, tables_b, r28, **kw))
        _sec("decomposition x_B to 6.9b",
             lambda: decomposition(x_b, bi.SIZE_PRED, py["6.9b"], strata, tables_b, r69, **kw))
        _sec("decomposition x_A to 2.8b",
             lambda: decomposition(x_a, "1b", py["2.8b"], strata, tables_a, tuple(bg.R_28), **kw))
        _sec("decomposition x_A to 6.9b",
             lambda: decomposition(x_a, "1b", py["6.9b"], strata, tables_a, tuple(bh.R_69), **kw))
        _sec("sensitivity terciles",
             lambda: decomposition(x_b, bi.SIZE_PRED, out, strata, tables_b, r_cap,
                                   bucket_fn=fn.bucket_terciles, **kw)["beyond_all"])

        def _loo():
            tb = {r: {**tables_b[r], "pi": fn.wrong_target_propensity(fn.draw_rows_2i(root_2i, r),
                                                                      battery[r], loo=True)}
                  for r in r_cap}
            return decomposition(x_b, bi.SIZE_PRED, out, strata, tb, r_cap, **kw)["beyond_all"]
        _sec("sensitivity pi leave-one-out", _loo)
        six = tuple(r for r in r_cap if r not in ("add3_mid", "sub3_mid", "sub4_mid"))
        _sec("sensitivity six carried rungs",
             lambda: decomposition(x_b, bi.SIZE_PRED, out, strata, tables_b, six, **kw)["beyond_all"])
        _sec("sensitivity x_A 410m to olmo7b",
             lambda: decomposition(x_a410, "410m", out, strata, tables_a410, r_cap, **kw))

        def _a1():
            red = comparison["rederived_2i"]
            gh = comparison["rederived_2g2h"]
            anchors = {
                "olmo7b": (out, r_cap, _T_of(red["A"]), _T_of(red["within_alone"])),
                "2.8b": (py["2.8b"], r28, _T_of(gh["sampler_competitor"]), _T_of(red["reverse_2.8b"])),
                "6.9b": (py["6.9b"], r69,
                         _T_of(_run_test(x_a, "1b", py["6.9b"], strata, r69, **kw)),
                         _T_of(red["reverse_6.9b"]))}
            return a1_density(bits_a, bits_b, anchors, strata)
        _sec("A-1 density matching", _a1)
        sec["failures"] = sec_failures
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "declared_status": tree["declared_status"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2J, "licensed_sentence": _licensed(tree),
             "referents": referents,
             "primary": {**prim, "composite_report": report, "block_gate_T64": t64},
             "secondaries": sec, "a1": sec.get("A-1 density matching"),
             "n_perm": n_perm, "git_sha": _git_sha(), "model_contact": "none"}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(an2i._json_safe(v), indent=1, default=an2i._jsonable,
                                   allow_nan=False))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason")}, indent=1))
