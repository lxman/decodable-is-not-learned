# experiments/exp2l/verify_referents_2l.py
"""The Exp 2l referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the freeze.
Stops short of the verdict; 2l's own model contact is at the 13B
endpoint/sweep stages (the campaign, not this battery — zero here).

 1  frozen pins byte-identical: `battery_2k.check_frozen_2k`,
    `analyze_2j.check_frozen_2j`, `battery_2i.check_frozen_2i`,
    `battery_2g.check_frozen_imports_2g`,
    `battery_2i.check_pythia_predictor_files`, and `battery_2l.
    check_frozen_2l` if pinned (else print "empty")
 2  2k's three tags, 2i's four tags and 2j's two tags exist; 2k's seal
    binds (`analyze_2i.require_seal_2i` over `analyze_2k._seal_paths_2k`),
    2i's predictor seal binds; both seal shas == `battery_2l`'s
    literals; `PREDICTOR_SHA_2L` re-derives from the two
 3  referents_2l.json: own sha == the literal; N_FILES_2L entries; zero
    refusals (Task 5: REFERENTS_2L_SHA256 / N_FILES_2L pinned)
 4  the manifest: `load_manifest_13b` at the pin; 16 grid entries + step
    0 + main; endpoint/step-0 revisions the literals; 12 shards each;
    `checkpoints_2g.candidate` reproduces every entry's `files` from
    the committed Hub inventory
 5  `analyze_2k.load_tier_2k` on the real 2k tier at both sizes over
    the nine: zero failures; x_A^(256) == `predictor_2k.json`'s
    counts; the four 64-draw blocks sum to the 256-draw counts
 6  x_B: `analyze_2i.load_predictor_records_2i` + `sampler_counts_olmo`
    over the nine == 2i's sealed predictor counts; 2i's committed
    `rung_set_2i.json` R_CAP == the nine
 7  the rung-set rule (`rung_set_from_counts_2l`) on hand counts
    (test_battery_2l's case) and on 2i's committed OLMo-2 7B endpoint
    counts (prints the R_PRIMARY the 7B endpoint would have given —
    descriptive only, not a claim about 13B)
 8  the tree (`verdict_2l` + `_licensed_2l`) on literal inputs: every
    terminal (SHARED/LINEAGE/BOTH/NEITHER/INSUFFICIENT_DATA), the THIN
    and UNDERPOWERED disclosures, the T_BAR/ALPHA boundaries
    (`fires_2i`)
 9  record stamps round-trip: `item_record_2l` -> `step_record_
    failures_2l` clean; `item_record_2i(which=...)` ->
    `endpoint_record_failures_2l` clean; `gate1_failures_13b` /
    `gate1_rederive_13b` clean on a hand pair
10  the 13B tree on the real `EXP2L`: no halt marker; endpoint/rung
    set/power absent BEFORE the campaign (printed "absent —
    pre-campaign"), or present and `load_endpoint_which_2l` +
    `_load_rung_set_2l` + `_check_rung_set_derivation_2l` +
    `load_power_2l` PASS after it; sweep absent, or `load_sweep_13b` +
    `gate1_rederive_13b` PASS
11  `s4_matched_2l` on the real predictors with a synthetic outcome:
    every rung's `k` in [1, 64], `n_blocks == 64 // k`;
    `battery_2k.matched_k_256`'s own return keys present
12  the import surface: `check_imports_2l()` in THIS process passes
    (Task 5: IMPORTED_SHA256_2L pinned)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2L = Path(__file__).resolve().parent
if str(EXP2L.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2L.parent.parent))

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
from experiments.exp2l import analyze_2l as an  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2l import make_referents_2l as mkr  # noqa: E402

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
         "check_frozen_imports_2g/check_pythia_predictor_files/check_frozen_2l")
def _c1(ctx):
    bk.check_frozen_2k()
    an2j.check_frozen_2j()
    bi.check_frozen_2i()
    bg.check_frozen_imports_2g()
    bi.check_pythia_predictor_files()
    if bl.FROZEN_SHA256_2L:
        bl.check_frozen_2l()
    else:
        print("      (check_frozen_2l: FROZEN_SHA256_2L empty)")


@check(2, "2k's three tags, 2i's four tags, 2j's two tags exist; both predictor seals bind; "
         "seal shas == literals; PREDICTOR_SHA_2L re-derives")
def _c2(ctx):
    for tag in (bk.PREREG_TAG_2K, bk.SEAL_TAG_2K, "exp2k-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (bi.PREREG_TAG, bi.PREDICTOR_SEAL_TAG, bi.ENDPOINT_SEAL_TAG, "exp2i-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (an2j.PREREG_TAG_2J, "exp2j-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    seal_2k = json.loads(bk.seal_path(bk.EXP2K).read_text())
    psl_2k = an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(bk.EXP2K, seal_2k))
    _eq(psl_2k["failures"], [], "2k seal binds")
    seal_2i = an2i._load_predictor_seal_content(bi.EXP2I)
    psl_2i = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(bi.EXP2I, seal_2i))
    _eq(psl_2i["failures"], [], "2i predictor seal binds")
    _eq(seal_2k["sha256"], bl.SEAL_2K_SHA256, "2k seal sha == literal")
    _eq(seal_2i["sha256"], bl.SEAL_2I_SHA256, "2i seal sha == literal")
    _eq(bl.predictor_sha_2l(seal_2k["sha256"], seal_2i["sha256"]), bl.PREDICTOR_SHA_2L,
       "PREDICTOR_SHA_2L re-derives")


@check(3, "referents_2l.json: literal sha, N_FILES_2L entries, zero refusals")
def _c3(ctx):
    if an.REFERENTS_2L_SHA256 is None or mkr.N_FILES_2L is None:
        return "SKIP"
    _eq(Path(an.REFERENTS_PATH_2L).is_file(), True, "referents_2l.json on disk")
    bad = mkr.check_referents(an.REFERENTS_PATH_2L, sha_pin=an.REFERENTS_2L_SHA256)
    _eq(bad, [], "zero refusals")


@check(4, "the manifest: load_manifest_13b at the pin; 16 grid + step0 + main; endpoint/step0 "
         "revisions; 12 shards each; checkpoints_2g.candidate reproduces every entry's files")
def _c4(ctx):
    man = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    ctx["manifest"] = man
    _eq(len(man["entries_13b"]), 17, "16 grid points + step 0")
    _eq(man["entries_13b"][str(bl.ENDPOINT_STEP_13B)]["revision"], bl.REV_13B_ENDPOINT,
       "endpoint revision literal")
    _eq(man["entries_13b"][str(bl.STEP0)]["revision"], bl.REV_13B_STEP0, "step-0 revision literal")
    for step, e in man["entries_13b"].items():
        _eq(len(e["lfs_sha256"]), 12, f"step {step}: 12 shards")
    _eq(len(man["main"]["lfs_sha256"]), 12, "main: 12 shards")
    inv = bl.load_inventory_13b()
    table = inv[bl.REPO_13B]
    main_files = table[bl.REV_13B_MAIN]["files"]
    for step, e in man["entries_13b"].items():
        cand = ck.candidate(e["revision"], table[e["revision"]]["files"], main_files)
        _eq(cand["files"], e["files"], f"step {step}: candidate reproduces files")


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
                                            rungs=bl.R_CAP_2K)
        _eq(failures, [], f"{size}: tier loads cleanly")
        for r in bl.R_CAP_2K:
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
    x_b = bi.sampler_counts_olmo(bl.R_CAP_2K, root=bi.EXP2I, battery=battery, verify_fn=verify)
    seal_2i = an2i._load_predictor_seal_content(bi.EXP2I)
    for r in bl.R_CAP_2K:
        _eq(x_b[r], seal_2i["counts"][r], f"{r}: x_B == 2i's sealed counts")
    rs2i = an2i._load_rung_set(bi.EXP2I)
    _eq(tuple(sorted(rs2i["R_CAP"])), tuple(sorted(bl.R_CAP_2K)), "2i's R_CAP == the nine")


@check(7, "rung_set_from_counts_2l on hand counts (test_battery_2l's case) and on 2i's "
         "committed OLMo-2 7B endpoint counts (descriptive)")
def _c7(ctx):
    floors = ctx["floors"]
    counts = {r: 0 for r in bt.RUNGS}
    for r in ("antonym", "add_base8", "sub3_mid"):
        counts[r] = 480
    counts["count_div13"] = 480
    counts["reverse_string"] = 480
    rs = bl.rung_set_from_counts_2l(counts, floors)
    _eq(rs["R_PRIMARY"], ["add_base8", "antonym", "sub3_mid"], "hand-count case: R_PRIMARY")
    _eq(rs["R_ELEVEN_EXTRA"], ["count_div13"], "hand-count case: R_ELEVEN_EXTRA")
    _eq(rs["R_EXTRA"], ["reverse_string"], "hand-count case: R_EXTRA")
    counts7b = {r: json.loads((bi.EXP2I / "results" / "endpoint" / "stage1_final" /
                               f"{r}.json").read_text())["correct"] for r in bt.RUNGS}
    rs7b = bl.rung_set_from_counts_2l(counts7b, floors)
    print(f"      (2i's committed 7B endpoint would give R_PRIMARY {rs7b['R_PRIMARY']} "
         f"— descriptive, not a 13B claim)")


@check(8, "the tree on literal inputs: every terminal, THIN/UNDERPOWERED disclosures, "
         "T_BAR/ALPHA boundaries")
def _c8(ctx):
    def prim(T, p, fires, eligible=("r1", "r2", "r3")):
        return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
               "eligible": list(eligible), "per_rung": {}}

    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    under_b = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}}
    nine = tuple(sorted(bl.R_CAP_2K))

    ins = an.verdict_2l(["x"], None, None, None, nine)
    _eq(ins["verdict"], "INSUFFICIENT_DATA", "refusal -> INSUFFICIENT_DATA")
    _eq(an._licensed_2l(ins), an.LICENSED_2L["INSUFFICIENT_DATA"], "refusal licence")

    for a, b, want in ((True, False, "SHARED"), (False, True, "LINEAGE"),
                       (True, True, "BOTH"), (False, False, "NEITHER")):
        t = an.verdict_2l([], prim(0.2 if a else 0.02, 0.001, a), prim(0.2 if b else 0.02, 0.001, b),
                          powered, nine)
        _eq(t["verdict"], want, f"{want} terminal")
        _eq(an._licensed_2l(t).startswith(an.LICENSED_2L[want]), True, f"{want} licence prefix")

    thin_rungs = nine[:2]
    t_thin = an.verdict_2l([], prim(0.02, 0.3, False), prim(0.02, 0.3, False), powered, thin_rungs)
    _eq(an.DISCLOSURE_THIN_2L in t_thin["disclosures"], True, "thin disclosed")

    t_under = an.verdict_2l([], prim(0.2, 0.001, True), prim(0.02, 0.3, False), under_b, nine)
    _eq(an.DISCLOSURE_UNDERPOWERED_2L["B"] in t_under["disclosures"], True, "underpowered B disclosed")

    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR, "p": an.ALPHA - 1e-6}}), True,
       "T == T_BAR (inclusive), p < ALPHA fires")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR - 1e-9, "p": an.ALPHA - 1e-6}}), False,
       "T just under T_BAR does not fire")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR + 0.1, "p": an.ALPHA}}), False,
       "p == ALPHA (not strictly under) does not fire")


@check(9, "record stamps round-trip: item_record_2l -> step_record_failures_2l clean; "
         "item_record_2i(which=...) -> endpoint_record_failures_2l clean; "
         "gate1_failures_13b/gate1_rederive_13b clean on a hand pair")
def _c9(ctx):
    from experiments.exp2i.run.endpoint_2i import item_record_2i
    battery, verify = ctx["battery"], ctx["verify"]
    man = ctx["manifest"]
    cap = battery["antonym"]
    ev = {"bits": [1] * 10 + [0] * (bk.N_ITEMS - 10), "correct": 10,
         "continuations": [f" {it['answer']}" if i < 10 else " zzz"
                           for i, it in enumerate(cap["eval_items"])]}
    entry = bl.entry_13b(man, 1000)
    esha = "E" * 64
    rec = bl.item_record_2l(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry), step=1000,
                            endpoint_sha=esha, t_s=0.0)
    bad = an.step_record_failures_2l(rec, step=1000, rung="antonym", cap=cap, entry=entry,
                                     verify_fn=verify, endpoint_sha=esha)
    _eq(bad, [], "item_record_2l -> step_record_failures_2l round trip")

    entry_ep = bl.entry_13b(man, bl.ENDPOINT_STEP_13B)
    rec2 = item_record_2i(rung="antonym", family=bl.FAMILY, size=bl.SIZE_OUT, which="stage1_final",
                          cap=cap, ev=ev, ckpt=_ckpt(entry_ep),
                          seal={"tag": bl.PREDICTOR_TAGS_2L, "sha256": bl.PREDICTOR_SHA_2L}, t_s=0.0)
    bad2 = an.endpoint_record_failures_2l(rec2, which="stage1_final", rung="antonym", cap=cap,
                                          entry=entry_ep, verify_fn=verify)
    _eq(bad2, [], "item_record_2i -> endpoint_record_failures_2l round trip")

    ep_recs = {r: rec2 for r in bt.RUNGS}
    gate_rec = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
               "continuation_diffs": {r: 0 for r in bt.RUNGS},
               "continuations_compared": {r: bk.N_ITEMS for r in bt.RUNGS},
               "digest_sweep": "D", "digest_endpoint": "D", "commit_sweep": "c" * 40,
               "commit_endpoint": "c" * 40, "prereg_tag": bl.PREREG_TAG_2L}
    bad3 = bl.gate1_failures_13b(gate_rec, ep_recs)
    _eq(bad3, [], "gate1_failures_13b round trip")
    bad4 = bl.gate1_rederive_13b(ep_recs, ep_recs, gate_rec)
    _eq(bad4, [], "gate1_rederive_13b round trip")


@check(10, "the 13B tree on the real EXP2L: no halt marker; endpoint/rung-set/power/sweep "
          "status before or after the campaign")
def _c10(ctx):
    _eq(bl.halt_marker_path(bl.EXP2L).exists(), False, "no halt marker")
    rung_set_p, power_p = bl.rung_set_path(bl.EXP2L), bl.power_path(bl.EXP2L)
    if not rung_set_p.is_file() and not power_p.is_file():
        print("      (endpoint/rung set/power: absent — pre-campaign)")
    else:
        battery, verify, floors = ctx["battery"], ctx["verify"], ctx["floors"]
        man = ctx["manifest"]
        entry_stage1 = bl.entry_13b(man, bl.ENDPOINT_STEP_13B)
        stage1 = an.load_endpoint_which_2l(bl.EXP2L, "stage1_final", battery, verify, entry=entry_stage1)
        rs = an._load_rung_set_2l(bl.EXP2L)
        _eq(an._check_rung_set_derivation_2l(rs, stage1, floors), [], "rung set re-derivation PASS")
        _eq(an._check_rung_set_vs_endpoint_2l(rs, stage1), [], "rung set vs endpoint PASS")
        # freeze F-3: the attested endpoint-record shas, measured
        _eq(an._check_rung_set_endpoint_shas_2l(rs, bl.EXP2L), [], "endpoint_file_sha256 PASS")
        power = an.load_power_2l(bl.EXP2L, tuple(rs["R_PRIMARY"]), bl.PREDICTOR_SHA_2L)
        _eq(power["A"]["declared_status"] in an2i.DECLARED_STATUSES_2I, True, "load_power_2l PASS")
    gate1_p = bl.gate1_path(bl.EXP2L)
    if not gate1_p.is_file():
        print("      (sweep: absent — pre-campaign)")
    else:
        battery, verify = ctx["battery"], ctx["verify"]
        man = ctx["manifest"]
        entry_stage1 = bl.entry_13b(man, bl.ENDPOINT_STEP_13B)
        stage1 = an.load_endpoint_which_2l(bl.EXP2L, "stage1_final", battery, verify, entry=entry_stage1)
        esha = bl.endpoint_sha256(bl.EXP2L)
        sweep = an.load_sweep_13b(bl.EXP2L, battery, verify, manifest=man, endpoint_sha=esha)
        gate1 = json.loads(gate1_p.read_text())
        _eq(bl.gate1_rederive_13b(sweep[bl.ENDPOINT_STEP_13B], stage1, gate1), [],
           "gate1_rederive_13b PASS")


@check(11, "s4_matched_2l on the real predictors with a synthetic outcome: k in [1,64], "
          "n_blocks == 64 // k; matched_k_256's own return keys present")
def _c11(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    rungs = bl.R_CAP_2K
    rows = {r: fn.draw_rows_2i(bi.EXP2I, r) for r in rungs}
    bits_b = {r: fn.verified_bits(rows[r], battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    seal = json.loads(bk.seal_path(bk.EXP2K).read_text())
    x_a256 = {r: seal["counts"]["1b"][r] for r in rungs}
    rng = np.random.default_rng(0)
    out = {}
    for r in rungs:
        y = [int(v) for v in rng.integers(0, bl.n_trained_13b() + 1, size=bk.N_ITEMS)]
        out[r] = {"y": y, "n_pos": sum(1 for v in y if v > 0),
                 "first": [None if v == 0 else 1000 for v in y]}
    s4 = an.s4_matched_2l(bits_b, x_a64, x_a256, out, strata, rungs)
    for r in rungs:
        p = s4["per_rung"][r]
        _eq(1 <= p["k"] <= 64, True, f"{r}: k in [1,64]")
        _eq(p["n_blocks"], 64 // p["k"], f"{r}: n_blocks == 64 // k")
    _eq(set(bk.matched_k_256(0.5, 0.5)), {"k", "capped", "n_blocks"}, "matched_k_256 return keys")


@check(12, "the import surface: check_imports_2l() in THIS process passes")
def _c12(ctx):
    if an.IMPORTED_SHA256_2L is None:
        return "SKIP"
    an.check_imports_2l()


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
