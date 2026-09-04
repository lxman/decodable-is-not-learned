# experiments/exp2m/analyze_2m.py
"""Experiment 2m — the third family (design `experiment-2m-design.md`).
2l's two-test construction with the outcome model swapped to
SmolLM3-3B's stage-1 grid and BOTH committed predictors read
cross-family and UNCONDITIONED on 2g's base strata. Zero model contact
at analysis; nothing sampled anywhere in 2m.

Predictors, loaded through their OWN seals exactly as 2l loads them
(design §3.3): x_A^(256), its 64/128/192 ladder and four 64-draw blocks
re-derived from 2k's raw draws by `analyze_2k.load_tier_2k` at both
sizes and cross-checked by `seal_failures_2k`; x_B by 2i's
`sampler_counts_olmo` after `load_predictor_records_2i` and
`_check_predictor_seal_sampling`, cross-checked by
`_check_predictor_counts_2i`. Both seal tags must bind; both seal shas
must equal `battery_2m`'s literals; the composite must equal
`PREDICTOR_SHA_2M`, which every 2m record must carry.

The SmolLM3 trees (design §3.4–§3.6): three endpoint whichs against the
manifest's entries (two repos), sweep records against each grid step's
entry and the twin's `from_config` shape, their `endpoint_sha256`
against the composite re-derived from the 104 committed endpoint files,
every record's `dtype == DTYPE_2M`, gate 1 attested AND re-derived, the
halt marker refused, the rung set re-derived, the power record's
claims re-derived (B on BASE strata), the import surface pinned at
entry, exit and after the secondaries.

Tests: A = x_A^(256) on 2g's base strata; B = x_B on 2g's base strata
(dial b — no conditioning). Both over R_PRIMARY. Tree = `verdict_tree_
2m` → SHARED / PYTHIA-ONLY / OLMO-ONLY / NEITHER with 2m's disclosures.
S8 (new) reads the four committed big-model orders against 3B's. Every
loader refusal COLLECTED and delivered as INSUFFICIENT_DATA."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2M = Path(__file__).resolve().parent
if str(EXP2M.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2M.parent.parent))

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
from experiments.exp2l import analyze_2l as an2l  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402

RESULTS = EXP2M / "results"
REFERENTS_PATH_2M = EXP2M / "referents_2m.json"
REFERENTS_2M_SHA256 = "b237454c88f4de511faa3bf12f348089ff34fafe9e2e2eeaf32878ebfecfc9e1"  # Task 5
IMPORTED_SHA256_2M = {   # Task 5: pinned from tests/import_scan_2m.py (4 modules)
    bg.REPO / "experiments/exp2m/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    bg.REPO / "experiments/exp2m/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    bg.REPO / "experiments/exp2m/run/preflight_2m.py":
        "931f5d90210c1030069d34038f744750d4fee5ab23e3f106f6887cb9317da18d",
    bg.REPO / "experiments/exp2m/verify_referents_2m.py":
        "7baa94e1d7044f0d9f6fe5f6eb40a9567f8babd7a2a4f675ed369084869ff9cb",   # freeze F-2: item 9's hand pair + the F-2 assertions
}
WORLDS_2M = ("INSUFFICIENT_DATA", "SHARED", "PYTHIA-ONLY", "OLMO-ONLY", "NEITHER")
ALPHA, T_BAR, N_PERM, N_BOOT = st.ALPHA, st.T_BAR, st.N_PERM, st.N_BOOT
collect_total = an2i.collect_total
_run_test = an2i._run_test

CALIBRATION_SENTENCE_2M = (
    "Each test (A: Pythia-1b at 256 draws, B: OLMo-2 1B at 64 draws) is calibrated at alpha .01 "
    "on its own, unconditioned, on 2g's base strata; the reported world — SHARED, PYTHIA-ONLY, "
    "OLMO-ONLY or NEITHER — is their conjunction, and the union of the four worlds is not "
    "alpha-calibrated (3d's calibration lesson, stated in advance).")

# design §2 (what is known / what is sealed), condensed to the facts
KNOWN_INPUTS_CAVEAT_2M = (
    "Known to the designer before any SmolLM3-3B weight was loaded: everything through 2l's "
    "close-out — four sealed forecasts (2g's sampler competitor on Pythia-2.8b, 2h on 6.9b, 2i on "
    "OLMo-2 7B, 2l on OLMo-2 13B), 2j's mechanism reading, 2k's DENSITY result, and 2l's full "
    "texture on 13B (Test A .1261 with its per-rung table, Test B .1814, the four 64-draw blocks "
    ".072-.080, the ladder .0760/.1005/.1115/.1261, 410m .1270, within-alone .2045, "
    "cross-beyond-within .0770, the matched increment +.0687, S5 .1848, the antonym sign split); "
    "the Hub inventory of SmolLM3-3B's two repos (metadata only, 2026-09-03). The predictors "
    "x_A^(64/128/192/256) at 1b and 410m, x_B^(64) and 2j's pi are historically prior and "
    "tag-bound; nothing is sampled in 2m. Not known to anyone in this program: any output of "
    "SmolLM3-3B on any item at any checkpoint. The predictors were committed (2i 2026-08-26, 2k "
    "2026-08-30) before this family was named; the design is 2l's with the outcome swapped and "
    "Test B unconditioned; the instrument is tagged before any SmolLM3 weight loads, the endpoint "
    "stage sealed before the sweep, the projection sealed before gate 1 (design §2, §7). Corpus "
    "overlap is asymmetric and used by the worlds: OLMo-2's and SmolLM3's stage-1 mixes both draw "
    "on DCLM-derived web; Pythia's Pile predates DCLM (design §2).")

_L = {
    "SHARED": ("the essay's cross-family sentence generalises — \"smaller models of two families, "
               "given enough draws, forecast what a third family's training surfaces first\" — "
               "with Prediction 2's output-channel form holding across families at item grain on "
               "two predictor families and two outcome families (still one battery); the "
               "\"structure latent in the training distribution\" reading gains its second "
               "cross-family leg. Carried verbatim: NOT disjoint text — the corpus question (an "
               "outcome trained without web crawl: Comma v0.1) is the named next; the mechanism "
               "question stays open"),
    "PYTHIA-ONLY": ("the transfer does not follow corpus overlap (the predictor sharing the least "
                    "text with the outcome is the one that reaches it); OLMo-2 1B's 64-draw read "
                    "is the suspect, S1/S4 the descriptive adjudication; the essay's sentence "
                    "stands as 2l wrote it and gains \"on a second outcome family\"; the named "
                    "next is the OLMo-2 1B predictor at 256 draws (a predictor-side experiment)"),
    "OLMO-ONLY": ("the transfer follows the corpus; the shared-text caveat becomes the leading "
                  "account; the essay's cross-family sentence is bounded to \"between corpora "
                  "that share DCLM-era web\"; the corpus question is the named next, and the "
                  "essay says so"),
    "NEITHER": ("the cross-family finding is bounded at OLMo-2 as the outcome family in the essay "
                "and experiments.md; the full SmolLM3 record reported; the program's next step is "
                "Michael's call"),
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}
LICENSED_2M = {k: f"{v}. Disclosure (design §2): {KNOWN_INPUTS_CAVEAT_2M}" for k, v in _L.items()}
DISCLOSURE_THIN_2M = ("fewer than three rungs carried the primary (R_PRIMARY = R_3B ∩ 2k's nine) "
                      "— the reading is THIN regardless of the power record's declaration")
DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M = "fewer than three rungs actually carried Test "
DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2M = "R_PRIMARY is wider than the reading of Test "
DISCLOSURE_UNDERPOWERED_2M = {
    "A": ("Test A did not fire under DECLARED UNDERPOWERED IN ADVANCE: the Pythia-1b read of the "
          "third family's order is not detected at this resolution, neither confirmed nor ruled out"),
    "B": ("Test B did not fire under DECLARED UNDERPOWERED IN ADVANCE: the OLMo-2 1B read of the "
          "third family's order is not detected at this resolution, neither confirmed nor ruled out"),
}
# FREEZE F-3: `_run_test` stamps a `fires` key computed by `fires_2i` at
# 2g's bar on EVERY test it runs, including the descriptives. S5 and S8
# are non-gating with no alpha claim (design §5, dial g), so a reader of
# `secondaries[...]["test"]["fires"] == true` would be reading a firing
# rule that does not exist for them. The flag stays (it is `_run_test`'s
# own shape, frozen upstream); the row says in words what it is not.
NO_ALPHA_NOTE_2M = ("{name} is DESCRIPTIVE and non-gating (design §5): its `test.fires` is "
                    "`fires_2i` applied mechanically at 2g's bar and is NOT a firing rule for "
                    "{name} — no alpha claim is made, only T and p are reported, and nothing here "
                    "can move the verdict (a failure inside it lands in secondaries.failures, "
                    "never in referents.failures)")
DISCLOSURE_UNDEFINED_2M = {
    "A": ("Test A was undefined (the Pythia-1b predictor degenerate on every comparable rung), so "
          "the Pythia read is untested, not absent"),
    "B": ("Test B was undefined (the OLMo-2 1B predictor degenerate on every comparable rung), so "
          "the OLMo read is untested, not absent"),
}


def _thin_eligible_2m(test: str, res: dict) -> str | None:
    """2l F-4: a test that READ fewer than three rungs carries its own
    disclosure whatever |R_PRIMARY| was."""
    elig = list((res or {}).get("eligible") or [])
    if len(elig) >= 3:
        return None
    return (f"{DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M}{test}: it read {len(elig)} rung(s) {elig} — "
            f"dropped as n_pos-thin {list((res or {}).get('thin') or [])}, as predictor-degenerate "
            f"{list((res or {}).get('dropped_degenerate') or [])}; the reading is THIN regardless "
            f"of the power record's declaration, which simulates over R_PRIMARY minus the "
            f"degenerate rungs only")


def _partial_eligible_2m(test: str, res: dict, r_primary) -> str | None:
    """FREEZE F-1 (2l F-4's shape one level over). The power record
    declares over R_PRIMARY minus the PREDICTOR-degenerate rungs, and
    `check_power_claims_2m` re-derives exactly that set — but a rung can
    enter R_PRIMARY by clearing 2d's endpoint bar (as low as k = 9 on
    `add3_mid`/`sub4_mid`, 15 on `sub3_mid`, 19 on `arith_next`, all
    below the n_pos >= 20 eligibility floor) and then be dropped at
    analysis as n_pos-thin. 2l F-4's guard speaks only when fewer than
    THREE rungs survive, so `3 <= |eligible| < |R_PRIMARY|` left the
    declaration's scope — and therefore the licence's — silently wider
    than the reading's. Additive: a disclosure naming the rungs the test
    did not read. Mutually exclusive with `_thin_eligible_2m` by the
    `< 3` guard."""
    elig = list((res or {}).get("eligible") or [])
    prim = list(r_primary or [])
    if len(elig) < 3 or len(elig) >= len(prim):
        return None
    missing = [r for r in prim if r not in elig]
    return (f"{DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2M}{test}: it read {len(elig)} of the "
            f"{len(prim)} rungs in R_PRIMARY — {missing} did not carry it, dropped as n_pos-thin "
            f"{list((res or {}).get('thin') or [])} and as predictor-degenerate "
            f"{list((res or {}).get('dropped_degenerate') or [])}; the power record's declaration "
            f"and its rungs_simulated list cover R_PRIMARY minus the degenerate rungs, a WIDER "
            f"set than the reading, so the licence is bounded to the rungs named as read")


# ------------------------------------------------------------ pins

_EXPERIMENTS_ROOT_2M = str((bg.REPO / "experiments").resolve())


def check_imports_2m() -> None:
    """2j F-1 from commit one: every module under `experiments/` this
    process has imported must be covered by FROZEN_FILES_2M (its pinned
    dict must equal the documented tuple once pinned), 2g's
    FROZEN_IMPORT_SHA256_2G, the four tag-bound INSTRUMENT_BLOBS_2M,
    2j's/2k's/2l's own residual import pins (verified against disk
    here), or IMPORTED_SHA256_2M. Files under a `tests/` directory are
    excluded (disclosed, 2j's rule)."""
    if IMPORTED_SHA256_2M is None:
        raise RuntimeError("IMPORTED_SHA256_2M is None — the import surface is not pinned "
                           "(build incomplete)")
    if bm.FROZEN_SHA256_2M:
        pinned_frozen = {str(Path(p).resolve()) for p in bm.FROZEN_SHA256_2M}
        documented = {str(Path(p).resolve()) for p in bm.FROZEN_FILES_2M}
        if pinned_frozen != documented:
            raise RuntimeError(f"FROZEN_SHA256_2M does not cover FROZEN_FILES_2M: missing "
                               f"{sorted(documented - pinned_frozen)}; extra "
                               f"{sorted(pinned_frozen - documented)}")
    covered = {str(Path(p).resolve()) for p in bm.FROZEN_FILES_2M}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bm.INSTRUMENT_BLOBS_2M}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_2M.items()}
    upstream = {str(Path(p).resolve()): v for p, v in an2j.IMPORTED_SHA256_2J.items()}
    upstream.update({str(Path(p).resolve()): v for p, v in an2k.IMPORTED_SHA256_2K.items()})
    upstream.update({str(Path(p).resolve()): v for p, v in an2l.IMPORTED_SHA256_2L.items()})
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
        if not s.startswith(_EXPERIMENTS_ROOT_2M + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned or s in upstream:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


# ---------------------------------------------------- record failures

def _record_common_failures_2m(rec: dict, *, label, cap, verify_fn, seal_tag) -> list:
    """2l's `_record_common_failures_2l` with 2m's size/family, the
    composite predictor sha and the DTYPE pin (design §3.4 / dial l)."""
    bad = []
    for k, v in (("size", bm.SIZE_OUT), ("family", bm.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bm.DTYPE_2M)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("predictor_sha") != bm.PREDICTOR_SHA_2M:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bm.PREDICTOR_SHA_2M}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bt.N_ITEMS or len(conts) != bt.N_ITEMS:
        bad.append(f"{label}: bits/continuations are not {bt.N_ITEMS} long")
        return bad
    if rec.get("correct") != sum(bits):
        bad.append(f"{label}: correct {rec.get('correct')} != sum(bits) {sum(bits)}")
    bad += an2i._re_verify(conts, bits, cap, verify_fn, label)
    return bad


def endpoint_record_failures_2m(rec: dict, *, which, rung, cap, entry, verify_fn) -> list:
    label = f"endpoint smollm3_3b {which}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    if rec.get("which") != which:
        bad.append(f"{label}: which = {rec.get('which')!r}, expected {which!r}")
    if rec.get("commit") != entry.get("commit"):
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry.get('commit')}")
    bad += _record_common_failures_2m(rec, label=label, cap=cap, verify_fn=verify_fn,
                                      seal_tag=bm.PREDICTOR_TAGS_2M)
    return bad


