# experiments/exp2n/verify_referents_2n.py
"""The Exp 2n referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the freeze.
Stops short of the verdict; 2n's own model contact is at the Comma
v0.1-1T endpoint/sweep stages (the campaign, not this battery — zero
here).

 1  frozen pins byte-identical: `battery_2k.check_frozen_2k`,
    `analyze_2j.check_frozen_2j`, `battery_2i.check_frozen_2i`,
    `battery_2g.check_frozen_imports_2g`,
    `battery_2i.check_pythia_predictor_files`, `battery_2l.
    check_frozen_2l`, `battery_2m.check_frozen_2m` (2m is a frozen
    upstream now), and `battery_2n.check_frozen_2n` if pinned (else
    print "empty")
 2  2k's three tags, 2i's four tags, 2j's two tags, 2l's three tags AND
    2m's three tags (`exp2m-preregistered`, `exp2m-endpoint-sealed`,
    `exp2m-closed`) exist; 2k's seal binds (`analyze_2i.require_seal_2i`
    over `analyze_2k._seal_paths_2k`), 2i's predictor seal binds; both
    seal shas == `battery_2n`'s literals; `PREDICTOR_SHA_2N` re-derives
    from the two
 3  referents_2n.json: own sha == the literal; N_FILES_2N entries; zero
    refusals (Task 5: REFERENTS_2N_SHA256 / N_FILES_2N pinned)
 4  the manifest: `load_manifest_comma` at the pin; 24 grid entries +
    the twin + stage2_final + main; the endpoint revision/commit
    literals (`e295235994f32d763c359d324265a176e591f632`); 3 shards on
    every grid entry and on stage2_final and on main;
    `checkpoints_2g.candidate` reproduces every entry's `files` from
    the committed inventory (main_files = the weight-bearing `main`'s —
    unlike 2m's checkpoints repo); `EVERY40K_SUBSET_2N` a strict subset
    of `GRID_COMMA`
 5  `analyze_2k.load_tier_2k` on the real 2k tier at both sizes over
    the nine: zero failures; x_A^(256) == `predictor_2k.json`'s
    counts; the four 64-draw blocks sum to the 256-draw counts
 6  x_B: `analyze_2i.load_predictor_records_2i` + `sampler_counts_olmo`
    over the nine == 2i's sealed predictor counts; 2i's committed
    `rung_set_2i.json` R_CAP == the nine
 7  `rung_set_from_counts_2n` on hand counts (test_battery_2n's case)
    and on 2m's committed SmolLM3-3B `stage1_final` counts (prints the
    R_PRIMARY the SmolLM3 endpoint would give — descriptive only, not a
    Comma v0.1-1T claim)
 8  the tree (`verdict_2n` + `_licensed_2n`) on literal inputs: every
    terminal (PYTHIA-ONLY/OLMO-ONLY/SHARED/NEITHER/INSUFFICIENT_DATA),
    the THIN and UNDERPOWERED disclosures, the T_BAR/ALPHA boundaries
    (`fires_2i`)
 9  record stamps round-trip: `item_record_2n` -> `step_record_
    failures_2n` clean, INCLUDING the twin (`step=TWIN`, `commit None`,
    `kind "from_config"`, `dtype == DTYPE_2N`); `endpoint_item_record_
    2n` -> `endpoint_record_failures_2n` clean; `gate1_failures_comma` /
    `gate1_rederive_comma` clean on a hand pair
10  the Comma tree on the real `EXP2N`: no halt marker; endpoint/rung
    set/power absent BEFORE the campaign (printed "absent —
    pre-campaign"), or present and `load_endpoint_which_2n` (all three
    whichs) + `_load_rung_set_2n` + `_check_rung_set_derivation_2n` +
    `_check_rung_set_vs_endpoint_2n` + `_check_rung_set_endpoint_shas_
    2n` + `load_power_2n` PASS after it; sweep absent, or `load_sweep_
    comma` + `gate1_rederive_comma` PASS
11  `s4_matched_2n` on the real predictors with a synthetic outcome:
    every rung's `k` in [1, 64], `n_blocks == 64 // k`;
    `battery_2k.matched_k_256`'s own return keys present
12  the import surface: `check_imports_2n()` in THIS process passes
    (Task 5: IMPORTED_SHA256_2N pinned)
13  S8's FIVE committed outcomes load through their own frozen readers
    with zero failures: `load_committed_outcomes_2n` keys the five
    sources, `olmo2_13b` and `smollm3_3b` each cover the full 34-rung
    battery, `pythia_2.8b` covers 2g's eleven, every `y` is a 500-long
    list of ints, and `olmo2_13b`'s `add_base8` count has at least one
    positive item (≈ 3–5 min; the cold battery is allowed that)
14  the tokenizer/eos/render pins on stubs (dials n, o): `check_
    tokenizer_2n` accepts a pure `_Tok` stub carrying Comma's own
    facts and refuses on each of four broken stubs (right padding, a
    foreign pad id, a plain render that begins with a special id, a
    BOS render the stub swallows); `set_eos_stop_2n` overrides a stub
    model's `generation_config.eos_token_id` 2 -> 3 and reads it back;
    `render_2n` prefixes every prompt with `BOS_TOKEN_2N`; `read_
    increment_3b_2n(bm.EXP2M)` == `INCREMENT_3B_2N` to 4 dp; `s9_sign_
    ledger_2n` reproduces the four known-answer per-rung D literals
    (2l's and 2m's own committed A/B on `antonym`) read straight from
    their committed `verdict.json` files
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP2N = Path(__file__).resolve().parent
if str(EXP2N.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2N.parent.parent))

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
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2n import analyze_2n as an  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402
from experiments.exp2n import make_referents_2n as mkr  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


# FREEZE F-1: the loader's own measured eos facts, which every
# endpoint record must now carry (`endpoint_item_record_2n(eos_facts=…)`).
_EOS_FACTS = {"config_eos_token_id": bn.CONFIG_EOS_TOKEN_ID_2N, "generation_eos_token_id": bn.EOS_STOP_ID_2N}


def _ckpt(entry, digest="D"):
    return {"revision": entry["revision"], "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry.get("files", [])), "weight_sha256": digest, "config_source": "cs",
            "tokenizer_source": "ts"}


class _Tok:
    """A pure stand-in for the real tokenizer: implements exactly the
    surface `check_tokenizer_2n` reads. Every character maps to id 100 +
    ord(char) (never a special id), so the plain render never collides
    with pad/unk/bos/eos unless a flag deliberately makes it."""

    def __init__(self, *, padding_side="left", pad_token_id=None, eos_token_id=None, bos_token_id=None,
                unk_token_id=None, vocab_len=None, plain_adds_special=False, swallow_bos=False,
                pad_absent=False):
        self.padding_side = padding_side
        # FREEZE (attack item 8): `pad_token_id=None` means "the default"
        # in this stub's own vocabulary, so before the freeze the cold
        # battery could not express the tokenizer shape that DECLARES no
        # pad at all — the one `check_tokenizer_2n` must refuse hardest,
        # since 2c's harness passes `tok.pad_token_id` straight into
        # `generate`. `pad_absent=True` is that shape.
        self.pad_token_id = None if pad_absent else (bn.PAD_TOKEN_ID_2N if pad_token_id is None
                                                     else pad_token_id)
        self.eos_token_id = bn.EOS_TOKEN_ID_2N if eos_token_id is None else eos_token_id
        self.bos_token_id = bn.BOS_TOKEN_ID_2N if bos_token_id is None else bos_token_id
        self.unk_token_id = bn.UNK_TOKEN_ID_2N if unk_token_id is None else unk_token_id
        self._vocab_len = bn.VOCAB_LEN_2N if vocab_len is None else vocab_len
        self._plain_adds_special = plain_adds_special
        self._swallow_bos = swallow_bos
        self.all_special_ids = {bn.PAD_TOKEN_ID_2N, bn.UNK_TOKEN_ID_2N, bn.BOS_TOKEN_ID_2N, bn.EOS_TOKEN_ID_2N}

    def __len__(self):
        return self._vocab_len

    def __call__(self, text):
        if text.startswith(bn.BOS_TOKEN_2N):
            rest = text[len(bn.BOS_TOKEN_2N):]
            plain_ids = [100 + ord(c) for c in rest]
            ids = plain_ids if self._swallow_bos else [bn.BOS_TOKEN_ID_2N] + plain_ids
        else:
            plain_ids = [100 + ord(c) for c in text]
            ids = ([bn.EOS_TOKEN_ID_2N] + plain_ids) if self._plain_adds_special else plain_ids
        return {"input_ids": ids}


@check(1, "frozen pins: check_frozen_2k/check_frozen_2j/check_frozen_2i/"
         "check_frozen_imports_2g/check_pythia_predictor_files/check_frozen_2l/check_frozen_2m/"
         "check_frozen_2n")
def _c1(ctx):
    bk.check_frozen_2k()
    an2j.check_frozen_2j()
    bi.check_frozen_2i()
    bg.check_frozen_imports_2g()
    bi.check_pythia_predictor_files()
    bl.check_frozen_2l()
    bm.check_frozen_2m()
    if bn.FROZEN_SHA256_2N:
        bn.check_frozen_2n()
    else:
        print("      (check_frozen_2n: FROZEN_SHA256_2N empty)")


@check(2, "2k's three tags, 2i's four tags, 2j's two tags, 2l's three tags, 2m's three tags "
         "exist; both predictor seals bind; seal shas == literals; PREDICTOR_SHA_2N re-derives")
def _c2(ctx):
    for tag in (bk.PREREG_TAG_2K, bk.SEAL_TAG_2K, "exp2k-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (bi.PREREG_TAG, bi.PREDICTOR_SEAL_TAG, bi.ENDPOINT_SEAL_TAG, "exp2i-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (an2j.PREREG_TAG_2J, "exp2j-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (bl.PREREG_TAG_2L, bl.ENDPOINT_SEAL_TAG_2L, "exp2l-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (bm.PREREG_TAG_2M, bm.ENDPOINT_SEAL_TAG_2M, "exp2m-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    seal_2k = json.loads(bk.seal_path(bk.EXP2K).read_text())
    psl_2k = an2i.require_seal_2i(bk.SEAL_TAG_2K, an2k._seal_paths_2k(bk.EXP2K, seal_2k))
    _eq(psl_2k["failures"], [], "2k seal binds")
    seal_2i = an2i._load_predictor_seal_content(bi.EXP2I)
    psl_2i = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG, an2i._predictor_seal_paths(bi.EXP2I, seal_2i))
    _eq(psl_2i["failures"], [], "2i predictor seal binds")
    _eq(seal_2k["sha256"], bn.SEAL_2K_SHA256, "2k seal sha == literal")
    _eq(seal_2i["sha256"], bn.SEAL_2I_SHA256, "2i seal sha == literal")
    _eq(bn.predictor_sha_2n(seal_2k["sha256"], seal_2i["sha256"]), bn.PREDICTOR_SHA_2N,
       "PREDICTOR_SHA_2N re-derives")


@check(3, "referents_2n.json: literal sha, N_FILES_2N entries, zero refusals")
def _c3(ctx):
    if an.REFERENTS_2N_SHA256 is None or mkr.N_FILES_2N is None:
        return "SKIP"
    _eq(Path(an.REFERENTS_PATH_2N).is_file(), True, "referents_2n.json on disk")
    bad = mkr.check_referents(an.REFERENTS_PATH_2N, sha_pin=an.REFERENTS_2N_SHA256)
    _eq(bad, [], "zero refusals")


@check(4, "the manifest: load_manifest_comma at the pin; 24 grid + twin + stage2_final + main; "
         "endpoint revision + commit; 3 shards each; checkpoints_2g.candidate reproduces every "
         "entry's files; EVERY40K_SUBSET_2N a strict subset of GRID_COMMA")
def _c4(ctx):
    man = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    ctx["manifest"] = man
    _eq(len(man["entries_comma"]), 24, "24 grid points")
    ep = man["entries_comma"][str(bn.ENDPOINT_STEP_2N)]
    _eq(ep["revision"], bn.REV_ENDPOINT_2N, "endpoint revision literal")
    _eq(ep["commit"], "e295235994f32d763c359d324265a176e591f632", "endpoint commit literal")
    _eq(man["stage2_final"]["revision"], bn.REV_STAGE2_FINAL_2N, "stage2_final revision literal")
    _eq(man["twin"]["kind"], "from_config", "twin is a from_config entry")
    for step, e in man["entries_comma"].items():
        _eq(len(e["lfs_sha256"]), 3, f"step {step}: 3 shards")
    _eq(len(man["stage2_final"]["lfs_sha256"]), 3, "stage2_final: 3 shards")
    _eq(len(man["main"]["lfs_sha256"]), 3, "main: 3 shards")
    inv = bn.load_inventory_comma()
    table = inv[bn.REPO_COMMA]
    main_files = table[bn.REV_MAIN_2N]["files"]
    for step, e in man["entries_comma"].items():
        cand = ck.candidate(e["revision"], table[e["revision"]]["files"], main_files)
        _eq(cand["files"], e["files"], f"step {step}: candidate reproduces files")
    cand2 = ck.candidate(man["stage2_final"]["revision"], table[man["stage2_final"]["revision"]]["files"],
                         main_files)
    _eq(cand2["files"], man["stage2_final"]["files"], "stage2_final: candidate reproduces files")
    cand_main = ck.candidate(man["main"]["revision"], table[man["main"]["revision"]]["files"], main_files)
    _eq(cand_main["files"], man["main"]["files"], "main: candidate reproduces files")
    _eq(set(bn.EVERY40K_SUBSET_2N) < set(bn.GRID_COMMA), True,
       "EVERY40K_SUBSET_2N is a strict subset of GRID_COMMA")


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
                                            rungs=bn.R_CAP_2K)
        _eq(failures, [], f"{size}: tier loads cleanly")
        for r in bn.R_CAP_2K:
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
    x_b = bi.sampler_counts_olmo(bn.R_CAP_2K, root=bi.EXP2I, battery=battery, verify_fn=verify)
    seal_2i = an2i._load_predictor_seal_content(bi.EXP2I)
    for r in bn.R_CAP_2K:
        _eq(x_b[r], seal_2i["counts"][r], f"{r}: x_B == 2i's sealed counts")
    rs2i = an2i._load_rung_set(bi.EXP2I)
    _eq(tuple(sorted(rs2i["R_CAP"])), tuple(sorted(bn.R_CAP_2K)), "2i's R_CAP == the nine")


@check(7, "rung_set_from_counts_2n on hand counts (test_battery_2n's case) and on 2m's "
         "committed SmolLM3-3B stage1_final counts (descriptive)")
def _c7(ctx):
    floors = ctx["floors"]
    counts = {r: 0 for r in bt.RUNGS}
    for r in ("antonym", "add_base8", "sub3_mid"):
        counts[r] = 480
    counts["count_div13"] = 480
    counts["reverse_string"] = 480
    rs = bn.rung_set_from_counts_2n(counts, floors)
    _eq(rs["R_PRIMARY"], ["add_base8", "antonym", "sub3_mid"], "hand-count case: R_PRIMARY")
    _eq(rs["R_ELEVEN_EXTRA"], ["count_div13"], "hand-count case: R_ELEVEN_EXTRA")
    _eq(rs["R_EXTRA"], ["reverse_string"], "hand-count case: R_EXTRA")
    counts3b = {r: json.loads((bm.EXP2M / "results" / "endpoint" / "stage1_final" /
                              f"{r}.json").read_text())["correct"] for r in bt.RUNGS}
    rs3b = bn.rung_set_from_counts_2n(counts3b, floors)
    print(f"      (2m's committed SmolLM3 endpoint would give R_PRIMARY {rs3b['R_PRIMARY']} "
         f"— descriptive, not a Comma v0.1-1T claim)")


@check(8, "the tree on literal inputs: every terminal, THIN/UNDERPOWERED disclosures, "
         "T_BAR/ALPHA boundaries")
def _c8(ctx):
    def prim(T, p, fires, eligible=("r1", "r2", "r3")):
        return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
               "eligible": list(eligible), "per_rung": {}}

    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    under_b = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}}
    nine = tuple(sorted(bn.R_CAP_2K))

    ins = an.verdict_2n(["x"], None, None, None, nine)
    _eq(ins["verdict"], "INSUFFICIENT_DATA", "refusal -> INSUFFICIENT_DATA")
    _eq(an._licensed_2n(ins), an.LICENSED_2N["INSUFFICIENT_DATA"], "refusal licence")

    for a, b, want in ((True, False, "PYTHIA-ONLY"), (False, True, "OLMO-ONLY"),
                       (True, True, "SHARED"), (False, False, "NEITHER")):
        t = an.verdict_2n([], prim(0.2 if a else 0.02, 0.001, a), prim(0.2 if b else 0.02, 0.001, b),
                          powered, nine)
        _eq(t["verdict"], want, f"{want} terminal")
        _eq(an._licensed_2n(t).startswith(an.LICENSED_2N[want]), True, f"{want} licence prefix")

    thin_rungs = nine[:2]
    t_thin = an.verdict_2n([], prim(0.02, 0.3, False), prim(0.02, 0.3, False), powered, thin_rungs)
    _eq(an.DISCLOSURE_THIN_2N in t_thin["disclosures"], True, "thin disclosed")

    t_under = an.verdict_2n([], prim(0.2, 0.001, True), prim(0.02, 0.3, False), under_b, nine)
    _eq(an.DISCLOSURE_UNDERPOWERED_2N["B"] in t_under["disclosures"], True, "underpowered B disclosed")

    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR, "p": an.ALPHA - 1e-6}}), True,
       "T == T_BAR (inclusive), p < ALPHA fires")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR - 1e-9, "p": an.ALPHA - 1e-6}}), False,
       "T just under T_BAR does not fire")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR + 0.1, "p": an.ALPHA}}), False,
       "p == ALPHA (not strictly under) does not fire")


@check(9, "record stamps round-trip: item_record_2n -> step_record_failures_2n clean "
         "(incl. the twin); endpoint_item_record_2n -> endpoint_record_failures_2n clean; "
         "gate1_failures_comma/gate1_rederive_comma clean on a hand pair")
def _c9(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    man = ctx["manifest"]
    cap = battery["antonym"]
    ev = {"bits": [1] * 10 + [0] * (bk.N_ITEMS - 10), "correct": 10,
         "continuations": [f" {it['answer']}" if i < 10 else " zzz"
                           for i, it in enumerate(cap["eval_items"])]}
    entry = bn.entry_comma(man, 40000)
    esha = "E" * 64
    rec = bn.item_record_2n(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry), step=40000,
                            endpoint_sha=esha, t_s=0.0)
    bad = an.step_record_failures_2n(rec, step=40000, rung="antonym", cap=cap, entry=entry,
                                     verify_fn=verify, endpoint_sha=esha)
    _eq(bad, [], "item_record_2n -> step_record_failures_2n round trip")

    entry_twin = bn.entry_comma(man, bn.TWIN)
    twin_ckpt = {"revision": bn.TWIN, "commit": None, "kind": "from_config", "files": [],
                "weight_sha256": "T", "config_source": f"{bn.REPO_COMMA}@{entry_twin['config_commit']}",
                "tokenizer_source": f"{bn.REPO_COMMA}@{entry_twin['config_commit']}"}
    rec_twin = bn.item_record_2n(rung="antonym", cap=cap, ev=ev, ckpt=twin_ckpt, step=bn.TWIN,
                                 endpoint_sha=esha, t_s=0.0)
    bad_twin = an.step_record_failures_2n(rec_twin, step=bn.TWIN, rung="antonym", cap=cap,
                                          entry=entry_twin, verify_fn=verify, endpoint_sha=esha)
    _eq(bad_twin, [], "item_record_2n -> step_record_failures_2n round trip (twin)")
    _eq(rec_twin["dtype"], bn.DTYPE_2N, "twin record dtype == DTYPE_2N")

    entry_ep = bn.entry_which_comma(man, "stage1_final")
    rec2 = bn.endpoint_item_record_2n(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry_ep),
                                      which="stage1_final",
                                      seal={"tag": bn.PREDICTOR_TAGS_2N, "sha256": bn.PREDICTOR_SHA_2N},
                                      t_s=0.0, eos_facts=_EOS_FACTS)
    bad2 = an.endpoint_record_failures_2n(rec2, which="stage1_final", rung="antonym", cap=cap,
                                          entry=entry_ep, verify_fn=verify)
    _eq(bad2, [], "endpoint_item_record_2n -> endpoint_record_failures_2n round trip")
    # FREEZE F-1: the endpoint record carries the LOADER's measured eos
    # ids, and a record whose loader never applied `set_eos_stop_2n` is
    # refused even though `eos_stop_id` still reads the constant.
    _eq(rec2["generation_eos_token_id"], bn.EOS_STOP_ID_2N, "endpoint record carries the measured stop id")
    _eq(rec2["config_eos_token_id"], bn.CONFIG_EOS_TOKEN_ID_2N, "endpoint record discloses config's eos")
    missed = bn.endpoint_item_record_2n(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry_ep),
                                        which="stage1_final",
                                        seal={"tag": bn.PREDICTOR_TAGS_2N, "sha256": bn.PREDICTOR_SHA_2N},
                                        t_s=0.0,
                                        eos_facts={"config_eos_token_id": bn.CONFIG_EOS_TOKEN_ID_2N,
                                                   "generation_eos_token_id": bn.CONFIG_EOS_TOKEN_ID_2N})
    _eq(missed["eos_stop_id"], bn.EOS_STOP_ID_2N, "the constant is unchanged on a missed override")
    bad_eos = an.endpoint_record_failures_2n(missed, which="stage1_final", rung="antonym", cap=cap,
                                             entry=entry_ep, verify_fn=verify)
    _eq(any("generation_eos_token_id" in b and "not a measurement" in b for b in bad_eos), True,
       f"a missed stop-id override is refused: {bad_eos}")

    # M-3 (2m's final review, carried forward): `rec2` is built a second
    # time from an identical call, bound to `rec2b`, so `sweep_recs` and
    # `stage1_recs` are two independently-constructed records with
    # identical content rather than two dicts aliasing one `rec2` object.
    rec2b = bn.endpoint_item_record_2n(rung="antonym", cap=cap, ev=ev, ckpt=_ckpt(entry_ep),
                                       which="stage1_final",
                                       seal={"tag": bn.PREDICTOR_TAGS_2N, "sha256": bn.PREDICTOR_SHA_2N},
                                       t_s=0.0, eos_facts=_EOS_FACTS)
    sweep_recs = {r: rec2 for r in bt.RUNGS}
    stage1_recs = {r: rec2b for r in bt.RUNGS}
    gate_rec = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
               "continuation_diffs": {r: 0 for r in bt.RUNGS},
               "continuations_compared": {r: bk.N_ITEMS for r in bt.RUNGS},
               "digest_sweep": "D", "digest_endpoint": "D",
               "commit_sweep": entry_ep["commit"], "commit_endpoint": entry_ep["commit"],
               "prereg_tag": bn.PREREG_TAG_2N}
    bad3 = bn.gate1_failures_comma(gate_rec, stage1_recs)
    _eq(bad3, [], "gate1_failures_comma round trip")
    bad4 = bn.gate1_rederive_comma(sweep_recs, stage1_recs, gate_rec)
    _eq(bad4, [], "gate1_rederive_comma round trip")
    mixed = dict(stage1_recs)
    mixed["odd6"] = {**rec2, "weight_sha256": "OTHER"}
    _eq(any("did not come from one load" in b for b in bn.gate1_failures_comma(gate_rec, mixed)), True,
       "gate1_failures_comma measures the endpoint digest over all 34 records (freeze F-2)")
    _eq(any("did not come from one load" in b
           for b in an.which_coherence_failures_2n("stage1_final", mixed)), True,
       "which_coherence_failures_2n refuses a which assembled from two loads (freeze F-2)")
    _eq(an.which_coherence_failures_2n("stage1_final", stage1_recs), [],
       "which_coherence_failures_2n clean on one load")


@check(10, "the Comma tree on the real EXP2N: no halt marker; endpoint/rung-set/power/sweep "
          "status before or after the campaign")
def _c10(ctx):
    _eq(bn.halt_marker_path(bn.EXP2N).exists(), False, "no halt marker")
    rung_set_p, power_p = bn.rung_set_path(bn.EXP2N), bn.power_path(bn.EXP2N)
    rs = None
    if not rung_set_p.is_file():
        print("      (endpoint/rung set: absent — pre-campaign)")
    else:
        battery, verify, floors = ctx["battery"], ctx["verify"], ctx["floors"]
        man = ctx["manifest"]
        for which in bn.ENDPOINT_WHICH_2N:
            entry = bn.entry_which_comma(man, which)
            an.load_endpoint_which_2n(bn.EXP2N, which, battery, verify, entry=entry)
        entry_stage1 = bn.entry_which_comma(man, "stage1_final")
        stage1 = an.load_endpoint_which_2n(bn.EXP2N, "stage1_final", battery, verify, entry=entry_stage1)
        rs = an._load_rung_set_2n(bn.EXP2N)
        _eq(an._check_rung_set_derivation_2n(rs, stage1, floors), [], "rung set re-derivation PASS")
        _eq(an._check_rung_set_vs_endpoint_2n(rs, stage1), [], "rung set vs endpoint PASS")
        _eq(an._check_rung_set_endpoint_shas_2n(rs, bn.EXP2N), [], "endpoint_file_sha256 PASS")
    if not power_p.is_file():
        print("      (power: absent — pre-campaign)")
    else:
        if rs is None:
            rs = an._load_rung_set_2n(bn.EXP2N)
        power = an.load_power_2n(bn.EXP2N, tuple(rs["R_PRIMARY"]), bn.PREDICTOR_SHA_2N)
        _eq(power["A"]["declared_status"] in an2i.DECLARED_STATUSES_2I, True, "load_power_2n PASS")
    gate1_p = bn.gate1_path(bn.EXP2N)
    if not gate1_p.is_file():
        print("      (sweep: absent — pre-campaign)")
    else:
        battery, verify = ctx["battery"], ctx["verify"]
        man = ctx["manifest"]
        entry_stage1 = bn.entry_which_comma(man, "stage1_final")
        stage1 = an.load_endpoint_which_2n(bn.EXP2N, "stage1_final", battery, verify, entry=entry_stage1)
        esha = bn.endpoint_sha256(bn.EXP2N)
        sweep = an.load_sweep_comma(bn.EXP2N, battery, verify, manifest=man, endpoint_sha=esha)
        gate1 = json.loads(gate1_p.read_text())
        _eq(bn.gate1_rederive_comma(sweep[bn.ENDPOINT_STEP_2N], stage1, gate1), [],
           "gate1_rederive_comma PASS")


@check(11, "s4_matched_2n on the real predictors with a synthetic outcome: k in [1,64], "
          "n_blocks == 64 // k; matched_k_256's own return keys present")
def _c11(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    rungs = bn.R_CAP_2K
    rows = {r: fn.draw_rows_2i(bi.EXP2I, r) for r in rungs}
    bits_b = {r: fn.verified_bits(rows[r], battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    seal = json.loads(bk.seal_path(bk.EXP2K).read_text())
    x_a256 = {r: seal["counts"]["1b"][r] for r in rungs}
    rng = np.random.default_rng(0)
    out = {}
    for r in rungs:
        y = [int(v) for v in rng.integers(0, bn.n_trained_comma() + 1, size=bk.N_ITEMS)]
        out[r] = {"y": y, "n_pos": sum(1 for v in y if v > 0),
                 "first": [None if v == 0 else 1000 for v in y]}
    s4 = an.s4_matched_2n(bits_b, x_a64, x_a256, out, strata, rungs)
    for r in rungs:
        p = s4["per_rung"][r]
        _eq(1 <= p["k"] <= 64, True, f"{r}: k in [1,64]")
        _eq(p["n_blocks"], 64 // p["k"], f"{r}: n_blocks == 64 // k")
    _eq(set(bk.matched_k_256(0.5, 0.5)), {"k", "capped", "n_blocks"}, "matched_k_256 return keys")


@check(12, "the import surface: check_imports_2n() in THIS process passes")
def _c12(ctx):
    if an.IMPORTED_SHA256_2N is None:
        return "SKIP"
    an.check_imports_2n()


@check(13, "S8's five committed outcomes load through their own frozen readers with zero "
          "failures (≈ 3-5 min)")
def _c13(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    out = an.load_committed_outcomes_2n(battery, verify, root_2i=bi.EXP2I, root_2l=bl.EXP2L, root_2m=bm.EXP2M)
    _eq(set(out), {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b", "smollm3_3b"}, "S8's five sources")
    _eq(set(out["olmo2_13b"]), set(bt.RUNGS), "olmo2_13b covers the full 34-rung battery")
    _eq(set(out["smollm3_3b"]), set(bt.RUNGS), "smollm3_3b covers the full 34-rung battery")
    _eq(len(out["pythia_2.8b"]), len(bg.R_28), "pythia_2.8b covers 2g's eleven")
    for name, ok in out.items():
        for r, rec in ok.items():
            _eq(len(rec["y"]), bt.N_ITEMS, f"{name}/{r}: y is {bt.N_ITEMS} long")
            _eq(all(isinstance(v, int) for v in rec["y"]), True, f"{name}/{r}: y is all ints")
    _eq(out["olmo2_13b"]["add_base8"]["n_pos"] > 0, True, "olmo2_13b/add_base8 has a positive item")
    for name, ok in out.items():
        print(f"      ({name}: {len(ok)} rung(s), n_pos sum {sum(v['n_pos'] for v in ok.values())})")


@check(14, "check_tokenizer_2n accept + four refusals; set_eos_stop_2n on a stub; render_2n "
          "prefixing; read_increment_3b_2n(bm.EXP2M) == the literal; s9_sign_ledger_2n "
          "reproduces the committed literals")
def _c14(ctx):
    bn.check_tokenizer_2n(_Tok())
    for kw, needle in ((dict(padding_side="right"), "padding_side"),
                       (dict(pad_token_id=5), "pad_token_id"),
                       (dict(pad_absent=True), "pad_token_id"),
                       (dict(eos_token_id=2), "eos_token_id"),
                       (dict(bos_token_id=1), "bos_token_id"),
                       (dict(unk_token_id=0), "unk_token_id"),
                       (dict(vocab_len=bn.CONFIG_VOCAB_2N), "64000"),
                       (dict(plain_adds_special=True), "special"),
                       (dict(swallow_bos=True), "BOS")):
        try:
            bn.check_tokenizer_2n(_Tok(**kw))
        except RuntimeError as e:
            _eq(needle in str(e), True, f"check_tokenizer_2n should refuse on {kw} naming {needle!r}: {e}")
        else:
            raise AssertionError(f"check_tokenizer_2n accepted a broken stub {kw}")

    class _GenConfig:
        eos_token_id = 2

    class _Config:
        eos_token_id = bn.CONFIG_EOS_TOKEN_ID_2N
        bos_token_id = bn.BOS_TOKEN_ID_2N

    class _Model:
        generation_config = _GenConfig()
        config = _Config()

    m = _Model()
    facts = bn.set_eos_stop_2n(m)
    _eq(m.generation_config.eos_token_id, bn.EOS_STOP_ID_2N, "set_eos_stop_2n overrides to the pinned id")
    _eq(facts["generation_eos_token_id"], bn.EOS_STOP_ID_2N, "facts reflect the override")

    rendered = bn.render_2n(["Q: 1+1", "Q: 2+2"])
    _eq(rendered, [bn.BOS_TOKEN_2N + "Q: 1+1", bn.BOS_TOKEN_2N + "Q: 2+2"], "render_2n prefixes every prompt")

    inc = an.read_increment_3b_2n(bm.EXP2M)
    _eq(round(inc, 4), an.INCREMENT_3B_2N, "read_increment_3b_2n(bm.EXP2M) == the literal to 4 dp")

    A_stub = {"per_rung": {r: {"d": None} for r in an.OPTION_RUNGS_2N}}
    B_stub = {"per_rung": {r: {"d": None} for r in an.OPTION_RUNGS_2N}}
    s9 = an.s9_sign_ledger_2n(A_stub, B_stub, root_2l=bl.EXP2L, root_2m=bm.EXP2M)
    v2l = json.loads((bl.EXP2L / "results" / "verdict.json").read_text())
    v2m = json.loads((bm.EXP2M / "results" / "verdict.json").read_text())
    lits = {"2l A": (s9["rows"]["antonym"]["olmo2_13b_2l"]["A"], v2l["tests"]["A"]["per_rung"]["antonym"]["d"]),
           "2l B": (s9["rows"]["antonym"]["olmo2_13b_2l"]["B"], v2l["tests"]["B"]["per_rung"]["antonym"]["d"]),
           "2m A": (s9["rows"]["antonym"]["smollm3_3b_2m"]["A"], v2m["tests"]["A"]["per_rung"]["antonym"]["d"]),
           "2m B": (s9["rows"]["antonym"]["smollm3_3b_2m"]["B"], v2m["tests"]["B"]["per_rung"]["antonym"]["d"])}
    for name, (got, want) in lits.items():
        _eq(got, want, f"s9 antonym {name} reproduces the committed verdict literal")
    # Deferred minors (Task 3 m3 / Task 4 m5), closed at the freeze: the
    # four known-answer numbers as LITERALS, so this is a known-answer
    # gate and not a re-read of the dict it copies from. Sources: 2l's
    # VERDICT (antonym A -.066 / B +.256) and 2m's (A -.041 / B +.168).
    for name, got, want in (("2l A", s9["rows"]["antonym"]["olmo2_13b_2l"]["A"], -0.066),
                           ("2l B", s9["rows"]["antonym"]["olmo2_13b_2l"]["B"], 0.256),
                           ("2m A", s9["rows"]["antonym"]["smollm3_3b_2m"]["A"], -0.041),
                           ("2m B", s9["rows"]["antonym"]["smollm3_3b_2m"]["B"], 0.168)):
        _eq(round(float(got), 3), want, f"s9 antonym {name} == the committed literal to 3 dp")
    # 2k's/2i's 7B row is a literal table in analyze_2n; assert its values
    # here rather than re-reading the dict s9 copies from.
    _eq({r: dict(v) for r, v in an.SIGN_LEDGER_LITERALS_2N["olmo2_7b_known"].items()},
       {"antonym": {"A": 0.024, "B": 0.217}, "antonym6": {"A": 0.115, "B": 0.214},
        "odd6": {"A": 0.096, "B": 0.121}},
       "s9 7B literals (2k VERDICT A at 256; 2i VERDICT Test B per rung)")
    for r in an.OPTION_RUNGS_2N:
        _eq(s9["rows"][r]["olmo2_7b_known"], an.SIGN_LEDGER_LITERALS_2N["olmo2_7b_known"][r],
           f"s9 {r} 7B row is the literal table")


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
