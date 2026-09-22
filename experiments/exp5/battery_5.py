"""The Exp 5 battery (design `experiment-5-design.md` §3): every input a
committed value or a Hub-metadata pin. Nothing here is a dial.

Zero model contact, zero weight download: `refresh_inventory_5` is the one
NETWORK function (Hub metadata) and is never called by a test; the loader
family lives in `collect_5.py`."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
EXPERIMENTS = EXP5.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401 — before numpy (transitively)
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

RESULTS_5 = EXP5 / "results"
HUB_INVENTORY_PATH_5 = EXP5 / "hub_inventory_5.json"
CHECKPOINTS_PATH_5 = EXP5 / "checkpoints_5.json"
SLICE_PATH_5 = EXP5 / "slice_5.npz"
PROJECTION_PATH_5 = EXP5 / "projection.md"

CHECKPOINTS_SHA256_5 = "82658028d203a65108effe84eb7446bc046067c4f7373f6c584b159125d4b306"

PREREG_TAG_5 = "exp5-preregistered"
TARGETS_SEAL_TAG_5 = "exp5-targets-sealed"
CLOSED_TAG_5 = "exp5-closed"
INSTRUMENT_BLOBS_5 = (
    "experiments/exp5/_threads_5.py", "experiments/exp5/battery_5.py",
    "experiments/exp5/slice_5.py", "experiments/exp5/search_5.py",
    "experiments/exp5/stats_5.py", "experiments/exp5/collect_5.py",
    "experiments/exp5/analyze_5.py", "experiments/exp5/power_5.py",
    "experiments/exp5/run/finals_5.py", "experiments/exp5/run/sweep_5.py",
    "experiments/exp5/hub_inventory_5.json", "experiments/exp5/checkpoints_5.json",
    "experiments/exp5/slice_5.npz",
)

# ------------------------------------------------------------ sizes/pairs
SIZES_5 = ("160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b")
PAIRS_5 = tuple((s, L) for i, s in enumerate(SIZES_5) for L in SIZES_5[i + 1:])   # 21
SMALL_SIDES_5 = SIZES_5[:-1]
LARGE_SIDES_5 = SIZES_5[1:]
REPO_OF_5 = {s: f"EleutherAI/pythia-{s}" for s in SIZES_5}


def _pythia_shas() -> dict:
    from models import PYTHIA_SHAS   # exp2b's, via battery_2d's sys.path
    return PYTHIA_SHAS


# 2c's five pins + the two read from the Hub 2026-09-22 (design §3.1).
MAIN_SHA_5 = {
    "160m": "50f5173d932e8e61f858120bcb800b97af589f46",
    "410m": "9879c9b5f8bea9051dcb0e68dff21493d67e9d4f",
    "1b": "f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2",
    "1.4b": "fedc38a16eea3bd36a96b906d78d11d2ce18ed79",
    "2.8b": "2a259cdd96a4beb1cdf467512e3904197345f6a9",
    "6.9b": "c0e3eee36dc47af0c49f361c74cfe459c09f7f23",
    "12b": "bb1e3e710cdf6b524461d543cfb5ba773f0a81b6",
}
for _s, _sha in _pythia_shas().items():
    if MAIN_SHA_5.get(_s) != _sha:
        raise RuntimeError(f"MAIN_SHA_5[{_s}] != 2c's PYTHIA_SHAS")
del _s, _sha

FINAL_STEP_5 = 143000
SPINE_5 = (1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000, 143000)
N_WINDOW_SIDE_5 = 2
S11_STEP_5 = 142000
TOKENS_PER_STEP_5 = 2_097_152
TOTAL_STEPS_5 = 143000

# ------------------------------------------------------------- the bars
N_ITEMS = bt.N_ITEMS
RUNGS = bt.RUNGS
FAMILY_OF = bt.FAMILY_OF
T_BAR_5 = 0.01
ALPHA_5 = 0.01
MODIFIER_ALPHA_5 = 0.05
MODIFIER_MIN_CELLS_5 = 8
MIN_LIVE_CELLS_5 = 20
MIN_LIVE_RUNGS_5 = 5
MAX_ENUMERATE_BLOCKS_5 = 20
N_PERM_SAMPLED_5 = 10_000
PERM_SEED_5 = 0
N_BOOT_5 = 10_000
BOOT_SEED_5 = 0
DTYPE_5 = "float16"
BATCH_ARGMAX_5 = 16          # 2c's HFRunner default
LOSS_BATCH_5 = 8             # B-8
PAD_ID_5 = 0
SLICE_N_SCORED_5 = 2 ** 21
SLICE_MAX_TOKENS_5 = 2048
SLICE_MIN_TOKENS_5 = 64
SLICE_DATASET_5 = "monology/pile-uncopyrighted"
SLICE_REVISION_5 = "3be90335b66f24456a5d6659d9c8d208c0357119"
SLICE_FILE_5 = "val.jsonl.zst"
SLICE_FILE_SHA256_5 = "db5e5d1532bf8dc33a6589b50ecba1a8c96f7b4b9cb343d168e603c393007c26"
SLICE_FILE_SIZE_5 = 338_045_152
TOKENIZER_SIZE_5 = "2.8b"
TOKENIZER_JSON_SHA256_5 = "c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624"
SLICE_SHA256_5 = "dc48ebd4913309514a30c1acb6e3bbb399ef1b289c51c88758f4db994222c50b"
SLICE_META_PIN_5 = {"n_docs": 2965, "n_read": 3063, "n_skipped": 98, "n_scored": 2097152,
                    "last_doc_truncated": {"doc_index": 2964, "from": 960, "to": 482}}

# gate 1 tolerances (design §3.7 1(b)/(c)), pinned from the one measurement
GATE1_TOL_PER_RUNG_5 = 15
GATE1_TOL_SUM_5 = 120
GATE1_BENCH_5 = {"max_abs_diff": 8, "sum_abs_diff": 57,
                 "source": "tools/vast_bench/runs/2026-09-20-a100-40gb-vast51754225 — the 6.9b "
                           "final on an A100 (fp16, batch 16) against the Mac's committed m4 counts"}
GATE1_INTERIOR_5 = {"2.8b": (1000, 2000, 4000, 8000, 16000, 32000, 100000),
                    "6.9b": (1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000)}
GATE1_DESCRIPTIVE_12B_5 = (1000, 4000, 16000, 32000, 64000, 100000)    # B-6, non-gating

# B-6 ruling 2026-09-22: 2g's committed 12b replication sweep carries
# records for `battery_2g.PREDICTOR_RUNGS` (11) only, never all 34 —
# `mac_interior_counts_5("12b", ...)` reads exactly this set. Pinned as
# a literal (the `MAIN_SHA_5` pattern) and checked against the live
# module at import so a change to 2g's PREDICTOR_RUNGS is caught here,
# not silently absorbed.
GATE1_DESCRIPTIVE_12B_RUNGS_5 = ("antonym", "antonym6", "add_base8", "sub_base8",
                                 "add3_mid", "sub3_mid", "sub4_mid", "median5",
                                 "arith_next", "count_div13", "odd6")
if set(GATE1_DESCRIPTIVE_12B_RUNGS_5) != set(bg.PREDICTOR_RUNGS):
    raise RuntimeError("GATE1_DESCRIPTIVE_12B_RUNGS_5 != battery_2g.PREDICTOR_RUNGS")

GATE1_REFERENT_SOURCE_5 = {"410m": "2d", "1b": "2d", "2.8b": "2c", "6.9b": "2c", "12b": "2c"}

# S6 (B-11): the pythia repo's configs, read 2026-09-22
LR_MAX_5 = {"160m": 6.0e-4, "410m": 3.0e-4, "1b": 3.0e-4, "1.4b": 2.0e-4, "2.8b": 1.6e-4,
            "6.9b": 1.2e-4, "12b": 1.2e-4}
LR_MIN_FRAC_5 = 0.1
WARMUP_FRAC_5 = 0.01

# rung types (S5): Exp 4's partition, pinned by literal (asserted equal in tests)
_ARITHMETIC_5 = ("add3_mid", "sub3_mid", "add4_mid", "sub4_mid", "add_base8", "sub_base8",
                 "arith_next", "quad_next", "count_div13", "count_div7", "median5", "median7",
                 "oct2dec", "base7", "base12_digitsum", "base13", "mod13", "mod13_comp", "mod17",
                 "mod19", "isqrt_gap", "collatz_step2", "roman_sum7", "clock24", "clock24_d999")
_OPTION_5 = ("antonym", "antonym6", "odd6", "odd_one_out")
_STRING_5 = ("reverse_string", "rev_string7", "caesar", "caesar_len8", "hamming12")
RUNG_TYPE_5 = {**{r: "arithmetic" for r in _ARITHMETIC_5}, **{r: "option" for r in _OPTION_5},
               **{r: "string" for r in _STRING_5}}
if set(RUNG_TYPE_5) != set(RUNGS):
    raise RuntimeError("RUNG_TYPE_5 does not partition the 34 rungs")


# -------------------------------------------------------------- inventory

def refresh_inventory_5(sizes=SIZES_5, out_path=HUB_INVENTORY_PATH_5) -> dict:
    """NETWORK (Hub metadata only; disclosed in PROGRESS.md): every
    `step*` branch + `main` of each size, with each LFS file's sha256 and
    size (`checkpoints_2g.refresh_inventory`'s body over REPO_OF_5)."""
    from huggingface_hub import HfApi
    api = HfApi()
    out = {}
    for size in sizes:
        repo = REPO_OF_5[size]
        refs = api.list_repo_refs(repo)
        revs = sorted([b.name for b in refs.branches if b.name.startswith("step")],
                      key=lambda s: int(s[4:]))
        table = {}
        for rev in revs + ["main"]:
            info = api.model_info(repo, revision=rev, files_metadata=True)
            files = {s.rfilename: [s.lfs.sha256, s.size] for s in info.siblings
                     if s.lfs and s.rfilename != "optimizer.pt"}
            table[rev] = {"commit": info.sha, "files": files}
        out[repo] = table
    Path(out_path).write_text(json.dumps(out, indent=1, sort_keys=True))
    return out


def load_inventory_5(path=HUB_INVENTORY_PATH_5) -> dict:
    inv = json.loads(Path(path).read_text())
    for size in SIZES_5:
        if REPO_OF_5[size] not in inv or "main" not in inv[REPO_OF_5[size]]:
            raise ValueError(f"inventory lacks {REPO_OF_5[size]}/main")
    return inv


def revision_of_5(step: int) -> str:
    return "main" if int(step) == FINAL_STEP_5 else f"step{int(step)}"


def _step_of_rev(rev: str):
    if rev == "main":
        return FINAL_STEP_5
    if rev.startswith("step") and rev[4:].isdigit():
        return int(rev[4:])
    return None


def build_manifest_5(size: str, inv: dict) -> dict:
    """The available list under 2g's candidate-file rule over EVERY
    revision of the size: a trained revision is available iff it has a
    candidate whose signature equals no other revision's (main
    included); the final is `main` at the pinned commit; every exclusion
    carries its evidence (design §3.1)."""
    repo = REPO_OF_5[size]
    table = inv[repo]
    main_files = table["main"]["files"]
    cands = {rev: ck.candidate(rev, t["files"], main_files) for rev, t in table.items()}
    sigs = {rev: (ck.signature(table[rev]["files"], c) if c else None)
            for rev, c in cands.items()}

    def dups_of(rev):
        return sorted((r for r, s in sigs.items()
                       if r != rev and s is not None and s == sigs[rev]),
                      key=lambda r: (r == "main", _step_of_rev(r) or 0))

    def entry_of(rev):
        c = cands[rev]
        return {"revision": rev, "commit": table[rev]["commit"], "kind": c["kind"],
                "files": list(c["files"]),
                "lfs_sha256": {n: table[rev]["files"][n][0] for n in c["lfs"]},
                "lfs_size": {n: int(table[rev]["files"][n][1]) for n in c["lfs"]}}

    entries, excluded, ignored, step0 = {}, {}, [], None
    for rev in table:
        step = _step_of_rev(rev)
        if step is None:
            ignored.append(rev)
            continue
        if rev == f"step{FINAL_STEP_5}":
            continue                       # described in hub_step143000; the final is `main`
        c = cands[rev]
        if step == 0:
            step0 = ({**entry_of(rev), "duplicates": dups_of(rev)} if c
                     else {"revision": rev, "commit": table[rev]["commit"], "kind": None})
            continue
        if c is None:
            excluded[str(step)] = {"reason": "no candidate weight file of its own (main's "
                                             "stale copy only)", "revision": rev,
                                   "commit": table[rev]["commit"], "files": sorted(table[rev]["files"])}
            continue
        same = dups_of(rev)
        if rev != "main" and same:
            excluded[str(step)] = {"reason": "candidate files duplicate another revision's",
                                   "duplicates": same, "kind": c["kind"],
                                   "lfs_sha256": {n: table[rev]["files"][n][0] for n in c["lfs"]}}
            continue
        entries[str(step)] = entry_of(rev)
    if entries.get(str(FINAL_STEP_5), {}).get("commit") != MAIN_SHA_5[size]:
        raise ValueError(f"{repo}: the final is not 2c's/the design's pinned main commit "
                         f"{MAIN_SHA_5[size]}")
    hub = table.get(f"step{FINAL_STEP_5}")
    hub_c = cands.get(f"step{FINAL_STEP_5}")
    main_bins = tuple(v[0] for n, v in sorted(main_files.items())
                      if n.startswith("pytorch_model") and n.endswith(".bin"))
    hub_bins = tuple(v[0] for n, v in sorted(hub["files"].items())
                     if n.startswith("pytorch_model") and n.endswith(".bin")) if hub else ()
    hub_rec = {"commit": hub["commit"] if hub else None,
               "kind": hub_c["kind"] if hub_c else None,
               "lfs_sha256": ({n: hub["files"][n][0] for n in hub_c["lfs"]} if hub_c else {}),
               "signature_equals_main": bool((hub_c and sigs[f"step{FINAL_STEP_5}"] == sigs["main"])
                                             or (hub_bins and hub_bins == main_bins)),
               "duplicates": dups_of(f"step{FINAL_STEP_5}") if hub else []}

    def _stale_count(name):
        main_sha = main_files.get(name, [None])[0]
        if main_sha is None:
            return 0
        return sum(1 for r, t in table.items() if r != "main"
                   and t["files"].get(name, [None])[0] == main_sha)

    available = sorted(int(k) for k in entries)
    return {"size": size, "repo": repo, "main_commit": table["main"]["commit"],
            "entries": entries, "excluded": excluded, "available": available,
            "step0": step0, "ignored_revisions": sorted(ignored),
            "final_duplicates": dups_of("main"), "hub_step143000": hub_rec,
            "stale_main_copies": {"model.safetensors": _stale_count("model.safetensors"),
                                  "pytorch_model.bin": _stale_count("pytorch_model.bin")},
            "n_revisions": len(table)}


def build_all_5(inv: dict) -> dict:
    return {size: build_manifest_5(size, inv) for size in SIZES_5}


def write_manifest_5(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest_5(path=CHECKPOINTS_PATH_5, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    for size in SIZES_5:
        m = obj.get(size)
        if not m or m.get("main_commit") != MAIN_SHA_5[size] or \
                str(FINAL_STEP_5) not in m.get("entries", {}) or \
                m.get("available", [])[-1:] != [FINAL_STEP_5]:
            raise ValueError(f"{path}: {size} manifest is not the frozen layout")
    return obj


def entry_5(manifest: dict, size: str, step: int) -> dict:
    e = manifest[size]["entries"].get(str(int(step)))
    if e is None:
        raise ValueError(f"{size} step {step} is not an available entry")
    return e


def available_5(manifest: dict, size: str) -> tuple:
    return tuple(int(s) for s in manifest[size]["available"])


def spine_5(manifest: dict, size: str) -> tuple:
    """SPINE_5 with each unavailable point replaced by the next available
    step above it; a substitution that lands on another spine point (or
    nothing above) is refused — the spine must have nine distinct points."""
    avail = available_5(manifest, size)
    out = []
    for s in SPINE_5:
        if s in avail:
            out.append(s)
            continue
        above = [a for a in avail if a > s]
        if not above:
            raise ValueError(f"{size}: no available step above the excluded spine point {s}")
        out.append(above[0])
    if len(set(out)) != len(SPINE_5) or list(out) != sorted(out):
        raise ValueError(f"{size}: spine substitution collapsed two points: {out}")
    return tuple(out)


def spine_substitutions_5(manifest: dict, size: str) -> dict:
    return {str(s): t for s, t in zip(SPINE_5, spine_5(manifest, size)) if s != t}


# ------------------------------------------------------------ floors/bar

def load_floors_5() -> dict:
    return bg.load_floors()


def clears_5(count: int, floor: float, n: int = N_ITEMS) -> bool:
    return bool(st.binomial_bar(int(count), n, floor)["significant"])


# ----------------------------------------------------- the Mac's referents

def _argmax_2d_counts(size: str) -> dict:
    root = EXPERIMENTS / "exp2d" / "results" / "argmax" / f"{size}_trained"
    out = {}
    for r in RUNGS:
        rec = json.loads((root / f"{r}.json").read_text())
        if rec.get("rung") != r or rec.get("size") != size or rec.get("tier") != "argmax":
            raise ValueError(f"2d argmax record {size}/{r}: not the committed shape")
        out[r] = int(rec["correct"])
    return out


def _m4_2c_counts(size: str) -> dict:
    """2c's committed m4 final counts read over all 34 RUNGS, each
    re-asserted against `bg.FINAL_COUNT_PIN` WHERE the pin has an entry
    (2.8b's pin covers all 34; 12b's covers only the 11 rungs 2g's own
    predictor needed — `bg.load_m4_counts(size, rungs=RUNGS)` KeyErrors
    on 12b's un-pinned rungs even though their m4 records are on disk,
    so the full 34-rung read goes straight to `bg.m4_path` instead of
    through 2g's rungs-must-all-be-pinned loader)."""
    pin = bg.FINAL_COUNT_PIN.get(size, {})
    out = {}
    for r in RUNGS:
        rec = json.loads(bg.m4_path(size, r).read_text())
        if rec.get("capability") != r or rec.get("n") != N_ITEMS or \
                rec.get("mode") != "trained" or rec.get("size") != size:
            raise ValueError(f"m4 record {size}/{r}: not the committed shape")
        if r in pin and rec["correct"] != pin[r]:
            raise ValueError(f"m4 {size}/{r}: correct {rec['correct']} against "
                             f"the pin {pin[r]}")
        out[r] = int(rec["correct"])
    return out


def mac_final_counts_5(size: str):
    """The Mac's committed final counts on all 34 rungs, or None for the
    two sizes with no referent (160m, 1.4b — design §3.7 1(b))."""
    src = GATE1_REFERENT_SOURCE_5.get(size)
    if src is None:
        return None
    if src == "2d":
        return _argmax_2d_counts(size)
    if size == "6.9b":
        return {r: int(v) for r, v in bh.load_m4_counts_69().items()}
    return _m4_2c_counts(size)


def gate1_interior_steps_5(size: str) -> tuple:
    return tuple(GATE1_INTERIOR_5.get(size, ()))


def interior_record_path_5(size: str, step: int, rung: str) -> Path:
    if size == "2.8b":
        return bg.sweep_dir(bg.EXP2G, "2.8b") / f"step{int(step)}" / f"{rung}.json"
    if size == "6.9b":
        return bh.record_path_2h(bh.EXP2H, step, rung)
    if size == "12b":
        return bg.sweep_dir(bg.EXP2G, "12b") / f"step{int(step)}" / f"{rung}.json"
    raise ValueError(f"no committed interior referent for {size}")


def mac_interior_counts_5(size: str, step: int):
    """2.8b/6.9b: all 34 `RUNGS`, as always. 12b: exactly
    `GATE1_DESCRIPTIVE_12B_RUNGS_5` (11) — 2g's committed 12b
    replication sweep never wrote the other 23 rungs' record files, so
    the rungs whose files actually EXIST under `interior_record_path_5`
    are asserted to equal the pin before anything is read; any other
    set on disk is a refusal (a genuine data-shape defect, not a
    missing-checkpoint gap)."""
    steps = gate1_interior_steps_5(size) + (GATE1_DESCRIPTIVE_12B_5 if size == "12b" else ())
    if int(step) not in steps:
        return None
    if size == "12b":
        present = {r for r in RUNGS if interior_record_path_5(size, step, r).is_file()}
        if present != set(GATE1_DESCRIPTIVE_12B_RUNGS_5):
            raise ValueError(f"12b/step{step}: the record files present {sorted(present)} != "
                             f"GATE1_DESCRIPTIVE_12B_RUNGS_5 {sorted(GATE1_DESCRIPTIVE_12B_RUNGS_5)}")
        rungs = GATE1_DESCRIPTIVE_12B_RUNGS_5
    else:
        rungs = RUNGS
    out = {}
    for r in rungs:
        rec = json.loads(interior_record_path_5(size, step, r).read_text())
        if rec.get("rung") != r or int(rec.get("step")) != int(step) or rec.get("n") != N_ITEMS:
            raise ValueError(f"committed record {size}/step{step}/{r}: not the expected shape")
        out[r] = int(rec["correct"])
    return out


def tolerance_failures_5(counts: dict, referent: dict, *, label: str, rungs=None) -> list:
    """Per-rung |Δ| against `GATE1_TOL_PER_RUNG_5` and the summed |Δ|
    against `GATE1_TOL_SUM_5`, over `rungs` (default `None` → all of
    `RUNGS`, 34 — every pre-existing call is unchanged). When `rungs`
    names a PROPER SUBSET (B-6's 12b comparison, 11 of 34 —
    `analyze_5._b6_12b_5`), the sum bound is scaled to
    `GATE1_TOL_SUM_5 * len(rungs) / len(RUNGS)` and the failure
    message says so explicitly: `GATE1_TOL_SUM_5` (120) was set for a
    34-rung comparison and is not a meaningful bound unscaled over 11."""
    use_rungs = tuple(rungs) if rungs is not None else RUNGS
    bad, total = [], 0
    for r in use_rungs:
        if r not in counts or r not in referent:
            bad.append(f"{label}/{r}: count missing on one side")
            continue
        d = abs(int(counts[r]) - int(referent[r]))
        total += d
        if d > GATE1_TOL_PER_RUNG_5:
            bad.append(f"{label}/{r}: |Δ| {d} > {GATE1_TOL_PER_RUNG_5} "
                       f"({counts[r]} vs the Mac's {referent[r]})")
    if rungs is not None and len(use_rungs) != len(RUNGS):
        bound = GATE1_TOL_SUM_5 * len(use_rungs) / len(RUNGS)
        if total > bound:
            bad.append(f"{label}: sum |Δ| {total} > {bound:.2f} (GATE1_TOL_SUM_5 scaled to "
                       f"{len(use_rungs)}/{len(RUNGS)} rungs)")
    else:
        if total > GATE1_TOL_SUM_5:
            bad.append(f"{label}: sum |Δ| {total} > {GATE1_TOL_SUM_5}")
    return bad


# ------------------------------------------------------------------- S6

def lr_at_5(size: str, step: int) -> float:
    """GPT-NeoX's warmup + cosine (B-11): linear warmup over 1 % of the
    143,000 iterations, then cosine from lr to 0.1·lr at the last step."""
    lr, mn = LR_MAX_5[size], LR_MIN_FRAC_5 * LR_MAX_5[size]
    w = int(WARMUP_FRAC_5 * TOTAL_STEPS_5)
    if step < w:
        return lr * step / w
    frac = (step - w) / (TOTAL_STEPS_5 - w)
    return mn + 0.5 * (lr - mn) * (1.0 + math.cos(math.pi * frac))


def tokens_seen_5(step: int) -> int:
    return int(step) * TOKENS_PER_STEP_5


# ----------------------------------------------------------------- paths

def units_root_5(root) -> Path:
    return Path(root) / "results" / "units"


def unit_dir_5(root, size: str, step: int) -> Path:
    return units_root_5(root) / size / f"step{int(step)}"


def checkpoint_record_path_5(root, size, step) -> Path:
    return unit_dir_5(root, size, step) / "_checkpoint.json"


def loss_record_path_5(root, size, step) -> Path:
    return unit_dir_5(root, size, step) / "_loss.json"


def rung_record_path_5(root, size, step, rung) -> Path:
    return unit_dir_5(root, size, step) / f"{rung}.json"


def unit_record_path_5(root, size, step) -> Path:
    return unit_dir_5(root, size, step) / "_unit.json"


def halt_marker_path_5(root, size) -> Path:
    return units_root_5(root) / size / "HALTED"


def search_log_path_5(root, size) -> Path:
    return units_root_5(root) / size / "search_log.json"


def gate1c_path_5(root, size) -> Path:
    return units_root_5(root) / size / "gate1c.json"


def gate1a_path_5(root) -> Path:
    return Path(root) / "results" / "gate1a.json"


def gate1b_path_5(root) -> Path:
    return Path(root) / "results" / "gate1b.json"


def host_record_path_5(root) -> Path:
    return Path(root) / "results" / "host_5.json"


def loss_table_path_5(root) -> Path:
    return Path(root) / "results" / "loss_table_5.json"


def power_path_5(root) -> Path:
    return Path(root) / "results" / "power_5.json"


def projection_path_5() -> Path:
    return PROJECTION_PATH_5


def s9_dir_5(root, size, step) -> Path:
    return Path(root) / "results" / "s9" / size / f"step{int(step)}"


def unit_files_5() -> tuple:
    """The 36 files a unit holds beside `_unit.json`."""
    return ("_checkpoint.json", "_loss.json") + tuple(f"{r}.json" for r in RUNGS)


def unit_complete_5(root, size, step) -> bool:
    """`_unit.json` present and every file it names present with the sha
    it records (the unit record is written LAST by the runner)."""
    d = unit_dir_5(root, size, step)
    p = d / "_unit.json"
    if not p.is_file():
        return False
    try:
        rec = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    files = rec.get("files") or {}
    if set(files) != set(unit_files_5()):
        return False
    return all((d / name).is_file() and bg.sha256_file(d / name) == sha
               for name, sha in files.items())


# ------------------------------------------------------ record contracts

STACK_KEYS_5 = ("torch", "transformers", "numpy", "safetensors", "tokenizers", "huggingface_hub")


def host_record_failures_5(rec: dict) -> list:
    bad = []
    stack = rec.get("stack") or {}
    for k in STACK_KEYS_5:
        if not stack.get(k):
            bad.append(f"host record: stack lacks {k}")
    for k in ("device", "gpu", "python"):
        if not rec.get(k):
            bad.append(f"host record: {k} missing")
    tr = rec.get("transports") or {}
    for k in ("classic_mbps", "xet_mbps", "used"):
        if k not in tr:
            bad.append(f"host record: transports lacks {k} (gate 0: both transports measured)")
    return bad


def _same_host(rec: dict, host: dict, label: str) -> list:
    bad = []
    if (rec.get("stack") or {}) != host.get("stack"):
        bad.append(f"{label}: stack {rec.get('stack')} != the host record's {host.get('stack')}")
    if rec.get("device") != host.get("device"):
        bad.append(f"{label}: device {rec.get('device')!r} != the host record's "
                   f"{host.get('device')!r}")
    if rec.get("host_sha256") != host.get("sha256"):
        bad.append(f"{label}: host_sha256 is not the host record's")
    return bad


def checkpoint_record_failures_5(rec: dict, *, size, step, entry) -> list:
    bad = []
    label = f"{size}/step{step}/_checkpoint"
    for k, v in (("size", size), ("step", int(step)), ("revision", entry["revision"]),
                 ("commit", entry["commit"]), ("kind", entry["kind"])):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    for name, want in entry["lfs_sha256"].items():
        if (rec.get("sha256") or {}).get(name) != want:
            bad.append(f"{label}: downloaded {name} sha ≠ the manifest's")
    li = rec.get("loading_info") or {}
    if li != {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}:
        bad.append(f"{label}: loading info not empty: {li}")
    d = rec.get("digest")
    if not (isinstance(d, str) and len(d) == 64):
        bad.append(f"{label}: tensor digest missing")
    if not (isinstance(rec.get("n_params"), int) and rec["n_params"] > 0):
        bad.append(f"{label}: n_params missing")
    if rec.get("dtype") != DTYPE_5:
        bad.append(f"{label}: dtype {rec.get('dtype')!r} != {DTYPE_5!r}")
    return bad


def loss_record_failures_5(rec: dict, *, size, step, host, slice_sha,
                           n_scored=SLICE_N_SCORED_5) -> list:
    """`n_scored` is the committed slice's own count (2^21 on the real
    slice — the analyzer asserts that at the `"5 slice"` site; the test
    slices are smaller)."""
    bad = []
    label = f"{size}/step{step}/_loss"
    if rec.get("n_scored") != n_scored:
        bad.append(f"{label}: n_scored {rec.get('n_scored')} != {n_scored}")
    if rec.get("slice_sha256") != slice_sha:
        bad.append(f"{label}: slice_sha256 is not the pinned slice")
    if rec.get("batch_size") != LOSS_BATCH_5 or rec.get("pad_id") != PAD_ID_5:
        bad.append(f"{label}: batch/pad pins {rec.get('batch_size')}/{rec.get('pad_id')} "
                   f"!= {LOSS_BATCH_5}/{PAD_ID_5}")
    if rec.get("logits_dtype") != "float16" or rec.get("log_softmax_dtype") != "float32":
        bad.append(f"{label}: dtype facts are not fp16 logits / fp32 log-softmax")
    if rec.get("finite") is not True:
        bad.append(f"{label}: loss not finite ({rec.get('n_nonfinite')} non-finite tokens)")
    per_set = rec.get("per_set") or {}
    n = sum(int(v.get("n_tokens", 0)) for v in per_set.values())
    s = sum(float(v.get("loss", 0.0)) * int(v.get("n_tokens", 0)) for v in per_set.values())
    if n != n_scored:
        bad.append(f"{label}: per-set token counts sum to {n}, not {n_scored}")
    elif not isinstance(rec.get("loss"), float) or abs(s / n - rec["loss"]) > 1e-9:
        bad.append(f"{label}: loss {rec.get('loss')} is not the token-weighted mean of the "
                   f"per-set losses ({s / n if n else None})")
    if not isinstance(rec.get("per_doc_loss"), list) or not rec["per_doc_loss"]:
        bad.append(f"{label}: per_doc_loss missing")
    bad += _same_host(rec, host, label)
    return bad


def rung_record_failures_5(rec: dict, *, size, step, rung, cap, entry, verify_fn, host) -> list:
    bad = []
    label = f"{size}/step{step}/{rung}"
    for k, v in (("rung", rung), ("size", size), ("step", int(step)), ("n", N_ITEMS),
                 ("commit", entry["commit"]), ("dtype", DTYPE_5), ("n_shots", bt.N_SHOTS),
                 ("batch_size", BATCH_ARGMAX_5), ("prereg_tag", PREREG_TAG_5),
                 ("answer_type", cap["answer_type"])):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("items_sha256") != cap["items_sha256"]:
        bad.append(f"{label}: items_sha256 is not the pinned item file")
    if rec.get("max_new_tokens") != bt.max_new_tokens(rung):
        bad.append(f"{label}: max_new_tokens {rec.get('max_new_tokens')} != 2c's budget")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or not isinstance(conts, list) or \
            len(bits) != N_ITEMS or len(conts) != N_ITEMS:
        bad.append(f"{label}: bits/continuations are not {N_ITEMS} long")
        return bad + _same_host(rec, host, label)
    if rec.get("correct") != sum(bits):
        bad.append(f"{label}: correct {rec.get('correct')} ≠ sum(bits) {sum(bits)}")
    re_bits = [int(bool(verify_fn(c, it["answer"], cap["answer_type"])))
               for c, it in zip(conts, cap["eval_items"])]
    if re_bits != [int(b) for b in bits]:
        n = sum(1 for a, b in zip(re_bits, bits) if a != int(b))
        bad.append(f"{label}: re-verification disagrees with the stored bits on {n} item(s)")
    return bad + _same_host(rec, host, label)


def unit_record_failures_5(rec: dict, unit_dir) -> list:
    bad = []
    files = rec.get("files") or {}
    if set(files) != set(unit_files_5()):
        bad.append(f"{unit_dir}/_unit.json: file list is not the 36 unit files")
        return bad
    for name, sha in files.items():
        p = Path(unit_dir) / name
        if not p.is_file():
            bad.append(f"{unit_dir}/{name}: missing")
        elif bg.sha256_file(p) != sha:
            bad.append(f"{unit_dir}/{name}: sha ≠ the unit record's")
    return bad


# --------------------------------------------------------------- binding

def require_prereg_5(*, tag_exists=None, blob_sha=None, blobs=INSTRUMENT_BLOBS_5) -> dict:
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_5):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_5} does not exist")
    bound = {}
    for rel in blobs:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_5, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_5} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_5, "instrument_blobs": bound}