def step_record_failures_2m(rec: dict, *, step, rung, cap, entry, verify_fn, endpoint_sha) -> list:
    """`step` is an int or `TWIN`; the twin's record must carry
    `commit None` and `kind "from_config"` (2i's twin branch)."""
    key = bm.TWIN if step == bm.TWIN else f"step{int(step)}"
    label = f"smollm3_3b/{key}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    want_step = bm.TWIN if step == bm.TWIN else int(step)
    if rec.get("step") != want_step:
        bad.append(f"{label}: step = {rec.get('step')!r}, expected {want_step!r}")
    if step == bm.TWIN:
        if rec.get("commit") is not None:
            bad.append(f"{label}: commit is {rec.get('commit')!r}, expected None")
        if rec.get("kind") != "from_config":
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")
    elif rec.get("commit") != entry["commit"]:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")
    if rec.get("endpoint_sha256") != endpoint_sha:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")
    bad += _record_common_failures_2m(rec, label=label, cap=cap, verify_fn=verify_fn,
                                      seal_tag=bm.ENDPOINT_SEAL_TAG_2M)
    return bad


def which_coherence_failures_2m(which: str, records: dict) -> list:
    """FREEZE F-2 (2i F-1 / 3d F-2's shape on the endpoint side): the
    three endpoint `which`es have no checkpoint record, so — unlike a
    sweep step, whose `_checkpoint.json` digest is MEASURED against all
    34 item records — nothing checked that a which's 34 records came
    from ONE load. The stage is resumable (`endpoint_2m.run` re-loads
    and evaluates only the missing rungs), `load_thin_3b` goes through
    the ordinary HF cache with no sha verification against the
    manifest's `lfs_sha256`, and the rung set's own sha table and the
    104-file composite are both computed AFTER the records, so a mixed
    which is internally consistent. Additive: every record of a which
    must carry the same non-empty tensor digest, the same commit and
    the same config source."""
    bad = []
    for field, label in (("weight_sha256", "tensor digest"), ("commit", "commit"),
                         ("config_source", "config source")):
        vals = sorted({str(rec.get(field)) for rec in records.values()})
        if len(vals) > 1:
            bad.append(f"endpoint smollm3_3b {which}: the 34 records carry {len(vals)} different "
                       f"{label}s {vals} — they did not come from one load")
        elif vals and vals[0] in ("None", ""):
            bad.append(f"endpoint smollm3_3b {which}: every record's {label} is empty")
    return bad


