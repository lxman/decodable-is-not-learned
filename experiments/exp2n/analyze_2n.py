# experiments/exp2n/analyze_2n.py
"""Experiment 2n — the corpus question (design `experiment-2n-design.md`).
2m's two-test construction with the outcome model swapped to Comma
v0.1-1T's stage-1 grid and BOTH committed predictors read cross-family,
UNCONDITIONED on 2g's base strata, PLUS a preregistered corpus
annotation C (design §1, §3.8) reading whether the DCLM-class
predictor's edge on 2m survives on a corpus whose dominant sources the
Pile-trained predictor shares instead. Zero model contact at analysis;
nothing sampled anywhere in 2n.

Predictors, loaded through their OWN seals exactly as 2m loads them
(design §3.3): x_A^(256), its 64/128/192 ladder and four 64-draw blocks
re-derived from 2k's raw draws by `analyze_2k.load_tier_2k` at both
sizes and cross-checked by `seal_failures_2k`; x_B by 2i's
`sampler_counts_olmo` after `load_predictor_records_2i` and
`_check_predictor_seal_sampling`, cross-checked by
`_check_predictor_counts_2i`. Both seal tags must bind; both seal shas
must equal `battery_2n`'s literals; the composite must equal
`PREDICTOR_SHA_2N`, which every 2n record must carry.

The Comma trees (design §3.6-§3.9): three endpoint whichs against the
manifest's entries (ONE repo — `main` weight-bearing, unlike 2m's
checkpoints repo), sweep records against each grid step's entry and the
twin's `from_config` shape, their `endpoint_sha256` against the
composite re-derived from the 104 committed endpoint files, every
record's `dtype == DTYPE_2N`, `render == RENDER_2N` and `eos_stop_id ==
EOS_STOP_ID_2N` (dials n, o — the checkpoint record additionally pins
`generation_eos_token_id`), gate 1 attested AND re-derived, the halt
marker refused, the rung set re-derived, the power record's claims
re-derived (B on BASE strata), the import surface pinned at entry, exit
and after the secondaries.

Tests: A = x_A^(256) on 2g's base strata; B = x_B on 2g's base strata
(dial b — no conditioning). Both over R_PRIMARY. Tree = `verdict_tree_
2n` -> SHARED / PYTHIA-ONLY / OLMO-ONLY / NEITHER with 2n's disclosures
and the annotation C carried on every reason. S8 (2m's four rows, plus
SmolLM3-3B as a fifth) reads every committed big-model order against
Comma's; S8c is the descriptive Pile-vs-DCLM-class corpus contrast over
the same paired bootstrap; S9 a descriptive per-rung sign ledger on the
three option rungs across every cross-family-readable outcome. The
annotation C (never in the world, no alpha claim) reads x_B thinned to
x_A's per-rung rate against x_A^(256) itself, with a CI rule (B-LEADS /
A-LEADS / NO-LEAD / UNDEFINED) and `covers_3b_increment` measured
against 2m's own committed S4 increment (+.0659, read from its
verdict.json, never retyped). Every loader refusal COLLECTED and
delivered as INSUFFICIENT_DATA."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2N = Path(__file__).resolve().parent
if str(EXP2N.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2N.parent.parent))

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
from experiments.exp2m import analyze_2m as an2m  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402

RESULTS = EXP2N / "results"
REFERENTS_PATH_2N = EXP2N / "referents_2n.json"
REFERENTS_2N_SHA256 = "09ddc3aed6f0229d38fb4aed83b4c17f5b9a3bc96d077845f1526a1849d6431a"   # Task 5
IMPORTED_SHA256_2N = {
    bg.REPO / "experiments/exp2n/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    bg.REPO / "experiments/exp2n/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    bg.REPO / "experiments/exp2n/run/preflight_2n.py":
        "353df1efc4cb97ab180d9f6fe2db778bd5d5378e30cef5706573c5e3c0591812",
    bg.REPO / "experiments/exp2n/verify_referents_2n.py":
        "d9305ac96240ab11d5ca664763c88f6142ce323b03629092d02979ed866f1228",
}   # 4 modules, pinned from tests/import_scan_2n.py at Task 5
WORLDS_2N = ("INSUFFICIENT_DATA", "SHARED", "PYTHIA-ONLY", "OLMO-ONLY", "NEITHER")
ALPHA, T_BAR, N_PERM, N_BOOT = st.ALPHA, st.T_BAR, st.N_PERM, st.N_BOOT
collect_total = an2i.collect_total
_run_test = an2i._run_test

CALIBRATION_SENTENCE_2N = (
    "Each test (A: Pythia-1b at 256 draws, B: OLMo-2 1B at 64 draws) is calibrated at alpha .01 "
    "on its own, unconditioned, on 2g's base strata; the reported world — SHARED, PYTHIA-ONLY, "
    "OLMO-ONLY or NEITHER — is their conjunction, and the union of the four worlds is not "
    "alpha-calibrated (3d's calibration lesson, stated in advance). The annotation C (B-LEADS / "
    "A-LEADS / NO-LEAD on the matched-density paired difference) is a CI rule, never in the world, "
    "and makes no alpha claim.")

# design §2 (what is known / what is sealed), condensed to the facts
KNOWN_INPUTS_CAVEAT_2N = (
    "Known to the designer before any Comma v0.1-1T weight was loaded: everything through 2m's "
    "close-out — six sealed forecasts (2g's sampler competitor on Pythia-2.8b .17, 2h on 6.9b .20, "
    "2i on OLMo-2 7B .22, 2l on OLMo-2 13B .13/.18, 2m on SmolLM3-3B .17/.25), 2j's mechanism "
    "reading, 2k's DENSITY result, and 2m's full texture on SmolLM3-3B (Test A .1696 with its "
    "per-rung table, Test B .2514, the 64-draw blocks .0998-.1106, the ladder "
    ".1095/.1400/.1612/.1696, 410m .1693, the paired difference +.0818 [.057,.106], the "
    "matched-density increment +.0659, S5 .2417, S8 7B .4615 / 13B .3958 / 2.8b .2472 / 6.9b "
    ".2286, and the antonym sign ledger across outcomes). The Hub inventory of Comma v0.1-1T "
    "(metadata only, 2026-09-06); the tokenizer files loaded once through the stack into a "
    "scratchpad cache, no weight touched. The predictors x_A^(64/128/192/256) at 1b and 410m, "
    "x_B^(64) and 2j's pi are historically prior and tag-bound; nothing is sampled in 2n. Not "
    "known to anyone in this program: any output of Comma v0.1-1T on any item at any checkpoint. "
    "The predictors were committed (2i 2026-08-26, 2k 2026-08-30) before this family was named; "
    "the design is 2m's with the outcome swapped and the corpus annotation C added; the "
    "instrument is tagged before any Comma weight loads, the endpoint stage sealed before the "
    "sweep, the projection sealed before gate 1 (design §2, §7). Corpus overlap is asymmetric "
    "and INVERTED from 2m at the source level: on Comma the Pile-trained predictor shares the "
    "outcome's dominant source kinds and the DCLM-trained one shares only its curated minority "
    "(design §2) — the corpus account, if it is what 2m's texture was, predicts the roles to "
    "swap. \"From below\" holds in tokens for x_A only (design §2).")

_L = {
    "SHARED": ("the essay's cross-family sentence generalises to a fourth family — \"smaller "
               "models of two families, given enough draws, forecast what a fourth family's "
               "training surfaces first, including a family trained on no DCLM-class web\" — with "
               "Prediction 2's output-channel form holding across families at item grain on two "
               "predictor families and three outcome families (still one battery); the \"structure "
               "latent in the training distribution\" reading gains a leg that does not run through "
               "shared web text. Headline condition carried from 2l/2m: the shared component may "
               "lead the essay's sentence only if Test A's per-rung CI excludes zero on at least "
               "half the rungs it read; otherwise the sentence leads with Test B and names A as "
               "bar-clearing on a minority of rungs"),
    "PYTHIA-ONLY": ("the transfer follows the corpus in the direction the corpus account "
                    "predicted (the predictor sharing the outcome's dominant sources reaches it, "
                    "the DCLM one does not); the essay's sentence is bounded to \"between corpora "
                    "that share their dominant sources\", and the density competitor (x_B at 64 "
                    "draws) is named as the alternative S1/S4 adjudicate descriptively. Named "
                    "next: x_B at 256 draws on this outcome"),
    "OLMO-ONLY": ("the corpus account is disconfirmed in its own direction; the stronger "
                  "predictor reaches a Pile-like outcome the Pile predictor cannot; the essay's "
                  "cross-family sentence is bounded to \"the DCLM-trained predictor\", and the "
                  "program's next step is Michael's call"),
    "NEITHER": ("the cross-family finding is bounded at the two DCLM-class outcome families "
                "(three sealed outcomes) in the essay and experiments.md; the full Comma record "
                "reported; the next step is Michael's call"),
    "INSUFFICIENT_DATA": "nothing; the record states which referent failed",
}
LICENSED_2N = {k: f"{v}. Disclosure (design §2): {KNOWN_INPUTS_CAVEAT_2N}" for k, v in _L.items()}
DISCLOSURE_THIN_2N = ("fewer than three rungs carried the primary (R_PRIMARY = R_COMMA ∩ 2k's "
                      "nine) — the reading is THIN regardless of the power record's declaration")
DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N = "fewer than three rungs actually carried Test "
DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2N = "R_PRIMARY is wider than the reading of Test "
DISCLOSURE_UNDERPOWERED_2N = {
    "A": ("Test A did not fire under DECLARED UNDERPOWERED IN ADVANCE: the Pythia-1b read of "
          "Comma's order is not detected at this resolution, neither confirmed nor ruled out"),
    "B": ("Test B did not fire under DECLARED UNDERPOWERED IN ADVANCE: the OLMo-2 1B read of "
          "Comma's order is not detected at this resolution, neither confirmed nor ruled out"),
}
# FREEZE F-3 (2m's lineage): `_run_test` stamps a `fires` key computed by
# `fires_2i` at 2g's bar on EVERY test it runs, including the
# descriptives. S5, S8 and S8c are non-gating with no alpha claim
# (design §5, dial g), so a reader of `secondaries[...]["test"]["fires"]
# == true` would be reading a firing rule that does not exist for them.
# The flag stays (it is `_run_test`'s own shape, frozen upstream); the
# row says in words what it is not.
NO_ALPHA_NOTE_2N = ("{name} is DESCRIPTIVE and non-gating (design §5): its `test.fires` is "
                    "`fires_2i` applied mechanically at 2g's bar and is NOT a firing rule for "
                    "{name} — no alpha claim is made, only T and p are reported, and nothing here "
                    "can move the verdict (a failure inside it lands in secondaries.failures, "
                    "never in referents.failures)")
DISCLOSURE_UNDEFINED_2N = {
    "A": ("Test A was undefined (the Pythia-1b predictor degenerate on every comparable rung), so "
          "the Pythia read is untested, not absent"),
    "B": ("Test B was undefined (the OLMo-2 1B predictor degenerate on every comparable rung), so "
          "the OLMo read is untested, not absent"),
}

# ------------------------------------------------------------- annotation C

C_READINGS_2N = ("B-LEADS", "A-LEADS", "NO-LEAD", "UNDEFINED")
INCREMENT_3B_2N = 0.0659            # 2m S4, read from 2m's committed verdict.json and asserted equal to this to 4 dp
INCREMENT_7B_2K_2N = 0.054          # 2k S3 (known outcome), literal, source: experiments/exp2k/results/VERDICT.txt
INCREMENT_13B_2L_2N = 0.0687        # 2l S4 (sealed), literal, source: experiments/exp2l/results/VERDICT.txt
OPTION_RUNGS_2N = ("antonym", "antonym6", "odd6")
SIGN_LEDGER_LITERALS_2N = {"olmo2_7b_known": {"antonym": {"A": 0.024, "B": 0.217},
                                              "antonym6": {"A": 0.115, "B": 0.214},
                                              "odd6": {"A": 0.096, "B": 0.121}}}   # 2k VERDICT per-rung table at 256 (A); 2i VERDICT Test B per rung (B)
C_MODIFIERS_2N = {
    "B-LEADS-covers": ("with B-LEADS covering 2m's +.066: the DCLM predictor's margin is predictor-shaped, not "
                       "corpus-shaped; 2m's 'corpus plus density' reading is retired in favour of 'density plus "
                       "predictor strength'; the corpus question is answered in the negative at this resolution"),
    "B-LEADS-excludes": ("with B-LEADS but the interval excluding 2m's +.066: the DCLM predictor still leads, by a "
                         "different margin than on every DCLM-class outcome — the margin moved with the corpus "
                         "without reversing; neither account is retired"),
    "A-LEADS": ("with A-LEADS: the margin follows the corpus; the shared-text component is real and measurable at "
                "matched density; the cross-family sentence gains 'the margin between predictors tracks what their "
                "corpora share with the outcome's'"),
    "NO-LEAD-excludes": ("with NO-LEAD excluding 2m's +.066: the DCLM predictor's margin is gone on a Pile-like "
                         "corpus; the margin follows the corpus"),
    "NO-LEAD-covers": ("with NO-LEAD covering 2m's +.066: undecided at this resolution; the blind region is the "
                       "annotation's interval; nothing about the corpus is licensed beyond the disclosure"),
    "UNDEFINED": "with the annotation UNDEFINED (no interval): nothing about the corpus is licensed",
}


def _c_modifier_key_2n(c: dict) -> str:
    r = (c or {}).get("reading")
    if r == "A-LEADS":
        return "A-LEADS"
    if r in ("B-LEADS", "NO-LEAD"):
        return f"{r}-{'covers' if c.get('covers_3b_increment') else 'excludes'}"
    return "UNDEFINED"


def _thin_eligible_2n(test: str, res: dict) -> str | None:
    """2l F-4: a test that READ fewer than three rungs carries its own
    disclosure whatever |R_PRIMARY| was."""
    elig = list((res or {}).get("eligible") or [])
    if len(elig) >= 3:
        return None
    return (f"{DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N}{test}: it read {len(elig)} rung(s) {elig} — "
            f"dropped as n_pos-thin {list((res or {}).get('thin') or [])}, as predictor-degenerate "
            f"{list((res or {}).get('dropped_degenerate') or [])}; the reading is THIN regardless "
            f"of the power record's declaration, which simulates over R_PRIMARY minus the "
            f"degenerate rungs only")


def _partial_eligible_2n(test: str, res: dict, r_primary, rungs_simulated=None) -> str | None:
    """FREEZE F-1 (2l F-4's shape one level over). The power record
    declares over R_PRIMARY minus the PREDICTOR-degenerate rungs, and
    `check_power_claims_2n` re-derives exactly that set — but a rung can
    enter R_PRIMARY by clearing 2d's endpoint bar and then be dropped at
    analysis as n_pos-thin. 2l F-4's guard speaks only when fewer than
    THREE rungs survive, so `3 <= |eligible| < |R_PRIMARY|` left the
    declaration's scope — and therefore the licence's — silently wider
    than the reading's. Additive: a disclosure naming the rungs the test
    did not read. Mutually exclusive with `_thin_eligible_2n` by the
    `< 3` guard.

    R-1 (2m, ratified): SAME/WIDER is decided against the power
    record's OWN `rungs_simulated` list (passed in by `verdict_2n`;
    `None` when the record does not carry one), never re-derived from
    `res['dropped_degenerate']` — a retry-dropped rung folds into that
    field too, which is finer than the coarse `_degenerate_rungs`
    check `check_power_claims_2n` re-derives `rungs_simulated` from, so
    a naive re-derivation could read SAME while the declaration is
    wider by exactly the retry-dropped rung. SAME means the declared
    `rungs_simulated` list equals the eligible set exactly (a different
    route to the same set — every unread rung was dropped as
    predictor-degenerate); otherwise WIDER, naming the extra rungs, or
    disclosing that the list was not readable at all."""
    elig = list((res or {}).get("eligible") or [])
    prim = list(r_primary or [])
    if len(elig) < 3 or len(elig) >= len(prim):
        return None
    missing = [r for r in prim if r not in elig]
    dropped_degenerate = list((res or {}).get('dropped_degenerate') or [])
    thin = list((res or {}).get('thin') or [])
    sim = sorted(set(rungs_simulated or []))
    same = bool(sim) and sim == sorted(set(elig))
    if same:
        scope = ("the power record's declaration and its rungs_simulated list cover exactly "
                 "the rungs the test read, the SAME set reached by a different route (every "
                 "unread rung was dropped as predictor-degenerate)")
    elif rungs_simulated is None:
        scope = ("the power record's declaration and its rungs_simulated list cover R_PRIMARY "
                 "minus the degenerate rungs, a WIDER set than the reading (its rungs_simulated "
                 "list was not readable)")
    else:
        extra = [r for r in sim if r not in elig]
        scope = ("the power record's declaration and its rungs_simulated list cover R_PRIMARY "
                 f"minus the degenerate rungs, a WIDER set than the reading (also {extra})")
    return (f"{DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2N}{test}: it read {len(elig)} of the "
            f"{len(prim)} rungs in R_PRIMARY — {missing} did not carry it, dropped as n_pos-thin "
            f"{thin} and as predictor-degenerate {dropped_degenerate}; {scope}, so the licence is "
            f"bounded to the rungs named as read")


# ------------------------------------------------------------ pins

_EXPERIMENTS_ROOT_2N = str((bg.REPO / "experiments").resolve())


def check_imports_2n() -> None:
    """2j F-1 from commit one: every module under `experiments/` this
    process has imported must be covered by FROZEN_FILES_2N (its pinned
    dict must equal the documented tuple once pinned), 2g's
    FROZEN_IMPORT_SHA256_2G, the four tag-bound INSTRUMENT_BLOBS_2N, and
    2j's/2k's/2l's/2m's own residual import pins (verified against disk
    here), or IMPORTED_SHA256_2N. Files under a `tests/` directory are
    excluded (disclosed, 2j's rule)."""
    if IMPORTED_SHA256_2N is None:
        raise RuntimeError("IMPORTED_SHA256_2N is None — the import surface is not pinned "
                           "(build incomplete)")
    if bn.FROZEN_SHA256_2N:
        pinned_frozen = {str(Path(p).resolve()) for p in bn.FROZEN_SHA256_2N}
        documented = {str(Path(p).resolve()) for p in bn.FROZEN_FILES_2N}
        if pinned_frozen != documented:
            raise RuntimeError(f"FROZEN_SHA256_2N does not cover FROZEN_FILES_2N: missing "
                               f"{sorted(documented - pinned_frozen)}; extra "
                               f"{sorted(pinned_frozen - documented)}")
    covered = {str(Path(p).resolve()) for p in bn.FROZEN_FILES_2N}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bn.INSTRUMENT_BLOBS_2N}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_2N.items()}
    upstream = {str(Path(p).resolve()): v for p, v in an2j.IMPORTED_SHA256_2J.items()}
    upstream.update({str(Path(p).resolve()): v for p, v in an2k.IMPORTED_SHA256_2K.items()})
    upstream.update({str(Path(p).resolve()): v for p, v in an2l.IMPORTED_SHA256_2L.items()})
    upstream.update({str(Path(p).resolve()): v for p, v in an2m.IMPORTED_SHA256_2M.items()})
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
        if not s.startswith(_EXPERIMENTS_ROOT_2N + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned or s in upstream:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


# ---------------------------------------------------- record failures

def _record_common_failures_2n(rec: dict, *, label, cap, verify_fn, seal_tag) -> list:
    """2l's `_record_common_failures_2l` with 2n's size/family, the
    composite predictor sha, the DTYPE pin (design §3.4 / dial l) and
    the render/stop-id pins (design §3, dials n, o)."""
    bad = []
    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bn.DTYPE_2N),
                 ("render", bn.RENDER_2N), ("eos_stop_id", bn.EOS_STOP_ID_2N)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("predictor_sha") != bn.PREDICTOR_SHA_2N:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bn.PREDICTOR_SHA_2N}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != bt.N_ITEMS or len(conts) != bt.N_ITEMS:
        bad.append(f"{label}: bits/continuations are not {bt.N_ITEMS} long")
        return bad
    if rec.get("correct") != sum(bits):
        bad.append(f"{label}: correct {rec.get('correct')} != sum(bits) {sum(bits)}")
    bad += an2i._re_verify(conts, bits, cap, verify_fn, label)
    return bad


