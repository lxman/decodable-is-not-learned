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
import re
import subprocess
import sys
import zlib
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
# (Task 3), 1843 files (1704 committed inputs + 139 not-yet-existing stage
# artifacts, listed with sha256: null and required by analysis time). The
# 1698 -> 1702 committed-input bump (2026-08-25, whole-branch review fix
# wave, I-2) is FROZEN_SHA256 growing from 16 to 20 pinned modules; the
# 1702 -> 1704 bump is freeze F-3 (20 -> 22: power_2i.py, run/seal_2i.py).
REFERENTS_2I_SHA256 = \
    "8e9a7ab50fc1a5a5239d842cc436bcb17f692cd4d83f64ecb1664b8113df8f6c"

WORLDS = ("INSUFFICIENT_DATA", "SHARED", "LINEAGE", "BOTH", "NEITHER")
ALPHA, T_BAR = st.ALPHA, st.T_BAR
N_PERM, N_BOOT = st.N_PERM, st.N_BOOT

collect = an2g.collect              # generic (thunk, label) -> (value, failures)
_collect_total_2h = an2h.collect_total   # 2h F-1's widened surface
_median_bucket = an2h._median_bucket


def collect_total(thunk, label):
    """`analyze_2h.collect_total` (itself `analyze_2g.collect` widened to
    TypeError/AttributeError/OSError) with the COMPRESSED-STREAM shapes
    added — freeze F-2, 2h F-1's lineage one file type over.

    2h's widening covered the record shapes a killed or hand-edited
    tree presents: torn JSON, a list where a dict belongs, a directory
    where a file belongs. 2i is the first experiment in this line whose
    analyzer reads a GZIP file on the verdict path (`sampler_counts_
    olmo` -> `analyze_2d.read_rows` over x_B's own
    `<rung>.draws.jsonl.gz`), and a gzip stream fails in two ways that
    are neither `OSError` nor `ValueError`:

      * a TRUNCATED stream raises `EOFError` ("Compressed file ended
        before the end-of-stream marker was reached") — the exact tree
        an interrupted `write_draws` leaves, and the exact tree the
        commit watcher's 2-second settle can commit for a ~1 GB draws
        file (freeze attack item 25);
      * a CORRUPT stream raises `zlib.error` ("Error -3 while
        decompressing data") — a subclass of `Exception`, not `OSError`.

    Demonstrated at the freeze: on a full-shape world with `antonym`'s
    draws file truncated to 50% (and to 99%), `run()` RAISED `EOFError`
    instead of delivering INSUFFICIENT_DATA. Widening is additive and
    one-directional exactly as 2h's was — a caught failure lands in
    `failures` verbatim and the verdict is INSUFFICIENT_DATA; no tree
    that produced a verdict can now produce a different one, and no
    accepted dial is touched.

    `IndexError` is deliberately NOT added: the freeze swept every tree
    shape the three runners can leave and found none reachable
    (`read_rows` bounds-checks `item` before any list is indexed by it,
    and every other indexing site in the verdict path is guarded), and
    an `IndexError` that IS reachable would be a logic defect in the
    instrument, which must surface as a crash rather than be laundered
    into a refusal."""
    try:
        return _collect_total_2h(thunk, label)
    except (EOFError, zlib.error) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


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
# blob-bound to these five files — all five are on disk (Task 4 landed
# `run/sweep_2i.py`, the last of them; the fail-closed stub
# `run/_prereg_stub_2i.py` that `sample_2i.py`/`endpoint_2i.py` fell
# back onto before this module existed was removed the same task). In
# production a missing instrument file is still a refusal (`got is
# None` below). Both `require_prereg_2i` and `require_seal_2i` live
# here; `sample_2i.py`/`endpoint_2i.py` import `require_prereg_2i`
# directly from this module now.
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


def _predictor_seal_paths(root, seal=None) -> list:
    """The paths `PREDICTOR_SEAL_TAG` must bind. Freeze attack item 24:
    `run/endpoint_2i._seal_blob_paths` derives ITS set from the seal's
    own `files` dict (`seal_2i` hashes EVERYTHING under
    `results/predictor/`), this one from `bt.RUNGS`. On the real shape
    the two are equal — 1 seal + 34 draws + 34 records — but a stray
    file under `results/predictor/` would be in the seal's dict and
    outside the rule's, so the runner-side gate and the analyzer-side
    gate would bind different sets. Take the UNION: the seal file is
    itself blob-bound, so its `files` dict is bound too, and binding
    more is never weaker."""
    paths = [bi.predictor_seal_path(root)]
    for r in bt.RUNGS:
        paths.append(bi.predictor_draws_path(root, r))
        paths.append(bi.predictor_record_path(root, r))
    if isinstance(seal, dict) and isinstance(seal.get("files"), dict):
        known = set(paths)
        for rel in sorted(seal["files"]):
            p = Path(root) / rel
            if p not in known:
                paths.append(p)
                known.add(p)
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