def load_endpoint_which_2m(root, which, battery, verify_fn, *, entry) -> dict:
    out = {}
    for rung in bt.RUNGS:
        p = bm.endpoint_record_path(root, which, rung)
        if not p.is_file():
            raise FileNotFoundError(f"endpoint record missing: {p}")
        rec = json.loads(p.read_text())
        bad = endpoint_record_failures_2m(rec, which=which, rung=rung, cap=battery[rung],
                                          entry=entry, verify_fn=verify_fn)
        if bad:
            raise ValueError("; ".join(bad))
        out[rung] = rec
    coh = which_coherence_failures_2m(which, out)   # freeze F-2
    if coh:
        raise ValueError("; ".join(coh))
    return out


def checkpoint_record_failures_2m(crec: dict, *, step, entry: dict, step_records: dict) -> list:
    """2l F-2: revision, commit and the tensor digest MEASURED, the sha
    table's coverage over every candidate file (the index file has no
    LFS pin and is pinned by the commit alone — disclosed)."""
    bad = []
    for k in ("revision", "commit"):
        if crec.get(k) != entry.get(k):
            bad.append(f"smollm3_3b/step{int(step)}: checkpoint record {k} {crec.get(k)!r} is not "
                       f"the manifest's {entry.get(k)!r}")
    shas = crec.get("sha256")
    if not isinstance(shas, dict):
        bad.append(f"smollm3_3b/step{int(step)}: checkpoint record sha256 is not a table")
    else:
        uncovered = sorted(set(entry.get("files", [])) - set(shas))
        if uncovered:
            bad.append(f"smollm3_3b/step{int(step)}: the checkpoint record attests no sha for "
                       f"{uncovered} — a sha table over a subset of the candidate files is a "
                       f"coverage claim about an unstated set")
    dg = crec.get("digest")
    off = sorted(r for r, rec in step_records.items() if rec.get("weight_sha256") != dg)
    if off:
        bad.append(f"smollm3_3b/step{int(step)}: the checkpoint record's tensor digest {dg!r} is not "
                   f"the digest the item records carry on {off}")
    return bad


def twin_checkpoint_record_failures_2m(crec: dict, *, entry: dict, step_records: dict) -> list:
    """The twin's bespoke record measured: no commit, `from_config`,
    the pinned seed, the config source at the endpoint's commit, the
    digest the twin's item records carry."""
    bad = []
    if crec.get("revision") != bm.TWIN:
        bad.append(f"smollm3_3b/twin: checkpoint record revision {crec.get('revision')!r} is not 'twin'")
    if crec.get("commit") is not None:
        bad.append(f"smollm3_3b/twin: checkpoint record commit {crec.get('commit')!r} is not None")
    if crec.get("kind") != "from_config":
        bad.append(f"smollm3_3b/twin: checkpoint record kind {crec.get('kind')!r} is not 'from_config'")
    if crec.get("seed") != bm.TWIN_SEED:
        bad.append(f"smollm3_3b/twin: checkpoint record seed {crec.get('seed')!r} is not {bm.TWIN_SEED}")
    want_src = f"{bm.REPO_CKPT}@{entry.get('config_commit')}"
    if crec.get("config_source") != want_src:
        bad.append(f"smollm3_3b/twin: config_source {crec.get('config_source')!r} is not {want_src!r}")
    dg = crec.get("digest")
    off = sorted(r for r, rec in step_records.items() if rec.get("weight_sha256") != dg)
    if off:
        bad.append(f"smollm3_3b/twin: the checkpoint record's tensor digest {dg!r} is not the "
                   f"digest the item records carry on {off}")
    return bad


def load_sweep_3b(root, battery, verify_fn, *, manifest, endpoint_sha, steps=None, rungs=None) -> dict:
    """Every grid step + the twin: 34 records each through
    `step_record_failures_2m`, plus the checkpoint record's LFS shas
    against the manifest, empty loading info and the F-2 measurements
    (the twin through its own bespoke check)."""
    steps = tuple(steps) if steps is not None else bm.GRID_3B + (bm.TWIN,)
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for step in steps:
        entry = bm.entry_3b(manifest, step)
        out[step] = {}
        for rung in rungs:
            p = bm.record_path(root, step, rung)
            if not p.is_file():
                raise FileNotFoundError(f"sweep record missing: {p}")
            rec = json.loads(p.read_text())
            bad = step_record_failures_2m(rec, step=step, rung=rung, cap=battery[rung], entry=entry,
                                          verify_fn=verify_fn, endpoint_sha=endpoint_sha)
            if bad:
                raise ValueError("; ".join(bad))
            out[step][rung] = rec
        cp = bm.checkpoint_record_path(root, step)
        if not cp.is_file():
            raise FileNotFoundError(f"checkpoint record missing: {cp}")
        crec = json.loads(cp.read_text())
        if crec.get("size") != bm.SIZE_OUT or crec.get("step") != (bm.TWIN if step == bm.TWIN else int(step)):
            raise ValueError(f"smollm3_3b/{step}: checkpoint record size/step "
                             f"{crec.get('size')!r}/{crec.get('step')!r}")
        if step == bm.TWIN:
            cbad = twin_checkpoint_record_failures_2m(crec, entry=entry, step_records=out[step])
        else:
            for name, want in entry.get("lfs_sha256", {}).items():
                if crec.get("sha256", {}).get(name) != want:
                    raise ValueError(f"smollm3_3b/step{step}: downloaded {name} sha "
                                     f"{crec.get('sha256', {}).get(name)} != manifest {want}")
            if crec.get("loading_info", {}) != {"missing_keys": 0, "unexpected_keys": 0,
                                                 "mismatched_keys": 0}:
                raise ValueError(f"smollm3_3b/step{step}: loading info not empty")
            cbad = checkpoint_record_failures_2m(crec, step=step, entry=entry, step_records=out[step])
        if cbad:
            raise ValueError("; ".join(cbad))
    return out


# ------------------------------------------------------------ outcomes

def outcomes_3b(sweep: dict, *, rungs=None, steps=None) -> dict:
    """`analyze_2l.outcomes_13b`'s body over `trained_steps_3b()` (26
    points) or a SUBSET of it (`steps`, the log-head sensitivity). The
    twin is never in an outcome: a `steps` containing it, or any step
    off the grid, is refused."""
    steps = tuple(steps) if steps is not None else bm.trained_steps_3b()
    if any(s not in bm.GRID_3B for s in steps):
        raise ValueError(f"outcomes_3b: steps {steps} are not all on the frozen grid")
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


def rung_level_3b(out: dict, floors: dict, *, rungs=None) -> dict:
    steps = bm.trained_steps_3b()
    rungs = tuple(rungs) if rungs is not None else tuple(out)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in steps if s in c and st2d.binomial_bar(c[s], bt.N_ITEMS, floors[rung])["significant"]]
        final = bm.ENDPOINT_STEP_2M in clears
        res[rung] = {"s_star": clears[0] if clears else None, "clears": clears,
                     "final_clears": final, "transient_clears": ([] if final else clears)}
    return res