def endpoint_record_failures_2n(rec: dict, *, which, rung, cap, entry, verify_fn) -> list:
    label = f"endpoint comma_7b {which}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    if rec.get("which") != which:
        bad.append(f"{label}: which = {rec.get('which')!r}, expected {which!r}")
    if rec.get("commit") != entry.get("commit"):
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry.get('commit')}")
    bad += _record_common_failures_2n(rec, label=label, cap=cap, verify_fn=verify_fn,
                                      seal_tag=bn.PREDICTOR_TAGS_2N)
    return bad


def step_record_failures_2n(rec: dict, *, step, rung, cap, entry, verify_fn, endpoint_sha) -> list:
    """`step` is an int or `TWIN`; the twin's record must carry
    `commit None` and `kind "from_config"` (2i's twin branch)."""
    key = bn.TWIN if step == bn.TWIN else f"step{int(step)}"
    label = f"comma_7b/{key}/{rung}"
    bad = []
    if rec.get("rung") != rung:
        bad.append(f"{label}: rung = {rec.get('rung')!r}, expected {rung!r}")
    want_step = bn.TWIN if step == bn.TWIN else int(step)
    if rec.get("step") != want_step:
        bad.append(f"{label}: step = {rec.get('step')!r}, expected {want_step!r}")
    if step == bn.TWIN:
        if rec.get("commit") is not None:
            bad.append(f"{label}: commit is {rec.get('commit')!r}, expected None")
        if rec.get("kind") != "from_config":
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")
    elif rec.get("commit") != entry["commit"]:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")
    if rec.get("endpoint_sha256") != endpoint_sha:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")
    bad += _record_common_failures_2n(rec, label=label, cap=cap, verify_fn=verify_fn,
                                      seal_tag=bn.ENDPOINT_SEAL_TAG_2N)
    return bad


