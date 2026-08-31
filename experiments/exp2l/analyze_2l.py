# experiments/exp2l/analyze_2l.py
"""Experiment 2l — the sealed cross-family forecast (design
`experiment-2l-design.md`). 2i's two-test construction with the outcome
model swapped to OLMo-2 13B's stage-1 grid and the cross-family
predictor swapped to 2k's sealed 256-draw count. Zero model contact at
analysis; nothing sampled anywhere in 2l.

Predictors, loaded through their OWN seals (design §3.2): x_A^(256) and
its 64/128/192 ladder and four 64-draw blocks re-derived from 2k's raw
draws by `analyze_2k.load_tier_2k` (gate 1 vs 2d's committed rows,
tallies, seed census) at both sizes and cross-checked against
`predictor_2k.json` by `analyze_2k.seal_failures_2k`; x_B by 2i's
`sampler_counts_olmo` after `load_predictor_records_2i` (provenance) and
`_check_predictor_seal_sampling`, cross-checked by
`_check_predictor_counts_2i`. Both seal tags must bind; both seal shas
must equal `battery_2l`'s literals; the composite must equal
`PREDICTOR_SHA_2L`, which every 2l record must carry.

The 13B trees (design §3.3–§3.5): endpoint records against the
manifest's endpoint/main entries, sweep records against each step's
entry (the real step 0 included) and their `endpoint_sha256` against
the composite re-derived from the committed endpoint files, gate 1
attested (`gate1_failures_13b`) AND re-derived from the bytes
(`gate1_rederive_13b`), the halt marker refused. The rung set is
re-derived from the endpoint's own counts (`rung_set_from_counts_2l`)
and must equal the file. The power record's claims are re-derived
(2k F-2). The import surface is pinned at entry and exit (2j F-1).

Tests: A = x_A^(256) on 2g's base strata; B = x_B in strata = base |
median bucket of x_A^(256) (dial d). Both over R_PRIMARY. Tree = 2i's
`verdict_tree_2i` with 2l's disclosures (THIN, UNDERPOWERED) appended.
Every loader refusal COLLECTED and delivered as INSUFFICIENT_DATA."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2L = Path(__file__).resolve().parent
if str(EXP2L.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2L.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402

RESULTS = EXP2L / "results"
REFERENTS_PATH_2L = EXP2L / "referents_2l.json"
REFERENTS_2L_SHA256 = "ae4db62b326642766418323df1abe3d188cf78eeff3c0cbe013a7e38f7b7e902"    # Task 5
IMPORTED_SHA256_2L = {   # Task 5: pinned from tests/import_scan_2l.py (4 modules)
    bg.REPO / "experiments/exp2l/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    bg.REPO / "experiments/exp2l/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    bg.REPO / "experiments/exp2l/run/preflight_2l.py":
        "bf86069805a6e0e1e50503a26f4a38a4eacc7a32bdd4cd886688cb95a036cde5",
    bg.REPO / "experiments/exp2l/verify_referents_2l.py":     # re-pinned at the freeze (F-3)
        "3273ff897aeb238f7d8cd3515c46ecb12d3963624f73cd562577cab2ec0b014d",
}
WORLDS = an2i.WORLDS
ALPHA, T_BAR, N_PERM, N_BOOT = st.ALPHA, st.T_BAR, st.N_PERM, st.N_BOOT
collect_total = an2i.collect_total
_run_test = an2i._run_test

# design §2 (what is known / what is sealed), condensed to the facts
KNOWN_INPUTS_CAVEAT_2L = (
    "Known to the designer before any OLMo-2 13B weight was loaded: everything through 2k's "
    "close-out — the three sealed forecasts on Pythia and OLMo-2 7B, 2i's LINEAGE verdict "
    "(A .0949, B .2153), 2j's mechanism reading, 2k's DENSITY result with its full texture on "
    "7B's KNOWN outcome (T .1548; per-rung D; the four 64-draw blocks .0949/.1077/.0948/.0938; "
    "the ladder .0949/.1256/.1433/.1548; the matched lineage increment +.054; 410m .1695); the "
    "Hub inventory of OLMo-2 13B's branches (metadata only, 2026-08-30). The predictors "
    "x_A^(64/128/192/256) at 1b and 410m and x_B^(64) are historically prior and tag-bound; "
    "nothing is sampled in 2l. Not known to anyone in this program: any output of OLMo-2 13B on "
    "any item. The predictors were committed before the outcome model was named; the design is "
    "2i's with the outcome swapped and the cross-family predictor at 256 draws; the instrument "
    "is tagged before any 13B weight loads, the endpoint stage sealed before the sweep, the "
    "projection sealed before gate 1 (design §2, §7).")

_L = {
    "SHARED": ("the essay's cross-family sentence is licensed as a forecast — \"a smaller model "
               "of a different family, given enough draws, forecasts what training surfaces "
               "first\" — with 2k's density reading confirmed on a sealed outcome; Prediction 2's "
               "output-channel form is no longer \"a lineage instrument\"; the \"structure latent "
               "in the training distribution\" reading gains a cross-family leg at item grain on "
               "a hidden outcome; the named next experiment is a third family"),
    "LINEAGE": ("2k's DENSITY reading is demoted to \"on a known outcome\": the essay says the "
                "256-draw predictor cleared the bar on 7B's already-known order and did not "
                "forecast 13B's; the lineage sentence stands; the cross-family sentence stays "
                "unlicensed; next is the mechanism question on what 7B's order and 13B's share"),
    "BOTH": ("both components with their partials (T_A, T_B, within-alone, cross-beyond-within, "
             "the matched increment); the shared component is the headline only if T_A's CI "
             "excludes zero on the majority of R_PRIMARY"),
    "NEITHER": ("the two-family, four-outcome finding is bounded at 13B in the essay and "
                "experiments.md; the full 13B record reported; the program's next step is "
                "Michael's call"),
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}
LICENSED_2L = {k: f"{v}. Disclosure (design §2): {KNOWN_INPUTS_CAVEAT_2L}" for k, v in _L.items()}
DISCLOSURE_THIN_2L = ("fewer than three rungs carried the primary (R_PRIMARY = R_13B ∩ 2k's nine) "
                      "— the reading is THIN regardless of the power record's declaration")
# FREEZE F-4: §4's "fewer than three rungs → THIN" was keyed to the SIZE
# OF R_PRIMARY, not to the rungs a test actually read. `cells_for` drops
# a rung whose outcome has fewer than `ELIGIBILITY_MIN_POS` positive
# items, and `_run_test` drops a rung whose predictor is degenerate
# inside every stratum — so a test can run on one or two rungs, fire, and
# be licensed with no THIN caveat anywhere in the reason or the licence.
# Reachable: four of 2k's nine clear 2d's bar at 9–19 correct items
# (add3_mid 9, sub4_mid 9, sub3_mid 15, arith_next 19) and the count
# outcome's n_pos is bounded below by the endpoint count, not above 20,
# so a tree with R_PRIMARY = 3–4 mid-digit rungs plus one dense rung
# leaves the test one eligible rung with |R_PRIMARY| ≥ 3. Additive: a
# disclosure per test, never a change to `fires`.
DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L = "fewer than three rungs actually carried Test "


def _thin_eligible_2l(test: str, res: dict) -> str | None:
    elig = list((res or {}).get("eligible") or [])
    if len(elig) >= 3:
        return None
    return (f"{DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L}{test}: it read {len(elig)} rung(s) {elig} — "
            f"dropped as n_pos-thin {list((res or {}).get('thin') or [])}, as predictor-degenerate "
            f"{list((res or {}).get('dropped_degenerate') or [])}; the reading is THIN regardless "
            f"of the power record's declaration, which simulates over R_PRIMARY minus the "
            f"degenerate rungs only")
DISCLOSURE_UNDERPOWERED_2L = {
    "A": ("Test A did not fire under DECLARED UNDERPOWERED IN ADVANCE: the cross-family "
          "transfer is not detected at this resolution, neither confirmed nor ruled out"),
    "B": ("Test B did not fire under DECLARED UNDERPOWERED IN ADVANCE: the within-family "
          "increment is not detected at this resolution, neither confirmed nor ruled out"),
}


# ------------------------------------------------------------ pins

_EXPERIMENTS_ROOT_2L = str((bg.REPO / "experiments").resolve())


def check_imports_2l() -> None:
    """2j F-1 from commit one: every module under `experiments/` this
    process has imported must be covered by FROZEN_FILES_2L (its pinned
    dict must equal the documented tuple once pinned), 2g's
    FROZEN_IMPORT_SHA256_2G, the four tag-bound INSTRUMENT_BLOBS_2L, 2k's
    and 2j's own residual import pins (verified against disk here), or
    IMPORTED_SHA256_2L. Files under a `tests/` directory are excluded
    (disclosed, 2j's rule)."""
    if IMPORTED_SHA256_2L is None:
        raise RuntimeError("IMPORTED_SHA256_2L is None — the import surface is not pinned "
                           "(build incomplete)")
    if bl.FROZEN_SHA256_2L:
        pinned_frozen = {str(Path(p).resolve()) for p in bl.FROZEN_SHA256_2L}
        documented = {str(Path(p).resolve()) for p in bl.FROZEN_FILES_2L}
        if pinned_frozen != documented:
            raise RuntimeError(f"FROZEN_SHA256_2L does not cover FROZEN_FILES_2L: missing "
                               f"{sorted(documented - pinned_frozen)}; extra "
                               f"{sorted(pinned_frozen - documented)}")
    covered = {str(Path(p).resolve()) for p in bl.FROZEN_FILES_2L}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bl.INSTRUMENT_BLOBS_2L}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_2L.items()}
    upstream = {str(Path(p).resolve()): v for p, v in an2j.IMPORTED_SHA256_2J.items()}
    upstream.update({str(Path(p).resolve()): v for p, v in an2k.IMPORTED_SHA256_2K.items()})
    unpinned, drifted = [], []
    for p, want in sorted({**upstream, **pinned}.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(_EXPERIMENTS_ROOT_2L + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned or s in upstream:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


# ---------------------------------------------------- record failures

def _record_common_failures_2l(rec: dict, *, label, cap, verify_fn, seal_tag) -> list:
    """2i's `_record_common_failures` with 2l's size/family and the
    composite predictor sha (2i's hard-codes `olmo7b`)."""
    bad = []
    for k, v in (("size", bl.SIZE_OUT), ("family", bl.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("predictor_sha") != bl.PREDICTOR_SHA_2L:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bl.PREDICTOR_SHA_2L}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bt.N_ITEMS or len(conts) != bt.N_ITEMS:
        bad.append(f"{label}: bits/continuations are not {bt.N_ITEMS} long")
        return bad
    if rec.get("correct") != sum(bits):
        bad.append(f"{label}: correct {rec.get('correct')} != sum(bits) {sum(bits)}")
    bad += an2i._re_verify(conts, bits, cap, verify_fn, label)
    return bad


def endpoint_record_failures_2l(rec: dict, *, which, rung, cap, entry, verify_fn) -> list:
    label = f"endpoint olmo13b {which}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    if rec.get("which") != which:
        bad.append(f"{label}: which = {rec.get('which')!r}, expected {which!r}")
    if rec.get("commit") != entry.get("commit"):
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's "
                   f"{entry.get('commit')}")
    bad += _record_common_failures_2l(rec, label=label, cap=cap, verify_fn=verify_fn,
                                      seal_tag=bl.PREDICTOR_TAGS_2L)
    return bad


def step_record_failures_2l(rec: dict, *, step, rung, cap, entry, verify_fn, endpoint_sha) -> list:
    label = f"olmo13b/step{int(step)}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    if rec.get("step") != int(step):
        bad.append(f"{label}: step = {rec.get('step')!r}, expected {int(step)!r}")
    if rec.get("commit") != entry["commit"]:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")
    if rec.get("endpoint_sha256") != endpoint_sha:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")
    bad += _record_common_failures_2l(rec, label=label, cap=cap, verify_fn=verify_fn,
                                      seal_tag=bl.ENDPOINT_SEAL_TAG_2L)
    return bad


def load_endpoint_which_2l(root, which, battery, verify_fn, *, entry) -> dict:
    out = {}
    for rung in bt.RUNGS:
        p = bl.endpoint_record_path(root, which, rung)
        if not p.is_file():
            raise FileNotFoundError(f"endpoint record missing: {p}")
        rec = json.loads(p.read_text())
        bad = endpoint_record_failures_2l(rec, which=which, rung=rung, cap=battery[rung],
                                          entry=entry, verify_fn=verify_fn)
        if bad:
            raise ValueError("; ".join(bad))
        out[rung] = rec
    return out


def checkpoint_record_failures_2l(crec: dict, *, step, entry: dict, step_records: dict) -> list:
    """FREEZE F-2 (2i F-1's shape one record type over, with 3d F-2's
    coverage rule): the sweep's checkpoint record was read for its 12 LFS
    shard shas and otherwise ATTESTED — its revision, its commit, and the
    tensor digest of the weights that produced the step's 34 item records
    were never measured, and the sha table was checked over the 12 shards
    only, i.e. a coverage claim over an unstated subset of the 13
    candidate files the loader actually stages. Measured here.

    Disclosed rather than closed: the 13th candidate file
    (`model.safetensors.index.json`, which decides which tensor comes out
    of which shard) carries no LFS sha in the Hub metadata, so it has no
    content pin in the manifest — it is pinned by the revision commit
    alone. Requiring the record to attest a sha for it is a coverage
    claim; comparing that sha to a manifest entry is not available."""
    bad = []
    for k in ("revision", "commit"):
        if crec.get(k) != entry.get(k):
            bad.append(f"olmo13b/step{int(step)}: checkpoint record {k} {crec.get(k)!r} is not "
                       f"the manifest's {entry.get(k)!r}")
    shas = crec.get("sha256")
    if not isinstance(shas, dict):
        bad.append(f"olmo13b/step{int(step)}: checkpoint record sha256 is not a table")
    else:
        uncovered = sorted(set(entry.get("files", [])) - set(shas))
        if uncovered:
            bad.append(f"olmo13b/step{int(step)}: the checkpoint record attests no sha for "
                       f"{uncovered} — a sha table over a subset of the candidate files is a "
                       f"coverage claim about an unstated set")
    dg = crec.get("digest")
    off = sorted(r for r, rec in step_records.items() if rec.get("weight_sha256") != dg)
    if off:
        bad.append(f"olmo13b/step{int(step)}: the checkpoint record's tensor digest {dg!r} is not "
                   f"the digest the item records carry on {off}")
    return bad


def load_sweep_13b(root, battery, verify_fn, *, manifest, endpoint_sha, steps=None,
                   rungs=None) -> dict:
    """Every grid step + the real step 0: 34 records each through
    `step_record_failures_2l`, plus the checkpoint record's LFS shas
    against the manifest and empty loading info."""
    steps = tuple(steps) if steps is not None else bl.GRID_13B + (bl.STEP0,)
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for step in steps:
        entry = bl.entry_13b(manifest, step)
        out[step] = {}
        for rung in rungs:
            p = bl.record_path(root, step, rung)
            if not p.is_file():
                raise FileNotFoundError(f"sweep record missing: {p}")
            rec = json.loads(p.read_text())
            bad = step_record_failures_2l(rec, step=step, rung=rung, cap=battery[rung], entry=entry,
                                          verify_fn=verify_fn, endpoint_sha=endpoint_sha)
            if bad:
                raise ValueError("; ".join(bad))
            out[step][rung] = rec
        cp = bl.checkpoint_record_path(root, step)
        if not cp.is_file():
            raise FileNotFoundError(f"checkpoint record missing: {cp}")
        crec = json.loads(cp.read_text())
        for name, want in entry.get("lfs_sha256", {}).items():
            if crec.get("sha256", {}).get(name) != want:
                raise ValueError(f"olmo13b/step{step}: downloaded {name} sha "
                                 f"{crec.get('sha256', {}).get(name)} != manifest {want}")
        if crec.get("loading_info", {}) != {"missing_keys": 0, "unexpected_keys": 0,
                                             "mismatched_keys": 0}:
            raise ValueError(f"olmo13b/step{step}: loading info not empty")
        if crec.get("size") != bl.SIZE_OUT or crec.get("step") != int(step):
            raise ValueError(f"olmo13b/step{step}: checkpoint record size/step "
                             f"{crec.get('size')!r}/{crec.get('step')!r}")
        cbad = checkpoint_record_failures_2l(crec, step=step, entry=entry, step_records=out[step])
        if cbad:
            raise ValueError("; ".join(cbad))
    return out


# ------------------------------------------------------------ outcomes

def outcomes_13b(sweep: dict, *, rungs=None) -> dict:
    """`analyze_2i.outcomes_7b`'s body over `trained_steps_13b()` (16
    points). Step 0 is never in an outcome: `steps` excludes it even
    though `sweep` carries it."""
    steps = bl.trained_steps_13b()
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for rung in rungs:
        bits = {s: [int(b) for b in sweep[s][rung]["bits"]] for s in steps}
        y, first, last, stab = [], [], [], []
        for i in range(bt.N_ITEMS):
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
                     "counts_by_step": {int(s): int(sweep[s][rung]["correct"]) for s in steps}}
    return out


def rung_level_13b(out: dict, floors: dict, *, rungs=None) -> dict:
    steps = bl.trained_steps_13b()
    rungs = tuple(rungs) if rungs is not None else tuple(out)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in steps if st2d.binomial_bar(c[s], bt.N_ITEMS, floors[rung])["significant"]]
        final = bl.ENDPOINT_STEP_13B in clears
        res[rung] = {"s_star": clears[0] if clears else None, "clears": clears,
                     "final_clears": final, "transient_clears": ([] if final else clears)}
    return res