def _first_correct_outcome_3b(out: dict, rungs) -> dict:
    last_step = max(bm.trained_steps_3b())
    return {r: {"y": [0 if fc is None else (last_step + 1 - fc) for fc in out[r]["first"]],
                "n_pos": out[r]["n_pos"]} for r in rungs}


def collapses_3b(sweep: dict, *, rungs, threshold: int = 450) -> list:
    """2h's checkpoint-local pathology: a (step, rung) where ≥
    `threshold` of the 500 continuations are one identical string.
    Descriptive; the twin included (its init babble is the first
    entry)."""
    from collections import Counter
    res = []
    for step in sorted(sweep, key=lambda s: (s == bm.TWIN, s if s != bm.TWIN else 0)):
        for r in rungs:
            rec = sweep[step][r]
            top, n = Counter(rec["continuations"]).most_common(1)[0]
            if n >= threshold:
                res.append({"rung": r, "step": step, "continuation": top,
                            "n_identical": int(n), "correct": int(rec["correct"])})
    return res


def non_monotone_3b(out: dict, rungs) -> dict:
    res = {}
    for r in rungs:
        c = out[r]["counts_by_step"]
        steps = sorted(c)
        mx = max(c.values()) if c else 0
        drops = [[int(a), int(b), int(c[a]), int(c[b])] for a, b in zip(steps, steps[1:])
                 if c[a] - c[b] > 0.2 * mx]
        res[r] = {"drops": drops, "n_drops": len(drops), "max": int(mx)}
    return res


def ceiling_fraction_3b(out: dict, rungs, *, n_steps: int) -> dict:
    """design §4 (the outcome ceiling, disclosed): items verifying at
    EVERY grid point sit at y == n_steps; their share of the rung and
    of its positives, printed per rung. No rule is built on it."""
    res = {}
    for r in rungs:
        y = out[r]["y"]
        n_c = int(sum(1 for v in y if v == n_steps))
        n_pos = int(out[r]["n_pos"])
        res[r] = {"n_ceiling": n_c, "fraction": n_c / bt.N_ITEMS, "n_pos": n_pos,
                  "fraction_of_positives": (n_c / n_pos) if n_pos else None}
    return res


# ------------------------------------------------------------ rung set

def _load_rung_set_2m(root) -> dict:
    p = bm.rung_set_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    for k in ("R_3B", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA", "per_rung", "primary_is_the_nine",
              "endpoint_file_sha256"):
        if k not in rec:
            raise ValueError(f"{p}: missing {k!r}")
    if not set(rec["R_PRIMARY"]).issubset(set(bm.R_CAP_2K)):
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")
    if set(rec["R_PRIMARY"]) | set(rec["R_ELEVEN_EXTRA"]) | set(rec["R_EXTRA"]) != set(rec["R_3B"]):
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_3B")
    return rec


def _check_rung_set_vs_endpoint_2m(rung_set: dict, stage1_final: dict) -> list:
    bad = []
    per_rung = rung_set.get("per_rung", {})
    if not isinstance(per_rung, dict):
        return [f"rung set smollm3_3b: per_rung is {type(per_rung).__name__}, not a mapping"]
    absent = sorted(r for r in bt.RUNGS if r not in per_rung)
    if absent:
        bad.append(f"rung set smollm3_3b: per_rung carries no entry for {absent}")
    for r in bt.RUNGS:
        if r not in stage1_final or r not in per_rung:
            continue
        if per_rung[r].get("k") != stage1_final[r]["correct"]:
            bad.append(f"rung set smollm3_3b/{r}: per_rung k={per_rung[r].get('k')!r} disagrees with "
                       f"the endpoint's stage1_final correct={stage1_final[r]['correct']!r}")
    return bad


def _check_rung_set_derivation_2m(rung_set: dict, stage1_final: dict, floors: dict) -> list:
    bad = []
    counts = {r: stage1_final[r]["correct"] for r in bt.RUNGS if r in stage1_final}
    if len(counts) != len(bt.RUNGS):
        return [f"rung set re-derivation smollm3_3b: stage1_final missing rung(s) "
                f"{sorted(set(bt.RUNGS) - set(counts))}"]
    red = bm.rung_set_from_counts_2m(counts, floors)
    for key in ("R_3B", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA"):
        want, got = list(rung_set.get(key, [])), list(red[key])
        if got != want:
            bad.append(f"rung set re-derivation smollm3_3b/{key}: re-derived {got} disagrees with "
                       f"the file's {want}")
    if bool(rung_set.get("primary_is_the_nine")) != bool(red["primary_is_the_nine"]):
        bad.append("rung set re-derivation smollm3_3b/primary_is_the_nine disagrees")
    return bad


def _check_rung_set_endpoint_shas_2m(rung_set: dict, root) -> list:
    """2l F-3: the attested `endpoint_file_sha256` table measured —
    exactly the 102 endpoint records, each at its committed sha."""
    root = Path(root)
    got = rung_set.get("endpoint_file_sha256")
    if not isinstance(got, dict):
        return [f"rung set smollm3_3b: endpoint_file_sha256 is {type(got).__name__}, not a table "
                f"over the {len(bm.ENDPOINT_WHICH_2M) * len(bt.RUNGS)} endpoint records"]
    want = {}
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            p = bm.endpoint_record_path(root, which, r)
            if not p.is_file():
                return [f"rung set smollm3_3b: endpoint record {p} is missing, so "
                        f"endpoint_file_sha256 cannot be measured"]
            want[str(p.relative_to(root))] = bg.sha256_file(p)
    bad = []
    missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
    if missing:
        bad.append(f"rung set smollm3_3b: endpoint_file_sha256 attests nothing for {missing}")
    if extra:
        bad.append(f"rung set smollm3_3b: endpoint_file_sha256 carries {extra}, which are not the "
                   f"endpoint records")
    for rel in sorted(set(want) & set(got)):
        if got[rel] != want[rel]:
            bad.append(f"rung set smollm3_3b: endpoint_file_sha256[{rel}] {str(got[rel])[:12]} is "
                       f"not the committed record's {want[rel][:12]}")
    return bad


def _endpoint_seal_paths_2m(root) -> list:
    paths = [bm.rung_set_path(root), bm.power_path(root)]
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            paths.append(bm.endpoint_record_path(root, which, r))
    return paths


# --------------------------------------------------------------- power

POWER_CLAIM_FIELDS_2M = ("dropped_degenerate", "rungs_simulated", "n_pos_lower_bound", "t_bar",
                         "alpha", "thin")
BLOCK_SD_FIELDS_2M = ("n_sim", "mean_block_sd_at_declare", "mean_block_sd_null",
                      "per_block_mean_T_at_declare", "blocks")


def load_power_2m(root, r_primary, predictor_sha) -> dict:
    p = bm.power_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    if not isinstance(rec, dict):
        raise ValueError(f"{p}: not a 2m power record")
    for test in ("A", "B"):
        sub = rec.get(test)
        if not isinstance(sub, dict) or "declared_status" not in sub or "declaration" not in sub:
            raise ValueError(f"{p}: test {test!r} missing declared_status/declaration")
        if sub["declared_status"] not in an2i.DECLARED_STATUSES_2I:
            raise ValueError(f"{p}: test {test!r} declared_status {sub['declared_status']!r}")
        if not isinstance(sub.get("rungs"), list) or set(sub["rungs"]) != set(r_primary):
            raise ValueError(f"{p}: test {test!r} rungs {sub.get('rungs')} != R_PRIMARY "
                             f"{sorted(r_primary)}")
        if sub.get("n_trained_steps") != bm.n_trained_3b():
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bm.n_trained_3b()}")
    if rec.get("predictor_sha256") != predictor_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")
    bsd = rec.get("block_sd_A")
    if not isinstance(bsd, dict) or any(k not in bsd for k in BLOCK_SD_FIELDS_2M):
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — {BLOCK_SD_FIELDS_2M}")
    if sorted(rec.get("r_primary") or []) != sorted(r_primary):
        raise ValueError(f"{p}: r_primary {rec.get('r_primary')!r} is not the rung set's "
                         f"R_PRIMARY {sorted(r_primary)}")
    if bool(rec.get("primary_is_the_nine")) != (tuple(sorted(r_primary)) == tuple(sorted(bm.R_CAP_2K))):
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