def which_coherence_failures_2n(which: str, records: dict) -> list:
    """FREEZE F-2 (2i F-1 / 3d F-2's shape on the endpoint side): the
    three endpoint `which`es have no checkpoint record, so — unlike a
    sweep step, whose `_checkpoint.json` digest is MEASURED against all
    34 item records — nothing checked that a which's 34 records came
    from ONE load. The stage is resumable (`endpoint_2n.run` re-loads
    and evaluates only the missing rungs), `load_thin_comma` goes
    through the ordinary HF cache with no sha verification against the
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
            bad.append(f"endpoint comma_7b {which}: the 34 records carry {len(vals)} different "
                       f"{label}s {vals} — they did not come from one load")
        elif vals and vals[0] in ("None", ""):
            bad.append(f"endpoint comma_7b {which}: every record's {label} is empty")
    return bad


def load_endpoint_which_2n(root, which, battery, verify_fn, *, entry) -> dict:
    out = {}
    for rung in bt.RUNGS:
        p = bn.endpoint_record_path(root, which, rung)
        if not p.is_file():
            raise FileNotFoundError(f"endpoint record missing: {p}")
        rec = json.loads(p.read_text())
        bad = endpoint_record_failures_2n(rec, which=which, rung=rung, cap=battery[rung],
                                          entry=entry, verify_fn=verify_fn)
        if bad:
            raise ValueError("; ".join(bad))
        out[rung] = rec
    coh = which_coherence_failures_2n(which, out)   # freeze F-2
    if coh:
        raise ValueError("; ".join(coh))
    return out


def checkpoint_record_failures_2n(crec: dict, *, step, entry: dict, step_records: dict) -> list:
    """2l F-2: revision, commit and the tensor digest MEASURED, the sha
    table's coverage over every candidate file (the index file has no
    LFS pin and is pinned by the commit alone — disclosed), plus the
    generation eos-stop-id pin (dial o)."""
    bad = []
    for k in ("revision", "commit"):
        if crec.get(k) != entry.get(k):
            bad.append(f"comma_7b/step{int(step)}: checkpoint record {k} {crec.get(k)!r} is not "
                       f"the manifest's {entry.get(k)!r}")
    shas = crec.get("sha256")
    if not isinstance(shas, dict):
        bad.append(f"comma_7b/step{int(step)}: checkpoint record sha256 is not a table")
    else:
        uncovered = sorted(set(entry.get("files", [])) - set(shas))
        if uncovered:
            bad.append(f"comma_7b/step{int(step)}: the checkpoint record attests no sha for "
                       f"{uncovered} — a sha table over a subset of the candidate files is a "
                       f"coverage claim about an unstated set")
    dg = crec.get("digest")
    off = sorted(r for r, rec in step_records.items() if rec.get("weight_sha256") != dg)
    if off:
        bad.append(f"comma_7b/step{int(step)}: the checkpoint record's tensor digest {dg!r} is not the "
                   f"digest the item records carry on {off}")
    if crec.get("generation_eos_token_id") != bn.EOS_STOP_ID_2N:
        bad.append(f"comma_7b/step{int(step)}: checkpoint record generation_eos_token_id "
                   f"{crec.get('generation_eos_token_id')!r} is not the pinned stop id "
                   f"{bn.EOS_STOP_ID_2N} — the loader did not apply set_eos_stop_2n")
    return bad


def twin_checkpoint_record_failures_2n(crec: dict, *, entry: dict, step_records: dict) -> list:
    """The twin's bespoke record measured: no commit, `from_config`,
    the pinned seed, the config source at the endpoint's commit, the
    digest the twin's item records carry, and the generation eos-stop-id
    pin (dial o)."""
    bad = []
    if crec.get("revision") != bn.TWIN:
        bad.append(f"comma_7b/twin: checkpoint record revision {crec.get('revision')!r} is not 'twin'")
    if crec.get("commit") is not None:
        bad.append(f"comma_7b/twin: checkpoint record commit {crec.get('commit')!r} is not None")
    if crec.get("kind") != "from_config":
        bad.append(f"comma_7b/twin: checkpoint record kind {crec.get('kind')!r} is not 'from_config'")
    if crec.get("seed") != bn.TWIN_SEED:
        bad.append(f"comma_7b/twin: checkpoint record seed {crec.get('seed')!r} is not {bn.TWIN_SEED}")
    want_src = f"{bn.REPO_COMMA}@{entry.get('config_commit')}"
    if crec.get("config_source") != want_src:
        bad.append(f"comma_7b/twin: config_source {crec.get('config_source')!r} is not {want_src!r}")
    dg = crec.get("digest")
    off = sorted(r for r, rec in step_records.items() if rec.get("weight_sha256") != dg)
    if off:
        bad.append(f"comma_7b/twin: the checkpoint record's tensor digest {dg!r} is not the "
                   f"digest the item records carry on {off}")
    if crec.get("generation_eos_token_id") != bn.EOS_STOP_ID_2N:
        bad.append(f"comma_7b/twin: checkpoint record generation_eos_token_id "
                   f"{crec.get('generation_eos_token_id')!r} is not the pinned stop id "
                   f"{bn.EOS_STOP_ID_2N} — the loader did not apply set_eos_stop_2n")
    return bad


def load_sweep_comma(root, battery, verify_fn, *, manifest, endpoint_sha, steps=None, rungs=None) -> dict:
    """Every grid step + the twin: 34 records each through
    `step_record_failures_2n`, plus the checkpoint record's LFS shas
    against the manifest, empty loading info and the F-2 measurements
    (the twin through its own bespoke check)."""
    steps = tuple(steps) if steps is not None else bn.GRID_COMMA + (bn.TWIN,)
    rungs = tuple(rungs) if rungs is not None else tuple(bt.RUNGS)
    out = {}
    for step in steps:
        entry = bn.entry_comma(manifest, step)
        out[step] = {}
        for rung in rungs:
            p = bn.record_path(root, step, rung)
            if not p.is_file():
                raise FileNotFoundError(f"sweep record missing: {p}")
            rec = json.loads(p.read_text())
            bad = step_record_failures_2n(rec, step=step, rung=rung, cap=battery[rung], entry=entry,
                                          verify_fn=verify_fn, endpoint_sha=endpoint_sha)
            if bad:
                raise ValueError("; ".join(bad))
            out[step][rung] = rec
        cp = bn.checkpoint_record_path(root, step)
        if not cp.is_file():
            raise FileNotFoundError(f"checkpoint record missing: {cp}")
        crec = json.loads(cp.read_text())
        if crec.get("size") != bn.SIZE_OUT or crec.get("step") != (bn.TWIN if step == bn.TWIN else int(step)):
            raise ValueError(f"comma_7b/{step}: checkpoint record size/step "
                             f"{crec.get('size')!r}/{crec.get('step')!r}")
        if step == bn.TWIN:
            cbad = twin_checkpoint_record_failures_2n(crec, entry=entry, step_records=out[step])
        else:
            for name, want in entry.get("lfs_sha256", {}).items():
                if crec.get("sha256", {}).get(name) != want:
                    raise ValueError(f"comma_7b/step{step}: downloaded {name} sha "
                                     f"{crec.get('sha256', {}).get(name)} != manifest {want}")
            if crec.get("loading_info", {}) != {"missing_keys": 0, "unexpected_keys": 0,
                                                 "mismatched_keys": 0}:
                raise ValueError(f"comma_7b/step{step}: loading info not empty")
            cbad = checkpoint_record_failures_2n(crec, step=step, entry=entry, step_records=out[step])
        if cbad:
            raise ValueError("; ".join(cbad))
    return out


# ------------------------------------------------------------ outcomes

def outcomes_comma(sweep: dict, *, rungs=None, steps=None) -> dict:
    """`analyze_2l.outcomes_13b`'s body over `trained_steps_comma()` (24
    points) or a SUBSET of it (`steps`, the every-40k grid-density
    control). The twin is never in an outcome: a `steps` containing it,
    or any step off the grid, is refused."""
    steps = tuple(steps) if steps is not None else bn.trained_steps_comma()
    if any(s not in bn.GRID_COMMA for s in steps):
        raise ValueError(f"outcomes_comma: steps {steps} are not all on the frozen grid")
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


def rung_level_comma(out: dict, floors: dict, *, rungs=None) -> dict:
    steps = bn.trained_steps_comma()
    rungs = tuple(rungs) if rungs is not None else tuple(out)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in steps if s in c and st2d.binomial_bar(c[s], bt.N_ITEMS, floors[rung])["significant"]]
        final = bn.ENDPOINT_STEP_2N in clears
        res[rung] = {"s_star": clears[0] if clears else None, "clears": clears,
                     "final_clears": final, "transient_clears": ([] if final else clears)}
    return res


def _first_correct_outcome_comma(out: dict, rungs) -> dict:
    last_step = max(bn.trained_steps_comma())
    return {r: {"y": [0 if fc is None else (last_step + 1 - fc) for fc in out[r]["first"]],
                "n_pos": out[r]["n_pos"]} for r in rungs}


def collapses_comma(sweep: dict, *, rungs, threshold: int = 450) -> list:
    """2h's checkpoint-local pathology: a (step, rung) where ≥
    `threshold` of the 500 continuations are one identical string.
    Descriptive; the twin included (last, after the grid)."""
    from collections import Counter
    res = []
    for step in sorted(sweep, key=lambda s: (s == bn.TWIN, s if s != bn.TWIN else 0)):
        for r in rungs:
            rec = sweep[step][r]
            top, n = Counter(rec["continuations"]).most_common(1)[0]
            if n >= threshold:
                res.append({"rung": r, "step": step, "continuation": top,
                            "n_identical": int(n), "correct": int(rec["correct"])})
    return res


def non_monotone_comma(out: dict, rungs) -> dict:
    res = {}
    for r in rungs:
        c = out[r]["counts_by_step"]
        steps = sorted(c)
        mx = max(c.values()) if c else 0
        drops = [[int(a), int(b), int(c[a]), int(c[b])] for a, b in zip(steps, steps[1:])
                 if c[a] - c[b] > 0.2 * mx]
        res[r] = {"drops": drops, "n_drops": len(drops), "max": int(mx)}
    return res


def ceiling_fraction_comma(out: dict, rungs, *, n_steps: int) -> dict:
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

def _load_rung_set_2n(root) -> dict:
    p = bn.rung_set_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    for k in ("R_COMMA", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA", "per_rung", "primary_is_the_nine",
              "endpoint_file_sha256"):
        if k not in rec:
            raise ValueError(f"{p}: missing {k!r}")
    if not set(rec["R_PRIMARY"]).issubset(set(bn.R_CAP_2K)):
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")
    if set(rec["R_PRIMARY"]) | set(rec["R_ELEVEN_EXTRA"]) | set(rec["R_EXTRA"]) != set(rec["R_COMMA"]):
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_COMMA")
    return rec


def _check_rung_set_vs_endpoint_2n(rung_set: dict, stage1_final: dict) -> list:
    bad = []
    per_rung = rung_set.get("per_rung", {})
    if not isinstance(per_rung, dict):
        return [f"rung set comma_7b: per_rung is {type(per_rung).__name__}, not a mapping"]
    absent = sorted(r for r in bt.RUNGS if r not in per_rung)
    if absent:
        bad.append(f"rung set comma_7b: per_rung carries no entry for {absent}")
    for r in bt.RUNGS:
        if r not in stage1_final or r not in per_rung:
            continue
        if per_rung[r].get("k") != stage1_final[r]["correct"]:
            bad.append(f"rung set comma_7b/{r}: per_rung k={per_rung[r].get('k')!r} disagrees with "
                       f"the endpoint's stage1_final correct={stage1_final[r]['correct']!r}")
    return bad


def _check_rung_set_derivation_2n(rung_set: dict, stage1_final: dict, floors: dict) -> list:
    bad = []
    counts = {r: stage1_final[r]["correct"] for r in bt.RUNGS if r in stage1_final}
    if len(counts) != len(bt.RUNGS):
        return [f"rung set re-derivation comma_7b: stage1_final missing rung(s) "
                f"{sorted(set(bt.RUNGS) - set(counts))}"]
    red = bn.rung_set_from_counts_2n(counts, floors)
    for key in ("R_COMMA", "R_PRIMARY", "R_ELEVEN_EXTRA", "R_EXTRA"):
        want, got = list(rung_set.get(key, [])), list(red[key])
        if got != want:
            bad.append(f"rung set re-derivation comma_7b/{key}: re-derived {got} disagrees with "
                       f"the file's {want}")
    if bool(rung_set.get("primary_is_the_nine")) != bool(red["primary_is_the_nine"]):
        bad.append("rung set re-derivation comma_7b/primary_is_the_nine disagrees")
    return bad


def _check_rung_set_endpoint_shas_2n(rung_set: dict, root) -> list:
    """2l F-3: the attested `endpoint_file_sha256` table measured —
    exactly the 102 endpoint records, each at its committed sha."""
    root = Path(root)
    got = rung_set.get("endpoint_file_sha256")
    if not isinstance(got, dict):
        return [f"rung set comma_7b: endpoint_file_sha256 is {type(got).__name__}, not a table "
                f"over the {len(bn.ENDPOINT_WHICH_2N) * len(bt.RUNGS)} endpoint records"]
    want = {}
    for which in bn.ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            p = bn.endpoint_record_path(root, which, r)
            if not p.is_file():
                return [f"rung set comma_7b: endpoint record {p} is missing, so "
                        f"endpoint_file_sha256 cannot be measured"]
            want[str(p.relative_to(root))] = bg.sha256_file(p)
    bad = []
    missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
    if missing:
        bad.append(f"rung set comma_7b: endpoint_file_sha256 attests nothing for {missing}")
    if extra:
        bad.append(f"rung set comma_7b: endpoint_file_sha256 carries {extra}, which are not the "
                   f"endpoint records")
    for rel in sorted(set(want) & set(got)):
        if got[rel] != want[rel]:
            bad.append(f"rung set comma_7b: endpoint_file_sha256[{rel}] {str(got[rel])[:12]} is "
                       f"not the committed record's {want[rel][:12]}")
    return bad


def _endpoint_seal_paths_2n(root) -> list:
    paths = [bn.rung_set_path(root), bn.power_path(root)]
    for which in bn.ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            paths.append(bn.endpoint_record_path(root, which, r))
    return paths


# --------------------------------------------------------------- power

POWER_CLAIM_FIELDS_2N = ("dropped_degenerate", "rungs_simulated", "n_pos_lower_bound", "t_bar",
                         "alpha", "thin")
BLOCK_SD_FIELDS_2N = ("n_sim", "mean_block_sd_at_declare", "mean_block_sd_null",
                      "per_block_mean_T_at_declare", "blocks")
DELTA_SD_FIELDS_2N = ("n_sim", "delta_null_sd", "delta_sd_at_declare_A", "delta_sd_at_declare_B",
                      "delta_boot_sd_null", "min_detectable_delta", "formula", "k_by_rung", "rungs")
DELTA_FORMULA_LITERAL_2N = ("min_detectable_delta = 2.63 * delta_boot_sd_null (normal approximation: CI95 excludes "
                            "zero with power .75)")


def load_power_2n(root, r_primary, predictor_sha) -> dict:
    p = bn.power_path(root)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    rec = json.loads(p.read_text())
    if not isinstance(rec, dict):
        raise ValueError(f"{p}: not a 2n power record")
    for test in ("A", "B"):
        sub = rec.get(test)
        if not isinstance(sub, dict) or "declared_status" not in sub or "declaration" not in sub:
            raise ValueError(f"{p}: test {test!r} missing declared_status/declaration")
        if sub["declared_status"] not in an2i.DECLARED_STATUSES_2I:
            raise ValueError(f"{p}: test {test!r} declared_status {sub['declared_status']!r}")
        if not isinstance(sub.get("rungs"), list) or set(sub["rungs"]) != set(r_primary):
            raise ValueError(f"{p}: test {test!r} rungs {sub.get('rungs')} != R_PRIMARY "
                             f"{sorted(r_primary)}")
        if sub.get("n_trained_steps") != bn.n_trained_comma():
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bn.n_trained_comma()}")
    if rec.get("predictor_sha256") != predictor_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")
    bsd = rec.get("block_sd_A")
    if not isinstance(bsd, dict) or any(k not in bsd for k in BLOCK_SD_FIELDS_2N):
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — {BLOCK_SD_FIELDS_2N}")
    if sorted(rec.get("r_primary") or []) != sorted(r_primary):
        raise ValueError(f"{p}: r_primary {rec.get('r_primary')!r} is not the rung set's "
                         f"R_PRIMARY {sorted(r_primary)}")
    if bool(rec.get("primary_is_the_nine")) != (tuple(sorted(r_primary)) == tuple(sorted(bn.R_CAP_2K))):
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
    dsd = rec.get("delta_sd")
    if not isinstance(dsd, dict) or any(k not in dsd for k in DELTA_SD_FIELDS_2N):
        raise ValueError(f"{p}: delta_sd missing or incomplete (dial h) — {DELTA_SD_FIELDS_2N}")
    if dsd.get("formula") != DELTA_FORMULA_LITERAL_2N:
        raise ValueError(f"{p}: delta_sd formula {dsd.get('formula')!r} is not the literal "
                         f"{DELTA_FORMULA_LITERAL_2N!r}")
    return rec


def check_power_claims_2n(power, x_a256, x_b, strata, r_primary, stage1_final, *, bits_b, x_a64) -> list:
    """2k F-2: every re-derivable claim of both tests' power blocks
    against the analyzer's own re-derivation — BOTH on the base strata
    (dial b: Test B is unconditioned). Also re-derives the `delta_sd`
    block's `k_by_rung` (via `thinned_x_b_2n`) and `rungs` (design §4,
    dial h) over R_PRIMARY minus the UNION of both predictors' degenerate
    rungs."""
    bad = []
    dropped_by_test = {}
    for test, x in (("A", x_a256), ("B", x_b)):
        dropped_by_test[test] = set(an2i._degenerate_rungs(x, strata, r_primary))
        prim = (power or {}).get(test)
        if not isinstance(prim, dict):
            bad.append(f"2n power claims {test}: no block")
            continue
        missing = [k for k in POWER_CLAIM_FIELDS_2N if k not in prim]
        if missing:
            bad.append(f"2n power claims {test}: the record does not attest {missing}")
        dropped = list(dropped_by_test[test])
        keep = [r for r in r_primary if r not in dropped]
        if "dropped_degenerate" in prim and sorted(prim["dropped_degenerate"] or []) != sorted(dropped):
            bad.append(f"2n power claims {test}: dropped_degenerate "
                       f"{sorted(prim['dropped_degenerate'] or [])} != {sorted(dropped)}")
        if "rungs_simulated" in prim and sorted(prim["rungs_simulated"] or []) != sorted(keep):
            bad.append(f"2n power claims {test}: rungs_simulated "
                       f"{sorted(prim['rungs_simulated'] or [])} != {sorted(keep)}")
        if "n_pos_lower_bound" in prim:
            want = ({r: int(stage1_final[r]["correct"]) for r in r_primary} if stage1_final else None)
            got = prim["n_pos_lower_bound"]
            if want is None:
                bad.append(f"2n power claims {test}: n_pos_lower_bound cannot be re-derived")
            elif not isinstance(got, dict) or {k: int(v) for k, v in got.items()} != want:
                bad.append(f"2n power claims {test}: n_pos_lower_bound {got!r} != the endpoint's {want!r}")
        for field, want in (("t_bar", T_BAR), ("alpha", ALPHA)):
            if field in prim and prim[field] != want:
                bad.append(f"2n power claims {test}: {field} = {prim[field]!r}, not {want!r}")
        if "thin" in prim and bool(prim["thin"]) != (len(keep) < 3):
            bad.append(f"2n power claims {test}: thin = {prim['thin']!r} against {len(keep)} rung(s)")
        if test == "A":
            bsd = (power or {}).get("block_sd_A")
            if isinstance(bsd, dict) and "rungs" in bsd and sorted(bsd["rungs"] or []) != sorted(keep):
                bad.append(f"2n power claims block_sd_A: rungs {sorted(bsd['rungs'] or [])} is not "
                           f"Test A's non-degenerate set {sorted(keep)}")
    dropped_both = dropped_by_test.get("A", set()) | dropped_by_test.get("B", set())
    keep_both = [r for r in r_primary if r not in dropped_both]
    dsd = (power or {}).get("delta_sd")
    if not isinstance(dsd, dict):
        bad.append("2n power claims delta_sd: no block")
    else:
        if sorted(dsd.get("rungs") or []) != sorted(keep_both):
            bad.append(f"2n power claims delta_sd: rungs {sorted(dsd.get('rungs') or [])} != "
                       f"{sorted(keep_both)} (R_PRIMARY minus the union of both predictors' degenerate rungs)")
        _, want_k_raw = thinned_x_b_2n(bits_b, x_a64, tuple(keep_both))
        want_k = {r: int(v) for r, v in want_k_raw.items()}
        got_k = {r: int(v) for r, v in (dsd.get("k_by_rung") or {}).items() if isinstance(v, (int, float))}
        if got_k != want_k:
            bad.append(f"2n power claims delta_sd: k_by_rung {got_k!r} != re-derived {want_k!r}")
    return bad


# -------------------------------------------------------------- predictors

def load_predictors_2n(root_2i, root_2k, *, battery, verify_fn, tag_exists=None,
                       blobs_bound=None) -> tuple:
    """`analyze_2l.load_predictors_2l`'s body with 2n's literals and
    labels: both predictors through their own sealed readers; every
    seal bound; every sha measured. Returns (failures, ctx) with ctx =
    {seal_2k, seal_2i, predictor_sha, cells_2k{size: cells}, x_b,
    bits_b, rows_2i, r_cap_2i, psl_2k, psl_2i}."""
    failures, ctx = [], {}
    root_2i, root_2k = Path(root_2i), Path(root_2k)
    for m in bk.halt_markers(root_2k):
        failures.append(f"2n predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")
    seal_2k, f = collect_total(lambda: json.loads(bk.seal_path(root_2k).read_text()),
                               "2n predictor 2k seal read");                       failures += f
    psl_2k = an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(root_2k, seal_2k),
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2n predictor 2k seal binding: {m}" for m in psl_2k["failures"]]
    seal_2i, f = collect_total(lambda: an2i._load_predictor_seal_content(root_2i),
                               "2n predictor 2i seal content");                    failures += f
    psl_2i = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(root_2i, seal_2i),
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2n predictor 2i seal binding: {m}" for m in psl_2i["failures"]]
    if isinstance(seal_2k, dict) and seal_2k.get("sha256") != bn.SEAL_2K_SHA256:
        failures.append(f"2n predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")
    if isinstance(seal_2i, dict) and seal_2i.get("sha256") != bn.SEAL_2I_SHA256:
        failures.append(f"2n predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")
    predictor_sha = bn.PREDICTOR_SHA_2N
    if isinstance(seal_2k, dict) and isinstance(seal_2i, dict):
        got = bn.predictor_sha_2n(str(seal_2k.get("sha256")), str(seal_2i.get("sha256")))
        if got != bn.PREDICTOR_SHA_2N:
            failures.append("2n predictor composite sha does not re-derive from the two seals")
    cells_2k = {}
    if battery is not None and verify_fn is not None:
        for size in bk.SIZES_2K:
            def _tier(size=size):
                return an2k.load_tier_2k(root_2k, size, battery=battery, verify_fn=verify_fn,
                                         rungs=bn.R_CAP_2K)
            res, f = collect_total(_tier, f"2n predictor 2k tier {size} load");   failures += f
            f2, c = res if res is not None else ([], {})
            failures += [f"2n predictor {m}" for m in f2]
            cells_2k[size] = c
        if seal_2k is not None and all(len(cells_2k.get(s, {})) == len(bn.R_CAP_2K) for s in bk.SIZES_2K):
            sb, f = collect_total(lambda: an2k.seal_failures_2k(seal_2k, cells_2k, root_2k),
                                  "2n predictor 2k seal vs re-derivation")
            failures += f + [f"2n predictor {m}" for m in (sb or [])]
    else:
        failures.append("2n predictor 2k tier: not loaded (battery or verify missing)")
    rs2i, f = collect_total(lambda: an2i._load_rung_set(root_2i), "2n predictor 2i rung set file")
    failures += f
    if rs2i is not None and tuple(sorted(rs2i["R_CAP"])) != tuple(sorted(bn.R_CAP_2K)):
        failures.append(f"2n predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")
    manifest_2i, f = collect_total(
        lambda: bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256),
        "2n predictor 2i manifest");                                               failures += f
    entry_1b = None
    if manifest_2i is not None:
        entry_1b, f = collect_total(lambda: bi.entry_1b_endpoint(manifest_2i),
                                    "2n predictor 2i 1B endpoint entry");          failures += f
    _prec = battery is not None and entry_1b is not None
    records_2i, f = collect_total(
        lambda: an2i.load_predictor_records_2i(root_2i, battery, entry_1b=entry_1b) if _prec
        else (_ for _ in ()).throw(ValueError("battery or 1B entry missing")),
        "2n predictor 2i olmo1b records");                                         failures += f
    if seal_2i is not None and records_2i is not None:
        sb, f = collect_total(lambda: an2i._check_predictor_seal_sampling(seal_2i, records_2i),
                              "2n predictor 2i seal sampling block")
        failures += f + [f"2n predictor {m}" for m in (sb or [])]
    _xb = battery is not None and verify_fn is not None
    x_b, f = collect_total(lambda: bi.sampler_counts_olmo(bn.R_CAP_2K, root=root_2i, battery=battery,
                                                          verify_fn=verify_fn) if _xb
                           else (_ for _ in ()).throw(ValueError("battery/verify missing")),
                           "2n predictor x_B counts olmo1b");                     failures += f
    if seal_2i is not None and records_2i is not None and x_b is not None:
        cb, f = collect_total(lambda: an2i._check_predictor_counts_2i(seal_2i, records_2i, x_b),
                              "2n predictor x_B counts vs the sealed attestation")
        failures += f + [f"2n predictor {m}" for m in (cb or [])]

    def _rows_bits():
        rows, bits = {}, {}
        for r in bn.R_CAP_2K:
            rows[r] = fn.draw_rows_2i(root_2i, r)
            bits[r] = fn.verified_bits(rows[r], battery[r], verify_fn)
            if fn.counts_from_bits(bits[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")
        return rows, bits
    rb, f = collect_total(lambda: _rows_bits() if (_xb and x_b) else
                          (_ for _ in ()).throw(ValueError("x_B missing")), "2n predictor x_B rows and bits")
    failures += f
    rows_2i, bits_b = rb if rb is not None else (None, None)
    ctx.update(seal_2k=seal_2k, seal_2i=seal_2i, predictor_sha=predictor_sha, cells_2k=cells_2k,
               x_b=x_b, bits_b=bits_b, rows_2i=rows_2i, r_cap_2i=rs2i, psl_2k=psl_2k, psl_2i=psl_2i)
    return failures, ctx


# ------------------------------------------------------------ secondaries

def s3_paired_difference_2n(x_a, x_b, out, strata, rungs, *, n_boot=N_BOOT, seed=0) -> dict:
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


def s4_matched_2n(bits_b, x_a64, x_a256, out, strata, rungs) -> dict:
    """S4 (design §5): x_B thinned per rung to k_g = clip(round(256·r̄_A/
    r̄_B), 1, 64) (2k's rule) against x_A^(256) on the sealed outcome,
    T without permutation (2j's `t_only`); the increment = thinned-B T −
    T_A256 — with both predictors cross-family, which family's small
    model reads Comma's order better at equal draws. Feeds C."""
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


def thinned_x_b_2n(bits_b, x_a64, rungs) -> tuple:
    """C's thinned predictor (design §3.8): per rung, k_g from 2k's rule
    (`bk.matched_k_256` on the two 64-draw mean rates) and x_B^(k_g) = the
    count over the FIRST k_g draws of every item — one deterministic
    block, no seed (S4's all-blocks mean is printed beside it)."""
    x_thin, k_by_rung = {}, {}
    for r in rungs:
        ra = bk.mean_rate(x_a64[r], bk.DRAWS_PER_SEED)
        rb = bk.mean_rate(fn.counts_from_bits(bits_b[r]), bk.DRAWS_PER_SEED)
        k = int(bk.matched_k_256(ra, rb)["k"])
        k_by_rung[r] = k
        x_thin[r] = [int(sum(row[:k])) for row in bits_b[r]]
    return x_thin, k_by_rung


def paired_contrast_2n(group_a: dict, group_b: dict, out, strata, rungs, *, n_boot=N_BOOT, seed=0) -> dict:
    """The one paired item bootstrap 2n uses twice (design §1 C, §5 S8c):
    every predictor in both groups read on the SAME within-rung item
    resample; T per predictor = the plain mean over `rungs` of
    within-stratum Somers' D; contrast = mean(T over group_a) − mean(T
    over group_b); CI95 percentile over `n_boot` replicates. 2m's
    `s3_paired_difference_2m` is the case group_a={B}, group_b={A}."""
    rng = np.random.default_rng(seed)
    preds = {**group_a, **group_b}
    rungs = [r for r in rungs if r in out and all(r in x for x in preds.values())]
    n = bt.N_ITEMS

    def _t(idx_by_rung):
        ts = {}
        for name, x in preds.items():
            ds = []
            for r in rungs:
                idx = idx_by_rung[r]
                y = [out[r]["y"][i] for i in idx]
                s = [strata[r]["strata"][i] for i in idx]
                ds.append(st.somers_d_within([x[r][i] for i in idx], y, s)["d"])
            ts[name] = float(np.nanmean(ds)) if ds else None
        return ts

    def _contrast(ts):
        a = [ts[k] for k in group_a if ts[k] is not None and np.isfinite(ts[k])]
        b = [ts[k] for k in group_b if ts[k] is not None and np.isfinite(ts[k])]
        if len(a) != len(group_a) or len(b) != len(group_b):
            return None
        return float(np.mean(a) - np.mean(b))

    full = _t({r: list(range(n)) for r in rungs})
    contrast = _contrast(full) if rungs else None
    reps = []
    for _ in range(n_boot if rungs else 0):
        c = _contrast(_t({r: rng.integers(0, n, size=n).tolist() for r in rungs}))
        if c is not None and np.isfinite(c):
            reps.append(c)
    ci = [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))] if reps else None
    return {"rungs": rungs, "T": full, "group_a": list(group_a), "group_b": list(group_b),
            "contrast": contrast, "ci95": ci, "n_boot": len(reps), "n_boot_requested": n_boot,
            "note": "paired item bootstrap within rung on one tie structure; every predictor read on the same "
                    "resample; descriptive, no alpha claim"}