def _first_correct_outcome_13b(out: dict, rungs) -> dict:
    last_step = max(bl.trained_steps_13b())
    return {r: {"y": [0 if fc is None else (last_step + 1 - fc) for fc in out[r]["first"]],
                "n_pos": out[r]["n_pos"]} for r in rungs}


def collapses_13b(sweep: dict, *, rungs, threshold: int = 450) -> list:
    """2h's checkpoint-local pathology (count_div13 at step40000 emitting
    ' 13' on all 500): a (rung, step) where ≥ `threshold` of the 500
    continuations are one identical string. Descriptive; `correct` at
    that step printed beside it. Steps in the sweep dict, step 0 included."""
    from collections import Counter
    res = []
    for step in sorted(sweep):
        for r in rungs:
            rec = sweep[step][r]
            top, n = Counter(rec["continuations"]).most_common(1)[0]
            if n >= threshold:
                res.append({"rung": r, "step": int(step), "continuation": top,
                            "n_identical": int(n), "correct": int(rec["correct"])})
    return res


def non_monotone_13b(out: dict, rungs) -> dict:
    """Per rung: every consecutive-grid-point drop in the rung-level
    count larger than 20 % of the rung's maximum."""
    res = {}
    for r in rungs:
        c = out[r]["counts_by_step"]
        steps = sorted(c)
        mx = max(c.values()) if c else 0
        drops = [[int(a), int(b), int(c[a]), int(c[b])] for a, b in zip(steps, steps[1:])
                 if c[a] - c[b] > 0.2 * mx]
        res[r] = {"drops": drops, "n_drops": len(drops), "max": int(mx)}
    return res


