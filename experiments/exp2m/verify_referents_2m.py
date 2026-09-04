# experiments/exp2m/verify_referents_2m.py
"""The Exp 2m referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the freeze.
Stops short of the verdict; 2m's own model contact is at the SmolLM3-3B
endpoint/sweep stages (the campaign, not this battery — zero here).

 1  frozen pins byte-identical: `battery_2k.check_frozen_2k`,
    `analyze_2j.check_frozen_2j`, `battery_2i.check_frozen_2i`,
    `battery_2g.check_frozen_imports_2g`,
    `battery_2i.check_pythia_predictor_files`, `battery_2l.
    check_frozen_2l` (2l is a frozen upstream now), and `battery_2m.
    check_frozen_2m` if pinned (else print "empty")
 2  2k's three tags, 2i's four tags, 2j's two tags AND 2l's three tags
    (`exp2l-preregistered`, `exp2l-endpoint-sealed`, `exp2l-closed`)
    exist; 2k's seal binds (`analyze_2i.require_seal_2i` over
    `analyze_2k._seal_paths_2k`), 2i's predictor seal binds; both seal
    shas == `battery_2m`'s literals; `PREDICTOR_SHA_2M` re-derives from
    the two
 3  referents_2m.json: own sha == the literal; N_FILES_2M entries; zero
    refusals (Task 5: REFERENTS_2M_SHA256 / N_FILES_2M pinned)
 4  the manifest: `load_manifest_3b` at the pin; 26 grid entries + the
    twin + stage3_final + base; the endpoint revision/commit literals
    (`d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4`); 2 shards on every
    grid entry and on stage3_final and on base; `checkpoints_2g.
    candidate` reproduces every grid entry's `files` from the
    committed checkpoints-repo inventory (main_files = the weightless
    `main`'s) and the base entry's from the base repo's;
    `LOG_HEAD_SUBSET_2M` a strict subset of `GRID_3B`
 5  `analyze_2k.load_tier_2k` on the real 2k tier at both sizes over
    the nine: zero failures; x_A^(256) == `predictor_2k.json`'s
    counts; the four 64-draw blocks sum to the 256-draw counts
 6  x_B: `analyze_2i.load_predictor_records_2i` + `sampler_counts_olmo`
    over the nine == 2i's sealed predictor counts; 2i's committed
    `rung_set_2i.json` R_CAP == the nine
 7  `rung_set_from_counts_2m` on hand counts (test_battery_2m's case)
    and on 2l's committed OLMo-2 13B `stage1_final` counts (prints the
    R_PRIMARY the 13B endpoint would give — descriptive only, not a
    SmolLM3-3B claim)
 8  the tree (`verdict_2m` + `_licensed_2m`) on literal inputs: every
    terminal (PYTHIA-ONLY/OLMO-ONLY/SHARED/NEITHER/INSUFFICIENT_DATA),
    the THIN and UNDERPOWERED disclosures, the T_BAR/ALPHA boundaries
    (`fires_2i`)
 9  record stamps round-trip: `item_record_2m` -> `step_record_
    failures_2m` clean, INCLUDING the twin (`step=TWIN`, `commit None`,
    `kind "from_config"`, `dtype == DTYPE_2M`); `endpoint_item_record_
    2m` -> `endpoint_record_failures_2m` clean; `gate1_failures_3b` /
    `gate1_rederive_3b` clean on a hand pair
10  the SmolLM3 tree on the real `EXP2M`: no halt marker; endpoint/rung
    set/power absent BEFORE the campaign (printed "absent —
    pre-campaign"), or present and `load_endpoint_which_2m` (all three
    whichs) + `_load_rung_set_2m` + `_check_rung_set_derivation_2m` +
    `_check_rung_set_vs_endpoint_2m` + `_check_rung_set_endpoint_shas_
    2m` + `load_power_2m` PASS after it; sweep absent, or `load_sweep_
    3b` + `gate1_rederive_3b` PASS
11  `s4_matched_2m` on the real predictors with a synthetic outcome:
    every rung's `k` in [1, 64], `n_blocks == 64 // k`;
    `battery_2k.matched_k_256`'s own return keys present
12  the import surface: `check_imports_2m()` in THIS process passes
    (Task 5: IMPORTED_SHA256_2M pinned)
13  S8's four committed outcomes load through their own frozen readers
    with zero failures: `load_committed_outcomes_2m` keys the four
    sources, `olmo2_13b` covers the full 34-rung battery, `pythia_2.8b`
    covers 2g's eleven, every `y` is a 500-long list of ints, and
    `olmo2_13b`'s `add_base8` count has at least one positive item
    (≈ 2–4 min; the cold battery is allowed that)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2M = Path(__file__).resolve().parent
if str(EXP2M.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2M.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2m import analyze_2m as an  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2m import make_referents_2m as mkr  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


def _ckpt(entry, digest="D"):
    return {"revision": entry["revision"], "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry.get("files", [])), "weight_sha256": digest, "config_source": "cs",
            "tokenizer_source": "ts"}


@check(1, "frozen pins: check_frozen_2k/check_frozen_2j/check_frozen_2i/"
         "check_frozen_imports_2g/check_pythia_predictor_files/check_frozen_2l/check_frozen_2m")
def _c1(ctx):
    bk.check_frozen_2k()
    an2j.check_frozen_2j()
    bi.check_frozen_2i()
    bg.check_frozen_imports_2g()
    bi.check_pythia_predictor_files()
    bl.check_frozen_2l()
    if bm.FROZEN_SHA256_2M:
        bm.check_frozen_2m()
    else:
        print("      (check_frozen_2m: FROZEN_SHA256_2M empty)")


@check(2, "2k's three tags, 2i's four tags, 2j's two tags, 2l's three tags exist; both "
         "predictor seals bind; seal shas == literals; PREDICTOR_SHA_2M re-derives")
def _c2(ctx):
    for tag in (bk.PREREG_TAG_2K, bk.SEAL_TAG_2K, "exp2k-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (bi.PREREG_TAG, bi.PREDICTOR_SEAL_TAG, bi.ENDPOINT_SEAL_TAG, "exp2i-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (an2j.PREREG_TAG_2J, "exp2j-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (bl.PREREG_TAG_2L, bl.ENDPOINT_SEAL_TAG_2L, "exp2l-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    seal_2k = json.loads(bk.seal_path(bk.EXP2K).read_text())
    psl_2k = an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(bk.EXP2K, seal_2k))
    _eq(psl_2k["failures"], [], "2k seal binds")
    seal_2i = an2i._load_predictor_seal_content(bi.EXP2I)
    psl_2i = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(bi.EXP2I, seal_2i))
    _eq(psl_2i["failures"], [], "2i predictor seal binds")
    _eq(seal_2k["sha256"], bm.SEAL_2K_SHA256, "2k seal sha == literal")
    _eq(seal_2i["sha256"], bm.SEAL_2I_SHA256, "2i seal sha == literal")
    _eq(bm.predictor_sha_2m(seal_2k["sha256"], seal_2i["sha256"]), bm.PREDICTOR_SHA_2M,
       "PREDICTOR_SHA_2M re-derives")


@check(3, "referents_2m.json: literal sha, N_FILES_2M entries, zero refusals")
def _c3(ctx):
    if an.REFERENTS_2M_SHA256 is None or mkr.N_FILES_2M is None:
        return "SKIP"
    _eq(Path(an.REFERENTS_PATH_2M).is_file(), True, "referents_2m.json on disk")
    bad = mkr.check_referents(an.REFERENTS_PATH_2M, sha_pin=an.REFERENTS_2M_SHA256)
    _eq(bad, [], "zero refusals")


@check(4, "the manifest: load_manifest_3b at the pin; 26 grid + twin + stage3_final + base; "
         "endpoint/stage3_final revisions + endpoint commit; 2 shards each; checkpoints_2g."
         "candidate reproduces every entry's files; LOG_HEAD_SUBSET_2M a strict subset of GRID_3B")
def _c4(ctx):
    man = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    ctx["manifest"] = man
    _eq(len(man["entries_3b"]), 26, "26 grid points")
    ep = man["entries_3b"][str(bm.ENDPOINT_STEP_2M)]
    _eq(ep["revision"], bm.REV_ENDPOINT_2M, "endpoint revision literal")
    _eq(ep["commit"], "d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4", "endpoint commit literal")
    _eq(man["stage3_final"]["revision"], bm.REV_STAGE3_FINAL_2M, "stage3_final revision literal")
    _eq(man["twin"]["kind"], "from_config", "twin is a from_config entry")
    for step, e in man["entries_3b"].items():
        _eq(len(e["lfs_sha256"]), 2, f"step {step}: 2 shards")
    _eq(len(man["stage3_final"]["lfs_sha256"]), 2, "stage3_final: 2 shards")
    _eq(len(man["base"]["lfs_sha256"]), 2, "base: 2 shards")
    inv = bm.load_inventory_3b()
    table_c, table_b = inv[bm.REPO_CKPT], inv[bm.REPO_BASE]
    main_files_c = table_c[bm.REV_CKPT_MAIN]["files"]
    for step, e in man["entries_3b"].items():
        cand = ck.candidate(e["revision"], table_c[e["revision"]]["files"], main_files_c)
        _eq(cand["files"], e["files"], f"step {step}: candidate reproduces files")
    cand3 = ck.candidate(man["stage3_final"]["revision"], table_c[man["stage3_final"]["revision"]]["files"],
                         main_files_c)
    _eq(cand3["files"], man["stage3_final"]["files"], "stage3_final: candidate reproduces files")
    cands_b = {rev: ck.candidate(rev, t["files"], table_b[bm.REV_BASE_2M]["files"]) for rev, t in table_b.items()}
    _eq(cands_b[bm.REV_BASE_2M]["files"], man["base"]["files"],
       "base: candidate reproduces files from the base repo")
    _eq(set(bm.LOG_HEAD_SUBSET_2M) < set(bm.GRID_3B), True,
       "LOG_HEAD_SUBSET_2M is a strict subset of GRID_3B")


@check(5, "analyze_2k.load_tier_2k on the real 2k tier at both sizes over the nine: zero "
         "failures; x_A^(256) == predictor_2k.json; the four blocks sum to 256's counts")
def _c5(ctx):
    battery = bg.load_battery()
    verify = a2d.load_verify()
    floors = bg.load_floors()
    ctx["battery"], ctx["verify"], ctx["floors"] = battery, verify, floors
    seal = json.loads(bk.seal_path(bk.EXP2K).read_text())
    for size in bk.SIZES_2K:
        failures, cells = an2k.load_tier_2k(bk.EXP2K, size, battery=battery, verify_fn=verify,
                                            rungs=bm.R_CAP_2K)
        _eq(failures, [], f"{size}: tier loads cleanly")
        for r in bm.R_CAP_2K:
            x256 = cells[r]["counts"][bk.K_TOTAL]
            _eq(x256, seal["counts"][size][r], f"{size}/{r}: x_A^(256) == predictor_2k.json")
            blocks_sum = [sum(bk.block_counts(cells[r]["bits"], b)[i] for b in range(len(bk.SEEDS_2K)))
                         for i in range(bk.N_ITEMS)]
            _eq(blocks_sum, x256, f"{size}/{r}: four 64-draw blocks sum to the 256-draw counts")


@check(6, "x_B: load_predictor_records_2i + sampler_counts_olmo over the nine == 2i's sealed "
         "counts; 2i's committed rung_set_2i.json R_CAP == the nine")
def _c6(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    man2i = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    entry_1b = bi.entry_1b_endpoint(man2i)
    records = an2i.load_predictor_records_2i(bi.EXP2I, battery, entry_1b=entry_1b)
    _eq(set(records), set(bt.RUNGS), "predictor records cover the full 34-rung battery")
    x_b = bi.sampler_counts_olmo(bm.R_CAP_2K, root=bi.EXP2I, battery=battery, verify_fn=verify)
    seal_2i = an2i._load_predictor_seal_content(bi.EXP2I)
    for r in bm.R_CAP_2K:
        _eq(x_b[r], seal_2i["counts"][r], f"{r}: x_B == 2i's sealed counts")
    rs2i = an2i._load_rung_set(bi.EXP2I)
    _eq(tuple(sorted(rs2i["R_CAP"])), tuple(sorted(bm.R_CAP_2K)), "2i's R_CAP == the nine")


@check(7, "rung_set_from_counts_2m on hand counts (test_battery_2m's case) and on 2l's "
         "committed OLMo-2 13B stage1_final counts (descriptive)")
def _c7(ctx):
    floors = ctx["floors"]
    counts = {r: 0 for r in bt.RUNGS}
    for r in ("antonym", "add_base8", "sub3_mid"):
        counts[r] = 480
    counts["count_div13"] = 480
    counts["reverse_string"] = 480
    rs = bm.rung_set_from_counts_2m(counts, floors)
    _eq(rs["R_PRIMARY"], ["add_base8", "antonym", "sub3_mid"], "hand-count case: R_PRIMARY")
    _eq(rs["R_ELEVEN_EXTRA"], ["count_div13"], "hand-count case: R_ELEVEN_EXTRA")
    _eq(rs["R_EXTRA"], ["reverse_string"], "hand-count case: R_EXTRA")
    counts13b = {r: json.loads((bl.EXP2L / "results" / "endpoint" / "stage1_final" /
                               f"{r}.json").read_text())["correct"] for r in bt.RUNGS}
    rs13b = bm.rung_set_from_counts_2m(counts13b, floors)
    print(f"      (2l's committed 13B endpoint would give R_PRIMARY {rs13b['R_PRIMARY']} "
         f"— descriptive, not a SmolLM3-3B claim)")


@check(8, "the tree on literal inputs: every terminal, THIN/UNDERPOWERED disclosures, "
         "T_BAR/ALPHA boundaries")
def _c8(ctx):
    def prim(T, p, fires, eligible=("r1", "r2", "r3")):
        return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
               "eligible": list(eligible), "per_rung": {}}

    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    under_b = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}}
    nine = tuple(sorted(bm.R_CAP_2K))

    ins = an.verdict_2m(["x"], None, None, None, nine)
    _eq(ins["verdict"], "INSUFFICIENT_DATA", "refusal -> INSUFFICIENT_DATA")
    _eq(an._licensed_2m(ins), an.LICENSED_2M["INSUFFICIENT_DATA"], "refusal licence")

    for a, b, want in ((True, False, "PYTHIA-ONLY"), (False, True, "OLMO-ONLY"),
                       (True, True, "SHARED"), (False, False, "NEITHER")):
        t = an.verdict_2m([], prim(0.2 if a else 0.02, 0.001, a), prim(0.2 if b else 0.02, 0.001, b),
                          powered, nine)
        _eq(t["verdict"], want, f"{want} terminal")
        _eq(an._licensed_2m(t).startswith(an.LICENSED_2M[want]), True, f"{want} licence prefix")

    thin_rungs = nine[:2]
    t_thin = an.verdict_2m([], prim(0.02, 0.3, False), prim(0.02, 0.3, False), powered, thin_rungs)
    _eq(an.DISCLOSURE_THIN_2M in t_thin["disclosures"], True, "thin disclosed")

    t_under = an.verdict_2m([], prim(0.2, 0.001, True), prim(0.02, 0.3, False), under_b, nine)
    _eq(an.DISCLOSURE_UNDERPOWERED_2M["B"] in t_under["disclosures"], True, "underpowered B disclosed")

    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR, "p": an.ALPHA - 1e-6}}), True,
       "T == T_BAR (inclusive), p < ALPHA fires")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR - 1e-9, "p": an.ALPHA - 1e-6}}), False,
       "T just under T_BAR does not fire")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR + 0.1, "p": an.ALPHA}}), False,
       "p == ALPHA (not strictly under) does not fire")


@check(9, "record stamps round-trip: item_record_2m -> step_record_failures_2m clean "
         "(incl. the twin); endpoint_item_record_2m -> endpoint_record_failures_2m clean; "
         "gate1_failures_3b/gate1_rederive_3b clean on a hand pair")
def _c9(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    man = ctx["manifest"]
    cap = battery["antonym"]
    ev = {"bits": [1] * 10 + [0] * (bk.N_ITEMS - 10), "correct": 10,
         "continuations": [f" {it['answer']}" if i < 10 else " zzz"
                           for i, it in enumerate(cap["eval_items"])]}
    entry = bm.entry_3b(man, 40000)
    esha = "E" * 64
    rec = bm.item_record_2m(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry), step=40000,
                            endpoint_sha=esha, t_s=0.0)
    bad = an.step_record_failures_2m(rec, step=40000, rung="antonym", cap=cap, entry=entry,
                                     verify_fn=verify, endpoint_sha=esha)
    _eq(bad, [], "item_record_2m -> step_record_failures_2m round trip")

    entry_twin = bm.entry_3b(man, bm.TWIN)
    twin_ckpt = {"revision": bm.TWIN, "commit": None, "kind": "from_config", "files": [],
                "weight_sha256": "T", "config_source": f"{bm.REPO_CKPT}@{entry_twin['config_commit']}",
                "tokenizer_source": f"{bm.REPO_CKPT}@{entry_twin['config_commit']}"}
    rec_twin = bm.item_record_2m(rung="antonym", cap=cap, ev=ev, ckpt=twin_ckpt, step=bm.TWIN,
                                 endpoint_sha=esha, t_s=0.0)
    bad_twin = an.step_record_failures_2m(rec_twin, step=bm.TWIN, rung="antonym", cap=cap,
                                          entry=entry_twin, verify_fn=verify, endpoint_sha=esha)
    _eq(bad_twin, [], "item_record_2m -> step_record_failures_2m round trip (twin)")
    _eq(rec_twin["dtype"], bm.DTYPE_2M, "twin record dtype == DTYPE_2M")

    entry_ep = bm.entry_which_3b(man, "stage1_final")
    rec2 = bm.endpoint_item_record_2m(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry_ep),
                                      which="stage1_final",
                                      seal={"tag": bm.PREDICTOR_TAGS_2M, "sha256": bm.PREDICTOR_SHA_2M},
                                      t_s=0.0)
    bad2 = an.endpoint_record_failures_2m(rec2, which="stage1_final", rung="antonym", cap=cap,
                                          entry=entry_ep, verify_fn=verify)
    _eq(bad2, [], "endpoint_item_record_2m -> endpoint_record_failures_2m round trip")

    # M-4 (final review): built as two independently-constructed dicts,
    # not the same object passed twice, so gate1_rederive_3b compares
    # two distinct records rather than one aliased to itself.
    sweep_recs = {r: rec2 for r in bt.RUNGS}
    stage1_recs = {r: rec2 for r in bt.RUNGS}
    # Freeze F-2: `digest_endpoint`/`commit_endpoint` are now MEASURED
    # against the digest and commit all 34 stage1_final records carry,
    # so the hand pair states the real ones (the "c"*40 placeholder this
    # fixture used before was a fiction the old gate could not see).
    gate_rec = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
               "continuation_diffs": {r: 0 for r in bt.RUNGS},
               "continuations_compared": {r: bk.N_ITEMS for r in bt.RUNGS},
               "digest_sweep": "D", "digest_endpoint": "D",
               "commit_sweep": entry_ep["commit"], "commit_endpoint": entry_ep["commit"],
               "prereg_tag": bm.PREREG_TAG_2M}
    bad3 = bm.gate1_failures_3b(gate_rec, stage1_recs)
    _eq(bad3, [], "gate1_failures_3b round trip")
    bad4 = bm.gate1_rederive_3b(sweep_recs, stage1_recs, gate_rec)
    _eq(bad4, [], "gate1_rederive_3b round trip")
    mixed = dict(stage1_recs)
    mixed["odd6"] = {**rec2, "weight_sha256": "OTHER"}
    _eq(any("did not come from one load" in b for b in bm.gate1_failures_3b(gate_rec, mixed)), True,
       "gate1_failures_3b measures the endpoint digest over all 34 records (freeze F-2)")
    _eq(any("did not come from one load" in b
           for b in an.which_coherence_failures_2m("stage1_final", mixed)), True,
       "which_coherence_failures_2m refuses a which assembled from two loads (freeze F-2)")
    _eq(an.which_coherence_failures_2m("stage1_final", stage1_recs), [],
       "which_coherence_failures_2m clean on one load")


@check(10, "the SmolLM3 tree on the real EXP2M: no halt marker; endpoint/rung-set/power/sweep "
          "status before or after the campaign")
def _c10(ctx):
    _eq(bm.halt_marker_path(bm.EXP2M).exists(), False, "no halt marker")
    rung_set_p, power_p = bm.rung_set_path(bm.EXP2M), bm.power_path(bm.EXP2M)
    # M-3 (final review): test each artifact independently — the state
    # between the endpoint stage and power_2m (rung set written, power
    # absent) must not fall into an "after" branch that dies inside
    # load_power_2m with a bare FileNotFoundError.
    rs = None
    if not rung_set_p.is_file():
        print("      (endpoint/rung set: absent — pre-campaign)")
    else:
        battery, verify, floors = ctx["battery"], ctx["verify"], ctx["floors"]
        man = ctx["manifest"]
        for which in bm.ENDPOINT_WHICH_2M:
            entry = bm.entry_which_3b(man, which)
            an.load_endpoint_which_2m(bm.EXP2M, which, battery, verify, entry=entry)
        entry_stage1 = bm.entry_which_3b(man, "stage1_final")
        stage1 = an.load_endpoint_which_2m(bm.EXP2M, "stage1_final", battery, verify, entry=entry_stage1)
        rs = an._load_rung_set_2m(bm.EXP2M)
        _eq(an._check_rung_set_derivation_2m(rs, stage1, floors), [], "rung set re-derivation PASS")
        _eq(an._check_rung_set_vs_endpoint_2m(rs, stage1), [], "rung set vs endpoint PASS")
        _eq(an._check_rung_set_endpoint_shas_2m(rs, bm.EXP2M), [], "endpoint_file_sha256 PASS")
    if not power_p.is_file():
        print("      (power: absent — pre-campaign)")
    else:
        if rs is None:
            rs = an._load_rung_set_2m(bm.EXP2M)
        power = an.load_power_2m(bm.EXP2M, tuple(rs["R_PRIMARY"]), bm.PREDICTOR_SHA_2M)
        _eq(power["A"]["declared_status"] in an2i.DECLARED_STATUSES_2I, True, "load_power_2m PASS")
    gate1_p = bm.gate1_path(bm.EXP2M)
    if not gate1_p.is_file():
        print("      (sweep: absent — pre-campaign)")
    else:
        battery, verify = ctx["battery"], ctx["verify"]
        man = ctx["manifest"]
        entry_stage1 = bm.entry_which_3b(man, "stage1_final")
        stage1 = an.load_endpoint_which_2m(bm.EXP2M, "stage1_final", battery, verify, entry=entry_stage1)
        esha = bm.endpoint_sha256(bm.EXP2M)
        sweep = an.load_sweep_3b(bm.EXP2M, battery, verify, manifest=man, endpoint_sha=esha)
        gate1 = json.loads(gate1_p.read_text())
        _eq(bm.gate1_rederive_3b(sweep[bm.ENDPOINT_STEP_2M], stage1, gate1), [],
           "gate1_rederive_3b PASS")


@check(11, "s4_matched_2m on the real predictors with a synthetic outcome: k in [1,64], "
          "n_blocks == 64 // k; matched_k_256's own return keys present")
def _c11(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    rungs = bm.R_CAP_2K
    rows = {r: fn.draw_rows_2i(bi.EXP2I, r) for r in rungs}
    bits_b = {r: fn.verified_bits(rows[r], battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    seal = json.loads(bk.seal_path(bk.EXP2K).read_text())
    x_a256 = {r: seal["counts"]["1b"][r] for r in rungs}
    rng = np.random.default_rng(0)
    out = {}
    for r in rungs:
        y = [int(v) for v in rng.integers(0, bm.n_trained_3b() + 1, size=bk.N_ITEMS)]
        out[r] = {"y": y, "n_pos": sum(1 for v in y if v > 0),
                 "first": [None if v == 0 else 1000 for v in y]}
    s4 = an.s4_matched_2m(bits_b, x_a64, x_a256, out, strata, rungs)
    for r in rungs:
        p = s4["per_rung"][r]
        _eq(1 <= p["k"] <= 64, True, f"{r}: k in [1,64]")
        _eq(p["n_blocks"], 64 // p["k"], f"{r}: n_blocks == 64 // k")
    _eq(set(bk.matched_k_256(0.5, 0.5)), {"k", "capped", "n_blocks"}, "matched_k_256 return keys")


@check(12, "the import surface: check_imports_2m() in THIS process passes")
def _c12(ctx):
    if an.IMPORTED_SHA256_2M is None:
        return "SKIP"
    an.check_imports_2m()


@check(13, "S8's four committed outcomes load through their own frozen readers with zero "
          "failures (≈ 2-4 min)")
def _c13(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    out = an.load_committed_outcomes_2m(battery, verify)
    _eq(set(out), {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b"}, "S8's four sources")
    _eq(set(out["olmo2_13b"]), set(bt.RUNGS), "olmo2_13b covers the full 34-rung battery")
    _eq(len(out["pythia_2.8b"]), len(bg.R_28), "pythia_2.8b covers 2g's eleven")
    for name, ok in out.items():
        for r, rec in ok.items():
            _eq(len(rec["y"]), bt.N_ITEMS, f"{name}/{r}: y is {bt.N_ITEMS} long")
            _eq(all(isinstance(v, int) for v in rec["y"]), True, f"{name}/{r}: y is all ints")
    _eq(out["olmo2_13b"]["add_base8"]["n_pos"] > 0, True, "olmo2_13b/add_base8 has a positive item")
    for name, ok in out.items():
        print(f"      ({name}: {len(ok)} rung(s), n_pos sum {sum(v['n_pos'] for v in ok.values())})")


def main() -> int:
    ctx = {}
    n_ok = 0
    for n, name, fn_ in CHECKS:
        try:
            result = fn_(ctx)
        except Exception as e:  # noqa: BLE001
            print(f"  [{n:2d}] FAIL  {name}: {type(e).__name__}: {e}")
            return 1
        if result == "SKIP":
            print(f"  [{n:2d}] skip  {name} (pending Task 5)", flush=True)
        else:
            print(f"  [{n:2d}] ok    {name}", flush=True)
            n_ok += 1
    print(f"referent battery: {n_ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
