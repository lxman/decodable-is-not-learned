# experiments/exp2h/battery_2h.py
"""The Exp 2h battery: the sampler confirmation on 6.9b, a thin delta
on frozen `experiments/exp2g` (design `experiment-2h-design.md`
§3-§5). Everything not defined here is exp2g's, imported frozen and
re-asserted by sha256 (`FROZEN_2G_SHA256`, `check_frozen_2h`).

Three deltas from exp2g, all local to this module:

1. The primary predictor generalizes `analyze_2g.sampler_counts_1b`'s
   body to a `size` argument (`sampler_counts`) — exp2g's function
   stays 1b-only and untouched.
2. The outcome is 6.9b's checkpoint grid. 6.9b is never a member of
   `battery_2g.SWEEP_SIZES` (bound to `REPO_OF`/`GRID`/`EXCLUDED_GRID`,
   none of which carry a 6.9b entry), so the manifest and loader
   family are built here from `checkpoints_2g.candidate`/`.signature`
   directly rather than through `checkpoints_2g.build_manifest`, which
   is bound to those exp2g-only dicts.
3. R_69 (design §4) is re-derived from 2c's committed m4 6.9b counts
   under 2d's floor, the same rule `battery_2g.check_rung_sets` uses
   for R_28/R_12b (`battery_2g.rising_by_bar`, reused directly).

Zero model contact, zero network: the loader family
(`download_entry_69`/`clean_dir_69`/`load_checkpoint_69`/`free_69`)
imports `huggingface_hub`/`torch`/`transformers` lazily inside each
function body, never at module import, and nothing here calls them."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

EXP2H = Path(__file__).resolve().parent
EXPERIMENTS = EXP2H.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402

EXP2C = bg.EXP2C
EXP2D = bg.EXP2D
EXP2G = EXPERIMENTS / "exp2g"
RESULTS = EXP2H / "results"
CHECKPOINTS_PATH_69 = EXP2H / "checkpoints_2h.json"
HUB_INVENTORY_PATH_69 = EXP2H / "hub_inventory_69.json"
PREREG_TAG_2H = "exp2h-preregistered"

N_ITEMS = bt.N_ITEMS
SIZE = "6.9b"
REPO_69 = "EleutherAI/pythia-6.9b"
FINAL_STEP_69 = 143000

# §3.2/§8b: 2g's 22-trained-point shape including 64000 — 6.9b's Hub
# branch layout is clean (the 2026-08-24 scan: every step branch two
# unique bin shards, zero stale-main copies), so nothing is excluded.
GRID_69 = (0, 1000, 2000, 4000, 8000, 10000, 16000, 20000, 30000, 32000,
           40000, 50000, 60000, 64000, 70000, 80000, 90000, 100000, 110000,
           120000, 130000, 140000, 143000)
EXCLUDED_GRID_69: dict = {}


def trained_steps_69() -> tuple:
    return tuple(s for s in GRID_69 if s != 0)


def n_trained_69() -> int:
    return len(trained_steps_69())


def revision_of_69(step: int) -> str:
    """The final grid point is 2c's pinned `main` commit, never the
    Hub's step143000 branch (checkpoints_2g's finding C, same rule)."""
    return "main" if step == FINAL_STEP_69 else f"step{int(step)}"


# ---------------------------------------------- 2c's committed m4 counts

# §4: 2c's committed correct counts for ALL 34 rungs at 6.9b/main
# (`experiments/exp2c/results/m4/6.9b_trained/*.json`), in `bt.RUNGS`'
# family-contiguous order — the convention `battery_2g.FINAL_COUNT_PIN`
# uses for its "2.8b" row. Generated once by reading the committed
# files (`load_m4_counts_69` re-asserts every value against this pin).
FINAL_COUNT_PIN_69 = {
    "add4_mid": 0, "sub4_mid": 6, "add3_mid": 19, "sub3_mid": 14,
    "antonym6": 143, "antonym": 286, "arith_next": 58, "quad_next": 5,
    "base12_digitsum": 0, "base13": 0, "base7": 0, "oct2dec": 1,
    "caesar_len8": 0, "caesar": 0, "clock24_d999": 29, "clock24": 25,
    "collatz_step2": 82, "count_div13": 102, "count_div7": 23, "hamming12": 103,
    "isqrt_gap": 78, "median5": 79, "median7": 72, "mod13_comp": 30,
    "mod17": 33, "mod19": 31, "mod13": 38, "odd6": 107,
    "odd_one_out": 125, "rev_string7": 0, "reverse_string": 1, "roman_sum7": 72,
    "sub_base8": 52, "add_base8": 29,
}

# §4: the rungs whose committed final count clears 2d's floor by the
# one-sided exact binomial bar (`check_rung_set_69`, reusing
# `battery_2g.rising_by_bar`) — eight rungs, all inside
# `battery_2g.PREDICTOR_RUNGS`; two (count_div13, odd6) never used by
# 2g's 2.8b primary (R_28). add3_mid's final count (19) sits under the
# 20-item eligibility floor (`battery_2g.ELIGIBILITY_MIN_POS`) —
# disclosed, not enforced here (that gate belongs to the primary, on
# the realized sweep's n_pos, not on the m4 final count).
R_69 = ("antonym", "antonym6", "add_base8", "sub_base8", "add3_mid",
        "arith_next", "count_div13", "odd6")


def m4_path_69(rung: str) -> Path:
    return bg.m4_path(SIZE, rung)


def load_m4_counts_69(rungs=None) -> dict:
    """2c's committed correct counts at 6.9b, each re-asserted against
    `FINAL_COUNT_PIN_69` (mirrors `battery_2g.load_m4_counts`'s body
    for the one size not in `battery_2g.FINAL_COUNT_PIN`)."""
    rungs = tuple(rungs) if rungs is not None else tuple(FINAL_COUNT_PIN_69)
    out = {}
    for r in rungs:
        rec = json.loads(m4_path_69(r).read_text())
        if rec.get("capability") != r or rec.get("n") != N_ITEMS or \
                rec.get("mode") != "trained" or rec.get("size") != SIZE:
            raise ValueError(f"m4 record 6.9b/{r}: not the committed shape")
        if rec["correct"] != FINAL_COUNT_PIN_69[r]:
            raise ValueError(f"m4 6.9b/{r}: correct {rec['correct']} against "
                             f"the pin {FINAL_COUNT_PIN_69[r]}")
        out[r] = int(rec["correct"])
    return out


def check_rung_set_69(floors: dict) -> tuple:
    """§4: R_69 reproduces from the committed m4 counts + 2d's floor
    under `stats_2d.binomial_bar`, via `battery_2g.rising_by_bar`
    (the identical rule `battery_2g.check_rung_sets` applies to
    R_28/R_12b — reused, not re-implemented)."""
    got = bg.rising_by_bar(load_m4_counts_69(), floors)
    if set(got) != set(R_69):
        raise ValueError(f"R_69 from m4 + bar is {sorted(got)}, pinned "
                         f"{sorted(R_69)}")
    return tuple(R_69)


# ----------------------------------------- the sampled-count predictor

def sampler_counts(size: str, rungs) -> dict:
    """Per-item verified counts from 2d's committed main-tier draws at
    `size` ("1b" or "410m"), re-verified through 3c's total wrapper —
    `analyze_2g.sampler_counts_1b`'s body with `size` threaded (a NEW
    function here; exp2g's stays 1b-only, untouched). Loads the
    battery and the verify criterion itself so a caller need only name
    the size and rungs, as `battery_2h.sampler_counts` is specified."""
    from experiments.exp2d import analyze_2d as a2d
    if size not in bt.PROBE_SIZES:
        raise ValueError(f"sampler_counts: {size!r} is not a 2d probe size "
                         f"{bt.PROBE_SIZES}")
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    spec = a2d.TIERS["main"]
    out = {}
    for rung in rungs:
        cap = battery[rung]
        rows = a2d.read_rows(a2d.tier_draws_path(a2d.EXP2D, "main", size, rung),
                             seed=spec["seed"], dps=spec["draws_per_seed"])
        counts = [0] * N_ITEMS
        for row in rows:
            ans = cap["eval_items"][row["item"]]["answer"]
            counts[row["item"]] = sum(1 for d in row["draws"][str(spec["seed"])]
                                      if verify_fn(d, ans, cap["answer_type"]))
        out[rung] = counts
    return out


# ------------------------------------------------------------- manifest

def _pythia_sha_69() -> str:
    from models import PYTHIA_SHAS   # exp2b's, via battery_2d's sys.path
    return PYTHIA_SHAS[SIZE]


def load_inventory_69(path=HUB_INVENTORY_PATH_69) -> dict:
    inv = json.loads(Path(path).read_text())
    if REPO_69 not in inv or "main" not in inv[REPO_69]:
        raise ValueError(f"inventory lacks {REPO_69}/main")
    return inv


def build_manifest_69(inv: dict) -> dict:
    """Mirrors `checkpoints_2g.build_manifest`'s body for the single
    6.9b size (injected repo/grid, no exclusions), using
    `checkpoints_2g.candidate`/`.signature` directly — `build_manifest`
    itself is bound to `battery_2g.REPO_OF`/`.GRID`/`.EXCLUDED_GRID`,
    none of which carry a 6.9b entry."""
    table = inv[REPO_69]
    main_files = table["main"]["files"]
    cands = {rev: ck.candidate(rev, t["files"], main_files) for rev, t in table.items()}
    sigs = {rev: (ck.signature(table[rev]["files"], c) if c else None)
            for rev, c in cands.items()}

    def dups_of(rev):
        return sorted((r for r, s in sigs.items()
                       if r != rev and s is not None and s == sigs[rev]),
                      key=lambda r: (r == "main", int(r[4:]) if r.startswith("step") else 0))

    entries = {}
    for step in GRID_69:
        rev = revision_of_69(step)
        if rev not in table:
            raise ValueError(f"{REPO_69}: revision {rev} is not in the inventory")
        c = cands[rev]
        if c is None:
            raise ValueError(f"{REPO_69}/{rev}: no candidate weight file")
        same = dups_of(rev)
        if step != FINAL_STEP_69 and same:
            raise ValueError(f"{REPO_69}/{rev}: candidate files duplicate "
                             f"{same} — not a trustworthy grid point")
        entries[str(step)] = {
            "revision": rev, "commit": table[rev]["commit"], "kind": c["kind"],
            "files": list(c["files"]),
            "lfs_sha256": {n: table[rev]["files"][n][0] for n in c["lfs"]},
            "lfs_size": {n: int(table[rev]["files"][n][1]) for n in c["lfs"]},
        }
    main_entry = entries.get(str(FINAL_STEP_69))
    if main_entry is None or main_entry["commit"] != _pythia_sha_69():
        raise ValueError(f"{REPO_69}: the final grid point is not 2c's "
                         f"pinned main commit {_pythia_sha_69()}")

    # step143000's own branch, for the descriptive record — kept
    # separate from `final_duplicates` exactly as `checkpoints_2g`
    # keeps it (see 2g's own committed 2.8b/12b manifests: both carry
    # `final_duplicates: []` alongside a non-trivial `hub_step143000`).
    # `candidate()` is kind-specific: main publishes safetensors shards
    # so its candidate kind is "safetensors-shards"; step143000
    # publishes none, so its candidate kind is "bin-shards" — different
    # kinds can never produce equal `signature()` tuples, so
    # `dups_of("main")` structurally cannot list step143000 (nor can
    # any stale-copy step ever equal main's signature: the candidate
    # rule steers a single safetensors file matching main's sha to the
    # bin branch instead, unless the revision IS main). The
    # byte-identity is instead carried in `signature_equals_main`
    # below, via a direct comparison of the two sides' own bin-shard
    # shas — the same field 2g's 12b manifest uses for its analogous
    # `hub_step143000` fact.
    hub = table.get(f"step{FINAL_STEP_69}")
    hub_c = cands.get(f"step{FINAL_STEP_69}")
    main_bins = tuple(v[0] for n, v in sorted(main_files.items())
                      if n.startswith("pytorch_model") and n.endswith(".bin"))
    hub_bins = tuple(v[0] for n, v in sorted(hub["files"].items())
                     if n.startswith("pytorch_model") and n.endswith(".bin")) if hub else ()
    hub_rec = {
        "commit": hub["commit"] if hub else None,
        "kind": hub_c["kind"] if hub_c else None,
        "lfs_sha256": ({n: hub["files"][n][0] for n in hub_c["lfs"]} if hub_c else {}),
        "signature_equals_main": bool(hub_c and sigs[f"step{FINAL_STEP_69}"] == sigs["main"]
                                      or (hub_bins and hub_bins == main_bins)),
        "duplicates": dups_of(f"step{FINAL_STEP_69}") if hub else [],
    }

    def _stale_count(name: str) -> int:
        main_sha = main_files.get(name, [None])[0]
        if main_sha is None:
            return 0
        return sum(1 for r, t in table.items() if r != "main"
                  and t["files"].get(name, [None])[0] is not None
                  and t["files"][name][0] == main_sha)

    stale = {"model.safetensors": _stale_count("model.safetensors"),
             "pytorch_model.bin": _stale_count("pytorch_model.bin")}
    return {"size": SIZE, "repo": REPO_69, "main_commit": table["main"]["commit"],
            "grid": list(GRID_69), "trained_steps": list(trained_steps_69()),
            "entries": entries, "excluded": {}, "exclusion_evidence": {},
            "final_duplicates": dups_of("main"), "hub_step143000": hub_rec,
            "stale_main_copies": stale, "n_revisions": len(table)}


def write_manifest_69(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest_69(path=CHECKPOINTS_PATH_69, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    if obj.get("grid") != list(GRID_69) or obj.get("excluded", {}) != {}:
        raise ValueError(f"{path}: manifest is not the frozen 6.9b grid")
    if obj.get("main_commit") != _pythia_sha_69():
        raise ValueError(f"{path}: main commit is not 2c's pin")
    return obj


def entry_69(manifest: dict, step: int) -> dict:
    e = manifest.get("entries", {}).get(str(int(step)))
    if e is None:
        raise ValueError(f"6.9b step {step} is not a grid entry")
    return e


# ---------------------------------------------------- loader (stage 2)

CKPT_CACHE_69 = Path.home() / "emergence-lab" / "ckpt_cache_2h"


def _rev_dir_69(step, cache_root) -> Path:
    return Path(cache_root) / SIZE / f"step{int(step)}"


def _step_of_69(entry: dict) -> int:
    rev = entry["revision"]
    return FINAL_STEP_69 if rev == "main" else int(rev[4:])


def download_entry_69(entry: dict, cache_root=CKPT_CACHE_69) -> dict:
    from huggingface_hub import hf_hub_download
    rev_dir = _rev_dir_69(_step_of_69(entry), cache_root)
    paths = {}
    for name in entry["files"]:
        p = hf_hub_download(REPO_69, name, revision=entry["commit"],
                            cache_dir=str(rev_dir))
        paths[name] = Path(p).resolve()
    return paths


def verify_downloads_69(entry: dict, paths: dict) -> dict:
    shas = {}
    for name, p in paths.items():
        got = bg.sha256_file(p)
        want = entry["lfs_sha256"].get(name)
        if want is not None and got != want:
            raise ValueError(f"{name}: downloaded sha256 {got} against the "
                             f"manifest's {want} — not the pinned weights")
        shas[name] = got
    return shas


def pinned_config_69():
    from transformers import AutoConfig
    return AutoConfig.from_pretrained(REPO_69, revision=_pythia_sha_69())


def clean_dir_69(step: int, cache_root, paths: dict) -> Path:
    d = _rev_dir_69(step, cache_root) / "clean"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for name, src in paths.items():
        dst = d / name
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    pinned_config_69().to_json_file(str(d / "config.json"))
    return d


def load_checkpoint_69(step: int, entry: dict, *, cache_root=CKPT_CACHE_69,
                       device: str = "mps"):
    """MODEL CONTACT. The candidate files only, hashed, into 2c's
    pinned config; loading info must be empty; fp16 on `device`. Thin
    copy of `checkpoints_2g.load_checkpoint`, parameterized by
    REPO_69/_pythia_sha_69() since `checkpoints_2g`'s is bound to
    `battery_2g.REPO_OF`, which lacks 6.9b. Tensor digest is reused
    from `checkpoints_2g.tensor_digest` by import, not redefined."""
    import torch
    from transformers import AutoModelForCausalLM
    paths = download_entry_69(entry, cache_root)
    shas = verify_downloads_69(entry, paths)
    d = clean_dir_69(step, cache_root, paths)
    model, li = AutoModelForCausalLM.from_pretrained(
        str(d), config=pinned_config_69(), dtype=torch.float16,
        output_loading_info=True)
    bad = {k: list(li.get(k, [])) for k in ("missing_keys", "unexpected_keys",
                                             "mismatched_keys") if li.get(k)}
    if bad:
        raise ValueError(f"6.9b step {step}: the candidate files do not fill "
                         f"2c's architecture exactly: {bad}")
    model = model.to(device).eval()
    info = {"size": SIZE, "step": int(step), "revision": entry["revision"],
            "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry["files"]), "sha256": shas,
            "config_source": f"{REPO_69}@{_pythia_sha_69()}",
            "tokenizer_source": f"{REPO_69}@{_pythia_sha_69()}",
            "loading_info": {k: len(li.get(k, [])) for k in
                             ("missing_keys", "unexpected_keys", "mismatched_keys")}}
    return model, info


def free_69(step: int, cache_root=CKPT_CACHE_69) -> None:
    d = _rev_dir_69(step, cache_root)
    if d.exists():
        shutil.rmtree(d)


# ----------------------------------------------------------------- paths

def sweep_dir_2h(root) -> Path:
    return Path(root) / "results" / "sweep" / SIZE


def record_path_2h(root, step, rung) -> Path:
    return sweep_dir_2h(root) / f"step{int(step)}" / f"{rung}.json"


def checkpoint_record_path_2h(root, step) -> Path:
    return sweep_dir_2h(root) / f"step{int(step)}" / "_checkpoint.json"


def gate1_path_2h(root) -> Path:
    return sweep_dir_2h(root) / "gate1.json"


def halt_marker_path_2h(root) -> Path:
    return sweep_dir_2h(root) / "HALTED"


# ------------------------------------------------------- frozen imports

# exp2g is closed; its predictor is 2h's sealed competitor (design §3.1).
# Pins: the 7 exp2g modules this instrument imports or whose logic it
# mirrors, plus the three exp2g DATA files 2h's analyzer will load —
# the sealed predictor table, its own committed checkpoint manifest,
# and its own committed referent manifest.
FROZEN_2G_SHA256 = {
    EXP2G / "battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    EXP2G / "labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    EXP2G / "strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    EXP2G / "stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    EXP2G / "probe_2g.py":
        "63abc9e6518ac1ab53e4a70e0c716bccd357a11ea3fc2733de52e2ec4e23d451",
    EXP2G / "checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    EXP2G / "analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    EXP2G / "results" / "predictor" / "predictor.json":
        "9eadbac316ddc5db7f7af716e406d3434033ccbaceb64a39467febdba757adc7",
    EXP2G / "checkpoints_2g.json":
        "a5032f74f509669ea97600ad68cfe422e0fb6407a768b478f944868f42d3a2bc",
    EXP2G / "referents_2g.json":
        "def2e0e2b33f99016e5293a1bf87ea3487c7232aa7bf36fe5cf3f33be782fcb0",
}

PREDICTOR_2G_SHA = "9eadbac316ddc5db7f7af716e406d3434033ccbaceb64a39467febdba757adc7"


def check_frozen_2h() -> None:
    for path, want in FROZEN_2G_SHA256.items():
        got = bg.sha256_file(path)
        if got != want:
            raise ValueError(f"frozen file {path} has sha256 {got}, expected "
                             f"{want} — exp2g is closed and its predictor is "
                             f"2h's sealed competitor")


if __name__ == "__main__":
    check_frozen_2h()
    inv = load_inventory_69()
    manifest = build_manifest_69(inv)
    write_manifest_69(CHECKPOINTS_PATH_69, manifest)
    print(SIZE, len(manifest["entries"]), "entries; final_duplicates",
          manifest["final_duplicates"], "; hub step143000 == main:",
          manifest["hub_step143000"]["signature_equals_main"])
    floors = bg.load_floors()
    print("R_69 check:", check_rung_set_69(floors))
    print("sha256", bg.sha256_file(CHECKPOINTS_PATH_69))