# ------------------------------------------------------------ rung set

def _load_rung_set_2l(root) -> dict:
    p = bl.rung_set_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    for k in ("R_13B", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA", "per_rung", "primary_is_the_nine",
              "endpoint_file_sha256"):
        if k not in rec:
            raise ValueError(f"{p}: missing {k!r}")
    if not set(rec["R_PRIMARY"]).issubset(set(bl.R_CAP_2K)):
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")
    if set(rec["R_PRIMARY"]) | set(rec["R_ELEVEN_EXTRA"]) | set(rec["R_EXTRA"]) != set(rec["R_13B"]):
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_13B")
    return rec


def _check_rung_set_vs_endpoint_2l(rung_set: dict, stage1_final: dict) -> list:
    bad = []
    per_rung = rung_set.get("per_rung", {})
    if not isinstance(per_rung, dict):
        return [f"rung set olmo13b: per_rung is {type(per_rung).__name__}, not a mapping"]
    absent = sorted(r for r in bt.RUNGS if r not in per_rung)
    if absent:
        bad.append(f"rung set olmo13b: per_rung carries no entry for {absent}")
    for r in bt.RUNGS:
        if r not in stage1_final or r not in per_rung:
            continue
        if per_rung[r].get("k") != stage1_final[r]["correct"]:
            bad.append(f"rung set olmo13b/{r}: per_rung k={per_rung[r].get('k')!r} disagrees with "
                       f"the endpoint's stage1_final correct={stage1_final[r]['correct']!r}")
    return bad