def annotation_c_2n(bits_b, x_a64, x_a256, out, strata, rungs, *, increment_3b, n_boot=N_BOOT, seed=0) -> dict:
    """The corpus annotation (design §1, §3.8, dial g): Δ = T(x_B thinned
    to x_A's per-rung rate) − T(x_A^(256)) with the paired bootstrap;
    B-LEADS if the CI95 lower bound > 0, A-LEADS if the upper bound < 0,
    NO-LEAD otherwise, UNDEFINED with no interval; `covers_3b_increment`
    against 2m's committed +.0659 (read, not typed). Never in the world."""
    x_thin, k_by_rung = thinned_x_b_2n(bits_b, x_a64, rungs)
    pc = paired_contrast_2n({"B_thinned": x_thin}, {"A256": x_a256}, out, strata, rungs, n_boot=n_boot, seed=seed)
    ci = pc["ci95"]
    if ci is None or pc["contrast"] is None:
        reading = "UNDEFINED"
    elif ci[0] > 0:
        reading = "B-LEADS"
    elif ci[1] < 0:
        reading = "A-LEADS"
    else:
        reading = "NO-LEAD"
    covers = (ci is not None) and (ci[0] <= increment_3b <= ci[1])
    return {"reading": reading, "delta": pc["contrast"], "ci95": ci, "T_A256": pc["T"].get("A256"),
            "T_B_thinned": pc["T"].get("B_thinned"), "rungs": pc["rungs"], "k_by_rung": k_by_rung,
            "increment_3b": increment_3b, "covers_3b_increment": bool(covers),
            "committed_increments": {"olmo2_7b_known_2k": INCREMENT_7B_2K_2N, "olmo2_13b_2l": INCREMENT_13B_2L_2N,
                                     "smollm3_3b_2m": increment_3b},
            "n_boot": pc["n_boot"], "n_boot_requested": pc["n_boot_requested"], "no_alpha_claim": True,
            "rule": "B-LEADS: ci95[0] > 0; A-LEADS: ci95[1] < 0; NO-LEAD otherwise; UNDEFINED: no interval",
            "note": "a CI rule on one statistic at two predictor densities (x_B thinned to x_A's rate by 2k's block "
                    "rule, first block); never in the verdict's world; no alpha claim"}