def gate1_rederive_7b(sweep_endpoint_records: dict, stage1_final_records: dict,
                      gate_record: dict) -> list:
    """C-1: gate 1 must RE-DERIVE identity, not trust attestation.
    `gate1_failures_7b` above only checks the runner's own ATTESTED
    `bit_diffs`/`continuation_diffs`/`continuations_compared` fields —
    it never opens the two committed record sets and compares bytes.
    This does: for every one of the 34 rungs, recompute the bit and
    continuation diffs directly from `sweep_endpoint_records[rung]`
    (the sweep's step928646 record) vs `stage1_final_records[rung]`
    (the already-committed stage-2 endpoint record), and require (a)
    both re-derived diffs are zero, (b) the re-derived counts AGREE
    with `gate_record`'s own attested `bit_diffs`/`continuation_diffs`
    (an attestation that disagrees with the bytes on disk is itself a
    failure, regardless of which side is right), (c) full coverage —
    both records are exactly `bt.N_ITEMS` long AND the attested
    `continuations_compared` is the full count (the same F-2 coverage
    standard `gate1_failures_7b` already applies to the attested side).
    Any deviation is a failure naming the rung and the count."""
    bad = []
    bd_attested = gate_record.get("bit_diffs", {}) if isinstance(gate_record, dict) else {}
    cd_attested = gate_record.get("continuation_diffs", {}) if isinstance(gate_record, dict) else {}
    nc_attested = gate_record.get("continuations_compared", {}) if isinstance(gate_record, dict) else {}
    for r in bt.RUNGS:
        if r not in sweep_endpoint_records:
            bad.append(f"gate 1 olmo7b re-derive/{r}: no sweep step{bi.ENDPOINT_STEP_7B} "
                       f"record to re-derive against")
            continue
        if r not in stage1_final_records:
            bad.append(f"gate 1 olmo7b re-derive/{r}: no stage1_final endpoint "
                       f"record to re-derive against")
            continue
        s_bits = sweep_endpoint_records[r].get("bits")
        e_bits = stage1_final_records[r].get("bits")
        s_conts = sweep_endpoint_records[r].get("continuations")
        e_conts = stage1_final_records[r].get("continuations")
        if not isinstance(s_bits, list) or not isinstance(e_bits, list) or                 len(s_bits) != bt.N_ITEMS or len(e_bits) != bt.N_ITEMS:
            bad.append(f"gate 1 olmo7b re-derive/{r}: sweep/endpoint bits are not "
                       f"both {bt.N_ITEMS} long — coverage failure")
            continue
        if not isinstance(s_conts, list) or not isinstance(e_conts, list) or                 len(s_conts) != bt.N_ITEMS or len(e_conts) != bt.N_ITEMS:
            bad.append(f"gate 1 olmo7b re-derive/{r}: sweep/endpoint continuations "
                       f"are not both {bt.N_ITEMS} long — coverage failure")
            continue
        bit_diff = sum(1 for a, b in zip(s_bits, e_bits) if int(bool(a)) != int(bool(b)))
        cont_diff = sum(1 for a, b in zip(s_conts, e_conts) if a != b)
        if bit_diff != 0:
            bad.append(f"gate 1 olmo7b re-derive/{r}: {bit_diff} bit diff(s) "
                       f"between the sweep's step{bi.ENDPOINT_STEP_7B} record and "
                       f"the stage1_final endpoint record (re-derived from the "
                       f"bytes, not the attestation)")
        if cont_diff != 0:
            bad.append(f"gate 1 olmo7b re-derive/{r}: {cont_diff} continuation "
                       f"diff(s) (re-derived from the bytes, not the attestation)")
        if bd_attested.get(r) != bit_diff:
            bad.append(f"gate 1 olmo7b re-derive/{r}: attested bit_diffs "
                       f"{bd_attested.get(r)!r} disagrees with the re-derived "
                       f"{bit_diff}")
        if cd_attested.get(r) != cont_diff:
            bad.append(f"gate 1 olmo7b re-derive/{r}: attested continuation_diffs "
                       f"{cd_attested.get(r)!r} disagrees with the re-derived "
                       f"{cont_diff}")
        if nc_attested.get(r) != bt.N_ITEMS:
            bad.append(f"gate 1 olmo7b re-derive/{r}: attested "
                       f"continuations_compared {nc_attested.get(r)!r} is not the "
                       f"full {bt.N_ITEMS} — a zero diff count over a truncated "
                       f"comparison is not evidence")
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