def targets_seal_paths_5(root) -> list:
    paths = []
    for size in SIZES_5:
        d = unit_dir_5(root, size, FINAL_STEP_5)
        paths += [d / name for name in unit_files_5()] + [d / "_unit.json"]
    paths += [gate1a_path_5(root), gate1b_path_5(root), host_record_path_5(root),
              power_path_5(root)]
    return paths


def require_targets_seal_5(root, *, tag_exists=None, blobs_bound=None) -> dict:
    """Never raises (2i's `require_seal_2i`)."""
    return an2i.require_seal_2i(TARGETS_SEAL_TAG_5, targets_seal_paths_5(root),
                                tag_exists=tag_exists, blobs_bound=blobs_bound, repo_root=REPO)


# ---------------------------------------------------------- frozen pins

FROZEN_SHA256_5 = {
    REPO / "experiments/exp1/signatures/stats.py":
        "ceab3eb7f6daf9346b9231f0e4af7e458b43ba4e7361556aef926e1abde2611f",
    REPO / "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    REPO / "experiments/exp2b/probe_starved.py":
        "e6c81df28e4a7e07db3a123e4b06d3c8a98a7d330cd726596d41b1136c4cd27b",
    REPO / "experiments/exp2b/splits.py":
        "49df4c62c3c3bd611b9cf49be46001c12220045a3611a39be5e2bc5b89ded6e0",
    REPO / "experiments/exp2c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/battery/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/battery/base.py":
        "6d77c3c91c5ca0eb84e1a011ef64af0e04ade6fe8d1ad42d526be3a37fbacbb2",
    REPO / "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    REPO / "experiments/exp2c/battery/generators_controls.py":
        "baab6da475f90f8c07acb6d1eb317484bf36afeb40705684f43ecd5ec9fdade6",
    REPO / "experiments/exp2c/battery/generators_rescues.py":
        "d70215c89ffd58d3f18f9dcd99940c7e92655ba8185919f50b2090b7e900c257",
    REPO / "experiments/exp2c/battery/generators_rungs.py":
        "778bf30da104f71773c26aa909ef2fddcd81291676a2db5d30130581b8d162d0",
    REPO / "experiments/exp2c/battery/wordlists_2c.py":
        "f46c6092d6429a59b95531d1a58b1bbfc0576d692d1162b8dfd2b6daf051790f",
    REPO / "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    REPO / "experiments/exp2c/instrument.py":
        "c486213bfa4753a83593b5383e2c0c90a6379b156f59a236ceeac7d68961e052",
    REPO / "experiments/exp2c/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2c/run/power_table.py":
        "89816cf0e7e2418e748104dbc32fd50e12ded78988f2c2c04b05ff1a89c58da1",
    REPO / "experiments/exp2c/run/screen.py":
        "fef1814142955912066837fbd2119f5c2ae27fe31393ede890584313e2b06873",
    REPO / "experiments/exp2c/stats_bounds.py":
        "39057433f1d67cbbf803141dc25ee36cda9e96270b0634006c0fcab245ee49f8",
    REPO / "experiments/exp2d/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    REPO / "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    REPO / "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    REPO / "experiments/exp2f/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2f/analyze_2f.py":
        "79018ff34b6f41bd2a5e8fa0f922a2de567861750057a5eca1a3dad6cf3f61d3",
    REPO / "experiments/exp2f/collect_eval_2f.py":
        "189e3738471185b7205f106fdac9bc5da1d564caafc60e39f4d6e3546915d071",
    REPO / "experiments/exp2f/labels_2f.py":
        "8dc31850e5c47b7a1cc171b0388521ebe01005ddc123954c0073734cf9aaac25",
    REPO / "experiments/exp2f/make_referents_2f.py":
        "c08eec5cea9f49a05c6754c84b81e1cb8560537881b002faee02bcf085af1c10",
    REPO / "experiments/exp2f/probe_2f.py":
        "63c714d6e899dd9d6d5610a3d54c9254ec0749d03f44a703790d4a4354854f62",
    REPO / "experiments/exp2g/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    REPO / "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    REPO / "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    REPO / "experiments/exp2g/collect_eval_2g.py":
        "392ab84e2bac360bf041858a4b991824a3bda9ca414e34d0f84e44b22610efaf",
    REPO / "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    REPO / "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    REPO / "experiments/exp2g/probe_2g.py":
        "63abc9e6518ac1ab53e4a70e0c716bccd357a11ea3fc2733de52e2ec4e23d451",
    REPO / "experiments/exp2g/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2g/run/sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    REPO / "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    REPO / "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    REPO / "experiments/exp2h/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    REPO / "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    REPO / "experiments/exp2i/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    REPO / "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    REPO / "experiments/exp3/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp3/analyze_3.py":
        "aa0cb2374fbdffde2f9eaae26cee1ce51f9f42c0b32fd89f4f8754c983a92274",
    REPO / "experiments/exp3/sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    REPO / "experiments/exp3c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp3c/analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
}