def read_increment_3b_2n(root_2m) -> float:
    """2m's committed S4 increment from its verdict.json (a referent
    manifest entry) — the number C's `covers_3b_increment` is measured
    against. Raises ValueError if absent or not a finite number."""
    p = Path(root_2m) / "results" / "verdict.json"
    if not p.is_file():
        raise ValueError(f"2m increment: {p} missing")
    rec = json.loads(p.read_text())
    inc = ((rec.get("secondaries") or {}).get("S4 matched density") or {}).get("increment")
    if not isinstance(inc, (int, float)) or not np.isfinite(inc):
        raise ValueError(f"2m increment: S4 matched density increment is {inc!r}")
    return float(inc)


def s5_answer_prior_2n(rows_2i, battery, out, strata, rungs, **kw) -> dict:
    """S5 (design §5, dial g — non-gating): 2j's wrong-target propensity
    π on 2i's sealed OLMo-2 1B draws, against Comma's sealed order with
    2i's statistic on the base strata — the third sealed-outcome test of
    the second mechanism (2l read .1848, 2m read .2417)."""
    pi = {r: fn.wrong_target_propensity(rows_2i[r], battery[r]) for r in rungs}
    return {"pi": pi, "test": _run_test(pi, "olmo1b:pi", out, strata, rungs, **kw),
            "non_gating": True, "no_alpha_claim": True, "note": NO_ALPHA_NOTE_2N.format(name="S5"),
            "source": "2j wrong_target_propensity on 2i's sealed OLMo-2 1B draws"}