def check_power_claims_2m(power, x_a256, x_b, strata, r_primary, stage1_final) -> list:
    """2k F-2: every re-derivable claim of both tests' power blocks
    against the analyzer's own re-derivation — BOTH on the base strata
    (dial b: Test B is unconditioned)."""
    bad = []
    for test, x in (("A", x_a256), ("B", x_b)):
        prim = (power or {}).get(test)
        if not isinstance(prim, dict):
            bad.append(f"2m power claims {test}: no block")
            continue
        missing = [k for k in POWER_CLAIM_FIELDS_2M if k not in prim]
        if missing:
            bad.append(f"2m power claims {test}: the record does not attest {missing}")
        dropped = list(an2i._degenerate_rungs(x, strata, r_primary))
        keep = [r for r in r_primary if r not in dropped]
        if "dropped_degenerate" in prim and sorted(prim["dropped_degenerate"] or []) != sorted(dropped):
            bad.append(f"2m power claims {test}: dropped_degenerate "
                       f"{sorted(prim['dropped_degenerate'] or [])} != {sorted(dropped)}")
        if "rungs_simulated" in prim and sorted(prim["rungs_simulated"] or []) != sorted(keep):
            bad.append(f"2m power claims {test}: rungs_simulated "
                       f"{sorted(prim['rungs_simulated'] or [])} != {sorted(keep)}")
        if "n_pos_lower_bound" in prim:
            want = ({r: int(stage1_final[r]["correct"]) for r in r_primary} if stage1_final else None)
            got = prim["n_pos_lower_bound"]
            if want is None:
                bad.append(f"2m power claims {test}: n_pos_lower_bound cannot be re-derived")
            elif not isinstance(got, dict) or {k: int(v) for k, v in got.items()} != want:
                bad.append(f"2m power claims {test}: n_pos_lower_bound {got!r} != the endpoint's {want!r}")
        for field, want in (("t_bar", T_BAR), ("alpha", ALPHA)):
            if field in prim and prim[field] != want:
                bad.append(f"2m power claims {test}: {field} = {prim[field]!r}, not {want!r}")
        if "thin" in prim and bool(prim["thin"]) != (len(keep) < 3):
            bad.append(f"2m power claims {test}: thin = {prim['thin']!r} against {len(keep)} rung(s)")
        if test == "A":
            bsd = (power or {}).get("block_sd_A")
            if isinstance(bsd, dict) and "rungs" in bsd and sorted(bsd["rungs"] or []) != sorted(keep):
                bad.append(f"2m power claims block_sd_A: rungs {sorted(bsd['rungs'] or [])} is not "
                           f"Test A's non-degenerate set {sorted(keep)}")
    return bad


# -------------------------------------------------------------- predictors

def load_predictors_2m(root_2i, root_2k, *, battery, verify_fn, tag_exists=None,
                       blobs_bound=None) -> tuple:
    """`analyze_2l.load_predictors_2l`'s body with 2m's literals and
    labels: both predictors through their own sealed readers; every
    seal bound; every sha measured. Returns (failures, ctx) with ctx =
    {seal_2k, seal_2i, predictor_sha, cells_2k{size: cells}, x_b,
    bits_b, rows_2i, r_cap_2i, psl_2k, psl_2i}."""
    failures, ctx = [], {}
    root_2i, root_2k = Path(root_2i), Path(root_2k)
    for m in bk.halt_markers(root_2k):
        failures.append(f"2m predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")
    seal_2k, f = collect_total(lambda: json.loads(bk.seal_path(root_2k).read_text()),
                               "2m predictor 2k seal read");                       failures += f
    psl_2k = an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(root_2k, seal_2k),
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2m predictor 2k seal binding: {m}" for m in psl_2k["failures"]]
    seal_2i, f = collect_total(lambda: an2i._load_predictor_seal_content(root_2i),
                               "2m predictor 2i seal content");                    failures += f
    psl_2i = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(root_2i, seal_2i),
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2m predictor 2i seal binding: {m}" for m in psl_2i["failures"]]
    if isinstance(seal_2k, dict) and seal_2k.get("sha256") != bm.SEAL_2K_SHA256:
        failures.append(f"2m predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")
    if isinstance(seal_2i, dict) and seal_2i.get("sha256") != bm.SEAL_2I_SHA256:
        failures.append(f"2m predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")
    predictor_sha = bm.PREDICTOR_SHA_2M
    if isinstance(seal_2k, dict) and isinstance(seal_2i, dict):
        got = bm.predictor_sha_2m(str(seal_2k.get("sha256")), str(seal_2i.get("sha256")))
        if got != bm.PREDICTOR_SHA_2M:
            failures.append("2m predictor composite sha does not re-derive from the two seals")
    cells_2k = {}
    if battery is not None and verify_fn is not None:
        for size in bk.SIZES_2K:
            def _tier(size=size):
                return an2k.load_tier_2k(root_2k, size, battery=battery, verify_fn=verify_fn,
                                         rungs=bm.R_CAP_2K)
            res, f = collect_total(_tier, f"2m predictor 2k tier {size} load");   failures += f
            f2, c = res if res is not None else ([], {})
            failures += [f"2m predictor {m}" for m in f2]
            cells_2k[size] = c
        if seal_2k is not None and all(len(cells_2k.get(s, {})) == len(bm.R_CAP_2K) for s in bk.SIZES_2K):
            sb, f = collect_total(lambda: an2k.seal_failures_2k(seal_2k, cells_2k, root_2k),
                                  "2m predictor 2k seal vs re-derivation")
            failures += f + [f"2m predictor {m}" for m in (sb or [])]
    else:
        failures.append("2m predictor 2k tier: not loaded (battery or verify missing)")
    rs2i, f = collect_total(lambda: an2i._load_rung_set(root_2i), "2m predictor 2i rung set file")
    failures += f
    if rs2i is not None and tuple(sorted(rs2i["R_CAP"])) != tuple(sorted(bm.R_CAP_2K)):
        failures.append(f"2m predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")
    manifest_2i, f = collect_total(
        lambda: bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256),
        "2m predictor 2i manifest");                                               failures += f
    entry_1b = None
    if manifest_2i is not None:
        entry_1b, f = collect_total(lambda: bi.entry_1b_endpoint(manifest_2i),
                                    "2m predictor 2i 1B endpoint entry");          failures += f
    _prec = battery is not None and entry_1b is not None
    records_2i, f = collect_total(
        lambda: an2i.load_predictor_records_2i(root_2i, battery, entry_1b=entry_1b) if _prec
        else (_ for _ in ()).throw(ValueError("battery or 1B entry missing")),
        "2m predictor 2i olmo1b records");                                         failures += f
    if seal_2i is not None and records_2i is not None:
        sb, f = collect_total(lambda: an2i._check_predictor_seal_sampling(seal_2i, records_2i),
                              "2m predictor 2i seal sampling block")
        failures += f + [f"2m predictor {m}" for m in (sb or [])]
    _xb = battery is not None and verify_fn is not None
    x_b, f = collect_total(lambda: bi.sampler_counts_olmo(bm.R_CAP_2K, root=root_2i, battery=battery,
                                                          verify_fn=verify_fn) if _xb
                           else (_ for _ in ()).throw(ValueError("battery/verify missing")),
                           "2m predictor x_B counts olmo1b");                     failures += f
    if seal_2i is not None and records_2i is not None and x_b is not None:
        cb, f = collect_total(lambda: an2i._check_predictor_counts_2i(seal_2i, records_2i, x_b),
                              "2m predictor x_B counts vs the sealed attestation")
        failures += f + [f"2m predictor {m}" for m in (cb or [])]

    def _rows_bits():
        rows, bits = {}, {}
        for r in bm.R_CAP_2K:
            rows[r] = fn.draw_rows_2i(root_2i, r)
            bits[r] = fn.verified_bits(rows[r], battery[r], verify_fn)
            if fn.counts_from_bits(bits[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")
        return rows, bits
    rb, f = collect_total(lambda: _rows_bits() if (_xb and x_b) else
                          (_ for _ in ()).throw(ValueError("x_B missing")), "2m predictor x_B rows and bits")
    failures += f
    rows_2i, bits_b = rb if rb is not None else (None, None)
    ctx.update(seal_2k=seal_2k, seal_2i=seal_2i, predictor_sha=predictor_sha, cells_2k=cells_2k,
               x_b=x_b, bits_b=bits_b, rows_2i=rows_2i, r_cap_2i=rs2i, psl_2k=psl_2k, psl_2i=psl_2i)
    return failures, ctx


# ------------------------------------------------------------ secondaries

def s3_paired_difference_2m(x_a, x_b, out, strata, rungs, *, n_boot=N_BOOT, seed=0) -> dict:
    """design §1/§5 S3: T_B − T_A on ONE tie structure (same outcome,
    same base strata, same rungs), with a paired item bootstrap within
    each rung (items resampled with replacement, both predictors read
    on the SAME resample; per-rung within-stratum Somers' D via 2g's
    `somers_d_within`, T the plain mean over `rungs`). Descriptive: the
    densities differ (256 vs 64 draws). `rungs` should be the
    intersection of the two tests' eligible sets."""
    rng = np.random.default_rng(seed)
    rungs = [r for r in rungs if r in x_a and r in x_b and r in out]
    n = bt.N_ITEMS

    def _t(idx_by_rung):
        da, db = [], []
        for r in rungs:
            idx = idx_by_rung[r]
            y = [out[r]["y"][i] for i in idx]
            s = [strata[r]["strata"][i] for i in idx]
            da.append(st.somers_d_within([x_a[r][i] for i in idx], y, s)["d"])
            db.append(st.somers_d_within([x_b[r][i] for i in idx], y, s)["d"])
        if not da:
            return None, None
        return float(np.nanmean(da)), float(np.nanmean(db))

    t_a, t_b = _t({r: list(range(n)) for r in rungs})
    diffs = []
    for _ in range(n_boot if rungs else 0):
        a, b = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})
        if a is not None and b is not None and np.isfinite(a) and np.isfinite(b):
            diffs.append(b - a)
    ci = [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))] if diffs else None
    diff = None if (t_a is None or t_b is None or not np.isfinite(t_a) or not np.isfinite(t_b)) else t_b - t_a
    return {"rungs": rungs, "T_A": t_a, "T_B": t_b, "diff_B_minus_A": diff, "ci95": ci,
            "n_boot": len(diffs), "n_boot_requested": n_boot,
            "note": "paired item bootstrap within rung on one tie structure; the densities differ "
                    "(256 vs 64 draws); descriptive, no alpha claim"}