def _record_common_failures(rec: dict, *, label, cap, verify_fn, predictor_sha,
                            seal_tag) -> list:
    """The ~20-line skeleton `step_record_failures_2i` and
    `endpoint_record_failures_2i` both apply, factored out (finding 5):
    size/family/n/seal_tag, items_sha256, predictor_sha, the bits/
    continuations shape (returning early if malformed, exactly as
    each caller did inline before this split — no correct/re-
    verification check is reachable on a malformed record), `correct
    == sum(bits)`, and re-verification of the continuations against
    the stored bits. `rung` and the step-vs-which/commit checks stay
    in each caller: their shapes differ too much (the twin's `step`
    branch has no `which` analogue) to share cleanly."""
    bad = []
    for k, v in (("size", bi.SIZE_OUT), ("family", bi.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
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


def step_record_failures_2i(rec: dict, *, step, rung, cap, entry, verify_fn,
                            predictor_sha) -> list:
    """2g's step_record_failures shape, generalized: `family`/`size`
    added, `step` may be an int or the string `bi.TWIN` (the twin: the
    manifest entry carries `commit=None`, `kind="from_config"`, and the
    record must match), `seal_tag == ENDPOINT_SEAL_TAG` (Task 4's
    sweep is gated by the endpoint seal, not the predictor seal). The
    shared skeleton (size/family/n/seal_tag, items_sha256,
    predictor_sha, bits/continuations shape, correct == sum(bits),
    re-verification) lives in `_record_common_failures`; this adds only
    the fields the shared core cannot express: `rung`, and the step-or-
    twin/commit branch."""
    label = f"olmo7b/step{step}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
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
    bad += _record_common_failures(rec, label=label, cap=cap, verify_fn=verify_fn,
                                   predictor_sha=predictor_sha,
                                   seal_tag=bi.ENDPOINT_SEAL_TAG)
    return bad


def endpoint_record_failures_2i(rec: dict, *, which, rung, cap, entry, verify_fn,
                                predictor_sha) -> list:
    """The same shape as `step_record_failures_2i` with `which` in
    place of `step` and `seal_tag == PREDICTOR_SEAL_TAG` (the endpoint
    stage is gated by the predictor seal, not the endpoint seal —
    `endpoint_2i.py`'s `item_record_2i` stamps `seal_tag =
    seal["tag"]` where `seal` is the predictor seal). `rung`/`which`/
    `commit` here, the shared skeleton in `_record_common_failures`."""
    label = f"endpoint {which}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    if rec.get("which") != which:
        bad.append(f"{label}: which = {rec.get('which')!r}, expected {which!r}")
    want_commit = entry.get("commit")
    if want_commit is not None and rec.get("commit") != want_commit:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's "
                   f"{want_commit}")
    bad += _record_common_failures(rec, label=label, cap=cap, verify_fn=verify_fn,
                                   predictor_sha=predictor_sha,
                                   seal_tag=bi.PREDICTOR_SEAL_TAG)
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
    `power_2i.py`'s simulation (ruling 9: one implementation).

    Freeze R-2: an UNDEFINED test carries `T is None` (never NaN — see
    `_undefined_result_2i`), and an undefined test never fires. The
    guard is explicit rather than relying on `p < ALPHA` short-
    circuiting first: a caller that hands this a dict with `p = 0.0`
    and `T = None` must still get `False`, not a `TypeError`."""
    T, p = prim["stratified"]["T"], prim["stratified"]["p"]
    if T is None:
        return False
    return bool(p < ALPHA and T >= T_BAR)


def named_inside_2i(prim: dict):
    T, p = prim["stratified"]["T"], prim["stratified"]["p"]
    if T is None:                      # freeze R-2: an undefined test
        return None                    # names itself, not its (absent) T
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


# I-4 / Ruling 18: the two "undefined" reasons `_run_test` can land on
# without ever calling `primary_2i` (or after it raised) — a coarse
# per-stratum degeneracy pre-check (`_degenerate_rungs`, above) drops
# every rung before the call is even made, or `primary_2h`/`perm_test`
# itself raises because no rung is eligible (n_pos-thin) or the last
# surviving rung has no informative pair. Neither is a referent
# failure: the test is simply undefined, `fires=False`, and the OTHER
# test's result still stands.
_NO_INFORMATIVE_PAIR_RE = re.compile(r"perm_test: rung (\S+) has no informative pair")


def _undefined_result_2i(size_label: str, dropped, rungs, reason: str) -> dict:
    """The shape `_run_test` returns for an undefined test — never an
    exception. `stratified`/`raw` carry non-firing placeholders (T is
    None, p is 1.0) so a caller can never mistake this for a real,
    merely-non-firing statistical result.

    Freeze R-2: T is `None`, NOT `float("nan")`. `json.dump` writes a
    bare `NaN` token (allow_nan defaults True) which is not valid JSON
    — every strict parser (`json.loads(..., parse_constant=raise)`,
    most non-Python readers) rejects the verdict file. `None` round-
    trips as `null` everywhere. `fires_2i`/`named_inside_2i` guard on
    it explicitly and `verdict_tree_2i` formats it through `_fmt_T`."""
    empty = {"T": None, "p": 1.0, "n_perm": 0, "n_ge": 0}
    return {"stratified": dict(empty), "raw": dict(empty), "pooled_d": None,
           "per_rung": {}, "eligible": [], "thin": list(rungs),
           "size_pred": size_label, "dropped_degenerate": list(dropped),
           "fires": False, "named_inside": reason}


def _run_test(counts: dict, size_label: str, out: dict, strata: dict, rungs, *,
             n_perm=N_PERM, n_boot=N_BOOT) -> dict:
    """One test's full result: drop degenerate rungs, run `primary_2i`
    on the survivors, decide `fires`/`named_inside` through the one
    shared rule.

    Ruling 18: an all-degenerate (or no-eligible-rung) test is NOT a
    refusal. If `_degenerate_rungs` drops every rung up front, this
    short-circuits BEFORE ever calling `primary_2i` (`_undefined_
    result_2i`, 'every eligible rung degenerate'/'no eligible rung' —
    the latter only when `rungs` itself was already empty). If
    `primary_2i` raises 'primary_2h: no eligible rung' (every surviving
    rung is n_pos-thin, inside `cells_for`), that is caught and treated
    the same way. If it raises `stats_2g.perm_test`'s 'no informative
    pair' for ONE specific rung — a finer-grained degeneracy than the
    coarse per-stratum pre-check catches — that single rung is dropped
    and the call retried, one rung at a time, until either a result
    comes back or every rung is gone. Any OTHER exception is not
    caught here; it propagates to the caller's own `collect_total`."""
    dropped = list(_degenerate_rungs(counts, strata, rungs))
    keep = [r for r in rungs if r not in dropped]
    while True:
        if not keep:
            reason = ("undefined: every eligible rung degenerate (predictor "
                      "constant inside every stratum)" if dropped else
                      "undefined: no eligible rung")
            return _undefined_result_2i(size_label, dropped, rungs, reason)
        pred = _scores_predictor_2i(counts, size_label, keep)
        try:
            prim = primary_2i(pred, out, strata, size_pred=size_label,
                              rungs=tuple(keep), n_perm=n_perm, n_boot=n_boot)
        except ValueError as e:
            msg = str(e)
            m = _NO_INFORMATIVE_PAIR_RE.search(msg)
            if m and m.group(1) in keep:
                dropped.append(m.group(1))
                keep = [r for r in keep if r != m.group(1)]
                continue
            if "no eligible rung" in msg:
                return _undefined_result_2i(size_label, dropped, rungs,
                                            "undefined: no eligible rung")
            raise
        break
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

# I-4: the verbatim disclosure the reason string AND the licensed
# sentence must carry when a test is undefined — 2i's own wording, not
# a template, so it can be asserted for byte-exact equality.
DISCLOSURE_UNDEFINED_2I = {
    "A": ("Test A was undefined (predictor degenerate on every comparable "
          "rung), so the cross-family transfer is untested, not absent"),
    "B": ("Test B was undefined (predictor degenerate on every comparable "
          "rung), so the within-family increment is untested, not absent"),
}


def _is_undefined_2i(prim: dict) -> bool:
    return (not prim.get("fires")
           and str(prim.get("named_inside") or "").startswith("undefined"))


def _fmt_T(T) -> str:
    """Freeze R-2: an undefined test's T is `None` (never NaN), so the
    reason string says so in words instead of raising on `{None:.4f}`."""
    return "undefined" if T is None else f"{T:.4f}"


def verdict_tree_2i(failures, A, B) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader failure(s): "
                          f"{list(failures)[:5]}",
                "disclosures": []}
    a, b = A["fires"], B["fires"]
    if a and not b:
        verdict = "SHARED"
    elif b and not a:
        verdict = "LINEAGE"
    elif a and b:
        verdict = "BOTH"
    else:
        verdict = "NEITHER"
    parts = [f"A: T={_fmt_T(A['stratified']['T'])}, p={A['stratified']['p']:.4g}, "
            f"fires={a}"]
    if A.get("named_inside"):
        parts.append(f"A {A['named_inside']}")
    parts.append(f"B: T={_fmt_T(B['stratified']['T'])}, p={B['stratified']['p']:.4g}, "
                f"fires={b}")
    if B.get("named_inside"):
        parts.append(f"B {B['named_inside']}")
    disclosures = []
    if _is_undefined_2i(A):
        disclosures.append(DISCLOSURE_UNDEFINED_2I["A"])
    if _is_undefined_2i(B):
        disclosures.append(DISCLOSURE_UNDEFINED_2I["B"])
    parts.extend(disclosures)
    return {"verdict": verdict, "reason": "; ".join(parts), "disclosures": disclosures}


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