def load_committed_outcomes_2n(battery, verify_fn, *, root_2i, root_2l, root_2m) -> dict:
    """S8's sources: the four committed big-model count outcomes through
    their own frozen readers — Pythia-2.8b/6.9b via `analyze_2j.
    load_pythia_outcomes`, OLMo-2 7B via `analyze_2i.load_sweep_7b` +
    `outcomes_7b`, OLMo-2 13B via `analyze_2l.load_sweep_13b` +
    `outcomes_13b` — plus SmolLM3-3B via `analyze_2m.load_sweep_3b` +
    `outcomes_3b`, the fifth row, 2n's own addition. Every record
    re-verified by its own loader."""
    py = an2j.load_pythia_outcomes(battery, verify_fn)
    man2i = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    sweep7b = an2i.load_sweep_7b(root_2i, battery, verify_fn, manifest=man2i, predictor_sha=bn.SEAL_2I_SHA256)
    out7b = an2i.outcomes_7b(sweep7b, rungs=tuple(bt.RUNGS))
    man2l = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    sweep13b = an2l.load_sweep_13b(root_2l, battery, verify_fn, manifest=man2l,
                                   endpoint_sha=bl.endpoint_sha256(root_2l))
    out13b = an2l.outcomes_13b(sweep13b, rungs=tuple(bt.RUNGS))
    man2m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    sweep3b = an2m.load_sweep_3b(root_2m, battery, verify_fn, manifest=man2m, endpoint_sha=bm.endpoint_sha256(root_2m))
    out3b = an2m.outcomes_3b(sweep3b, rungs=tuple(bt.RUNGS))
    return {"pythia_2.8b": py["2.8b"], "pythia_6.9b": py["6.9b"], "olmo2_7b": out7b, "olmo2_13b": out13b,
            "smollm3_3b": out3b}


def s8_outcome_order_2n(out_comma, strata, r_primary, committed: dict, **kw) -> dict:
    """S8 (design §5): each committed outcome's per-item count read
    as x against Comma's order with 2i's statistic on the base strata,
    over r_primary ∩ that outcome's rung set. Descriptive: a KNOWN
    outcome of a large model, not a from-below predictor; p printed,
    no alpha claim."""
    res = {}
    for name, out_k in committed.items():
        rungs_k = [r for r in r_primary if r in out_k]
        x = {r: [int(v) for v in out_k[r]["y"]] for r in rungs_k}
        res[name] = {"rungs": rungs_k,
                     "test": _run_test(x, f"{name}:count", out_comma, strata, rungs_k, **kw),
                     "descriptive": True, "no_alpha_claim": True,
                     "note": NO_ALPHA_NOTE_2N.format(name="S8")}
    return res


def s8c_corpus_contrast_2n(committed_rows: dict, out, strata, r_primary, *, n_boot=N_BOOT, seed=0) -> dict:
    """S8c (design §5): mean T of the Pile-trained outcomes (Pythia-2.8b,
    6.9b) minus mean T of the DCLM-class outcomes (OLMo-2 7B, 13B,
    SmolLM3-3B), each read as x against Comma's order, paired bootstrap,
    over the rungs every row covers. Descriptive; no alpha claim."""
    pile = ["pythia_2.8b", "pythia_6.9b"]
    dclm = ["olmo2_7b", "olmo2_13b", "smollm3_3b"]
    rows = {k: {r: [int(v) for v in committed_rows[k][r]["y"]] for r in committed_rows[k]} for k in pile + dclm}
    rungs = [r for r in r_primary if all(r in rows[k] for k in pile + dclm)]
    pc = paired_contrast_2n({k: rows[k] for k in pile}, {k: rows[k] for k in dclm}, out, strata, rungs,
                            n_boot=n_boot, seed=seed)
    return {**pc, "pile_rows": pile, "dclm_rows": dclm, "descriptive": True, "no_alpha_claim": True,
            "note": NO_ALPHA_NOTE_2N.format(name="S8c") + "; contrast = mean(Pile rows) - mean(DCLM-class rows)"}


def _per_rung_d(test: dict, rung: str):
    pr_ = (test or {}).get("per_rung") or {}
    v = pr_.get(rung)
    if isinstance(v, dict):
        return v.get("d")
    return None


def s9_sign_ledger_2n(A: dict, B: dict, *, root_2l, root_2m) -> dict:
    """S9 (design §5): per-rung D on the three option rungs for A and B on
    this run, beside 2l's (13B) and 2m's (SmolLM3) committed per-rung D
    read from their verdict.json files (manifest entries) and 2k's/2i's
    7B readings as literals. Descriptive."""
    rows = {}
    v2l = json.loads((Path(root_2l) / "results" / "verdict.json").read_text())
    v2m = json.loads((Path(root_2m) / "results" / "verdict.json").read_text())
    for r in OPTION_RUNGS_2N:
        rows[r] = {"comma_7b": {"A": _per_rung_d(A, r), "B": _per_rung_d(B, r)},
                   "smollm3_3b_2m": {"A": _per_rung_d(v2m["tests"]["A"], r), "B": _per_rung_d(v2m["tests"]["B"], r)},
                   "olmo2_13b_2l": {"A": _per_rung_d(v2l["tests"]["A"], r), "B": _per_rung_d(v2l["tests"]["B"], r)},
                   "olmo2_7b_known": dict(SIGN_LEDGER_LITERALS_2N["olmo2_7b_known"][r])}
    return {"rows": rows, "option_rungs": list(OPTION_RUNGS_2N), "descriptive": True,
            "sources": {"olmo2_7b_known": "literals from experiments/exp2k/results/VERDICT.txt (A at 256) and "
                                          "experiments/exp2i/results/VERDICT.txt (Test B per rung)",
                        "olmo2_13b_2l": "experiments/exp2l/results/verdict.json tests.A/B.per_rung",
                        "smollm3_3b_2m": "experiments/exp2m/results/verdict.json tests.A/B.per_rung"}}