def check_frozen_5() -> None:
    if FROZEN_SHA256_5 is None:
        raise RuntimeError("FROZEN_SHA256_5 is None — not pinned (build incomplete)")
    bad = [f"{p}" for p, want in FROZEN_SHA256_5.items()
           if not Path(p).is_file() or bg.sha256_file(p) != want]
    if bad:
        raise RuntimeError("5: a frozen module drifted from its pin: " + "; ".join(bad))


# --------------------------------------------------- import-surface pin

IMPORTED_SHA256_5 = {
    REPO / "experiments/exp5/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp5/make_referents_5.py":
        "759948baff86f1947eaa0a6e3ccc4adf5a85c5b836ccbdb34480bc011b0d6576",
    REPO / "experiments/exp5/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp5/run/preflight_5.py":
        "975b3d50f62c2056e1de316c440a6d14ee4df481490f2722b64c6b2287bd4a9a",
    REPO / "experiments/exp5/run/s9_mac_5.py":
        "fca6804d97193860358411a9350d145953b7ce8abce252c811695bd284246dc6",
    REPO / "experiments/exp5/verify_referents_5.py":
        "80696db1e843b7bfa37f362a7789e430452d000a4a5e436fb370c75512bd3ae9",
}


def check_imports_5() -> None:
    """4c's `check_imports_4c` body, adapted (2j F-1 / lesson 11: the
    import surface is a verdict input). Every module under
    `experiments/` this process has imported (tests excluded) must be
    covered by `FROZEN_SHA256_5`, by `INSTRUMENT_BLOBS_5`, or pinned
    byte-identically by `IMPORTED_SHA256_5`. Called at ENTRY and EXIT
    by both runners and the analyzer."""
    if IMPORTED_SHA256_5 is None:
        raise RuntimeError("IMPORTED_SHA256_5 is None — the import surface is not pinned "
                           "(build incomplete)")
    covered = {str(Path(p).resolve()) for p in (FROZEN_SHA256_5 or {})}
    covered |= {str((REPO / rel).resolve()) for rel in INSTRUMENT_BLOBS_5}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_5.items()}
    drifted, unpinned = [], []
    for p, want in sorted(pinned.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    exp_root = str((REPO / "experiments").resolve())
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


# ------------------------------------------------------------------ git

def git_sha_5() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()


def projection_commit_5():
    """The adding commit for `experiments/exp5/projection.md` — the
    LAST line of `git log --diff-filter=A`, i.e. the earliest commit
    that added the file (a rewrite of history could add it again, so
    the design's own words are literal: 'the last line')."""
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--",
                          "experiments/exp5/projection.md"], cwd=REPO,
                         capture_output=True, text=True)
    lines = [ln for ln in out.stdout.strip().splitlines() if ln]
    return lines[-1] if lines else None


def is_ancestor_5(a: str, b: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b],
                          cwd=REPO).returncode == 0


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh_inventory_5()
    inv = load_inventory_5()
    obj = build_all_5(inv)
    write_manifest_5(CHECKPOINTS_PATH_5, obj)
    for size, m in obj.items():
        print(size, len(m["available"]), "available; excluded", sorted(m["excluded"], key=int),
              "; spine", spine_5(obj, size), "; hub step143000 == main:",
              m["hub_step143000"]["signature_equals_main"])
    print("sha256", bg.sha256_file(CHECKPOINTS_PATH_5))