def _check_rung_set_derivation_2l(rung_set: dict, stage1_final: dict, floors: dict) -> list:
    bad = []
    counts = {r: stage1_final[r]["correct"] for r in bt.RUNGS if r in stage1_final}
    if len(counts) != len(bt.RUNGS):
        return [f"rung set re-derivation olmo13b: stage1_final missing rung(s) "
                f"{sorted(set(bt.RUNGS) - set(counts))}"]
    red = bl.rung_set_from_counts_2l(counts, floors)
    for key in ("R_13B", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA"):
        want, got = list(rung_set.get(key, [])), list(red[key])
        if got != want:
            bad.append(f"rung set re-derivation olmo13b/{key}: re-derived {got} disagrees with "
                       f"the file's {want}")
    if bool(rung_set.get("primary_is_the_nine")) != bool(red["primary_is_the_nine"]):
        bad.append("rung set re-derivation olmo13b/primary_is_the_nine disagrees")
    return bad


def _check_rung_set_endpoint_shas_2l(rung_set: dict, root) -> list:
    """FREEZE F-3 (2i F-1 / 2j F-2's lineage): `rung_set_2l.json` carries
    an `endpoint_file_sha256` table the endpoint runner writes over the 68
    endpoint records. `_load_rung_set_2l` REQUIRED the key to be present
    and the verdict PUBLISHES it inside `referents["rung_set"]` — and
    nothing ever compared it to anything. An attestation that could be
    measured is measured here: exactly the 68 endpoint records, each at
    its committed sha."""
    root = Path(root)
    got = rung_set.get("endpoint_file_sha256")
    if not isinstance(got, dict):
        return [f"rung set olmo13b: endpoint_file_sha256 is {type(got).__name__}, not a table "
                f"over the {len(bl.ENDPOINT_WHICH) * len(bt.RUNGS)} endpoint records"]
    want = {}
    for which in bl.ENDPOINT_WHICH:
        for r in bt.RUNGS:
            p = bl.endpoint_record_path(root, which, r)
            if not p.is_file():
                return [f"rung set olmo13b: endpoint record {p} is missing, so "
                        f"endpoint_file_sha256 cannot be measured"]
            want[str(p.relative_to(root))] = bg.sha256_file(p)
    bad = []
    missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
    if missing:
        bad.append(f"rung set olmo13b: endpoint_file_sha256 attests nothing for {missing}")
    if extra:
        bad.append(f"rung set olmo13b: endpoint_file_sha256 carries {extra}, which are not the "
                   f"endpoint records")
    for rel in sorted(set(want) & set(got)):
        if got[rel] != want[rel]:
            bad.append(f"rung set olmo13b: endpoint_file_sha256[{rel}] {str(got[rel])[:12]} is "
                       f"not the committed record's {want[rel][:12]}")
    return bad


def _endpoint_seal_paths_2l(root) -> list:
    paths = [bl.rung_set_path(root), bl.power_path(root)]
    for which in bl.ENDPOINT_WHICH:
        for r in bt.RUNGS:
            paths.append(bl.endpoint_record_path(root, which, r))
    return paths


# --------------------------------------------------------------- power

POWER_CLAIM_FIELDS_2L = ("dropped_degenerate", "rungs_simulated", "n_pos_lower_bound", "t_bar",
                         "alpha", "thin")
BLOCK_SD_FIELDS_2L = ("n_sim", "mean_block_sd_at_declare", "mean_block_sd_null",
                      "per_block_mean_T_at_declare", "blocks")


def load_power_2l(root, r_primary, predictor_sha) -> dict:
    p = bl.power_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    if not isinstance(rec, dict):
        raise ValueError(f"{p}: not a 2l power record")
    for test in ("A", "B"):
        sub = rec.get(test)
        if not isinstance(sub, dict) or "declared_status" not in sub or "declaration" not in sub:
            raise ValueError(f"{p}: test {test!r} missing declared_status/declaration")
        if sub["declared_status"] not in an2i.DECLARED_STATUSES_2I:
            raise ValueError(f"{p}: test {test!r} declared_status {sub['declared_status']!r}")
        if not isinstance(sub.get("rungs"), list) or set(sub["rungs"]) != set(r_primary):
            raise ValueError(f"{p}: test {test!r} rungs {sub.get('rungs')} != R_PRIMARY "
                             f"{sorted(r_primary)}")
        if sub.get("n_trained_steps") != bl.n_trained_13b():
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bl.n_trained_13b()}")
    if rec.get("predictor_sha256") != predictor_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")
    bsd = rec.get("block_sd_A")
    if not isinstance(bsd, dict) or any(k not in bsd for k in BLOCK_SD_FIELDS_2L):
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — "
                         f"{BLOCK_SD_FIELDS_2L}")
    # FREEZE F-5 (2i F-1 / 2k F-2, on the record's own top level): the
    # power record's `r_primary` and `primary_is_the_nine`, and the shape
    # of the block-SD block the PROJECTION places its verdict call
    # against (dial f), were attested and compared to nothing.
    if sorted(rec.get("r_primary") or []) != sorted(r_primary):
        raise ValueError(f"{p}: r_primary {rec.get('r_primary')!r} is not the rung set's "
                         f"R_PRIMARY {sorted(r_primary)}")
    if bool(rec.get("primary_is_the_nine")) != (tuple(sorted(r_primary)) == tuple(sorted(bl.R_CAP_2K))):
        raise ValueError(f"{p}: primary_is_the_nine {rec.get('primary_is_the_nine')!r} against "
                         f"R_PRIMARY {sorted(r_primary)}")
    n_blocks = len(bk.SEEDS_2K)
    if bsd.get("blocks") != n_blocks:
        raise ValueError(f"{p}: block_sd_A blocks {bsd.get('blocks')!r} is not the predictor's "
                         f"{n_blocks} 64-draw blocks")
    pb = bsd.get("per_block_mean_T_at_declare")
    if not isinstance(pb, list) or len(pb) != n_blocks:
        raise ValueError(f"{p}: block_sd_A per_block_mean_T_at_declare is not {n_blocks} long")
    if bsd.get("n_sim") and "rungs" not in bsd:
        raise ValueError(f"{p}: block_sd_A simulated {bsd.get('n_sim')!r} time(s) and attests no "
                         f"rung set — the SD is over an unstated set of rungs")
    return rec