def s4_matched_2m(bits_b, x_a64, x_a256, out, strata, rungs) -> dict:
    """S4 (design §5): x_B thinned per rung to k_g = clip(round(256·r̄_A/
    r̄_B), 1, 64) (2k's rule) against x_A^(256) on the sealed outcome,
    T without permutation (2j's `t_only`); the increment = thinned-B T −
    T_A256 — with both predictors cross-family, which family's small
    model reads the third family's order better at equal draws."""
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


def s5_answer_prior_2m(rows_2i, battery, out, strata, rungs, **kw) -> dict:
    """S5 (design §5, dial g — non-gating): 2j's wrong-target propensity
    π on 2i's sealed OLMo-2 1B draws, against 3B's sealed order with
    2i's statistic on the base strata — the second mechanism's second
    sealed-outcome test (2l read .1848)."""
    pi = {r: fn.wrong_target_propensity(rows_2i[r], battery[r]) for r in rungs}
    return {"pi": pi, "test": _run_test(pi, "olmo1b:pi", out, strata, rungs, **kw),
            "non_gating": True, "no_alpha_claim": True, "note": NO_ALPHA_NOTE_2M.format(name="S5"),
            "source": "2j wrong_target_propensity on 2i's sealed OLMo-2 1B draws"}


def load_committed_outcomes_2m(battery, verify_fn, *, root_2i=bi.EXP2I, root_2l=bl.EXP2L) -> dict:
    """S8's sources: the four committed big-model count outcomes through
    their own frozen readers — Pythia-2.8b/6.9b via `analyze_2j.
    load_pythia_outcomes`, OLMo-2 7B via `analyze_2i.load_sweep_7b` +
    `outcomes_7b`, OLMo-2 13B via `analyze_2l.load_sweep_13b` +
    `outcomes_13b`. Every record re-verified by its own loader."""
    py = an2j.load_pythia_outcomes(battery, verify_fn)
    man2i = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    sweep7b = an2i.load_sweep_7b(root_2i, battery, verify_fn, manifest=man2i, predictor_sha=bm.SEAL_2I_SHA256)
    out7b = an2i.outcomes_7b(sweep7b, rungs=tuple(bt.RUNGS))
    man2l = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    sweep13b = an2l.load_sweep_13b(root_2l, battery, verify_fn, manifest=man2l,
                                   endpoint_sha=bl.endpoint_sha256(root_2l))
    out13b = an2l.outcomes_13b(sweep13b, rungs=tuple(bt.RUNGS))
    return {"pythia_2.8b": py["2.8b"], "pythia_6.9b": py["6.9b"], "olmo2_7b": out7b, "olmo2_13b": out13b}


def s8_outcome_order_2m(out_3b, strata, r_primary, committed: dict, **kw) -> dict:
    """S8 (design §5, new): each committed outcome's per-item count read
    as x against 3B's order with 2i's statistic on the base strata,
    over r_primary ∩ that outcome's rung set. Descriptive: a KNOWN
    outcome of a large model, not a from-below predictor; p printed,
    no alpha claim."""
    res = {}
    for name, out_k in committed.items():
        rungs_k = [r for r in r_primary if r in out_k]
        x = {r: [int(v) for v in out_k[r]["y"]] for r in rungs_k}
        res[name] = {"rungs": rungs_k,
                     "test": _run_test(x, f"{name}:count", out_3b, strata, rungs_k, **kw),
                     "descriptive": True, "no_alpha_claim": True,
                     "note": NO_ALPHA_NOTE_2M.format(name="S8")}
    return res


def _extra_rungs_2m(x_a64, x_b, out, strata, *, r_eleven_extra, r_extra) -> dict:
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

def verdict_tree_2m(failures, A, B) -> dict:
    """2i's `verdict_tree_2i` shape with 2m's world names (dial b): A
    fires alone → PYTHIA-ONLY; B fires alone → OLMO-ONLY; both →
    SHARED; neither → NEITHER."""
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader failure(s): {list(failures)[:5]}",
                "disclosures": []}
    a, b = A["fires"], B["fires"]
    if a and not b:
        verdict = "PYTHIA-ONLY"
    elif b and not a:
        verdict = "OLMO-ONLY"
    elif a and b:
        verdict = "SHARED"
    else:
        verdict = "NEITHER"
    parts = [f"A: T={an2i._fmt_T(A['stratified']['T'])}, p={A['stratified']['p']:.4g}, fires={a}"]
    if A.get("named_inside"):
        parts.append(f"A {A['named_inside']}")
    parts.append(f"B: T={an2i._fmt_T(B['stratified']['T'])}, p={B['stratified']['p']:.4g}, fires={b}")
    if B.get("named_inside"):
        parts.append(f"B {B['named_inside']}")
    disclosures = []
    if an2i._is_undefined_2i(A):
        disclosures.append(DISCLOSURE_UNDEFINED_2M["A"])
    if an2i._is_undefined_2i(B):
        disclosures.append(DISCLOSURE_UNDEFINED_2M["B"])
    parts.extend(disclosures)
    return {"verdict": verdict, "reason": "; ".join(parts), "disclosures": disclosures}