# ------------------------------------------- the predictor stage's provenance
#
# FREEZE F-1 (THE CLASS DEFECT — 2h's F-2 / 3d's lesson, one stage
# over). Before this block the analyzer read x_B's raw draws
# (`sampler_counts_olmo`, which opens ONLY `<rung>.draws.jsonl.gz`) and
# never once opened `results/predictor/olmo1b/<rung>.json` — the record
# that says WHICH OLMo-2 1B checkpoint produced those draws, against
# WHICH item file, at which seed / k / temperature / truncation /
# dtype. Nor was `predictor_2i.json`'s own `sampling` block ever
# compared with anything: `run/seal_2i.py` writes `revision` from the
# code LITERAL `battery_2i.REV_1B_ENDPOINT`, so the seal's attestation
# is true by construction and carries no information about what
# actually ran. Demonstrated at the freeze: replacing all 34 records
# with ones claiming `revision: "main"`, `family: "pythia"`,
# `items_sha256: <wrong>`, `seeds: [99]`, `draws_per_seed: 1` left the
# verdict BYTE-IDENTICAL and produced no failure — i.e. a stage 1 run
# at `main` instead of the pinned stage-1 endpoint (exactly the regime
# confound design §9 dial d rules out) would have supplied Test B's
# predictor in silence and DECIDED the world between SHARED and
# LINEAGE/BOTH.
#
# Closed additively, in the shape 2h's F-2 fix took: every field is
# re-derived against a source that was already pinned — the manifest
# (`CHECKPOINTS_2I_SHA256`), the battery (`ITEMS_SHA_PIN`), 2i's own
# frozen constants — and the record's own ATTESTED verified total is
# compared against the count re-derived from the raw draws through the
# production reader. Nothing new is trusted; a disagreement is a
# refusal naming the rung and the field.