def check_power_claims_2l(power, x_a256, x_b, strata, r_primary, stage1_final) -> list:
    """2k F-2: every re-derivable claim of both tests' power blocks
    against the analyzer's own re-derivation on the same predictors and
    strata the tests just ran on."""
    bad = []
    strata_b = an2i._composite_strata_median(strata, x_a256, r_primary)
    for test, x, s in (("A", x_a256, strata), ("B", x_b, strata_b)):
        prim = (power or {}).get(test)
        if not isinstance(prim, dict):
            bad.append(f"2l power claims {test}: no block")
            continue
        missing = [k for k in POWER_CLAIM_FIELDS_2L if k not in prim]
        if missing:
            bad.append(f"2l power claims {test}: the record does not attest {missing}")
        dropped = list(an2i._degenerate_rungs(x, s, r_primary))
        keep = [r for r in r_primary if r not in dropped]
        if "dropped_degenerate" in prim and sorted(prim["dropped_degenerate"] or []) != sorted(dropped):
            bad.append(f"2l power claims {test}: dropped_degenerate "
                       f"{sorted(prim['dropped_degenerate'] or [])} != {sorted(dropped)}")
        if "rungs_simulated" in prim and sorted(prim["rungs_simulated"] or []) != sorted(keep):
            bad.append(f"2l power claims {test}: rungs_simulated "
                       f"{sorted(prim['rungs_simulated'] or [])} != {sorted(keep)}")
        if "n_pos_lower_bound" in prim:
            want = ({r: int(stage1_final[r]["correct"]) for r in r_primary} if stage1_final else None)
            got = prim["n_pos_lower_bound"]
            if want is None:
                bad.append(f"2l power claims {test}: n_pos_lower_bound cannot be re-derived")
            elif not isinstance(got, dict) or {k: int(v) for k, v in got.items()} != want:
                bad.append(f"2l power claims {test}: n_pos_lower_bound {got!r} != the endpoint's "
                           f"{want!r}")
        for field, want in (("t_bar", T_BAR), ("alpha", ALPHA)):
            if field in prim and prim[field] != want:
                bad.append(f"2l power claims {test}: {field} = {prim[field]!r}, not {want!r}")
        if "thin" in prim and bool(prim["thin"]) != (len(keep) < 3):
            bad.append(f"2l power claims {test}: thin = {prim['thin']!r} against {len(keep)} rung(s)")
        if test == "A":                                            # freeze F-5
            bsd = (power or {}).get("block_sd_A")
            if isinstance(bsd, dict) and "rungs" in bsd and sorted(bsd["rungs"] or []) != sorted(keep):
                bad.append(f"2l power claims block_sd_A: rungs {sorted(bsd['rungs'] or [])} is not "
                           f"Test A's non-degenerate set {sorted(keep)}")
    return bad


# -------------------------------------------------------------- predictors

