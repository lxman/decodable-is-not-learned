# experiments/exp2i/analyze_2i.py
"""Exp 2i frozen analysis (design `experiment-2i-design.md` §1-§6): the
sampler confirmation carried cross-family. Two preregistered tests on
one sealed outcome — Test A (cross-family: Pythia-1b's committed count
x_A against OLMo-2 7B's stage-1 grid) and Test B (within-family, beyond
cross: OLMo-2 1B's sealed count x_B, in composite strata that condition
on x_A's zero cut) — read jointly into four worlds. No twin/SURFACE
terminal (design §3.6: the from_config 7B twin is a referent, never a
predictor).

Everything not defined here is frozen and re-asserted by sha256
(`battery_2i.FROZEN_SHA256`/`check_frozen_2i`, `check_pythia_predictor_
files`): 2g's strata/statistics, 2h's sampler-confirmation shape
(`primary_2h` reused UNCHANGED — it is a pure function of its (pred,
out, strata, rungs) arguments, bound to no exp2h-only global), 2d's row
format and binomial bar, 2c's harness, exp3's sampler contract, exp3c's
total verify wrapper. Every loader refusal COLLECTED and delivered as
INSUFFICIENT_DATA with the reason verbatim (2h's F-1/F-2/F-3 lessons,
carried forward): `collect_total` (imported from `analyze_2h`) widens
the caught-exception surface past a torn/hand-edited/directory-shaped
tree; gate 1's coverage is attested and REQUIRED, not merely zero;
`require_prereg_2i`/`require_seal_2i` bind the working tree to the
git blobs a tag actually carries, not merely to the tag's existence.

Tree: INSUFFICIENT_DATA -> the joint reading of Tests A and B ->
SHARED (A fires, B does not) / LINEAGE (B fires, A does not) / BOTH
(both fire) / NEITHER (neither fires); each non-firing test names
'below the effect bar' or 'inverted' inside it (`verdict_tree_2i`)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2I = Path(__file__).resolve().parent
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st2d  # noqa: E402
from experiments.exp2g import analyze_2g as an2g  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck2g  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import analyze_2h as an2h  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

RESULTS = EXP2I / "results"
REFERENTS_PATH_2I = EXP2I / "referents_2i.json"

# referents_2i.json's own sha256 — built and pinned by make_referents_2i.py
# (Task 3), 1837 files (1698 committed inputs + 139 not-yet-existing stage
# artifacts, listed with sha256: null and required by analysis time).
REFERENTS_2I_SHA256 = \
    "26c53980be17593001b6c17a36d91103cf3fb41163e257b4b5714b0208576a21"

WORLDS = ("INSUFFICIENT_DATA", "SHARED", "LINEAGE", "BOTH", "NEITHER")
ALPHA, T_BAR = st.ALPHA, st.T_BAR
N_PERM, N_BOOT = st.N_PERM, st.N_BOOT

collect = an2g.collect              # generic (thunk, label) -> (value, failures)
collect_total = an2h.collect_total  # the widened exception surface (2h F-1)
_median_bucket = an2h._median_bucket


# --------------------------------------------------------- known inputs

KNOWN_INPUTS_CAVEAT_2I = (
    "Known to the designer before any OLMo model was loaded: 2h's whole closed "
    "record (the per-rung loci at 2.8b/6.9b, the 410m replication, the "
    "reachability-vs-difficulty limit it disclosed); x_A — Pythia-1b's committed "
    "per-item sampled count (2d's main tier, seed 0, 64 T=1.0 draws per item, on "
    "disk since 2026-08-22); 2c's battery (items, shots, verify criterion) and "
    "2d's model-free floors; the Hub inventory of OLMo-2's checkpoint branches "
    "(metadata only — branch names, file lists, sizes, commits — read "
    "2026-08-25, no weights touched). Not known to anyone in this program: any "
    "output of any OLMo model on any item. The design was frozen and tagged "
    "before x_B (OLMo-2 1B's sampled count, sealed) or the OLMo-2 7B stage-1 "
    "endpoint (sealed, fixes R and the power record) were queried; the sweep "
    "comes after both (design §2, §7).")

LICENSED = {
    "SHARED": (
        "the essay's sentence changes from \"how often *the* smaller model "
        "already emits them\" to \"how often *a* smaller model already emits "
        "them, in either family\"; the \"structure latent in the training "
        "distribution\" reading gains a cross-family leg at item grain; the "
        "reachability-vs-difficulty limit in 2h §5 is resolved toward the "
        "items; the named next experiment is a third family or the OLMo-2 13B "
        "outcome"),
    "LINEAGE": (
        "the essay states the finding as lineage-bound (\"the smaller model of "
        "the same lineage\"), adds that Pythia-1b's counts carry Pythia's own "
        "path; cross-family forecasting is not licensed; next is the mechanism "
        "question (what about the smaller model's output makes an item "
        "reachable?)"),
    "BOTH": (
        "the essay states both components with their partials (T_A, T_B, "
        "within-alone, cross-beyond-within); the shared component is the "
        "headline only if T_A's CI excludes zero on the majority of R_∩"),
    "NEITHER": (
        "the two-outcome finding is demoted to \"on Pythia\" in the essay and "
        "experiments.md; the OLMo record is reported in full, including the "
        "endpoint table; the program's next step is Michael's call"),
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}

# design §4: each test at alpha .01, the world is their conjunction; the
# union of the four worlds is not alpha-calibrated (3d's calibration
# lesson, stated in advance rather than discovered at close-out).
CALIBRATION_SENTENCE_2I = (
    "Each test (A, B) is calibrated at alpha .01 on its own; the reported "
    "world — SHARED, LINEAGE, BOTH or NEITHER — is their conjunction, and the "
    "union of the four worlds is not alpha-calibrated (3d's calibration "
    "lesson, stated in advance).")


# ------------------------------------------------------- the prereg tag

# design §7 / Global Constraints: the tag `exp2i-preregistered` is
# blob-bound to these five files — `run/sweep_2i.py` does not exist yet
# (Task 4); in production a missing instrument file is a refusal. Both
# `require_prereg_2i` and `require_seal_2i` live here; `sample_2i.py`/
# `endpoint_2i.py` already try `from experiments.exp2i.analyze_2i import
# require_prereg_2i` first and fall back to the stub.
INSTRUMENT_BLOBS_2I = (
    "experiments/exp2i/battery_2i.py",
    "experiments/exp2i/analyze_2i.py",
    "experiments/exp2i/run/sample_2i.py",
    "experiments/exp2i/run/endpoint_2i.py",
    "experiments/exp2i/run/sweep_2i.py",
)


def require_prereg_2i(*, tag_exists=None, blob_sha=None) -> dict:
    """The real implementation the stage runners import by name once
    this module exists. Raises RuntimeError on any drift — this is the
    ONE gate every stage checks before touching a model."""
    tag_exists = tag_exists or pr.git_tag_exists
    if not tag_exists(bi.PREREG_TAG):
        raise RuntimeError(f"refusing: the preregistration tag {bi.PREREG_TAG!r} does "
                           f"not exist — the design must be frozen and tagged before "
                           f"any OLMo model contact")
    blob_sha = blob_sha or pr.git_blob_sha256
    blobs, drift = {}, []
    for rel in INSTRUMENT_BLOBS_2I:
        p = bi.REPO / rel
        got = bg.sha256_file(p) if p.is_file() else None
        want = blob_sha(bi.PREREG_TAG, rel)
        blobs[rel] = got
        if got is None:
            drift.append(f"{rel}: not on disk")
        elif want is None:
            drift.append(f"{rel}: no blob at {bi.PREREG_TAG}")
        elif want != got:
            drift.append(f"{rel}: working copy {got} != {want} at the tag")
    if drift:
        raise RuntimeError(f"refusing: the instrument has drifted from "
                           f"{bi.PREREG_TAG!r} — {'; '.join(drift)}")
    return {"tag": bi.PREREG_TAG, "instrument_blobs": blobs}


def require_seal_2i(tag, paths, *, tag_exists=None, blobs_bound=None,
                    repo_root=bi.REPO) -> dict:
    """Ruling 1: blob binding is the seal for the two stage artifacts
    (`PREDICTOR_SEAL_TAG` over the predictor + its 34 draws/records,
    `ENDPOINT_SEAL_TAG` over the 68 endpoint records + rung_set_2i.json
    + power_2i.json). NEVER RAISES — every failure (missing tag, drift,
    or an injected callable raising) lands in the returned dict's
    `failures` list, which the caller merges into `run()`'s own
    collected failures."""
    tag_exists = tag_exists or pr.git_tag_exists
    blobs_bound = blobs_bound or bi.blobs_bound
    try:
        exists = tag_exists(tag)
    except Exception as e:  # noqa: BLE001 — deliberately broad, never escapes
        return {"tag": tag, "n_paths": len(paths),
                "failures": [f"tag_exists({tag!r}) raised {type(e).__name__}: {e}"]}
    if not exists:
        return {"tag": tag, "n_paths": len(paths),
                "failures": [f"the tag {tag!r} does not exist"]}
    rel = [os.path.relpath(str(p), str(repo_root)) for p in paths]
    try:
        drift = blobs_bound(tag, rel, repo_root=repo_root)
    except Exception as e:  # noqa: BLE001
        return {"tag": tag, "n_paths": len(paths),
                "failures": [f"blobs_bound raised {type(e).__name__}: {e}"]}
    if drift:
        return {"tag": tag, "n_paths": len(paths),
                "failures": [f"{tag!r} does not bind {sorted(drift)}"]}
    return {"tag": tag, "n_paths": len(paths), "failures": []}


def _predictor_seal_paths(root) -> list:
    paths = [bi.predictor_seal_path(root)]
    for r in bt.RUNGS:
        paths.append(bi.predictor_draws_path(root, r))
        paths.append(bi.predictor_record_path(root, r))
    return paths


def _endpoint_seal_paths(root) -> list:
    paths = [bi.rung_set_path(root), bi.power_path(root)]
    for which in ("stage1_final", "main"):
        for r in bt.RUNGS:
            paths.append(bi.endpoint_record_path(root, which, r))
    return paths


# -------------------------------------------------------------- gate 1

# The gate1.json record Task 4's sweep runner writes, re-derived from
# the sweep's endpoint-step (928646) records vs the stage-2
# `stage1_final` endpoint records already committed (design §3.6):
# per-item bits identical on all 34 rungs, continuations identical with
# the COMPARED COUNT attested and REQUIRED to be 500/rung (2h's F-2
# coverage lesson — a zero diff count over a truncated comparison is
# not evidence), tensor digest equal, commit equal, the freeze tag
# stamped. Task 4 reads this list when it writes the record.
GATE1_FIELDS = (
    "rungs", "bit_diffs", "continuation_diffs", "continuations_compared",
    "digest_sweep", "digest_endpoint", "commit_sweep", "commit_endpoint",
    "prereg_tag",
)


def gate1_failures_7b(rec: dict, endpoint_records: dict) -> list:
    """`rec` is the gate1.json record; `endpoint_records` is the
    already-loaded `{rung: record}` dict for the stage-2 `stage1_final`
    endpoint. Any deviation is a failure; `pass` (if present) is
    ignored — everything here is re-derived from the attested fields,
    never trusted."""
    bad = []
    rungs = tuple(bt.RUNGS)
    if list(rec.get("rungs", [])) != list(rungs):
        bad.append("gate 1 olmo7b: rung list is not the full 34-rung sweep set")
    cs, ce = rec.get("commit_sweep"), rec.get("commit_endpoint")
    if not cs or not ce or cs != ce:
        bad.append(f"gate 1 olmo7b: commit through the sweep loader ({cs}) != "
                   f"through the endpoint loader ({ce})")
    dg_s, dg_e = rec.get("digest_sweep"), rec.get("digest_endpoint")
    if not dg_s or not dg_e or dg_s != dg_e:
        bad.append(f"gate 1 olmo7b: tensor digest through the sweep loader "
                   f"({dg_s}) != through the endpoint loader ({dg_e}) — the "
                   f"checkpoint loader path is not the production path")
    bd = rec.get("bit_diffs", {})
    cd = rec.get("continuation_diffs", {})
    nc = rec.get("continuations_compared", {})
    for r in rungs:
        if r not in endpoint_records:
            bad.append(f"gate 1 olmo7b/{r}: no stage1_final endpoint record to "
                       f"compare against")
            continue
        if bd.get(r) != 0:
            bad.append(f"gate 1 olmo7b/{r}: {bd.get(r)} bit diffs between the "
                       f"sweep's step928646 record and the endpoint's "
                       f"stage1_final record")
        if cd.get(r) != 0:
            bad.append(f"gate 1 olmo7b/{r}: {cd.get(r)} continuation diffs")
        if nc.get(r) != bt.N_ITEMS:
            bad.append(f"gate 1 olmo7b/{r}: {nc.get(r)} continuation pairs "
                       f"compared, not the full {bt.N_ITEMS} — a zero diff "
                       f"count over a truncated comparison is not evidence")
    if rec.get("prereg_tag") != bi.PREREG_TAG:
        bad.append(f"gate 1 olmo7b: prereg_tag {rec.get('prereg_tag')!r} is not "
                   f"{bi.PREREG_TAG!r}")
    return bad


# ------------------------------------------------------- step/endpoint records

def _re_verify(conts, bits, cap, verify_fn, label) -> list:
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bt.N_ITEMS or len(conts) != bt.N_ITEMS:
        return [f"{label}: bits/continuations are not {bt.N_ITEMS} long"]
    bad = []
    re = [int(bool(verify_fn(c, it["answer"], cap["answer_type"])))
         for c, it in zip(conts, cap["eval_items"])]
    if re != [int(b) for b in bits]:
        n = sum(1 for a, b in zip(re, bits) if a != int(b))
        bad.append(f"{label}: re-verification of the continuations disagrees "
                   f"with the stored bits on {n} item(s)")
    return bad


def step_record_failures_2i(rec: dict, *, step, rung, cap, entry, verify_fn,
                            predictor_sha) -> list:
    """2g's step_record_failures shape, generalized: `family`/`size`
    added, `step` may be an int or the string `bi.TWIN` (the twin: the
    manifest entry carries `commit=None`, `kind="from_config"`, and the
    record must match), `seal_tag == ENDPOINT_SEAL_TAG` (Task 4's
    sweep is gated by the endpoint seal, not the predictor seal)."""
    bad = []
    label = f"olmo7b/step{step}/{rung}"
    for k, v in (("rung", rung), ("size", bi.SIZE_OUT), ("family", bi.FAMILY),
                 ("n", bt.N_ITEMS), ("seal_tag", bi.ENDPOINT_SEAL_TAG)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    want_step = bi.TWIN if step == bi.TWIN else int(step)
    if rec.get("step") != want_step:
        bad.append(f"{label}: step = {rec.get('step')!r}, expected {want_step!r}")
    if step == bi.TWIN:
        if rec.get("commit") is not None:
            bad.append(f"{label}: commit is {rec.get('commit')!r}, expected None")
        if rec.get("kind") != "from_config":
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")
    else:
        want_commit = entry["commit"]
        if rec.get("commit") != want_commit:
            bad.append(f"{label}: commit {rec.get('commit')} is not the "
                       f"manifest's {want_commit}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("predictor_sha") != predictor_sha:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{predictor_sha}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bt.N_ITEMS or len(conts) != bt.N_ITEMS:
        bad.append(f"{label}: bits/continuations are not {bt.N_ITEMS} long")
        return bad
    if rec.get("correct") != sum(bits):
        bad.append(f"{label}: correct {rec.get('correct')} != sum(bits) {sum(bits)}")
    bad += _re_verify(conts, bits, cap, verify_fn, label)
    return bad


def endpoint_record_failures_2i(rec: dict, *, which, rung, cap, entry, verify_fn,
                                predictor_sha) -> list:
    """The same shape as `step_record_failures_2i` with `which` in
    place of `step` and `seal_tag == PREDICTOR_SEAL_TAG` (the endpoint
    stage is gated by the predictor seal, not the endpoint seal —
    `endpoint_2i.py`'s `item_record_2i` stamps `seal_tag =
    seal["tag"]` where `seal` is the predictor seal)."""
    bad = []
    label = f"endpoint {which}/{rung}"
    for k, v in (("rung", rung), ("size", bi.SIZE_OUT), ("family", bi.FAMILY),
                 ("which", which), ("n", bt.N_ITEMS),
                 ("seal_tag", bi.PREDICTOR_SEAL_TAG)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    want_commit = entry.get("commit")
    if want_commit is not None and rec.get("commit") != want_commit:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's "
                   f"{want_commit}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("predictor_sha") != predictor_sha:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{predictor_sha}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bt.N_ITEMS or len(conts) != bt.N_ITEMS:
        bad.append(f"{label}: bits/continuations are not {bt.N_ITEMS} long")
        return bad
    if rec.get("correct") != sum(bits):
        bad.append(f"{label}: correct {rec.get('correct')} != sum(bits) {sum(bits)}")
    bad += _re_verify(conts, bits, cap, verify_fn, label)
    return bad


def load_endpoint_which(root, which, battery, verify_fn, *, entry,
                        predictor_sha) -> dict:
    out = {}
    for rung in bt.RUNGS:
        p = bi.endpoint_record_path(root, which, rung)
        if not p.is_file():
            raise FileNotFoundError(f"endpoint record missing: {p}")
        rec = json.loads(p.read_text())
        bad = endpoint_record_failures_2i(rec, which=which, rung=rung, cap=battery[rung],
                                          entry=entry, verify_fn=verify_fn,
                                          predictor_sha=predictor_sha)
        if bad:
            raise ValueError("; ".join(bad))
        out[rung] = rec
    return out


def load_sweep_7b(root, battery, verify_fn, *, manifest, predictor_sha, steps=None,
                  rungs=None) -> dict:
    """2h's `load_sweep_69` shape over `GRID_7B + TWIN`: every record
    through `step_record_failures_2i`."""
    steps = tuple(steps) if steps is not None else bi.GRID_7B + (bi.TWIN,)
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for step in steps:
        entry = bi.entry_7b(manifest, step)
        out[step] = {}
        for rung in rungs:
            p = bi.record_path(root, step, rung)
            if not p.is_file():
                raise FileNotFoundError(f"sweep record missing: {p}")
            rec = json.loads(p.read_text())
            bad = step_record_failures_2i(rec, step=step, rung=rung, cap=battery[rung],
                                          entry=entry, verify_fn=verify_fn,
                                          predictor_sha=predictor_sha)
            if bad:
                raise ValueError("; ".join(bad))
            out[step][rung] = rec
        if step != bi.TWIN:
            cp = bi.checkpoint_record_path(root, step)
            if not cp.is_file():
                raise FileNotFoundError(f"checkpoint record missing: {cp}")
            crec = json.loads(cp.read_text())
            for name, want in entry.get("lfs_sha256", {}).items():
                if crec.get("sha256", {}).get(name) != want:
                    raise ValueError(f"olmo7b/step{step}: downloaded {name} sha "
                                     f"{crec.get('sha256', {}).get(name)} != "
                                     f"manifest {want}")
            if crec.get("loading_info", {}) != {"missing_keys": 0, "unexpected_keys": 0,
                                                 "mismatched_keys": 0}:
                raise ValueError(f"olmo7b/step{step}: loading info not empty")
    return out


# ------------------------------------------------------------ outcomes

def outcomes_7b(sweep: dict, *, rungs=None) -> dict:
    """`analyze_2g.outcomes`'s body with `bg.trained_steps(size)`
    replaced by `battery_2i.trained_steps_7b()` (GRID_7B, 21 points,
    the endpoint included). The twin is never in an outcome: it is
    excluded by construction — `steps` never contains `bi.TWIN`, even
    though `sweep` itself may carry a `bi.TWIN` key."""
    steps = bi.trained_steps_7b()
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
                     "counts_by_step": {int(s): int(sweep[s][rung]["correct"])
                                        for s in steps}}
    return out


def rung_level_7b(out: dict, floors: dict, *, rungs=None) -> dict:
    steps = bi.trained_steps_7b()
    rungs = tuple(rungs) if rungs is not None else tuple(out)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in steps
                  if st2d.binomial_bar(c[s], bt.N_ITEMS, floors[rung])["significant"]]
        final = bi.ENDPOINT_STEP_7B in clears
        res[rung] = {"s_star": clears[0] if clears else None,
                     "clears": clears, "final_clears": final,
                     "transient_clears": ([] if final else clears)}
    return res


# ------------------------------------------------------------- primary

# `primary_2h` is a pure function of its (pred, out, strata, rungs, ...)
# arguments — bound to no `bh.R_69`-shaped global anywhere in its body
# (confirmed by reading it) — so it is reused DIRECTLY, not copied. Its
# return shape (stratified/raw/pooled_d/per_rung/eligible/thin) is
# exactly what `_run_test` below wraps with `dropped_degenerate`/
# `fires`/`named_inside`.
primary_2i = an2h.primary_2h


def fires_2i(prim: dict) -> bool:
    """The one firing rule, shared between the analyzer and
    `power_2i.py`'s simulation (ruling 9: one implementation)."""
    T, p = prim["stratified"]["T"], prim["stratified"]["p"]
    return bool(p < ALPHA and T >= T_BAR)


def named_inside_2i(prim: dict):
    T, p = prim["stratified"]["T"], prim["stratified"]["p"]
    notes = []
    if p < ALPHA and T < T_BAR:
        notes.append(f"below the effect bar (T = {T:.4f} < {T_BAR}, p = {p:.4g})")
    if T < 0:
        hi = prim["stratified"].get("n_perm", 0)
        n_ge = prim["stratified"].get("n_ge", 0)
        p_inv = (1 + hi - n_ge) / (1 + hi) if hi else None
        notes.append(f"inverted (T = {T:.4f}; one-sided p for T_perm <= T_obs "
                     f"~ {p_inv})")
    return "; ".join(notes) if notes else None


def _scores_predictor_2i(counts: dict, size: str, rungs) -> dict:
    """Wraps a {rung: [counts]} dict into the {"cells": {rung: {size:
    {"trained": {"scores": ..., "eval_rule": {"scores": ...}}}}}} shape
    `cells_for`/`cell_scores` expect — no "untrained" key (2i has no
    twin arm, design §3.6)."""
    return {"cells": {r: {size: {"trained": {"scores": [float(c) for c in counts[r]],
                                             "eval_rule": {"scores": [float(c) for c in counts[r]]}}}}
                      for r in rungs}}


def _degenerate_rungs(counts: dict, strata: dict, rungs) -> list:
    """design §4: a rung is dropped from a test if its predictor has
    fewer than two distinct values inside EVERY stratum — D is
    undefined there (not zero-evidence: `d_from_pre` would silently
    return 0.0 for a constant predictor, which looks like 'no
    correlation detected' rather than 'undefined'). Returns the
    dropped rungs, sorted as given."""
    out = []
    for r in rungs:
        x = counts[r]
        s = strata[r]["strata"]
        by_stratum = {}
        for xi, si in zip(x, s):
            by_stratum.setdefault(si, set()).add(xi)
        if all(len(vals) < 2 for vals in by_stratum.values()):
            out.append(r)
    return out


def _run_test(counts: dict, size_label: str, out: dict, strata: dict, rungs, *,
             n_perm=N_PERM, n_boot=N_BOOT) -> dict:
    """One test's full result: drop degenerate rungs, run `primary_2i`
    on the survivors, decide `fires`/`named_inside` through the one
    shared rule. Raises (uncaught) if every rung is dropped or thin —
    the caller wraps this in `collect_total`."""
    dropped = _degenerate_rungs(counts, strata, rungs)
    keep = tuple(r for r in rungs if r not in dropped)
    pred = _scores_predictor_2i(counts, size_label, keep)
    prim = primary_2i(pred, out, strata, size_pred=size_label, rungs=keep,
                      n_perm=n_perm, n_boot=n_boot)
    prim["dropped_degenerate"] = list(dropped)
    prim["fires"] = fires_2i(prim)
    prim["named_inside"] = named_inside_2i(prim) if not prim["fires"] else None
    return prim


def _composite_strata(strata: dict, cond: dict, rungs) -> dict:
    """Test B's own construction (design §1, ruling 3): composite
    stratum = base stratum | 1[cond > 0] — the zero cut."""
    return {r: {"strata": [f"{s}|{int(c > 0)}"
                           for s, c in zip(strata[r]["strata"], cond[r])]}
           for r in rungs}


def _composite_strata_median(strata: dict, cond: dict, rungs) -> dict:
    """`cross_beyond_within`'s construction (ruling 3): composite
    stratum = base stratum | the MEDIAN bucket of `cond` over the whole
    rung (no natural zero cut on a spread predictor, unlike x_A's)."""
    out = {}
    for r in rungs:
        buckets = _median_bucket(cond[r])
        out[r] = {"strata": [f"{s}|{b}"
                             for s, b in zip(strata[r]["strata"], buckets)]}
    return out


# --------------------------------------------------------------- tree

def verdict_tree_2i(failures, A, B) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader failure(s): "
                          f"{list(failures)[:5]}"}
    a, b = A["fires"], B["fires"]
    if a and not b:
        verdict = "SHARED"
    elif b and not a:
        verdict = "LINEAGE"
    elif a and b:
        verdict = "BOTH"
    else:
        verdict = "NEITHER"
    parts = [f"A: T={A['stratified']['T']:.4f}, p={A['stratified']['p']:.4g}, "
            f"fires={a}"]
    if A.get("named_inside"):
        parts.append(f"A {A['named_inside']}")
    parts.append(f"B: T={B['stratified']['T']:.4f}, p={B['stratified']['p']:.4g}, "
                f"fires={b}")
    if B.get("named_inside"):
        parts.append(f"B {B['named_inside']}")
    return {"verdict": verdict, "reason": "; ".join(parts)}


# ---------------------------------------------------- referent loaders

def _load_predictor_seal_content(root) -> dict:
    p = bi.predictor_seal_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    for k in ("sha256", "tag", "files", "counts"):
        if k not in rec:
            raise ValueError(f"{p}: missing {k!r}")
    if rec["tag"] != bi.PREDICTOR_SEAL_TAG:
        raise ValueError(f"{p}: tag {rec['tag']!r} is not {bi.PREDICTOR_SEAL_TAG!r}")
    return rec


def _load_rung_set(root) -> dict:
    p = bi.rung_set_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    for k in ("R_OLMO", "R_CAP", "R_EXTRA", "per_rung", "endpoint_file_sha256"):
        if k not in rec:
            raise ValueError(f"{p}: missing {k!r}")
    if not set(rec["R_CAP"]).issubset(set(bi.STRATA_RUNGS)):
        raise ValueError(f"{p}: R_CAP is not a subset of the eleven strata rungs")
    if set(rec["R_CAP"]) | set(rec["R_EXTRA"]) != set(rec["R_OLMO"]):
        raise ValueError(f"{p}: R_CAP/R_EXTRA do not partition R_OLMO")
    return rec


def _check_rung_set_vs_endpoint(rung_set: dict, stage1_final: dict) -> list:
    """The rung set was computed (`endpoint_2i.py`, Task 2) from the
    SAME `stage1_final` counts committed to disk — re-verify that
    `per_rung[r]["k"]` (the count `rung_set_from_counts` scored) still
    equals the endpoint record's own `correct`, rung by rung. A
    mismatch means the rung set was derived from data that has since
    drifted — the R_CAP/R_EXTRA split can no longer be trusted."""
    bad = []
    per_rung = rung_set.get("per_rung", {})
    for r in bt.RUNGS:
        if r not in stage1_final or r not in per_rung:
            continue
        want = stage1_final[r]["correct"]
        got = per_rung[r].get("k")
        if got != want:
            bad.append(f"rung set olmo7b/{r}: per_rung k={got!r} disagrees with the "
                       f"endpoint's stage1_final correct={want!r}")
    return bad


def _load_power(root) -> dict:
    p = bi.power_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    for test in ("A", "B"):
        sub = rec.get(test)
        if not isinstance(sub, dict) or "declared_status" not in sub or \
                "declaration" not in sub:
            raise ValueError(f"{p}: test {test!r} missing declared_status/declaration")
    return rec


# ------------------------------------------------- non-gating secondaries

def _first_correct_outcome(out: dict, rungs) -> dict:
    last_step = max(bi.trained_steps_7b())
    return {r: {"y": [0 if fc is None else (last_step + 1 - fc) for fc in out[r]["first"]],
               "n_pos": out[r]["n_pos"]} for r in rungs}


def _extra_rungs_raw_2i(x_a: dict, x_b: dict, out: dict, r_extra) -> dict:
    res = {}
    for r in r_extra:
        y = out[r]["y"]
        s = ["0"] * len(y)
        da = st.somers_d_within(x_a[r], y, s)
        db = st.somers_d_within(x_b[r], y, s)
        res[r] = {"raw_d_A": da["d"], "raw_d_B": db["d"], "n_pos": out[r]["n_pos"]}
    return res


def _main_vs_endpoint_2i(stage1: dict, main: dict) -> dict:
    out = {}
    for r in bt.RUNGS:
        b1, bm = stage1[r]["bits"], main[r]["bits"]
        gained = sum(1 for a, b in zip(b1, bm) if a == 0 and b == 1)
        lost = sum(1 for a, b in zip(b1, bm) if a == 1 and b == 0)
        out[r] = {"correct_stage1_final": stage1[r]["correct"],
                  "correct_main": main[r]["correct"],
                  "items_gained": gained, "items_lost": lost}
    return out


def _reverse_direction(x_b: dict, strata: dict, rungs_cap, battery, verify_fn, *,
                       n_perm, n_boot) -> dict:
    """x_B against 2g's committed 2.8b outcome and 2h's committed 6.9b
    outcome, loaded through their own frozen loaders, sha-pinned.
    KNOWN_OUTCOME stamped: both outcomes were already known before x_B
    was sealed (design §2) — this is the cheapest cross-family reading
    in the OTHER direction, no new model contact."""
    manifest28 = ck2g.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=an2g.CHECKPOINTS_SHA256)
    rungs28 = tuple(r for r in rungs_cap if r in bg.R_28)
    sweep28 = an2g.load_sweep(bg.EXP2G, "2.8b", battery, verify_fn, manifest=manifest28,
                              seal_sha=bh.PREDICTOR_2G_SHA)
    out28 = an2g.outcomes(sweep28, "2.8b", rungs=rungs28)
    res28 = _run_test(x_b, bi.SIZE_PRED, out28, strata, rungs28, n_perm=n_perm,
                      n_boot=n_boot)
    res28["known_outcome"] = True

    manifest69 = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69,
                                     sha_pin=an2h.CHECKPOINTS_2H_SHA256)
    rungs69 = tuple(r for r in rungs_cap if r in bh.R_69)
    sweep69 = an2h.load_sweep_69(bh.EXP2H, battery, verify_fn, manifest=manifest69,
                                 seal_sha=bh.PREDICTOR_2G_SHA)
    out69 = an2h.outcomes_69(sweep69, rungs=rungs69)
    res69 = _run_test(x_b, bi.SIZE_PRED, out69, strata, rungs69, n_perm=n_perm,
                      n_boot=n_boot)
    res69["known_outcome"] = True
    return {"vs_2.8b": res28, "vs_6.9b": res69}


def _outcomes_and_tests_2i(sweep, strata, x_a, x_b, rung_set, *, n_perm, n_boot):
    """The GATING core (freeze F-1 standard, one unit behind one
    `collect_total`): outcomes over all 34 rungs, then Test A (plain
    strata) and Test B (composite, x_A's zero cut) over R_CAP."""
    out = outcomes_7b(sweep, rungs=tuple(bt.RUNGS))
    r_cap = tuple(rung_set["R_CAP"])
    A = _run_test(x_a, "1b", out, strata, r_cap, n_perm=n_perm, n_boot=n_boot)
    strata_b = _composite_strata(strata, x_a, r_cap)
    B = _run_test(x_b, bi.SIZE_PRED, out, strata_b, r_cap, n_perm=n_perm, n_boot=n_boot)
    return out, A, B


# ----------------------------------------------------------------- run

def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                          capture_output=True, text=True).stdout.strip()


def run(root=EXP2I, *, write=False, n_perm=N_PERM, n_boot=N_BOOT, tag_exists=None,
        blob_sha=None, blobs_bound=None, manifest_sha=bi.CHECKPOINTS_2I_SHA256,
        referents_sha=REFERENTS_2I_SHA256, out_path=None) -> dict:
    # `referents_sha` follows 2g's/2h's own convention: the DEFAULT is
    # the real committed pin; a caller passes `referents_sha=None`
    # EXPLICITLY to skip the check entirely (a synthetic world's tree
    # is unrelated to the real, committed referents_2i.json).
    failures = []

    _, f = collect_total(bg.check_frozen_imports_2g, "upstream frozen imports")
    failures += f
    _, f = collect_total(bi.check_frozen_2i, "frozen imports")
    failures += f
    _, f = collect_total(bi.check_pythia_predictor_files, "pythia predictor files")
    failures += f

    prereg, f = collect_total(lambda: require_prereg_2i(tag_exists=tag_exists,
                                                        blob_sha=blob_sha), "prereg tag")
    failures += f

    manifest, f = collect_total(
        lambda: bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=manifest_sha),
        "checkpoint manifest")
    failures += f

    if referents_sha is not None:
        from experiments.exp2i import make_referents_2i as mkr
        mf, f = collect_total(
            lambda: mkr.check_referents(REFERENTS_PATH_2I, sha_pin=referents_sha),
            "referent manifest")
        failures += f + (mf or [])

    battery, f = collect_total(bg.load_battery, "battery")
    failures += f
    floors, f = collect_total(bg.load_floors, "2d floors")
    failures += f
    verify_fn, f = collect_total(a2d.load_verify, "verify criterion")
    failures += f

    # the strata table lives inside 2g's sealed predictor — read it the
    # same way analyze_2h does, rather than rebuilding it locally from
    # the battery (both are equal, since `strata_for` is a pure function
    # of the committed items, but this is the committed, sha-pinned
    # source the design names).
    pred2g, f = collect_total(
        lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA),
        "2g predictor (strata source)")
    failures += f
    strata = sg.from_json(pred2g["strata"]) if pred2g else None
    gates = {}
    if strata is not None:
        sgg, f = collect_total(lambda: sg.check_strata_pins(strata), "strata gate")
        failures += f
        gates["strata"] = sgg

    predictor_rec, f = collect_total(lambda: _load_predictor_seal_content(root),
                                     "predictor seal content")
    failures += f
    psl = require_seal_2i(bi.PREDICTOR_SEAL_TAG, _predictor_seal_paths(root),
                          tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"predictor seal: {m}" for m in psl["failures"]]

    rung_set, f = collect_total(lambda: _load_rung_set(root), "rung set")
    failures += f

    power, f = collect_total(lambda: _load_power(root), "power record")
    failures += f
    esl = require_seal_2i(bi.ENDPOINT_SEAL_TAG, _endpoint_seal_paths(root),
                          tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"endpoint seal: {m}" for m in esl["failures"]]

    entry_stage1 = entry_main = None
    if manifest is not None:
        entry_stage1, f = collect_total(lambda: bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B),
                                        "7B endpoint entry")
        failures += f
        entry_main, f = collect_total(lambda: bi.entry_main(manifest, bi.REPO_7B),
                                      "7B main entry")
        failures += f

    _stage1_ready = (battery is not None and verify_fn is not None and
                     predictor_rec is not None and entry_stage1 is not None)
    stage1_final, f = collect_total(
        lambda: load_endpoint_which(root, "stage1_final", battery, verify_fn,
                                    entry=entry_stage1,
                                    predictor_sha=predictor_rec["sha256"])
        if _stage1_ready else
        (_ for _ in ()).throw(ValueError("battery, verify criterion, predictor "
                                         "seal or manifest entry missing")),
        "endpoint stage1_final")
    failures += f

    _main_ready = (battery is not None and verify_fn is not None and
                  predictor_rec is not None and entry_main is not None)
    main_rec, f = collect_total(
        lambda: load_endpoint_which(root, "main", battery, verify_fn,
                                    entry=entry_main,
                                    predictor_sha=predictor_rec["sha256"])
        if _main_ready else
        (_ for _ in ()).throw(ValueError("battery, verify criterion, predictor "
                                         "seal or manifest entry missing")),
        "endpoint main")
    failures += f

    # gate 1 (design §3.6): the sweep's endpoint-step record vs the
    # stage-2 stage1_final endpoint record.
    g1p = bi.gate1_path(root)
    if bi.halt_marker_path(root).exists():
        halted, f = collect_total(
            lambda: bi.halt_marker_path(root).read_text().strip()[:200],
            "gate 1 olmo7b halt marker")
        failures += f
        if not f:
            failures.append(f"gate 1 olmo7b: the runner halted ({halted})")
    gate1 = None
    if not g1p.is_file():
        failures.append(f"gate 1 olmo7b: record missing ({g1p})")
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()),
                                 "gate 1 olmo7b record")
        failures += f
        if gate1 is not None:
            _gate_ready = stage1_final is not None
            gbad, f = collect_total(
                lambda: gate1_failures_7b(gate1, stage1_final) if _gate_ready else
                (_ for _ in ()).throw(ValueError("stage1_final endpoint records "
                                                 "missing")),
                "gate 1 olmo7b re-derivation")
            failures += f + (gbad or [])

    if rung_set is not None and stage1_final is not None:
        rbad, f = collect_total(
            lambda: _check_rung_set_vs_endpoint(rung_set, stage1_final),
            "rung set vs endpoint")
        failures += f + (rbad or [])

    _pred_ready = rung_set is not None and battery is not None and verify_fn is not None
    x_a, f = collect_total(
        lambda: bi.sampler_counts_pythia("1b", rung_set["R_OLMO"]) if _pred_ready else
        (_ for _ in ()).throw(ValueError("rung set, battery or verify criterion missing")),
        "predictor x_A")
    failures += f
    x_b, f = collect_total(
        lambda: bi.sampler_counts_olmo(rung_set["R_OLMO"], root=root, battery=battery,
                                       verify_fn=verify_fn) if _pred_ready else
        (_ for _ in ()).throw(ValueError("rung set, battery or verify criterion missing")),
        "predictor x_B")
    failures += f

    _sweep_ready = (manifest is not None and battery is not None and
                    verify_fn is not None and predictor_rec is not None)
    sweep, f = collect_total(
        lambda: load_sweep_7b(root, battery, verify_fn, manifest=manifest,
                              predictor_sha=predictor_rec["sha256"]) if _sweep_ready
        else (_ for _ in ()).throw(ValueError("manifest, battery, verify criterion "
                                              "or predictor seal missing")),
        "sweep olmo7b")
    failures += f

    core = None
    if not failures:
        core, f = collect_total(
            lambda: _outcomes_and_tests_2i(sweep, strata, x_a, x_b, rung_set,
                                           n_perm=n_perm, n_boot=n_boot),
            "primary olmo7b")
        failures += f

    referents = {"failures": list(failures), "gates": gates,
                 "manifest_sha256": manifest_sha, "prereg": prereg,
                 "predictor_seal": psl, "endpoint_seal": esl,
                 "gate1": {k: v for k, v in (gate1 if isinstance(gate1, dict) else {}).items()
                           if k not in ("timing",)},
                 "power": power, "rung_set": rung_set}

    if failures:
        tree = verdict_tree_2i(failures, None, None)
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2I,
             "licensed_sentence": LICENSED["INSUFFICIENT_DATA"], "referents": referents,
             "tests": None, "secondaries": None, "n_perm": n_perm,
             "git_sha": _git_sha()}
    else:
        out, A, B = core
        tree = verdict_tree_2i([], A, B)
        r_cap = tuple(rung_set["R_CAP"])
        r_extra = tuple(rung_set["R_EXTRA"])
        r_olmo = tuple(rung_set["R_OLMO"])

        sec, sec_failures = {}, []

        def _sec(name, thunk):
            val, f = collect_total(thunk, name)
            if f:
                sec[name] = {"failed": f[0]}
                sec_failures.extend(f)
            else:
                sec[name] = val

        _sec("within_alone",
            lambda: _run_test(x_b, bi.SIZE_PRED, out, strata, r_cap, n_perm=n_perm,
                              n_boot=n_boot))

        def _cross_beyond_within():
            strata_med = _composite_strata_median(strata, x_b, r_cap)
            return _run_test(x_a, "1b", out, strata_med, r_cap, n_perm=n_perm,
                             n_boot=n_boot)
        _sec("cross_beyond_within", _cross_beyond_within)

        def _rep410m_cross():
            x_a410 = bi.sampler_counts_pythia("410m", r_cap)
            return _run_test(x_a410, "410m", out, strata, r_cap, n_perm=n_perm,
                             n_boot=n_boot)
        _sec("replication_410m_cross", _rep410m_cross)

        _sec("first_correct_A",
            lambda: _run_test(x_a, "1b", _first_correct_outcome(out, r_cap), strata,
                              r_cap, n_perm=n_perm, n_boot=n_boot))

        def _fc_b():
            strata_b = _composite_strata(strata, x_a, r_cap)
            return _run_test(x_b, bi.SIZE_PRED, _first_correct_outcome(out, r_cap),
                             strata_b, r_cap, n_perm=n_perm, n_boot=n_boot)
        _sec("first_correct_B", _fc_b)

        _sec("reverse_direction",
            lambda: _reverse_direction(x_b, strata, r_cap, battery, verify_fn,
                                       n_perm=n_perm, n_boot=n_boot))

        _sec("extra_rungs_raw", lambda: _extra_rungs_raw_2i(x_a, x_b, out, r_extra))

        def _rung_level_sec():
            rl = rung_level_7b(out, floors, rungs=r_cap)
            table = {r: {"s_star": rl[r]["s_star"],
                        "mean_rate_A": float(sum(x_a[r]) / len(x_a[r]) /
                                             bi.DRAWS_PER_ITEM),
                        "mean_rate_B": float(sum(x_b[r]) / len(x_b[r]) /
                                             bi.DRAWS_PER_ITEM),
                        "counts_by_step": out[r]["counts_by_step"]} for r in r_cap}
            return {"note": "descriptive by design: R_CAP only", "table": table}
        _sec("rung_level", _rung_level_sec)

        def _flat_rungs():
            rl_all = rung_level_7b(out, floors, rungs=tuple(bt.RUNGS))
            return {r: {"s_star": rl_all[r]["s_star"],
                       "transient_clears": rl_all[r]["transient_clears"],
                       "counts_by_step": out[r]["counts_by_step"]}
                   for r in bt.RUNGS if r not in r_olmo}
        _sec("flat_rungs", _flat_rungs)

        _sec("twin_counts",
            lambda: {r: sweep[bi.TWIN][r]["correct"] for r in bt.RUNGS} if bi.TWIN in sweep
            else (_ for _ in ()).throw(ValueError("twin missing from the sweep")))

        _sec("main_vs_endpoint",
            lambda: _main_vs_endpoint_2i(stage1_final, main_rec)
            if stage1_final is not None and main_rec is not None else
            (_ for _ in ()).throw(ValueError("endpoint stage1_final/main records "
                                             "missing")))

        sec["failures"] = sec_failures
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2I,
             "licensed_sentence": LICENSED[tree["verdict"]], "referents": referents,
             "tests": {"A": A, "B": B}, "secondaries": sec, "n_perm": n_perm,
             "git_sha": _git_sha()}
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