PREDICTOR_RECORD_PINS_2I = ("family", "size", "mode", "revision", "n_items",
                            "seeds", "draws_per_seed", "k_total", "temperature",
                            "truncation", "dtype", "untrained_seed",
                            "stream_namespace")


def predictor_record_failures_2i(rec: dict, *, rung, cap, entry_1b) -> list:
    """`results/predictor/olmo1b/<rung>.json` (written by
    `run/sample_2i.py`) against everything already pinned. Returns a
    list of failure strings; never raises for a well-typed dict."""
    from experiments.exp3.sampler import STREAM_NAMESPACE
    label = f"predictor olmo1b/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    want = {
        "family": bi.FAMILY, "size": bi.SIZE_PRED, "mode": "trained",
        # design §3.2 / dial d: x_B is the 1B's STAGE-1 ENDPOINT, the
        # regime-matched checkpoint — never `main`, whose anneal is a
        # different mixture and a different question.
        "revision": bi.REV_1B_ENDPOINT,
        "n_items": bt.N_ITEMS, "seeds": [bi.SAMPLING_SEED],
        "draws_per_seed": bi.DRAWS_PER_ITEM, "k_total": bi.DRAWS_PER_ITEM,
        "temperature": 1.0, "truncation": "none", "dtype": a2d.SAMPLING_DTYPE,
        "untrained_seed": None, "stream_namespace": STREAM_NAMESPACE,
    }
    for k in PREDICTOR_RECORD_PINS_2I:
        if rec.get(k) != want[k]:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {want[k]!r}")
    want_commit = entry_1b.get("commit")
    if rec.get("commit") != want_commit:
        bad.append(f"{label}: commit {rec.get('commit')!r} is not the manifest's "
                   f"{want_commit!r} for {bi.REV_1B_ENDPOINT}")
    # item alignment (freeze attack item 5): the sha of the item file AND
    # the answer column the draws were actually verified against.
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("answer_type") != cap["answer_type"]:
        bad.append(f"{label}: answer_type = {rec.get('answer_type')!r}, expected "
                   f"{cap['answer_type']!r}")
    answers = rec.get("answers")
    want_answers = [str(it["answer"]) for it in cap["eval_items"]]
    if not isinstance(answers, list) or len(answers) != len(want_answers):
        bad.append(f"{label}: answers column is not {len(want_answers)} long")
    else:
        n = sum(1 for a, b in zip(answers, want_answers) if a != b)
        if n:
            bad.append(f"{label}: the record's answer column differs from the "
                       f"pinned item file on {n} item(s) — the draws were "
                       f"verified against different items")
    if rec.get("max_new_tokens") != bt.max_new_tokens(rung):
        bad.append(f"{label}: max_new_tokens = {rec.get('max_new_tokens')!r}, "
                   f"expected 2c's {bt.max_new_tokens(rung)}")
    tallies = rec.get("per_seed_tallies")
    key = str(bi.SAMPLING_SEED)
    if not isinstance(tallies, dict) or key not in tallies or \
            not isinstance(tallies[key], dict):
        bad.append(f"{label}: per_seed_tallies has no seed-{key} entry")
    elif tallies[key].get("n_draws") != bt.N_ITEMS * bi.DRAWS_PER_ITEM:
        bad.append(f"{label}: {tallies[key].get('n_draws')!r} draws tallied, not "
                   f"the full {bt.N_ITEMS * bi.DRAWS_PER_ITEM} — a coverage "
                   f"shortfall, not a rate")
    if rec.get("draws_file") != bi.predictor_draws_path(bi.EXP2I, rung).name:
        bad.append(f"{label}: draws_file = {rec.get('draws_file')!r}, expected "
                   f"{bi.predictor_draws_path(bi.EXP2I, rung).name!r}")
    return bad


def load_predictor_records_2i(root, battery, *, entry_1b) -> dict:
    out = {}
    for rung in bt.RUNGS:
        p = bi.predictor_record_path(root, rung)
        if not p.is_file():
            raise FileNotFoundError(f"predictor record missing: {p}")
        rec = json.loads(p.read_text())
        bad = predictor_record_failures_2i(rec, rung=rung, cap=battery[rung],
                                           entry_1b=entry_1b)
        if bad:
            raise ValueError("; ".join(bad))
        out[rung] = rec
    return out