def verdict_2m(failures, A, B, power, r_primary) -> dict:
    tree = verdict_tree_2m(failures, A, B)
    if failures:
        return tree
    disclosures = list(tree.get("disclosures", []))
    if len(r_primary) < 3:
        disclosures.append(DISCLOSURE_THIN_2M)
    for test, res in (("A", A), ("B", B)):
        d = _thin_eligible_2m(test, res)
        if d:
            disclosures.append(d)
        else:
            d2 = _partial_eligible_2m(test, res, r_primary)   # freeze F-1
            if d2:
                disclosures.append(d2)
    for test, res in (("A", A), ("B", B)):
        status = (power or {}).get(test, {}).get("declared_status")
        if not res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":
            disclosures.append(DISCLOSURE_UNDERPOWERED_2M[test])
    reason = tree["reason"]
    extra = [d for d in disclosures if d not in tree.get("disclosures", [])]
    if extra:
        reason = "; ".join([reason] + extra)
    return {"verdict": tree["verdict"], "reason": reason, "disclosures": disclosures}


def _licensed_2m(tree) -> str:
    licensed = LICENSED_2M[tree["verdict"]]
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

def run(root_2m=EXP2M, root_2i=bi.EXP2I, root_2k=bk.EXP2K, root_2l=bl.EXP2L, *, write=False,
        n_perm=N_PERM, n_boot=N_BOOT, tag_exists=None, blob_sha=None, blobs_bound=None,
        referents_sha=_LITERAL, imports_pinned=_LITERAL, out_path=None, frozen_check=None,
        s8_loader=None) -> dict:
    # `frozen_check` and `s8_loader` are TEST-ONLY injections (2k's
    # pattern): the campaign never passes them. `s8_loader` lets the
    # world fixtures reuse one load of the four committed outcomes.
    failures = []
    root_2m, root_2i, root_2k, root_2l = Path(root_2m), Path(root_2i), Path(root_2k), Path(root_2l)
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_2M_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if IMPORTED_SHA256_2M is None else True

    # ---- the halt scan FIRST (2d F-1)
    if bm.halt_marker_path(root_2m).exists():
        halted, f = collect_total(lambda: bm.halt_marker_path(root_2m).read_text().strip()[:200],
                                  "2m gate 1 smollm3_3b halt marker read")
        failures += f
        if not f:
            failures.append(f"2m gate 1 smollm3_3b: the runner halted ({halted})")
    # ---- pins, import surface (entry), prereg, manifest, referents
    _, f = collect_total(frozen_check or bm.check_frozen_2m, "2m frozen modules");   failures += f
    if imports_pinned:
        _, f = collect_total(check_imports_2m, "2m import surface (entry)");         failures += f
    elif imports_pinned is not False:
        failures.append("2m import surface: not pinned (build incomplete)")
    prereg, f = collect_total(lambda: bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha),
                              "2m prereg tag");                                       failures += f
    manifest, f = collect_total(
        lambda: bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256),
        "2m checkpoint manifest SmolLM3");                                            failures += f
    if referents_sha is None:
        failures.append("2m referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        from experiments.exp2m import make_referents_2m as mkr
        mf, f = collect_total(lambda: mkr.check_referents(REFERENTS_PATH_2M, sha_pin=referents_sha),
                              "2m referent manifest");                                failures += f + (mf or [])
    # ---- upstream pins, battery, floors, verify, strata
    for thunk, label in ((bg.check_frozen_imports_2g, "2m upstream 2g frozen imports"),
                         (bi.check_frozen_2i, "2m upstream 2i frozen imports"),
                         (an2j.check_frozen_2j, "2m upstream 2j frozen imports"),
                         (bl.check_frozen_2l, "2m upstream 2l frozen imports"),
                         (bi.check_pythia_predictor_files, "2m upstream x_A committed 2d files")):
        _, f = collect_total(thunk, label); failures += f
    battery, f = collect_total(bg.load_battery, "2m battery items");                  failures += f
    floors, f = collect_total(bg.load_floors, "2m floors 2d");                         failures += f
    verify_fn, f = collect_total(a2d.load_verify, "2m verify criterion 3c");           failures += f
    pred2g, f = collect_total(
        lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA),
        "2m strata source 2g predictor");                                              failures += f
    strata = sg.from_json(pred2g["strata"]) if pred2g else None
    if strata is not None:
        _, f = collect_total(lambda: sg.check_strata_pins(strata), "2m strata pins 2g"); failures += f

    # ---- the predictors through their seals
    fp, pctx = load_predictors_2m(root_2i, root_2k, battery=battery, verify_fn=verify_fn,
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += fp
    cells_2k, x_b, bits_b, rows_2i = (pctx.get("cells_2k") or {}), pctx.get("x_b"), \
        pctx.get("bits_b"), pctx.get("rows_2i")

    # ---- the SmolLM3 endpoint stage, the rung set, the power record, the seal
    rung_set, f = collect_total(lambda: _load_rung_set_2m(root_2m), "2m rung set file"); failures += f
    r_primary = tuple(rung_set["R_PRIMARY"]) if rung_set else ()
    power, f = collect_total(lambda: load_power_2m(root_2m, r_primary, bm.PREDICTOR_SHA_2M)
                             if rung_set else (_ for _ in ()).throw(ValueError("rung set missing")),
                             "2m power record");                                       failures += f
    esl = an2i.require_seal_2i(bm.ENDPOINT_SEAL_TAG_2M, _endpoint_seal_paths_2m(root_2m),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2m endpoint seal binding: {m}" for m in esl["failures"]]
    entries = None
    if manifest is not None:
        entries, f = collect_total(lambda: {w: bm.entry_which_3b(manifest, w) for w in bm.ENDPOINT_WHICH_2M},
                                   "2m SmolLM3 endpoint entries");                     failures += f
    _ep = battery is not None and verify_fn is not None and entries is not None
    ep_recs = {}
    for which in bm.ENDPOINT_WHICH_2M:
        rec, f = collect_total(
            lambda which=which: load_endpoint_which_2m(root_2m, which, battery, verify_fn, entry=entries[which])
            if _ep else (_ for _ in ()).throw(ValueError("battery/verify/entries missing")),
            f"2m endpoint {which}");                                                   failures += f
        ep_recs[which] = rec
    stage1_final = ep_recs.get("stage1_final")
    if rung_set is not None and stage1_final is not None:
        rb, f = collect_total(lambda: _check_rung_set_vs_endpoint_2m(rung_set, stage1_final),
                              "2m rung set vs endpoint");                              failures += f + (rb or [])
        if floors is not None:
            rb2, f = collect_total(lambda: _check_rung_set_derivation_2m(rung_set, stage1_final, floors),
                                   "2m rung set re-derivation");                      failures += f + (rb2 or [])
    if rung_set is not None:
        rb3, f = collect_total(lambda: _check_rung_set_endpoint_shas_2m(rung_set, root_2m),
                               "2m rung set endpoint shas");                          failures += f + (rb3 or [])
    endpoint_sha, f = collect_total(lambda: bm.endpoint_sha256(root_2m), "2m endpoint composite sha")
    failures += f

    # ---- gate 1 (attested), the sweep, gate 1 (re-derived from the bytes)
    g1p = bm.gate1_path(root_2m)
    gate1 = None
    if not g1p.is_file():
        failures.append(f"2m gate 1 smollm3_3b: record missing ({g1p})")
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()), "2m gate 1 smollm3_3b record")
        failures += f
        if gate1 is not None:
            gb, f = collect_total(lambda: bm.gate1_failures_3b(gate1, stage1_final) if stage1_final
                                  else (_ for _ in ()).throw(ValueError("stage1_final missing")),
                                  "2m gate 1 smollm3_3b attestation");                failures += f + (gb or [])
    _sw = manifest is not None and _ep and endpoint_sha is not None
    sweep, f = collect_total(
        lambda: load_sweep_3b(root_2m, battery, verify_fn, manifest=manifest, endpoint_sha=endpoint_sha)
        if _sw else (_ for _ in ()).throw(ValueError("manifest/battery/verify/endpoint sha missing")),
        "2m sweep smollm3_3b");                                                        failures += f
    _g = sweep is not None and stage1_final is not None and gate1 is not None
    g2, f = collect_total(
        lambda: bm.gate1_rederive_3b(sweep[bm.ENDPOINT_STEP_2M], stage1_final, gate1) if _g
        else (_ for _ in ()).throw(ValueError("sweep, endpoint or gate 1 record missing")),
        "2m gate 1 smollm3_3b re-derivation (byte identity)");                        failures += f + (g2 or [])

    # ---- the gating core: outcomes, A, B — one unit; BOTH on the base strata (dial b)
    core = None
    if not failures:
        def _core():
            out = outcomes_3b(sweep, rungs=tuple(bt.RUNGS))
            x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL] for r in r_primary}
            A = _run_test(x256, "1b:k256", out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)
            B = _run_test(x_b, bi.SIZE_PRED, out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)
            return out, x256, A, B
        core, f = collect_total(_core, "2m primary smollm3_3b");                       failures += f
    if not failures and core is not None:
        pf, f = collect_total(lambda: check_power_claims_2m(power, core[1], x_b, strata, r_primary, stage1_final),
                              "2m power claims");                                      failures += f + (pf or [])
    if not failures and core is not None:
        _, f = collect_total(check_imports_2m if imports_pinned else (lambda: None),
                             "2m import surface (exit)");                              failures += f

    referents = {"failures": list(failures), "prereg": prereg, "manifest_sha256": bm.CHECKPOINTS_2M_SHA256,
                 "predictor_seal_2k": pctx.get("psl_2k"), "predictor_seal_2i": pctx.get("psl_2i"),
                 "predictor_sha": bm.PREDICTOR_SHA_2M, "endpoint_seal": esl,
                 "endpoint_sha256": endpoint_sha, "rung_set": rung_set,
                 "gate1": {k: v for k, v in (gate1 if isinstance(gate1, dict) else {}).items()
                           if k not in ("timing",)},
                 "gate1_2k": {s: {r: c["gate1_rederived"] for r, c in cells_2k.get(s, {}).items()}
                              for s in bk.SIZES_2K},
                 "pins_active": {"frozen_modules": frozen_check is None,
                                 "import_surface": bool(imports_pinned),
                                 "referent_manifest": referents_sha not in (False, None)},
                 "dtype": bm.DTYPE_2M, "batch_size": bm.BATCH_SIZE_2M, "power": power}
    common = {"known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2M,
              "calibration_note": CALIBRATION_SENTENCE_2M, "n_perm": n_perm,
              "git_sha": _git_sha(), "model_contact": "none at analysis"}
    if failures:
        tree = verdict_2m(failures, None, None, None, ())
        v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
             "licensed_sentence": LICENSED_2M["INSUFFICIENT_DATA"], "referents": referents,
             "tests": None, "secondaries": None}
    else:
        out, x256, A, B = core
        tree = verdict_2m([], A, B, power, r_primary)
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
        _sec("S3 B beyond A", lambda: _run_test(
            x_b, bi.SIZE_PRED, out, an2i._composite_strata_median(strata, x256, r_primary), r_primary, **kw))
        _sec("S3 A beyond B", lambda: _run_test(
            x256, "1b:k256", out, an2i._composite_strata_median(strata, x_b, r_primary), r_primary, **kw))
        _sec("S3 paired difference", lambda: s3_paired_difference_2m(
            x256, x_b, out, strata, [r for r in A["eligible"] if r in B["eligible"]], n_boot=n_boot))
        _sec("S4 matched density", lambda: s4_matched_2m(bits_b, x64, x256, out, strata, r_primary))
        _sec("S5 answer prior", lambda: s5_answer_prior_2m(rows_2i, battery, out, strata, r_primary, **kw))
        _sec("S6 twin stage3 base", lambda: {
            "twin_counts": {r: int(sweep[bm.TWIN][r]["correct"]) for r in bt.RUNGS},
            "stage3_final_vs_endpoint": an2i._main_vs_endpoint_2i(stage1_final, ep_recs["stage3_final"]),
            "base_vs_endpoint": an2i._main_vs_endpoint_2i(stage1_final, ep_recs["base"])})

        def _s7():
            rl = rung_level_3b(out, floors, rungs=tuple(bt.RUNGS))
            first = _first_correct_outcome_3b(out, r_primary)
            return {"rung_level": {r: {**rl[r], "counts_by_step": out[r]["counts_by_step"],
                                       "ever": int(sum(1 for v in out[r]["y"] if v > 0)),
                                       "final": int(out[r]["counts_by_step"][bm.ENDPOINT_STEP_2M])}
                                   for r in bt.RUNGS},
                    "flat_rungs": [r for r in bt.RUNGS if r not in rung_set["R_3B"]],
                    "transient_clears_on_flat": {r: rl[r]["transient_clears"] for r in bt.RUNGS
                                                 if r not in rung_set["R_3B"] and rl[r]["transient_clears"]},
                    "collapses": collapses_3b(sweep, rungs=tuple(bt.RUNGS)),
                    "non_monotone": non_monotone_3b(out, tuple(bt.RUNGS)),
                    "ceiling_fraction": ceiling_fraction_3b(out, tuple(bt.RUNGS), n_steps=bm.n_trained_3b()),
                    "first_correct_A": _run_test(x256, "1b:k256", first, strata, r_primary, **kw),
                    "first_correct_B": _run_test(x_b, bi.SIZE_PRED, first, strata, r_primary, **kw),
                    "live_items_A": {r: {"k64": sum(1 for c in x64[r] if c > 0),
                                         "k256": sum(1 for c in x256[r] if c > 0)} for r in r_primary}}
        _sec("S7 textures", _s7)

        def _s8():
            loader = s8_loader or (lambda: load_committed_outcomes_2m(battery, verify_fn, root_2i=root_2i,
                                                                      root_2l=root_2l))
            return s8_outcome_order_2m(out, strata, r_primary, loader(), **kw)
        _sec("S8 outcome order", _s8)

        def _extras():
            x64_all = bi.sampler_counts_pythia("1b", tuple(rung_set["R_ELEVEN_EXTRA"]) + tuple(rung_set["R_EXTRA"]))
            xb_all = bi.sampler_counts_olmo(tuple(rung_set["R_ELEVEN_EXTRA"]) + tuple(rung_set["R_EXTRA"]),
                                            root=root_2i, battery=battery, verify_fn=verify_fn)
            return _extra_rungs_2m(x64_all, xb_all, out, strata, r_eleven_extra=tuple(rung_set["R_ELEVEN_EXTRA"]),
                                   r_extra=tuple(rung_set["R_EXTRA"]))
        _sec("extra rungs", _extras)

        def _sens():
            sub = outcomes_3b(sweep, rungs=tuple(bt.RUNGS), steps=bm.LOG_HEAD_SUBSET_2M)
            return {"B_conditioned_on_A_median": _run_test(
                        x_b, bi.SIZE_PRED, out, an2i._composite_strata_median(strata, x256, r_primary), r_primary, **kw),
                    "B_zero_cut": _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x256, r_primary),
                                            r_primary, **kw),
                    "log_head_subset": {"steps": list(bm.LOG_HEAD_SUBSET_2M),
                                        "A": _run_test(x256, "1b:k256", sub, strata, r_primary, **kw),
                                        "B": _run_test(x_b, bi.SIZE_PRED, sub, strata, r_primary, **kw)},
                    "primary_is_the_nine": bool(rung_set["primary_is_the_nine"]),
                    "R_PRIMARY": list(r_primary)}
        _sec("sensitivities", _sens)
        sec["failures"] = sec_failures
        v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
             "licensed_sentence": _licensed_2m(tree), "referents": referents,
             "tests": {"A": A, "B": B}, "secondaries": sec}
        # 2l F-1: re-check the import surface once the record is complete.
        _, f = collect_total(check_imports_2m if imports_pinned else (lambda: None),
                             "2m import surface (post-secondaries)")
        if f:
            failures += f
            referents["failures"] = list(failures)
            t2 = verdict_2m(failures, None, None, None, ())
            v = {"verdict": t2["verdict"], "reason": t2["reason"], **common,
                 "licensed_sentence": LICENSED_2M["INSUFFICIENT_DATA"], "referents": referents,
                 "tests": None, "secondaries": None}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(an2i._json_safe(v), indent=1, default=an2i._jsonable, allow_nan=False))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason")}, indent=1))