def _extra_rungs_2n(x_a64, x_b, out, strata, *, r_eleven_extra, r_extra) -> dict:
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

def verdict_tree_2n(failures, A, B) -> dict:
    """2i's `verdict_tree_2i` shape with 2n's world names (dial b): A
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
        disclosures.append(DISCLOSURE_UNDEFINED_2N["A"])
    if an2i._is_undefined_2i(B):
        disclosures.append(DISCLOSURE_UNDEFINED_2N["B"])
    parts.extend(disclosures)
    return {"verdict": verdict, "reason": "; ".join(parts), "disclosures": disclosures}


def verdict_2n(failures, A, B, power, r_primary, annotation=None) -> dict:
    tree = verdict_tree_2n(failures, A, B)
    if failures:
        return {**tree, "annotation": annotation}
    disclosures = list(tree.get("disclosures", []))
    if len(r_primary) < 3:
        disclosures.append(DISCLOSURE_THIN_2N)
    for test, res in (("A", A), ("B", B)):
        d = _thin_eligible_2n(test, res)
        if d:
            disclosures.append(d)
        else:
            d2 = _partial_eligible_2n(
                test, res, r_primary,
                rungs_simulated=(power or {}).get(test, {}).get("rungs_simulated"))   # freeze F-1 / R-1
            if d2:
                disclosures.append(d2)
    for test, res in (("A", A), ("B", B)):
        status = (power or {}).get(test, {}).get("declared_status")
        if not res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":
            disclosures.append(DISCLOSURE_UNDERPOWERED_2N[test])
    reason = tree["reason"]
    extra = [d for d in disclosures if d not in tree.get("disclosures", [])]
    if extra:
        reason = "; ".join([reason] + extra)
    if annotation and annotation.get("C"):
        c = annotation["C"]
        delta, ci = c.get("delta"), c.get("ci95")
        if isinstance(delta, (int, float)) and isinstance(ci, list) and len(ci) == 2 \
                and all(isinstance(v, (int, float)) for v in ci):
            reason += f"; C: {c['reading']} (delta {delta:.4f}, ci95 [{ci[0]:.4f}, {ci[1]:.4f}])"
        else:
            reason += f"; C: {c['reading']}"
    return {"verdict": tree["verdict"], "reason": reason, "disclosures": disclosures, "annotation": annotation}


def _licensed_2n(tree) -> str:
    licensed = LICENSED_2N[tree["verdict"]]
    if tree.get("disclosures"):
        licensed = "; ".join([licensed] + list(tree["disclosures"]))
    if tree.get("annotation"):
        licensed = "; ".join([licensed, C_MODIFIERS_2N[_c_modifier_key_2n(tree["annotation"]["C"])]])
    return licensed


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


_LITERAL = object()


# ----------------------------------------------------------------- run

def run(root_2n=EXP2N, root_2i=bi.EXP2I, root_2k=bk.EXP2K, root_2l=bl.EXP2L, root_2m=bm.EXP2M, *,
        write=False, n_perm=N_PERM, n_boot=N_BOOT, tag_exists=None, blob_sha=None, blobs_bound=None,
        referents_sha=_LITERAL, imports_pinned=_LITERAL, out_path=None, frozen_check=None,
        s8_loader=None) -> dict:
    # `frozen_check` and `s8_loader` are TEST-ONLY injections (2k's
    # pattern): the campaign never passes them. `s8_loader` lets the
    # world fixtures reuse one load of the five committed outcomes.
    failures = []
    root_2n, root_2i, root_2k, root_2l, root_2m = Path(root_2n), Path(root_2i), Path(root_2k), \
        Path(root_2l), Path(root_2m)
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_2N_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if IMPORTED_SHA256_2N is None else True

    # ---- the halt scan FIRST (2d F-1)
    if bn.halt_marker_path(root_2n).exists():
        halted, f = collect_total(lambda: bn.halt_marker_path(root_2n).read_text().strip()[:200],
                                  "2n gate 1 comma_7b halt marker read")
        failures += f
        if not f:
            failures.append(f"2n gate 1 comma_7b: the runner halted ({halted})")
    # ---- pins, import surface (entry), prereg, manifest, referents
    _, f = collect_total(frozen_check or bn.check_frozen_2n, "2n frozen modules");   failures += f
    if imports_pinned:
        _, f = collect_total(check_imports_2n, "2n import surface (entry)");         failures += f
    elif imports_pinned is not False:
        failures.append("2n import surface: not pinned (build incomplete)")
    prereg, f = collect_total(lambda: bn.require_prereg_2n(tag_exists=tag_exists, blob_sha=blob_sha),
                              "2n prereg tag");                                       failures += f
    manifest, f = collect_total(
        lambda: bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256),
        "2n checkpoint manifest Comma");                                            failures += f
    if referents_sha is None:
        failures.append("2n referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        from experiments.exp2n import make_referents_2n as mkr
        mf, f = collect_total(lambda: mkr.check_referents(REFERENTS_PATH_2N, sha_pin=referents_sha),
                              "2n referent manifest");                                failures += f + (mf or [])
    # ---- upstream pins, battery, floors, verify, strata
    for thunk, label in ((bg.check_frozen_imports_2g, "2n upstream 2g frozen imports"),
                         (bi.check_frozen_2i, "2n upstream 2i frozen imports"),
                         (an2j.check_frozen_2j, "2n upstream 2j frozen imports"),
                         (bl.check_frozen_2l, "2n upstream 2l frozen imports"),
                         (bi.check_pythia_predictor_files, "2n upstream x_A committed 2d files")):
        _, f = collect_total(thunk, label); failures += f
    battery, f = collect_total(bg.load_battery, "2n battery items");                  failures += f
    floors, f = collect_total(bg.load_floors, "2n floors 2d");                         failures += f
    verify_fn, f = collect_total(a2d.load_verify, "2n verify criterion 3c");           failures += f
    pred2g, f = collect_total(
        lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA),
        "2n strata source 2g predictor");                                              failures += f
    strata = sg.from_json(pred2g["strata"]) if pred2g else None
    if strata is not None:
        _, f = collect_total(lambda: sg.check_strata_pins(strata), "2n strata pins 2g"); failures += f

    # ---- the increment C is measured against (2m's committed S4)
    increment_3b, f = collect_total(lambda: read_increment_3b_2n(root_2m),
                                    "2n increment 3b from 2m verdict");               failures += f
    if increment_3b is not None and round(increment_3b, 4) != round(INCREMENT_3B_2N, 4):
        failures.append(f"2n increment 3b: 2m's committed {increment_3b} is not the literal {INCREMENT_3B_2N}")

    # ---- the predictors through their seals
    fp, pctx = load_predictors_2n(root_2i, root_2k, battery=battery, verify_fn=verify_fn,
                                  tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += fp
    cells_2k, x_b, bits_b, rows_2i = (pctx.get("cells_2k") or {}), pctx.get("x_b"), \
        pctx.get("bits_b"), pctx.get("rows_2i")

    # ---- the Comma endpoint stage, the rung set, the power record, the seal
    rung_set, f = collect_total(lambda: _load_rung_set_2n(root_2n), "2n rung set file"); failures += f
    r_primary = tuple(rung_set["R_PRIMARY"]) if rung_set else ()
    power, f = collect_total(lambda: load_power_2n(root_2n, r_primary, bn.PREDICTOR_SHA_2N)
                             if rung_set else (_ for _ in ()).throw(ValueError("rung set missing")),
                             "2n power record");                                       failures += f
    esl = an2i.require_seal_2i(bn.ENDPOINT_SEAL_TAG_2N, _endpoint_seal_paths_2n(root_2n),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2n endpoint seal binding: {m}" for m in esl["failures"]]
    entries = None
    if manifest is not None:
        entries, f = collect_total(lambda: {w: bn.entry_which_comma(manifest, w) for w in bn.ENDPOINT_WHICH_2N},
                                   "2n Comma endpoint entries");                     failures += f
    _ep = battery is not None and verify_fn is not None and entries is not None
    ep_recs = {}
    for which in bn.ENDPOINT_WHICH_2N:
        rec, f = collect_total(
            lambda which=which: load_endpoint_which_2n(root_2n, which, battery, verify_fn, entry=entries[which])
            if _ep else (_ for _ in ()).throw(ValueError("battery/verify/entries missing")),
            f"2n endpoint {which}");                                                   failures += f
        ep_recs[which] = rec
    stage1_final = ep_recs.get("stage1_final")
    if rung_set is not None and stage1_final is not None:
        rb, f = collect_total(lambda: _check_rung_set_vs_endpoint_2n(rung_set, stage1_final),
                              "2n rung set vs endpoint");                              failures += f + (rb or [])
        if floors is not None:
            rb2, f = collect_total(lambda: _check_rung_set_derivation_2n(rung_set, stage1_final, floors),
                                   "2n rung set re-derivation");                      failures += f + (rb2 or [])
    if rung_set is not None:
        rb3, f = collect_total(lambda: _check_rung_set_endpoint_shas_2n(rung_set, root_2n),
                               "2n rung set endpoint shas");                          failures += f + (rb3 or [])
    endpoint_sha, f = collect_total(lambda: bn.endpoint_sha256(root_2n), "2n endpoint composite sha")
    failures += f

    # ---- gate 1 (attested), the sweep, gate 1 (re-derived from the bytes)
    g1p = bn.gate1_path(root_2n)
    gate1 = None
    if not g1p.is_file():
        failures.append(f"2n gate 1 comma_7b: record missing ({g1p})")
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()), "2n gate 1 comma_7b record")
        failures += f
        if gate1 is not None:
            gb, f = collect_total(lambda: bn.gate1_failures_comma(gate1, stage1_final) if stage1_final
                                  else (_ for _ in ()).throw(ValueError("stage1_final missing")),
                                  "2n gate 1 comma_7b attestation");                failures += f + (gb or [])
    _sw = manifest is not None and _ep and endpoint_sha is not None
    sweep, f = collect_total(
        lambda: load_sweep_comma(root_2n, battery, verify_fn, manifest=manifest, endpoint_sha=endpoint_sha)
        if _sw else (_ for _ in ()).throw(ValueError("manifest/battery/verify/endpoint sha missing")),
        "2n sweep comma_7b");                                                        failures += f
    _g = sweep is not None and stage1_final is not None and gate1 is not None
    g2, f = collect_total(
        lambda: bn.gate1_rederive_comma(sweep[bn.ENDPOINT_STEP_2N], stage1_final, gate1) if _g
        else (_ for _ in ()).throw(ValueError("sweep, endpoint or gate 1 record missing")),
        "2n gate 1 comma_7b re-derivation (byte identity)");                        failures += f + (g2 or [])

    # ---- the gating core: outcomes, A, B — one unit; BOTH on the base strata (dial b)
    core = None
    if not failures:
        def _core():
            out = outcomes_comma(sweep, rungs=tuple(bt.RUNGS))
            x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL] for r in r_primary}
            A = _run_test(x256, "1b:k256", out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)
            B = _run_test(x_b, bi.SIZE_PRED, out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)
            return out, x256, A, B
        core, f = collect_total(_core, "2n primary comma_7b");                       failures += f
    if not failures and core is not None:
        def _power_claims():
            x64 = {r: cells_2k["1b"][r]["counts"][64] for r in r_primary}
            return check_power_claims_2n(power, core[1], x_b, strata, r_primary, stage1_final,
                                         bits_b=bits_b, x_a64=x64)
        pf, f = collect_total(_power_claims, "2n power claims");                        failures += f + (pf or [])
    if not failures and core is not None:
        _, f = collect_total(check_imports_2n if imports_pinned else (lambda: None),
                             "2n import surface (exit)");                              failures += f

    referents = {"failures": list(failures), "prereg": prereg, "manifest_sha256": bn.CHECKPOINTS_2N_SHA256,
                 "predictor_seal_2k": pctx.get("psl_2k"), "predictor_seal_2i": pctx.get("psl_2i"),
                 "predictor_sha": bn.PREDICTOR_SHA_2N, "endpoint_seal": esl,
                 "endpoint_sha256": endpoint_sha, "rung_set": rung_set,
                 "gate1": {k: v for k, v in (gate1 if isinstance(gate1, dict) else {}).items()
                           if k not in ("timing",)},
                 "gate1_2k": {s: {r: c["gate1_rederived"] for r, c in cells_2k.get(s, {}).items()}
                              for s in bk.SIZES_2K},
                 "pins_active": {"frozen_modules": frozen_check is None,
                                 "import_surface": bool(imports_pinned),
                                 "referent_manifest": referents_sha not in (False, None)},
                 "dtype": bn.DTYPE_2N, "batch_size": bn.BATCH_SIZE_2N, "render": bn.RENDER_2N,
                 "eos_stop_id": bn.EOS_STOP_ID_2N, "increment_3b": increment_3b, "power": power}
    common = {"known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2N,
              "calibration_note": CALIBRATION_SENTENCE_2N, "n_perm": n_perm,
              "git_sha": _git_sha(), "model_contact": "none at analysis"}
    if failures:
        tree = verdict_2n(failures, None, None, None, ())
        v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
             "licensed_sentence": LICENSED_2N["INSUFFICIENT_DATA"], "referents": referents,
             "tests": None, "secondaries": None, "annotation": None}
    else:
        out, x256, A, B = core
        kw = dict(n_perm=n_perm, n_boot=n_boot)
        bits1b = {r: cells_2k["1b"][r]["bits"] for r in r_primary}
        x64 = {r: cells_2k["1b"][r]["counts"][64] for r in r_primary}
        C, fC = collect_total(
            lambda: annotation_c_2n(bits_b, x64, x256, out, strata,
                                    [r for r in A["eligible"] if r in B["eligible"]],
                                    increment_3b=increment_3b, n_boot=n_boot),
            "2n annotation C")
        if fC:
            failures += fC
            referents["failures"] = list(failures)
            tree = verdict_2n(failures, None, None, None, ())
            v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
                 "licensed_sentence": LICENSED_2N["INSUFFICIENT_DATA"], "referents": referents,
                 "tests": None, "secondaries": None, "annotation": None}
        else:
            tree = verdict_2n([], A, B, power, r_primary, annotation={"C": C})
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
            _sec("S3 paired difference", lambda: s3_paired_difference_2n(
                x256, x_b, out, strata, [r for r in A["eligible"] if r in B["eligible"]], n_boot=n_boot))
            _sec("S4 matched density", lambda: s4_matched_2n(bits_b, x64, x256, out, strata, r_primary))
            _sec("S5 answer prior", lambda: s5_answer_prior_2n(rows_2i, battery, out, strata, r_primary, **kw))
            _sec("S6 twin stage2 main", lambda: {
                "twin_counts": {r: int(sweep[bn.TWIN][r]["correct"]) for r in bt.RUNGS},
                "stage2_final_vs_endpoint": an2i._main_vs_endpoint_2i(stage1_final, ep_recs["stage2_final"]),
                "main_vs_endpoint": an2i._main_vs_endpoint_2i(stage1_final, ep_recs["main"])})

            def _s7():
                rl = rung_level_comma(out, floors, rungs=tuple(bt.RUNGS))
                first = _first_correct_outcome_comma(out, r_primary)
                return {"rung_level": {r: {**rl[r], "counts_by_step": out[r]["counts_by_step"],
                                           "ever": int(sum(1 for v in out[r]["y"] if v > 0)),
                                           "final": int(out[r]["counts_by_step"][bn.ENDPOINT_STEP_2N])}
                                       for r in bt.RUNGS},
                        "flat_rungs": [r for r in bt.RUNGS if r not in rung_set["R_COMMA"]],
                        "transient_clears_on_flat": {r: rl[r]["transient_clears"] for r in bt.RUNGS
                                                     if r not in rung_set["R_COMMA"] and rl[r]["transient_clears"]},
                        "collapses": collapses_comma(sweep, rungs=tuple(bt.RUNGS)),
                        "non_monotone": non_monotone_comma(out, tuple(bt.RUNGS)),
                        "ceiling_fraction": ceiling_fraction_comma(out, tuple(bt.RUNGS), n_steps=bn.n_trained_comma()),
                        "first_correct_A": _run_test(x256, "1b:k256", first, strata, r_primary, **kw),
                        "first_correct_B": _run_test(x_b, bi.SIZE_PRED, first, strata, r_primary, **kw),
                        "live_items_A": {r: {"k64": sum(1 for c in x64[r] if c > 0),
                                             "k256": sum(1 for c in x256[r] if c > 0)} for r in r_primary}}
            _sec("S7 textures", _s7)

            def _s8_loader():
                return load_committed_outcomes_2n(battery, verify_fn, root_2i=root_2i, root_2l=root_2l,
                                                  root_2m=root_2m)
            committed_rows, f = collect_total(s8_loader or _s8_loader, "2n S8 committed outcomes load")
            sec_failures.extend(f)
            _sec("S8 outcome order", lambda: s8_outcome_order_2n(out, strata, r_primary, committed_rows, **kw))
            _sec("S8c corpus contrast", lambda: s8c_corpus_contrast_2n(
                committed_rows, out, strata, r_primary, n_boot=n_boot))
            _sec("S9 sign ledger", lambda: s9_sign_ledger_2n(A, B, root_2l=root_2l, root_2m=root_2m))
            _sec("C corpus annotation", lambda: C)

            def _extras():
                x64_all = bi.sampler_counts_pythia("1b", tuple(rung_set["R_ELEVEN_EXTRA"]) + tuple(rung_set["R_EXTRA"]))
                xb_all = bi.sampler_counts_olmo(tuple(rung_set["R_ELEVEN_EXTRA"]) + tuple(rung_set["R_EXTRA"]),
                                                root=root_2i, battery=battery, verify_fn=verify_fn)
                return _extra_rungs_2n(x64_all, xb_all, out, strata, r_eleven_extra=tuple(rung_set["R_ELEVEN_EXTRA"]),
                                       r_extra=tuple(rung_set["R_EXTRA"]))
            _sec("extra rungs", _extras)

            def _sens():
                sub = outcomes_comma(sweep, rungs=tuple(bt.RUNGS), steps=bn.EVERY40K_SUBSET_2N)
                return {"B_conditioned_on_A_median": _run_test(
                            x_b, bi.SIZE_PRED, out, an2i._composite_strata_median(strata, x256, r_primary), r_primary, **kw),
                        "B_zero_cut": _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x256, r_primary),
                                                r_primary, **kw),
                        "every40k_subset": {"steps": list(bn.EVERY40K_SUBSET_2N),
                                            "A": _run_test(x256, "1b:k256", sub, strata, r_primary, **kw),
                                            "B": _run_test(x_b, bi.SIZE_PRED, sub, strata, r_primary, **kw),
                                            "control": True,
                                            "note": "the grid-density control (2m process note 3): y "
                                                    "re-counted over the 12-point subset"},
                        "primary_is_the_nine": bool(rung_set["primary_is_the_nine"]),
                        "R_PRIMARY": list(r_primary)}
            _sec("sensitivities", _sens)
            sec["failures"] = sec_failures
            v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
                 "licensed_sentence": _licensed_2n(tree), "referents": referents,
                 "tests": {"A": A, "B": B}, "secondaries": sec, "annotation": {"C": C}}
            # 2l F-1: re-check the import surface once the record is complete.
            _, f = collect_total(check_imports_2n if imports_pinned else (lambda: None),
                                 "2n import surface (post-secondaries)")
            if f:
                failures += f
                referents["failures"] = list(failures)
                t2 = verdict_2n(failures, None, None, None, ())
                v = {"verdict": t2["verdict"], "reason": t2["reason"], **common,
                     "licensed_sentence": LICENSED_2N["INSUFFICIENT_DATA"], "referents": referents,
                     "tests": None, "secondaries": None, "annotation": None}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(an2i._json_safe(v), indent=1, default=an2i._jsonable, allow_nan=False))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason")}, indent=1))