def _check_predictor_seal_sampling(seal: dict, records: dict) -> list:
    """`predictor_2i.json`'s `sampling` block is written by
    `run/seal_2i.py` from CODE LITERALS — it agrees with the design by
    construction and says nothing about the run. Measure it: every
    field must match both 2i's own frozen constants AND what all 34
    per-rung records actually recorded."""
    bad = []
    s = seal.get("sampling")
    if not isinstance(s, dict):
        return ["predictor seal: no sampling block"]
    for k, want in (("size", bi.SIZE_PRED), ("repo", bi.REPO_1B),
                    ("revision", bi.REV_1B_ENDPOINT), ("seed", bi.SAMPLING_SEED),
                    ("draws_per_item", bi.DRAWS_PER_ITEM), ("temperature", 1.0),
                    ("dtype", a2d.SAMPLING_DTYPE)):
        if s.get(k) != want:
            bad.append(f"predictor seal: sampling.{k} = {s.get(k)!r}, expected "
                       f"{want!r}")
    for rung, rec in records.items():
        if rec.get("revision") != s.get("revision"):
            bad.append(f"predictor seal: sampling.revision {s.get('revision')!r} "
                       f"disagrees with olmo1b/{rung}'s {rec.get('revision')!r}")
        if rec.get("commit") != s.get("commit"):
            bad.append(f"predictor seal: sampling.commit {s.get('commit')!r} "
                       f"disagrees with olmo1b/{rung}'s {rec.get('commit')!r}")
    return bad


def _check_predictor_counts_2i(seal: dict, records: dict, x_b: dict) -> list:
    """The other half of F-1's closure, the 3d shape: the record's own
    ATTESTED verified total and the seal's own per-item `counts` are
    compared against x_B AS THE VERDICT COMPUTES IT — re-derived from
    the raw draws through `sampler_counts_olmo`, the production reader.
    An attestation that disagrees with the bytes is a failure whichever
    side is right."""
    bad = []
    key = str(bi.SAMPLING_SEED)
    seal_counts = seal.get("counts")
    # freeze F-2's sibling: a `counts` that is not a dict used to make
    # this whole cross-check a silent no-op. A check that can be
    # switched off by the shape of the thing it checks is not a check.
    if not isinstance(seal_counts, dict):
        return [f"predictor seal: counts is {type(seal_counts).__name__}, not a "
                f"per-rung mapping — the seal's per-item claim cannot be "
                f"compared with the re-derived counts"]
    missing = sorted(r for r in x_b if r not in seal_counts)
    if missing:
        bad.append(f"predictor seal: counts carries no entry for {missing} — "
                   f"rung(s) x_B is computed over")
    for rung, counts in sorted(x_b.items()):
        rec = records.get(rung)
        if isinstance(rec, dict):
            t = rec.get("per_seed_tallies", {})
            att = t.get(key, {}).get("full_string") if isinstance(t, dict) else None
            if att != sum(counts):
                bad.append(f"predictor olmo1b/{rung}: attested full_string {att!r} "
                           f"disagrees with the {sum(counts)} re-derived from the "
                           f"draws")
        if isinstance(seal_counts, dict) and rung in seal_counts:
            got = seal_counts[rung]
            if list(got) != list(counts):
                n = (sum(1 for a, b in zip(got, counts) if a != b)
                     if isinstance(got, list) and len(got) == len(counts)
                     else "the wrong number of")
                bad.append(f"predictor seal: counts[{rung!r}] disagrees with the "
                           f"re-derived per-item counts on {n} item(s)")
    return bad


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
    # freeze F-2's sibling: `per_rung` that is not a dict, or that is
    # missing rungs, made this check a silent no-op (`r not in []` is
    # True for every rung, so every rung `continue`d). Require the
    # mapping the rule actually writes.
    if not isinstance(per_rung, dict):
        return [f"rung set olmo7b: per_rung is {type(per_rung).__name__}, not a "
                f"per-rung mapping"]
    absent = sorted(r for r in bt.RUNGS if r not in per_rung)
    if absent:
        bad.append(f"rung set olmo7b: per_rung carries no entry for {absent} — "
                   f"`rung_set_from_counts` scores all {len(bt.RUNGS)}")
    for r in bt.RUNGS:
        if r not in stage1_final or r not in per_rung:
            continue
        want = stage1_final[r]["correct"]
        got = per_rung[r].get("k")
        if got != want:
            bad.append(f"rung set olmo7b/{r}: per_rung k={got!r} disagrees with the "
                       f"endpoint's stage1_final correct={want!r}")
    return bad


def _check_rung_set_derivation(rung_set: dict, stage1_final: dict, floors: dict) -> list:
    """I-1: the rung set must be RE-DERIVED, not merely internally
    consistent with the endpoint's own count column
    (`_check_rung_set_vs_endpoint`, above, only checks `k == correct`
    — a file could carry the right per-rung counts and still have had
    its R_OLMO/R_CAP/R_EXTRA hand-edited or built by a different rule).
    `bi.rung_set_from_counts` applied to the endpoint's own `correct`
    column over ALL 34 rungs must reproduce `rung_set_2i.json`'s
    R_OLMO/R_CAP/R_EXTRA exactly — as sets (which rungs) and as lists
    in the file's own order (`rung_set_from_counts` is a deterministic,
    sorted, pure function of `counts`/`floors`, so an order mismatch
    with an identical rung SET means the file was hand-edited or built
    by a different rule, not that the rule is order-insensitive).
    Mismatch is a failure naming the differing rungs."""
    bad = []
    counts = {r: stage1_final[r]["correct"] for r in bt.RUNGS if r in stage1_final}
    if len(counts) != len(bt.RUNGS):
        missing = sorted(set(bt.RUNGS) - set(counts))
        bad.append(f"rung set re-derivation: stage1_final missing rung(s) {missing}")
        return bad
    rederived = bi.rung_set_from_counts(counts, floors)
    for key in ("R_OLMO", "R_CAP", "R_EXTRA"):
        want = list(rung_set.get(key, []))
        got = list(rederived[key])
        if set(got) != set(want):
            diff = sorted(set(got) ^ set(want))
            bad.append(f"rung set re-derivation/{key}: re-derived {sorted(got)} "
                       f"disagrees with the file's {sorted(want)} — differing "
                       f"rung(s) {diff}")
        elif got != want:
            bad.append(f"rung set re-derivation/{key}: content agrees but the "
                       f"order differs from the re-derived rule's own ({got} vs "
                       f"the file's {want})")
    return bad