def load_predictors_2l(root_2i, root_2k, *, battery, verify_fn, tag_exists=None,
                       blobs_bound=None) -> tuple:
    """Both predictors through their own sealed readers; every seal
    bound; every sha measured. Returns (failures, ctx) with ctx =
    {seal_2k, seal_2i, predictor_sha, cells_2k{size: cells}, x_b,
    bits_b, rows_2i, r_cap_2i, psl_2k, psl_2i}."""
    failures, ctx = [], {}
    root_2i, root_2k = Path(root_2i), Path(root_2k)
    for m in bk.halt_markers(root_2k):
        failures.append(f"2l predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")
    seal_2k, f = collect_total(lambda: json.loads(bk.seal_path(root_2k).read_text()),
                               "2l predictor 2k seal read");                       failures += f
    psl_2k = an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(root_2k, seal_2k),
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2l predictor 2k seal binding: {m}" for m in psl_2k["failures"]]
    seal_2i, f = collect_total(lambda: an2i._load_predictor_seal_content(root_2i),
                               "2l predictor 2i seal content");                    failures += f
    psl_2i = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(root_2i, seal_2i),
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2l predictor 2i seal binding: {m}" for m in psl_2i["failures"]]
    if isinstance(seal_2k, dict) and seal_2k.get("sha256") != bl.SEAL_2K_SHA256:
        failures.append(f"2l predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")
    if isinstance(seal_2i, dict) and seal_2i.get("sha256") != bl.SEAL_2I_SHA256:
        failures.append(f"2l predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")
    predictor_sha = bl.PREDICTOR_SHA_2L
    if isinstance(seal_2k, dict) and isinstance(seal_2i, dict):
        got = bl.predictor_sha_2l(str(seal_2k.get("sha256")), str(seal_2i.get("sha256")))
        if got != bl.PREDICTOR_SHA_2L:
            failures.append("2l predictor composite sha does not re-derive from the two seals")
    # ---- x_A^(256): 2k's tier at both sizes, re-derived + seal cross-check
    cells_2k = {}
    if battery is not None and verify_fn is not None:
        for size in bk.SIZES_2K:
            def _tier(size=size):
                return an2k.load_tier_2k(root_2k, size, battery=battery, verify_fn=verify_fn,
                                         rungs=bl.R_CAP_2K)
            res, f = collect_total(_tier, f"2l predictor 2k tier {size} load");   failures += f
            f2, c = res if res is not None else ([], {})
            failures += [f"2l predictor {m}" for m in f2]
            cells_2k[size] = c
        if seal_2k is not None and all(len(cells_2k.get(s, {})) == len(bl.R_CAP_2K) for s in bk.SIZES_2K):
            sb, f = collect_total(lambda: an2k.seal_failures_2k(seal_2k, cells_2k, root_2k),
                                  "2l predictor 2k seal vs re-derivation")
            failures += f + [f"2l predictor {m}" for m in (sb or [])]
    else:
        failures.append("2l predictor 2k tier: not loaded (battery or verify missing)")
    # ---- 2k's rung set record must say the nine (2k's own check, repeated)
    rs2i, f = collect_total(lambda: an2i._load_rung_set(root_2i), "2l predictor 2i rung set file")
    failures += f
    if rs2i is not None and tuple(sorted(rs2i["R_CAP"])) != tuple(sorted(bl.R_CAP_2K)):
        failures.append(f"2l predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")
    # ---- x_B: 2i's provenance, counts, attestation
    manifest_2i, f = collect_total(
        lambda: bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256),
        "2l predictor 2i manifest");                                               failures += f
    entry_1b = None
    if manifest_2i is not None:
        entry_1b, f = collect_total(lambda: bi.entry_1b_endpoint(manifest_2i),
                                    "2l predictor 2i 1B endpoint entry");          failures += f
    _prec = battery is not None and entry_1b is not None
    records_2i, f = collect_total(
        lambda: an2i.load_predictor_records_2i(root_2i, battery, entry_1b=entry_1b) if _prec
        else (_ for _ in ()).throw(ValueError("battery or 1B entry missing")),
        "2l predictor 2i olmo1b records");                                         failures += f
    if seal_2i is not None and records_2i is not None:
        sb, f = collect_total(lambda: an2i._check_predictor_seal_sampling(seal_2i, records_2i),
                              "2l predictor 2i seal sampling block")
        failures += f + [f"2l predictor {m}" for m in (sb or [])]
    _xb = battery is not None and verify_fn is not None
    x_b, f = collect_total(lambda: bi.sampler_counts_olmo(bl.R_CAP_2K, root=root_2i, battery=battery,
                                                          verify_fn=verify_fn) if _xb
                           else (_ for _ in ()).throw(ValueError("battery/verify missing")),
                           "2l predictor x_B counts olmo1b");                     failures += f
    if seal_2i is not None and records_2i is not None and x_b is not None:
        cb, f = collect_total(lambda: an2i._check_predictor_counts_2i(seal_2i, records_2i, x_b),
                              "2l predictor x_B counts vs the sealed attestation")
        failures += f + [f"2l predictor {m}" for m in (cb or [])]

    def _rows_bits():
        rows, bits = {}, {}
        for r in bl.R_CAP_2K:
            rows[r] = fn.draw_rows_2i(root_2i, r)
            bits[r] = fn.verified_bits(rows[r], battery[r], verify_fn)
            if fn.counts_from_bits(bits[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")
        return rows, bits
    rb, f = collect_total(lambda: _rows_bits() if (_xb and x_b) else
                          (_ for _ in ()).throw(ValueError("x_B missing")), "2l predictor x_B rows and bits")
    failures += f
    rows_2i, bits_b = rb if rb is not None else (None, None)
    ctx.update(seal_2k=seal_2k, seal_2i=seal_2i, predictor_sha=predictor_sha, cells_2k=cells_2k,
               x_b=x_b, bits_b=bits_b, rows_2i=rows_2i, r_cap_2i=rs2i, psl_2k=psl_2k, psl_2i=psl_2i)
    return failures, ctx


# ------------------------------------------------------------ secondaries

def s4_matched_2l(bits_b, x_a64, x_a256, out, strata, rungs) -> dict:
    """S4 (design §5): x_B thinned per rung to k_g = clip(round(256·r̄_A/
    r̄_B), 1, 64) (2k's rule) against x_A^(256) on the sealed outcome,
    T without permutation (2j's `t_only`); the increment = thinned-B T −
    T_A256 (2k: +.054 on 7B)."""
    per, means = {}, []
    for r in rungs:
        ra = bk.mean_rate(x_a64[r], bk.DRAWS_PER_SEED)
        rb = bk.mean_rate(fn.counts_from_bits(bits_b[r]), bk.DRAWS_PER_SEED)
        m = bk.matched_k_256(ra, rb)
        reading = an2j._block_reading(r, bits_b[r], m["k"], m["n_blocks"], bi.SIZE_PRED, out, strata)
        per[r] = {**m, "rate_A64": ra, "rate_B64": rb, **reading}
        if reading["mean"] is not None:
            means.append(reading["mean"])
    t_a = an2j.t_only(x_a256, "1b:k256", out, strata, rungs)
    t_b = float(np.mean(means)) if means else None
    return {"per_rung": per, "thinned_B": {"T": t_b}, "T_A256": t_a["T"],
            "increment": (None if t_b is None or t_a["T"] is None else t_b - t_a["T"])}


def s5_answer_prior_2l(rows_2i, battery, out, strata, rungs, **kw) -> dict:
    """S5 (design §5, dial g — non-gating): 2j's wrong-target propensity
    π on 2i's sealed OLMo-2 1B draws, against 13B's sealed order with
    2i's statistic on the base strata. 2j found .199 on 7B's KNOWN
    outcome; this is its first reading on an outcome it could not have
    been fitted to."""
    pi = {r: fn.wrong_target_propensity(rows_2i[r], battery[r]) for r in rungs}
    return {"pi": pi, "test": _run_test(pi, "olmo1b:pi", out, strata, rungs, **kw),
            "non_gating": True,
            "source": "2j wrong_target_propensity on 2i's sealed OLMo-2 1B draws"}


def _extra_rungs_2l(x_a64, x_b, out, strata, *, r_eleven_extra, r_extra) -> dict:
    """Rungs clearing the bar at 13B that carry no 256-draw predictor:
    the rest of the eleven get x_A^(64)/x_B stratified D (2g's strata);
    the rest of R_13B get raw single-stratum D. Printed, never gating."""
    eleven, extra = {}, {}
    for r in r_eleven_extra:
        y, s = out[r]["y"], strata[r]["strata"]
        eleven[r] = {"stratified_d_A64": st.somers_d_within(x_a64[r], y, s)["d"],
                     "stratified_d_B": st.somers_d_within(x_b[r], y, s)["d"], "n_pos": out[r]["n_pos"]}
    for r in r_extra:
        y = out[r]["y"]
        s = ["0"] * len(y)
        extra[r] = {"raw_d_A64": st.somers_d_within(x_a64[r], y, s)["d"],
                    "raw_d_B": st.somers_d_within(x_b[r], y, s)["d"], "n_pos": out[r]["n_pos"]}
    return {"eleven_extra": eleven, "extra": extra}


# ----------------------------------------------------------------- tree

def verdict_2l(failures, A, B, power, r_primary) -> dict:
    tree = an2i.verdict_tree_2i(failures, A, B)
    if failures:
        return tree
    disclosures = list(tree.get("disclosures", []))
    if len(r_primary) < 3:
        disclosures.append(DISCLOSURE_THIN_2L)
    for test, res in (("A", A), ("B", B)):          # freeze F-4
        d = _thin_eligible_2l(test, res)
        if d:
            disclosures.append(d)
    for test, res in (("A", A), ("B", B)):
        status = (power or {}).get(test, {}).get("declared_status")
        if not res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":
            disclosures.append(DISCLOSURE_UNDERPOWERED_2L[test])
    reason = tree["reason"]
    extra = [d for d in disclosures if d not in tree.get("disclosures", [])]
    if extra:
        reason = "; ".join([reason] + extra)
    return {"verdict": tree["verdict"], "reason": reason, "disclosures": disclosures}


def _licensed_2l(tree) -> str:
    licensed = LICENSED_2L[tree["verdict"]]
    if tree.get("disclosures"):
        licensed = "; ".join([licensed] + list(tree["disclosures"]))
    return licensed


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


_LITERAL = object()


# ----------------------------------------------------------------- run

def run(root_2l=EXP2L, root_2i=bi.EXP2I, root_2k=bk.EXP2K, *, write=False, n_perm=N_PERM,
        n_boot=N_BOOT, tag_exists=None, blob_sha=None, blobs_bound=None, referents_sha=_LITERAL,
        imports_pinned=_LITERAL, out_path=None, frozen_check=None) -> dict:
    # `frozen_check` is a TEST-ONLY injection (2k's pattern) until Task 5
    # pins FROZEN_SHA256_2L; the campaign never passes it.
    failures = []
    root_2l, root_2i, root_2k = Path(root_2l), Path(root_2i), Path(root_2k)
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_2L_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if IMPORTED_SHA256_2L is None else True

    # ---- the halt scan FIRST (2d F-1): a halted tree never reaches a loader
    if bl.halt_marker_path(root_2l).exists():
        halted, f = collect_total(lambda: bl.halt_marker_path(root_2l).read_text().strip()[:200],
                                  "2l gate 1 olmo13b halt marker read")
        failures += f
        if not f:
            failures.append(f"2l gate 1 olmo13b: the runner halted ({halted})")
    # ---- pins, import surface (entry), prereg, manifest, referents
    _, f = collect_total(frozen_check or bl.check_frozen_2l, "2l frozen modules");   failures += f
    if imports_pinned:
        _, f = collect_total(check_imports_2l, "2l import surface (entry)");         failures += f
    elif imports_pinned is not False:
        failures.append("2l import surface: not pinned (build incomplete)")
    prereg, f = collect_total(lambda: bl.require_prereg_2l(tag_exists=tag_exists, blob_sha=blob_sha),
                              "2l prereg tag");                                       failures += f
    manifest, f = collect_total(
        lambda: bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256),
        "2l checkpoint manifest 13B");                                                failures += f
    if referents_sha is None:
        failures.append("2l referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        from experiments.exp2l import make_referents_2l as mkr
        mf, f = collect_total(lambda: mkr.check_referents(REFERENTS_PATH_2L, sha_pin=referents_sha),
                              "2l referent manifest");                                failures += f + (mf or [])
    # ---- upstream pins, battery, floors, verify, strata
    for thunk, label in ((bg.check_frozen_imports_2g, "2l upstream 2g frozen imports"),
                         (bi.check_frozen_2i, "2l upstream 2i frozen imports"),
                         (an2j.check_frozen_2j, "2l upstream 2j frozen imports"),
                         (bi.check_pythia_predictor_files, "2l upstream x_A committed 2d files")):
        _, f = collect_total(thunk, label); failures += f
    battery, f = collect_total(bg.load_battery, "2l battery items");                  failures += f
    floors, f = collect_total(bg.load_floors, "2l floors 2d");                         failures += f
    verify_fn, f = collect_total(a2d.load_verify, "2l verify criterion 3c");           failures += f
    pred2g, f = collect_total(
        lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA),
        "2l strata source 2g predictor");                                              failures += f
    strata = sg.from_json(pred2g["strata"]) if pred2g else None
    if strata is not None:
        _, f = collect_total(lambda: sg.check_strata_pins(strata), "2l strata pins 2g"); failures += f

    # ---- the predictors through their seals
    fp, pctx = load_predictors_2l(root_2i, root_2k, battery=battery, verify_fn=verify_fn,
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += fp
    cells_2k, x_b, bits_b, rows_2i = (pctx.get("cells_2k") or {}), pctx.get("x_b"), \
        pctx.get("bits_b"), pctx.get("rows_2i")

    # ---- the 13B endpoint stage, the rung set, the power record, the seal
    rung_set, f = collect_total(lambda: _load_rung_set_2l(root_2l), "2l rung set file"); failures += f
    r_primary = tuple(rung_set["R_PRIMARY"]) if rung_set else ()
    power, f = collect_total(lambda: load_power_2l(root_2l, r_primary, bl.PREDICTOR_SHA_2L)
                             if rung_set else (_ for _ in ()).throw(ValueError("rung set missing")),
                             "2l power record");                                       failures += f
    esl = an2i.require_seal_2i(bl.ENDPOINT_SEAL_TAG_2L, _endpoint_seal_paths_2l(root_2l),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2l endpoint seal binding: {m}" for m in esl["failures"]]
    entry_stage1 = entry_main = None
    if manifest is not None:
        entry_stage1, f = collect_total(lambda: bl.entry_13b(manifest, bl.ENDPOINT_STEP_13B),
                                        "2l 13B endpoint entry");                     failures += f
        entry_main, f = collect_total(lambda: bl.entry_main_13b(manifest), "2l 13B main entry")
        failures += f
    _ep = battery is not None and verify_fn is not None
    stage1_final, f = collect_total(
        lambda: load_endpoint_which_2l(root_2l, "stage1_final", battery, verify_fn, entry=entry_stage1)
        if _ep and entry_stage1 else (_ for _ in ()).throw(ValueError("battery/verify/entry missing")),
        "2l endpoint stage1_final");                                                   failures += f
    main_rec, f = collect_total(
        lambda: load_endpoint_which_2l(root_2l, "main", battery, verify_fn, entry=entry_main)
        if _ep and entry_main else (_ for _ in ()).throw(ValueError("battery/verify/entry missing")),
        "2l endpoint main");                                                           failures += f
    if rung_set is not None and stage1_final is not None:
        rb, f = collect_total(lambda: _check_rung_set_vs_endpoint_2l(rung_set, stage1_final),
                              "2l rung set vs endpoint");                              failures += f + (rb or [])
        if floors is not None:
            rb2, f = collect_total(lambda: _check_rung_set_derivation_2l(rung_set, stage1_final, floors),
                                   "2l rung set re-derivation");                      failures += f + (rb2 or [])
    if rung_set is not None:
        rb3, f = collect_total(lambda: _check_rung_set_endpoint_shas_2l(rung_set, root_2l),
                               "2l rung set endpoint shas");                          failures += f + (rb3 or [])
    endpoint_sha, f = collect_total(lambda: bl.endpoint_sha256(root_2l), "2l endpoint composite sha")
    failures += f

    # ---- gate 1 (attested), the sweep, gate 1 (re-derived from the bytes)
    g1p = bl.gate1_path(root_2l)
    gate1 = None
    if not g1p.is_file():
        failures.append(f"2l gate 1 olmo13b: record missing ({g1p})")
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()), "2l gate 1 olmo13b record")
        failures += f
        if gate1 is not None:
            gb, f = collect_total(lambda: bl.gate1_failures_13b(gate1, stage1_final) if stage1_final
                                  else (_ for _ in ()).throw(ValueError("stage1_final missing")),
                                  "2l gate 1 olmo13b attestation");                   failures += f + (gb or [])
    _sw = manifest is not None and _ep and endpoint_sha is not None
    sweep, f = collect_total(
        lambda: load_sweep_13b(root_2l, battery, verify_fn, manifest=manifest, endpoint_sha=endpoint_sha)
        if _sw else (_ for _ in ()).throw(ValueError("manifest/battery/verify/endpoint sha missing")),
        "2l sweep olmo13b");                                                           failures += f
    _g = sweep is not None and stage1_final is not None and gate1 is not None
    g2, f = collect_total(
        lambda: bl.gate1_rederive_13b(sweep[bl.ENDPOINT_STEP_13B], stage1_final, gate1) if _g
        else (_ for _ in ()).throw(ValueError("sweep, endpoint or gate 1 record missing")),
        "2l gate 1 olmo13b re-derivation (byte identity)");                           failures += f + (g2 or [])

    # ---- the gating core: outcomes, A, B — one unit
    core = None
    if not failures:
        def _core():
            out = outcomes_13b(sweep, rungs=tuple(bt.RUNGS))
            x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL] for r in r_primary}
            A = _run_test(x256, "1b:k256", out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)
            strata_b = an2i._composite_strata_median(strata, x256, r_primary)
            B = _run_test(x_b, bi.SIZE_PRED, out, strata_b, r_primary, n_perm=n_perm, n_boot=n_boot)
            return out, x256, A, B
        core, f = collect_total(_core, "2l primary olmo13b");                          failures += f
    if not failures and core is not None:
        pf, f = collect_total(lambda: check_power_claims_2l(power, core[1], x_b, strata, r_primary, stage1_final),
                              "2l power claims");                                      failures += f + (pf or [])
    if not failures and core is not None:
        _, f = collect_total(check_imports_2l if imports_pinned else (lambda: None),
                             "2l import surface (exit)");                              failures += f

    referents = {"failures": list(failures), "prereg": prereg, "manifest_sha256": bl.CHECKPOINTS_2L_SHA256,
                 "predictor_seal_2k": pctx.get("psl_2k"), "predictor_seal_2i": pctx.get("psl_2i"),
                 "predictor_sha": bl.PREDICTOR_SHA_2L, "endpoint_seal": esl,
                 "endpoint_sha256": endpoint_sha, "rung_set": rung_set,
                 "gate1": {k: v for k, v in (gate1 if isinstance(gate1, dict) else {}).items()
                           if k not in ("timing",)},
                 "gate1_2k": {s: {r: c["gate1_rederived"] for r, c in cells_2k.get(s, {}).items()}
                              for s in bk.SIZES_2K},
                 "pins_active": {"frozen_modules": frozen_check is None,
                                 "import_surface": bool(imports_pinned),
                                 "referent_manifest": referents_sha not in (False, None)},
                 "power": power}
    common = {"known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2L,
              "calibration_note": an2i.CALIBRATION_SENTENCE_2I, "n_perm": n_perm,
              "git_sha": _git_sha(), "model_contact": "none at analysis"}
    if failures:
        tree = verdict_2l(failures, None, None, None, ())
        v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
             "licensed_sentence": LICENSED_2L["INSUFFICIENT_DATA"], "referents": referents,
             "tests": None, "secondaries": None}
    else:
        out, x256, A, B = core
        tree = verdict_2l([], A, B, power, r_primary)
        kw = dict(n_perm=n_perm, n_boot=n_boot)
        bits1b = {r: cells_2k["1b"][r]["bits"] for r in r_primary}
        x64 = {r: cells_2k["1b"][r]["counts"][64] for r in r_primary}
        sec, sec_failures = {}, []

        def _sec(name, thunk):
            val, f = collect_total(thunk, name)
            if f:
                sec[name] = {"failed": f[0]}
                sec_failures.extend(f)
            else:
                sec[name] = val

        _sec("S1 ladder 1b", lambda: an2k.ladder_2k(bits1b, out, strata, r_primary, "1b", **kw))
        _sec("S1 blocks 1b", lambda: an2k.s1_blocks(bits1b, out, strata, r_primary, "1b", **kw))

        def _s2():
            b410 = {r: cells_2k["410m"][r]["bits"] for r in r_primary}
            x256_410 = {r: cells_2k["410m"][r]["counts"][bk.K_TOTAL] for r in r_primary}
            return {"primary_form": _run_test(x256_410, "410m:k256", out, strata, r_primary, **kw),
                    "ladder": an2k.ladder_2k(b410, out, strata, r_primary, "410m", **kw),
                    "blocks": an2k.s1_blocks(b410, out, strata, r_primary, "410m", **kw)}
        _sec("S2 410m at 256", _s2)
        _sec("S3 within alone", lambda: _run_test(x_b, bi.SIZE_PRED, out, strata, r_primary, **kw))
        _sec("S3 cross beyond within", lambda: _run_test(
            x256, "1b:k256", out, an2i._composite_strata_median(strata, x_b, r_primary), r_primary, **kw))
        _sec("S4 matched density", lambda: s4_matched_2l(bits_b, x64, x256, out, strata, r_primary))
        _sec("S5 answer prior", lambda: s5_answer_prior_2l(rows_2i, battery, out, strata, r_primary, **kw))
        _sec("S6 step0 and main", lambda: {
            "step0_counts": {r: int(sweep[bl.STEP0][r]["correct"]) for r in bt.RUNGS},
            "main_vs_endpoint": an2i._main_vs_endpoint_2i(stage1_final, main_rec)})

        def _s7():
            rl = rung_level_13b(out, floors, rungs=tuple(bt.RUNGS))
            first = _first_correct_outcome_13b(out, r_primary)
            return {"rung_level": {r: {**rl[r], "counts_by_step": out[r]["counts_by_step"],
                                       "ever": int(sum(1 for v in out[r]["y"] if v > 0)),
                                       "final": int(out[r]["counts_by_step"][bl.ENDPOINT_STEP_13B])}
                                   for r in bt.RUNGS},
                    "flat_rungs": [r for r in bt.RUNGS if r not in rung_set["R_13B"]],
                    "transient_clears_on_flat": {r: rl[r]["transient_clears"] for r in bt.RUNGS
                                                 if r not in rung_set["R_13B"] and rl[r]["transient_clears"]},
                    "collapses": collapses_13b(sweep, rungs=tuple(bt.RUNGS)),
                    "non_monotone": non_monotone_13b(out, tuple(bt.RUNGS)),
                    "first_correct_A": _run_test(x256, "1b:k256", first, strata, r_primary, **kw),
                    "first_correct_B": _run_test(x_b, bi.SIZE_PRED, first,
                                                 an2i._composite_strata_median(strata, x256, r_primary),
                                                 r_primary, **kw),
                    "live_items_A": {r: {"k64": sum(1 for c in x64[r] if c > 0),
                                         "k256": sum(1 for c in x256[r] if c > 0)} for r in r_primary}}
        _sec("S7 textures", _s7)

        def _extras():
            x64_all = bi.sampler_counts_pythia("1b", tuple(rung_set["R_ELEVEN_EXTRA"]) + tuple(rung_set["R_EXTRA"]))
            xb_all = bi.sampler_counts_olmo(tuple(rung_set["R_ELEVEN_EXTRA"]) + tuple(rung_set["R_EXTRA"]),
                                            root=root_2i, battery=battery, verify_fn=verify_fn)
            return _extra_rungs_2l(x64_all, xb_all, out, strata, r_eleven_extra=tuple(rung_set["R_ELEVEN_EXTRA"]),
                                   r_extra=tuple(rung_set["R_EXTRA"]))
        _sec("extra rungs", _extras)

        def _sens():
            return {"B_zero_cut": _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x256, r_primary),
                                            r_primary, **kw),
                    "primary_is_the_nine": bool(rung_set["primary_is_the_nine"]),
                    "R_PRIMARY": list(r_primary)}
        _sec("sensitivities", _sens)
        sec["failures"] = sec_failures
        v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
             "licensed_sentence": _licensed_2l(tree), "referents": referents,
             "tests": {"A": A, "B": B}, "secondaries": sec}
        # FREEZE F-1 (2j F-1's lineage, one call site over): the "(exit)"
        # check above runs BEFORE the thirteen secondaries, so a module
        # first imported inside one of them was never on the pinned
        # surface. Demonstrated at the freeze: an unpinned `experiments/`
        # module imported inside S1 left the verdict SHARED with zero
        # failures, and `check_imports_2l()` raised only when called
        # afterwards, by hand. Additive: re-check once the record is
        # complete and deliver the frozen refusal terminal if the surface
        # grew. (Not reachable through the real producer — no secondary
        # imports anything new — so this is a pin made total, not a bug
        # fixed.)
        _, f = collect_total(check_imports_2l if imports_pinned else (lambda: None),
                             "2l import surface (post-secondaries)")
        if f:
            failures += f
            referents["failures"] = list(failures)
            t2 = verdict_2l(failures, None, None, None, ())
            v = {"verdict": t2["verdict"], "reason": t2["reason"], **common,
                 "licensed_sentence": LICENSED_2L["INSUFFICIENT_DATA"], "referents": referents,
                 "tests": None, "secondaries": None}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(an2i._json_safe(v), indent=1, default=an2i._jsonable,
                                   allow_nan=False))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason")}, indent=1))