# the value set `power_2i._one_test_power` writes to `declared_status`
# — shared so the writer and this reader can never drift apart (review
# minor: "whatever set power_2i writes — make them one shared
# constant"). THIN is I-3's addition: a test that loses so many rungs
# to degeneracy that fewer than three survive is not simulated at all.
DECLARED_STATUSES_2I = ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE", "THIN")


def _load_power(root, rung_set=None) -> dict:
    p = bi.power_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    r_cap = (set(rung_set["R_CAP"]) if isinstance(rung_set, dict)
            and "R_CAP" in rung_set else None)
    n_trained = len(bi.trained_steps_7b())
    for test in ("A", "B"):
        sub = rec.get(test)
        if not isinstance(sub, dict) or "declared_status" not in sub or \
                "declaration" not in sub:
            raise ValueError(f"{p}: test {test!r} missing declared_status/declaration")
        if sub["declared_status"] not in DECLARED_STATUSES_2I:
            raise ValueError(f"{p}: test {test!r} declared_status "
                             f"{sub['declared_status']!r} is not one of "
                             f"{DECLARED_STATUSES_2I}")
        rungs = sub.get("rungs")
        if not isinstance(rungs, list):
            raise ValueError(f"{p}: test {test!r} missing rungs")
        # freeze: EQUALITY, not `issubset`. `_one_test_power` writes
        # `rec["rungs"] = list(rungs)` where `rungs` IS R_CAP, so a
        # power record covering a strict subset — a table computed over
        # three of eleven rungs, say — is not a power statement about
        # the test that will run, and `issubset` accepted it.
        if r_cap is not None and set(rungs) != r_cap:
            raise ValueError(f"{p}: test {test!r} rungs {sorted(rungs)} are not "
                             f"R_CAP {sorted(r_cap)} (missing "
                             f"{sorted(r_cap - set(rungs))}, extra "
                             f"{sorted(set(rungs) - r_cap)})")
        if sub.get("n_trained_steps") != n_trained:
            raise ValueError(f"{p}: test {test!r} n_trained_steps "
                             f"{sub.get('n_trained_steps')!r} != {n_trained}")
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
                                 seal_sha=bh.PREDICTOR_2G_SHA, rungs=rungs69)
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
    """Total by construction. This is the ONE call in `run()` that sits
    outside every `collect_total` — it is evaluated while building the
    verdict dict itself, on BOTH branches — and `subprocess.run` raises
    `FileNotFoundError` when git is not on PATH and `NotADirectoryError`
    when `cwd` is gone. Either would have turned the very refusal those
    same conditions cause (`require_prereg_2i` needs git) into an
    uncaught exception, i.e. the INSUFFICIENT_DATA terminal would be
    unreachable on exactly the machine that most needs it. Freeze
    finding, closed one-directionally: an empty string, never a raise."""
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


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
    psl = require_seal_2i(bi.PREDICTOR_SEAL_TAG,
                          _predictor_seal_paths(root, predictor_rec),
                          tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"predictor seal: {m}" for m in psl["failures"]]

    rung_set, f = collect_total(lambda: _load_rung_set(root), "rung set")
    failures += f

    power, f = collect_total(lambda: _load_power(root, rung_set), "power record")
    failures += f
    esl = require_seal_2i(bi.ENDPOINT_SEAL_TAG, _endpoint_seal_paths(root),
                          tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"endpoint seal: {m}" for m in esl["failures"]]

    entry_stage1 = entry_main = entry_1b = None
    if manifest is not None:
        entry_stage1, f = collect_total(lambda: bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B),
                                        "7B endpoint entry")
        failures += f
        entry_1b, f = collect_total(lambda: bi.entry_1b_endpoint(manifest),
                                    "1B endpoint entry")
        failures += f
        entry_main, f = collect_total(lambda: bi.entry_main(manifest, bi.REPO_7B),
                                      "7B main entry")
        failures += f

    # F-1: x_B's own provenance, re-derived — WHICH OLMo-2 1B checkpoint,
    # against WHICH items, at which seed/k/temperature/truncation/dtype.
    _prec_ready = battery is not None and entry_1b is not None
    predictor_records, f = collect_total(
        lambda: load_predictor_records_2i(root, battery, entry_1b=entry_1b)
        if _prec_ready else
        (_ for _ in ()).throw(ValueError("battery or 1B manifest entry missing")),
        "predictor olmo1b records")
    failures += f
    if predictor_rec is not None and predictor_records is not None:
        sbad, f = collect_total(
            lambda: _check_predictor_seal_sampling(predictor_rec, predictor_records),
            "predictor seal sampling block")
        failures += f + (sbad or [])

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
                # freeze R-4: this site checks the runner's ATTESTED
                # fields only (`gate1_failures_7b`); the byte-level
                # re-derivation is the SEPARATE site below, labelled
                # "... re-derivation (byte identity)". The two labels
                # used to be prefix-ambiguous ("re-derivation" matched
                # both), which made every failure needle that names one
                # of them silently match the other.
                "gate 1 olmo7b attestation")
            failures += f + (gbad or [])

    if rung_set is not None and stage1_final is not None:
        rbad, f = collect_total(
            lambda: _check_rung_set_vs_endpoint(rung_set, stage1_final),
            "rung set vs endpoint")
        failures += f + (rbad or [])

    # I-1: the rung set must be RE-DERIVED (bi.rung_set_from_counts over
    # the endpoint's own correct column + the real floors), not merely
    # internally count-consistent — a hand-edited R_CAP/R_EXTRA can
    # still pass the check above.
    if rung_set is not None and stage1_final is not None and floors is not None:
        rbad2, f = collect_total(
            lambda: _check_rung_set_derivation(rung_set, stage1_final, floors),
            "rung set re-derivation")
        failures += f + (rbad2 or [])

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

    # F-1's other half (3d's shape): the per-rung record's ATTESTED
    # verified total and the seal's own per-item counts, against x_B as
    # the verdict computes it from the raw draws.
    if predictor_rec is not None and predictor_records is not None and x_b is not None:
        cbad, f = collect_total(
            lambda: _check_predictor_counts_2i(predictor_rec, predictor_records, x_b),
            "predictor counts vs the sealed attestation")
        failures += f + (cbad or [])

    _sweep_ready = (manifest is not None and battery is not None and
                    verify_fn is not None and predictor_rec is not None)
    sweep, f = collect_total(
        lambda: load_sweep_7b(root, battery, verify_fn, manifest=manifest,
                              predictor_sha=predictor_rec["sha256"]) if _sweep_ready
        else (_ for _ in ()).throw(ValueError("manifest, battery, verify criterion "
                                              "or predictor seal missing")),
        "sweep olmo7b")
    failures += f

    # C-1: gate 1 must RE-DERIVE identity, not trust attestation — this
    # runs AFTER the sweep is loaded (its own collect_total block, not
    # folded into the attested-only check above), comparing the
    # sweep's step928646 records against the already-committed
    # stage1_final endpoint records byte for byte.
    _gate_rederive_ready = (sweep is not None and stage1_final is not None and
                            gate1 is not None)
    g2bad, f = collect_total(
        lambda: gate1_rederive_7b(sweep[bi.ENDPOINT_STEP_7B], stage1_final, gate1)
        if _gate_rederive_ready else
        (_ for _ in ()).throw(ValueError("sweep, stage1_final endpoint records or "
                                         "gate 1 record missing")),
        "gate 1 olmo7b re-derivation (byte identity)")
    failures += f + (g2bad or [])

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
             "calibration_note": CALIBRATION_SENTENCE_2I,
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
        # I-4: an undefined test's disclosure rides on the licensed
        # sentence too, not only the reason string — a reader who never
        # opens `reason` still learns which half of the finding is
        # untested rather than absent.
        licensed = LICENSED[tree["verdict"]]
        if tree.get("disclosures"):
            licensed = "; ".join([licensed] + list(tree["disclosures"]))
        v = {"verdict": tree["verdict"], "reason": tree["reason"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2I,
             "calibration_note": CALIBRATION_SENTENCE_2I,
             "licensed_sentence": licensed, "referents": referents,
             "tests": {"A": A, "B": B}, "secondaries": sec, "n_perm": n_perm,
             "git_sha": _git_sha()}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        # freeze R-2: `allow_nan=False` guarantees the written verdict is
        # STRICT JSON (no bare `NaN`/`Infinity` tokens, which most non-
        # Python readers reject), and `_json_safe` makes that guarantee
        # reachable rather than a crash — every non-finite float becomes
        # `null` BEFORE the encoder sees it. Not only `_undefined_
        # result_2i`'s T: `stats_2g.d_from_pre` returns NaN for a rung
        # with no informative pair (reachable in the non-gating
        # `extra_rungs_raw` descriptive, whose R_EXTRA rungs are never
        # screened for constant y) and `bootstrap_d` returns NaN
        # lo/hi when no resample is finite. Presentation only — `v`
        # itself, and every statistic in it, is untouched.
        outp.write_text(json.dumps(_json_safe(v), indent=1, default=_jsonable,
                                   allow_nan=False))
    return v


def _json_safe(o):
    """Recursively replace non-finite floats (NaN, ±Infinity) with
    None so the written verdict is strict JSON. Containers are rebuilt;
    everything else is returned untouched for `_jsonable` to handle."""
    if isinstance(o, float) and not np.isfinite(o):
        return None
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _json_safe(x) for k, x in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_safe(x) for x in o]
    if isinstance(o, np.ndarray):
        return [_json_safe(x) for x in o.tolist()]
    return o


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
