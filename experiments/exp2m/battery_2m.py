# experiments/exp2m/battery_2m.py
"""Experiment 2m — constants, the two-repo SmolLM3 inventory + manifest,
the SmolLM3 loader family (its own tokenizer pins, the seeded twin),
paths, the rung-set rule, record stamps, the gate-1 checkers, the pins
and the prereg binding (design `experiment-2m-design.md` §3–§4).
Everything not defined here is imported frozen and sha-pinned
(`FROZEN_SHA256_2M`, `check_frozen_2m`): 2l's instrument (four
tag-bound blobs, now frozen bytes), 2k's tier readers, 2i's record
shapes and seal machinery, 2g's strata and statistics, 2d's bar, 2c's
harness.

Deltas from `battery_2l`, all local to this module:

1. TWO repos: `HuggingFaceTB/SmolLM3-3B-checkpoints` carries the 86
   stage-1 revisions (`stage1-step-<N>`), the stage-2/3 revisions and a
   WEIGHTLESS `main`; `HuggingFaceTB/SmolLM3-3B-Base` carries the
   released base on its one branch. Every manifest entry carries its
   `repo`; the candidate-file loader keys the cache by revision under
   `SIZE_OUT` and reads the repo from the entry.
2. No step 0 exists: a seeded `from_config` TWIN of the stage-1 config
   at the endpoint's commit stands in (2i's construction), loaded in
   the sweep after gate 1, never in an outcome.
3. The tokenizer declares no pad token and adds no BOS on a plain
   render: `load_tokenizer_3b` sets `pad_token = PAD_TOKEN_2M` and
   `check_tokenizer_2m` pins left padding, the pad id, the eos id and
   the absence of a prepended special id. `battery_2i.load_thin` is
   NOT reused (it applies OLMo-2's pad check); `load_thin_3b` carries
   its body with this module's tokenizer loader.
4. `DTYPE_2M` and `BATCH_SIZE_2M` are single pre-tag constants; every
   record's `dtype` is OVERRIDDEN to `DTYPE_2M` (2i's `item_record_2i`
   hard-codes "float16") and the analyzer requires it.
5. The predictors are 2k's and 2i's sealed artifacts: nothing is
   sampled. `PREDICTOR_SHA_2M` is a composite of the two seal shas with
   a "2m|" prefix — distinct from 2l's composite of the same seals.
6. Three endpoint whichs (stage1_final, stage3_final, base): the
   endpoint seal binds 3 × 34 records + the rung set + the power record.

The loader functions import `huggingface_hub`/`torch`/`transformers`
lazily inside their bodies; nothing here calls them; no test does."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

EXP2M = Path(__file__).resolve().parent
EXPERIMENTS = EXP2M.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import strata_2g  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402

RESULTS = EXP2M / "results"
HUB_INVENTORY_PATH = EXP2M / "hub_inventory_smollm3.json"
CHECKPOINTS_PATH = EXP2M / "checkpoints_2m.json"
CHECKPOINTS_2M_SHA256 = "1a6dd3361b3e75a7ccc61e8f86c50ef59350bc3429fc4cb3bdcdb2be5ca599bd"

FAMILY = "smollm3"
SIZE_OUT = "smollm3_3b"
REPO_CKPT = "HuggingFaceTB/SmolLM3-3B-checkpoints"
REPO_BASE = "HuggingFaceTB/SmolLM3-3B-Base"
REV_ENDPOINT_2M = "stage1-step-3440000"
ENDPOINT_STEP_2M = 3440000
REV_STAGE3_FINAL_2M = "stage3-step-4720000"
STAGE3_STEP_2M = 4720000
REV_BASE_2M = "main"
REV_CKPT_MAIN = "main"                     # weightless on the checkpoints repo (README only)
TOKENS_PER_STEP_2M = 2_359_296             # the README's global batch, descriptive
TWIN = bi.TWIN                             # "twin"
TWIN_SEED = 0

# design §3.5 / dial c: the dense head (every 40k to 400k), every 200k to
# 3.4M, the endpoint — 26 trained points on the branch's 40k lattice.
GRID_3B = (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000, 400000,
           600000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000, 2200000,
           2400000, 2600000, 2800000, 3000000, 3200000, 3400000, 3440000)
# design §5 sensitivity: 2i's log-head shape as a strict subset (21 points).
LOG_HEAD_SUBSET_2M = (40000, 80000, 160000, 320000, 400000, 600000, 800000, 1000000, 1200000,
                      1400000, 1600000, 1800000, 2000000, 2200000, 2400000, 2600000, 2800000,
                      3000000, 3200000, 3400000, 3440000)
if not set(LOG_HEAD_SUBSET_2M) < set(GRID_3B):
    raise RuntimeError("LOG_HEAD_SUBSET_2M must be a strict subset of GRID_3B")

PREREG_TAG_2M = "exp2m-preregistered"
ENDPOINT_SEAL_TAG_2M = "exp2m-endpoint-sealed"
INSTRUMENT_BLOBS_2M = ("experiments/exp2m/analyze_2m.py",
                       "experiments/exp2m/battery_2m.py",
                       "experiments/exp2m/run/endpoint_2m.py",
                       "experiments/exp2m/run/sweep_2m.py")

N_ITEMS = bt.N_ITEMS
STRATA_RUNGS = tuple(strata_2g.COVARIATE_OF)       # 2g's eleven
R_CAP_2K = tuple(bk.R_CAP_DESIGN)                  # the nine with a 256-draw predictor
BATCH_SIZE_2M = 16                                 # dial m — a pre-tag constant, threaded explicitly
DTYPE_2M = "float16"                               # dial l — a pre-tag constant; the fp32 fallback is a re-tag

# The tokenizer's facts (design §2, Hub metadata 2026-09-03; dial n).
PAD_TOKEN_2M = "<|finetune_right_pad_id|>"
PAD_TOKEN_ID_2M = 128004
EOS_TOKEN_ID_2M = 128001
BOS_TOKEN_2M = "<|begin_of_text|>"                 # in the vocabulary; NEVER prepended by any stage
BOS_TOKEN_ID_2M = 128000

# The two predictor seals, as committed (2k close-out, 2i close-out) — the
# same two literals 2l carries; asserted equal to the seal files by test.
SEAL_2K_SHA256 = "3c4778b06de20c38090ea0f488e4f1664019076d7015b447b30e57f95ae2be9a"
SEAL_2I_SHA256 = "d80ada5058b422645514c199046f00e9d5ab86a8139fb6a725f487ed8560be24"
PREDICTOR_TAGS_2M = f"{bk.SEAL_TAG_2K}+{bi.PREDICTOR_SEAL_TAG}"


def predictor_sha_2m(seal_2k_sha: str, seal_2i_sha: str) -> str:
    """The composite `predictor_sha` every 2m record stamps: both
    predictors are already sealed, so 2m's own predictor identity is a
    function of the two seals — with a "2m|" prefix so it is distinct
    from 2l's composite of the same two seals."""
    return hashlib.sha256(f"2m|{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()


PREDICTOR_SHA_2M = predictor_sha_2m(SEAL_2K_SHA256, SEAL_2I_SHA256)

_STAGE1_RE_2M = re.compile(r"^stage1-step-(\d+)$")


def trained_steps_3b() -> tuple:
    return tuple(GRID_3B)


def n_trained_3b() -> int:
    return len(trained_steps_3b())


# ------------------------------------------------------------ inventory

def _retry(fn, *args, tries: int = 3, sleep: float = 5.0, **kwargs):
    last = None
    for i in range(tries):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 — deliberately broad, retried
            last = exc
            if i < tries - 1:
                time.sleep(sleep)
    raise last


def load_inventory_3b(path=HUB_INVENTORY_PATH) -> dict:
    inv = json.loads(Path(path).read_text())
    if REPO_CKPT not in inv or REV_CKPT_MAIN not in inv[REPO_CKPT]:
        raise ValueError(f"inventory lacks {REPO_CKPT}/{REV_CKPT_MAIN}")
    if REPO_BASE not in inv or REV_BASE_2M not in inv[REPO_BASE]:
        raise ValueError(f"inventory lacks {REPO_BASE}/{REV_BASE_2M}")
    return inv


def refresh_inventory_3b(out_path=HUB_INVENTORY_PATH) -> dict:
    """NETWORK (metadata only) — the ONE Hub scan of the whole build:
    every branch of `REPO_CKPT` (86 stage-1, the stage-2/3 and long-
    context branches, the post-training branches, the weightless
    `main`) and `main` of `REPO_BASE`; file lists with LFS sha256 + size
    and the branch commit. Refuses if `out_path` exists — this runs
    ONCE, ever."""
    p = Path(out_path)
    if p.exists():
        raise FileExistsError(f"{p} already exists — refresh_inventory_3b is the ONE scan "
                              f"of this build and refuses to overwrite a committed inventory")
    from huggingface_hub import HfApi
    api = HfApi()

    def _info(repo: str, rev: str) -> dict:
        info = _retry(api.model_info, repo, revision=rev, files_metadata=True)
        files = {s.rfilename: [s.lfs.sha256, s.size] for s in info.siblings if s.lfs}
        return {"commit": info.sha, "files": files}

    refs = _retry(api.list_repo_refs, REPO_CKPT)
    revs = sorted({b.name for b in refs.branches} | {REV_CKPT_MAIN})
    table_c = {rev: _info(REPO_CKPT, rev) for rev in revs}
    table_b = {REV_BASE_2M: _info(REPO_BASE, REV_BASE_2M)}
    out = {REPO_CKPT: table_c, REPO_BASE: table_b}
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    return out


# ------------------------------------------------------------- manifest

def _weight_entry(repo: str, rev: str, table: dict, cands: dict) -> dict:
    c = cands.get(rev)
    if c is None:
        raise ValueError(f"{repo}/{rev}: no candidate weight file")
    files = table[rev]["files"]
    return {"repo": repo, "revision": rev, "commit": table[rev]["commit"], "kind": c["kind"],
            "files": list(c["files"]),
            "lfs_sha256": {n: files[n][0] for n in c["lfs"]},
            "lfs_size": {n: int(files[n][1]) for n in c["lfs"]}}


def build_manifest_3b(inv: dict) -> dict:
    """`battery_2l.build_manifest_13b`'s body over two repos: 2g's
    `ck.candidate`/`ck.signature` directly (the shard regex accepts
    `model-0000N-of-00002.safetensors`; the checkpoints repo's `main`
    carries no weights, and `candidate` tolerates an empty main table),
    the duplicate-signature refusal across ALL scanned checkpoint
    revisions for every grid point AND the stage-3 endpoint; the stage-1
    endpoint alone may duplicate (a stage-2 copy), recorded under
    `endpoint_duplicates`. The twin entry carries the endpoint's commit
    as `config_commit`; the base entry comes from `REPO_BASE`."""
    table_c, table_b = inv[REPO_CKPT], inv[REPO_BASE]
    main_files_c = table_c[REV_CKPT_MAIN]["files"]
    cands_c = {rev: ck.candidate(rev, t["files"], main_files_c) for rev, t in table_c.items()}
    sigs_c = {rev: (ck.signature(table_c[rev]["files"], c) if c else None) for rev, c in cands_c.items()}

    def dups_of(rev: str) -> list:
        return sorted(r for r, s in sigs_c.items() if r != rev and s is not None and s == sigs_c[rev])

    entries = {}
    for step in trained_steps_3b():
        matches = [r for r in table_c if _STAGE1_RE_2M.fullmatch(r)
                   and int(_STAGE1_RE_2M.fullmatch(r).group(1)) == step]
        if len(matches) != 1:
            raise ValueError(f"{REPO_CKPT}: step {step} matches {matches} in the inventory — "
                             f"exactly one stage1 branch is expected")
        rev = matches[0]
        entry = _weight_entry(REPO_CKPT, rev, table_c, cands_c)
        same = dups_of(rev)
        if step != ENDPOINT_STEP_2M and same:
            raise ValueError(f"{REPO_CKPT}/{rev}: candidate files duplicate {same} — not a "
                             f"trustworthy grid point")
        entries[str(step)] = entry
    endpoint_entry = entries[str(ENDPOINT_STEP_2M)]
    if endpoint_entry["revision"] != REV_ENDPOINT_2M:
        raise ValueError(f"{REPO_CKPT}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_ENDPOINT_2M!r}")
    if REV_STAGE3_FINAL_2M not in table_c:
        raise ValueError(f"{REPO_CKPT}: the stage-3 endpoint {REV_STAGE3_FINAL_2M!r} is not in the "
                         f"inventory")
    stage3 = _weight_entry(REPO_CKPT, REV_STAGE3_FINAL_2M, table_c, cands_c)
    same3 = dups_of(REV_STAGE3_FINAL_2M)
    if same3:
        raise ValueError(f"{REPO_CKPT}/{REV_STAGE3_FINAL_2M}: the stage-3 endpoint's candidate files "
                         f"duplicate {same3} — not a trustworthy descriptive point")
    twin = {"repo": REPO_CKPT, "revision": TWIN, "commit": None, "files": [], "kind": "from_config",
            "seed": TWIN_SEED, "config_commit": endpoint_entry["commit"]}
    if REV_BASE_2M not in table_b:
        raise ValueError(f"{REPO_BASE}: the base revision {REV_BASE_2M!r} is not in the inventory")
    cands_b = {rev: ck.candidate(rev, t["files"], table_b[REV_BASE_2M]["files"]) for rev, t in table_b.items()}
    base = _weight_entry(REPO_BASE, REV_BASE_2M, table_b, cands_b)
    return {"repo_ckpt": REPO_CKPT, "repo_base": REPO_BASE, "grid_3b": list(GRID_3B),
            "trained_steps_3b": list(trained_steps_3b()), "log_head_subset": list(LOG_HEAD_SUBSET_2M),
            "tokens_per_step": TOKENS_PER_STEP_2M, "entries_3b": entries, "twin": twin,
            "stage3_final": stage3, "base": base, "endpoint_duplicates": dups_of(REV_ENDPOINT_2M),
            "n_revisions": {REPO_CKPT: len(table_c), REPO_BASE: len(table_b)}}


def write_manifest(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest_3b(path=CHECKPOINTS_PATH, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    if obj.get("grid_3b") != list(GRID_3B) or obj.get("log_head_subset") != list(LOG_HEAD_SUBSET_2M) \
            or not isinstance(obj.get("twin"), dict) or obj["twin"].get("kind") != "from_config":
        raise ValueError(f"{path}: manifest is not the frozen SmolLM3 grid")
    return obj


def entry_3b(manifest: dict, step) -> dict:
    if step == TWIN:
        e = manifest.get("twin")
    else:
        e = manifest.get("entries_3b", {}).get(str(int(step)))
    if e is None:
        raise ValueError(f"SmolLM3 step {step!r} is not a grid entry")
    return e


def entry_stage3_3b(manifest: dict) -> dict:
    e = manifest.get("stage3_final")
    if e is None:
        raise ValueError("manifest lacks a stage3_final entry")
    return e


def entry_base_3b(manifest: dict) -> dict:
    e = manifest.get("base")
    if e is None:
        raise ValueError("manifest lacks a base entry")
    return e


def entry_which_3b(manifest: dict, which: str) -> dict:
    if which == "stage1_final":
        return entry_3b(manifest, ENDPOINT_STEP_2M)
    if which == "stage3_final":
        return entry_stage3_3b(manifest)
    if which == "base":
        return entry_base_3b(manifest)
    raise ValueError(f"{which!r} is not one of {ENDPOINT_WHICH_2M}")


# -------------------------------------------------------- loader family

CKPT_CACHE_2M = Path.home() / "emergence-lab" / "ckpt_cache_2m"


def _cache_dir_3b(key, cache_root) -> Path:
    return Path(cache_root) / SIZE_OUT / str(key)


def download_entry_3b(entry: dict, cache_root=CKPT_CACHE_2M) -> dict:
    """MODEL CONTACT (weight bytes, ≈ 6.15 GB per revision). Never
    executed by a test."""
    from huggingface_hub import hf_hub_download
    rev_dir = _cache_dir_3b(entry["revision"], cache_root)
    paths = {}
    for name in entry["files"]:
        p = hf_hub_download(entry["repo"], name, revision=entry["commit"], cache_dir=str(rev_dir))
        paths[name] = Path(p).resolve()
    return paths


def clean_dir_3b(rev_key, cache_root, paths: dict, *, config) -> Path:
    """`battery_2l.clean_dir_13b` with the 2m cache key: the candidate
    files only, hardlinked, plus the entry's pinned `config` written as
    `config.json` (2i stop #1). `config` REQUIRED."""
    d = _cache_dir_3b(rev_key, cache_root) / "clean"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for name, src in paths.items():
        dst = d / name
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    config.to_json_file(str(d / "config.json"))
    return d


def load_checkpoint_3b(entry: dict, *, cache_root=CKPT_CACHE_2M, device: str = "mps", dtype=DTYPE_2M):
    """MODEL CONTACT. `battery_2l.load_checkpoint_13b`'s body with the
    repo read from the entry: candidate files hashed against the
    manifest, config pinned to the entry's own commit, loading info
    required empty, tensor digest via `ck.tensor_digest`. Never
    executed by a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    repo = entry["repo"]
    paths = download_entry_3b(entry, cache_root)
    shas = bi.verify_downloads(entry, paths)
    config = AutoConfig.from_pretrained(repo, revision=entry["commit"])
    d = clean_dir_3b(entry["revision"], cache_root, paths, config=config)
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(
        str(d), config=config, dtype=dt, low_cpu_mem_usage=True, output_loading_info=True)
    counts = bi._check_loading_info(li, f"{repo}@{entry['revision']} (candidate files)")
    model = model.to(device).eval()
    info = {"repo": repo, "revision": entry["revision"], "commit": entry["commit"],
            "kind": entry["kind"], "files": list(entry["files"]), "sha256": shas,
            "config_source": f"{repo}@{entry['commit']}", "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    return model, info


def check_tokenizer_2m(tok_like) -> None:
    """The pure assertions `load_tokenizer_3b` applies (design §3.2,
    dial n): left padding, SmolLM3's own pad id (set by the loader — the
    tokenizer declares none), the eos id, no special id prepended to a
    plain render. Raises `RuntimeError` naming the offending field."""
    side = getattr(tok_like, "padding_side", None)
    if side != "left":
        raise RuntimeError(f"padding_side is {side!r}, not 'left'")
    pad_id = getattr(tok_like, "pad_token_id", None)
    if pad_id != PAD_TOKEN_ID_2M:
        raise RuntimeError(f"pad_token_id is {pad_id!r}, not {PAD_TOKEN_ID_2M} — "
                           f"SmolLM3's own {PAD_TOKEN_2M}")
    eos_id = getattr(tok_like, "eos_token_id", None)
    if eos_id != EOS_TOKEN_ID_2M:
        raise RuntimeError(f"eos_token_id is {eos_id!r}, not {EOS_TOKEN_ID_2M}")
    first_id = tok_like("Q:")["input_ids"][0]
    specials = set(tok_like.all_special_ids)
    if first_id in specials:
        raise RuntimeError(f"a special id {first_id} is prepended to 'Q:' — the plain render "
                           f"must add no BOS (dial n)")


def load_tokenizer_3b(repo: str, commit: str):
    """MODEL-ADJACENT NETWORK (tokenizer files). Left padding, the pad
    token set to the vocabulary's own `<|finetune_right_pad_id|>` when
    the tokenizer declares none, then `check_tokenizer_2m`. Never
    executed by a test."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, revision=commit)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = PAD_TOKEN_2M
    check_tokenizer_2m(tok)
    return tok


def load_thin_3b(repo: str, commit: str, *, device: str = "mps", dtype=DTYPE_2M):
    """The second loader path: `battery_2i.load_thin`'s body (plain
    `from_pretrained` through the ordinary HF cache) with THIS module's
    tokenizer loader (2i's applies OLMo-2's pad check). Never executed
    by a test."""
    import torch
    from transformers import AutoModelForCausalLM
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(repo, revision=commit, dtype=dt,
                                                      output_loading_info=True)
    counts = bi._check_loading_info(li, f"{repo}@{commit} (thin load)")
    model = model.to(device).eval()
    tok = load_tokenizer_3b(repo, commit)
    info = {"repo": repo, "commit": commit, "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    return model, tok, info


def load_twin_3b(*, config_commit: str, device: str = "mps", dtype=DTYPE_2M, seed: int = TWIN_SEED):
    """The init referent (design §3.1, dial i): no step 0 exists on the
    branch, so a seeded `from_config` twin stands in — the stage-1
    config pinned at the endpoint's commit, `torch.manual_seed(seed)`
    immediately before construction. Descriptive only, never in an
    outcome. Never executed by a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    config = AutoConfig.from_pretrained(REPO_CKPT, revision=config_commit)
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    torch.manual_seed(int(seed))
    model = AutoModelForCausalLM.from_config(config, dtype=dt)
    model = model.to(device).eval()
    info = {"repo": REPO_CKPT, "revision": TWIN, "seed": int(seed),
            "config_source": f"{REPO_CKPT}@{config_commit}", "tensor_digest": ck.tensor_digest(model)}
    return model, info


def free_checkpoint_3b(rev_key, cache_root=CKPT_CACHE_2M) -> None:
    d = _cache_dir_3b(rev_key, cache_root)
    if d.exists():
        shutil.rmtree(d)


# ----------------------------------------------------------------- paths

def sweep_dir(root) -> Path:
    return Path(root) / "results" / "sweep" / SIZE_OUT


def _step_key(step) -> str:
    return TWIN if step == TWIN else f"step{int(step)}"


def record_path(root, step, rung: str) -> Path:
    return sweep_dir(root) / _step_key(step) / f"{rung}.json"


def checkpoint_record_path(root, step) -> Path:
    return sweep_dir(root) / _step_key(step) / "_checkpoint.json"


def gate1_path(root) -> Path:
    return sweep_dir(root) / "gate1.json"


def halt_marker_path(root) -> Path:
    return sweep_dir(root) / "HALTED"


def endpoint_dir(root) -> Path:
    return Path(root) / "results" / "endpoint"


ENDPOINT_WHICH_2M = ("stage1_final", "stage3_final", "base")


def endpoint_record_path(root, which: str, rung: str) -> Path:
    if which not in ENDPOINT_WHICH_2M:
        raise ValueError(f"{which!r} is not one of {ENDPOINT_WHICH_2M}")
    return endpoint_dir(root) / which / f"{rung}.json"


def rung_set_path(root) -> Path:
    return endpoint_dir(root) / "rung_set_2m.json"


def power_path(root) -> Path:
    return endpoint_dir(root) / "power_2m.json"


# ----------------------------------------------------------- rung-set rule

def rung_set_from_counts_2m(counts: dict, floors: dict) -> dict:
    """§4: R_3B = the rungs clearing 2d's bar at the stage-1 endpoint;
    R_PRIMARY = R_3B ∩ R_CAP_2K (the nine with a 256-draw predictor —
    both tests run here); R_ELEVEN_EXTRA = the rest of 2g's eleven that
    clear (printed with the 64-draw x_A and x_B, never in the verdict);
    R_EXTRA = the rest of R_3B (raw single-stratum D). Pure; sorted; a
    partition of R_3B."""
    from experiments.exp2d import stats_2d as st
    per_rung = {r: st.binomial_bar(int(k), N_ITEMS, float(floors[r])) for r, k in counts.items()}
    r_3b = tuple(r for r in sorted(counts) if per_rung[r]["significant"])
    r_primary = tuple(r for r in r_3b if r in R_CAP_2K)
    r_eleven_extra = tuple(r for r in r_3b if r in STRATA_RUNGS and r not in R_CAP_2K)
    r_extra = tuple(r for r in r_3b if r not in STRATA_RUNGS)
    return {"R_3B": list(r_3b), "R_PRIMARY": list(r_primary),
            "R_ELEVEN_EXTRA": list(r_eleven_extra), "R_EXTRA": list(r_extra),
            "primary_is_the_nine": tuple(r_primary) == tuple(sorted(R_CAP_2K)),
            "per_rung": per_rung}


# ------------------------------------------------------- endpoint sha

def composite_sha(files: dict) -> str:
    lines = "\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))
    return hashlib.sha256(lines.encode()).hexdigest()


def endpoint_files(root) -> dict:
    """{relpath: sha256} over the 102 endpoint records + the rung set +
    the power record — the content `ENDPOINT_SEAL_TAG_2M` binds. A
    missing file is a hard error."""
    root = Path(root)
    paths = [rung_set_path(root), power_path(root)]
    for which in ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            paths.append(endpoint_record_path(root, which, r))
    out = {}
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(str(p))
        out[str(p.relative_to(root))] = bg.sha256_file(p)
    return out


def endpoint_sha256(root) -> str:
    return composite_sha(endpoint_files(root))


# ---------------------------------------------------------- record stamps

def item_record_2m(*, rung, cap, ev, ckpt, step, endpoint_sha, t_s) -> dict:
    """A sweep record: 2i's `item_record_2i` (frozen, imported) with 2m's
    family/size, `seal_tag = ENDPOINT_SEAL_TAG_2M`, `predictor_sha =
    PREDICTOR_SHA_2M`, plus `endpoint_sha256` and the `dtype` OVERRIDE
    (`item_record_2i` hard-codes "float16"; `DTYPE_2M` is the truth).
    `step` is an int or `TWIN`."""
    from experiments.exp2i.run.endpoint_2i import item_record_2i
    rec = item_record_2i(rung=rung, family=FAMILY, size=SIZE_OUT, cap=cap, ev=ev, ckpt=ckpt,
                         seal={"tag": ENDPOINT_SEAL_TAG_2M, "sha256": PREDICTOR_SHA_2M},
                         t_s=t_s, step=(TWIN if step == TWIN else int(step)))
    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2M
    return rec


def endpoint_item_record_2m(*, rung, cap, ev, ckpt, which, seal, t_s) -> dict:
    """An endpoint record: `item_record_2i(which=…)` with the `dtype`
    override — used by the endpoint stage and every fixture."""
    from experiments.exp2i.run.endpoint_2i import item_record_2i
    rec = item_record_2i(rung=rung, family=FAMILY, size=SIZE_OUT, which=which, cap=cap, ev=ev,
                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2M
    return rec


def checkpoint_record_2m(*, step, ckpt: dict, info: dict, seconds: float) -> dict:
    """`_common_2i.checkpoint_record`'s payload with 2m's size and the
    repo (that helper hard-codes 2i's size)."""
    return {"family": FAMILY, "size": SIZE_OUT, "step": int(step), "repo": info.get("repo"),
            "revision": ckpt["revision"], "commit": ckpt["commit"],
            "sha256": dict(info.get("sha256", {})), "loading_info": info.get("loading_info"),
            "digest": ckpt["weight_sha256"], "download_seconds": round(seconds, 1)}


def twin_checkpoint_record_2m(*, info: dict) -> dict:
    """The twin's bespoke checkpoint record (2i's `run_twin` shape):
    no commit, no files, the seed and the config source."""
    return {"family": FAMILY, "size": SIZE_OUT, "step": TWIN, "repo": info.get("repo", REPO_CKPT),
            "revision": TWIN, "commit": None, "kind": "from_config", "seed": int(info["seed"]),
            "digest": info["tensor_digest"], "config_source": info["config_source"]}


# ---------------------------------------------------------------- gate 1

GATE1_FIELDS_2M = ("rungs", "bit_diffs", "continuation_diffs", "continuations_compared",
                   "digest_sweep", "digest_endpoint", "commit_sweep", "commit_endpoint",
                   "prereg_tag")


def gate1_failures_3b(rec: dict, endpoint_records: dict) -> list:
    """`battery_2l.gate1_failures_13b`'s body on the 2m labels: the
    runner's ATTESTED fields against the rule (coverage 500/rung
    required, both digests and commits equal, the prereg tag stamped)."""
    bad = []
    rungs = tuple(bt.RUNGS)
    if list(rec.get("rungs", [])) != list(rungs):
        bad.append("gate 1 smollm3_3b: rung list is not the full 34-rung sweep set")
    cs, ce = rec.get("commit_sweep"), rec.get("commit_endpoint")
    if not cs or not ce or cs != ce:
        bad.append(f"gate 1 smollm3_3b: commit through the sweep loader ({cs}) != through the "
                   f"endpoint loader ({ce})")
    dg_s, dg_e = rec.get("digest_sweep"), rec.get("digest_endpoint")
    if not dg_s or not dg_e or dg_s != dg_e:
        bad.append(f"gate 1 smollm3_3b: tensor digest through the sweep loader ({dg_s}) != "
                   f"through the endpoint loader ({dg_e}) — the checkpoint loader path is "
                   f"not the production path")
    bd, cd, nc = rec.get("bit_diffs", {}), rec.get("continuation_diffs", {}), \
        rec.get("continuations_compared", {})
    for r in rungs:
        if r not in endpoint_records:
            bad.append(f"gate 1 smollm3_3b/{r}: no stage1_final endpoint record to compare against")
            continue
        if bd.get(r) != 0:
            bad.append(f"gate 1 smollm3_3b/{r}: {bd.get(r)} bit diffs between the sweep's "
                       f"step{ENDPOINT_STEP_2M} record and the endpoint's stage1_final record")
        if cd.get(r) != 0:
            bad.append(f"gate 1 smollm3_3b/{r}: {cd.get(r)} continuation diffs")
        if nc.get(r) != N_ITEMS:
            bad.append(f"gate 1 smollm3_3b/{r}: {nc.get(r)} continuation pairs compared, not the "
                       f"full {N_ITEMS} — a zero diff count over a truncated comparison is "
                       f"not evidence")
    if rec.get("prereg_tag") != PREREG_TAG_2M:
        bad.append(f"gate 1 smollm3_3b: prereg_tag {rec.get('prereg_tag')!r} is not "
                   f"{PREREG_TAG_2M!r}")
    return bad


def gate1_rederive_3b(sweep_endpoint_records: dict, stage1_final_records: dict,
                      gate_record: dict) -> list:
    """`battery_2l.gate1_rederive_13b`'s body on the 2m labels: bit and
    continuation diffs RE-DERIVED from the two committed record sets,
    required zero AND equal to the attestation, coverage 500 on both
    sides and in the attestation."""
    bad = []
    g = gate_record if isinstance(gate_record, dict) else {}
    bd_att, cd_att, nc_att = g.get("bit_diffs", {}), g.get("continuation_diffs", {}), \
        g.get("continuations_compared", {})
    for r in bt.RUNGS:
        if r not in sweep_endpoint_records:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: no sweep step{ENDPOINT_STEP_2M} record "
                       f"to re-derive against")
            continue
        if r not in stage1_final_records:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: no stage1_final endpoint record to "
                       f"re-derive against")
            continue
        s_bits, e_bits = sweep_endpoint_records[r].get("bits"), stage1_final_records[r].get("bits")
        s_c, e_c = sweep_endpoint_records[r].get("continuations"), \
            stage1_final_records[r].get("continuations")
        if not isinstance(s_bits, list) or not isinstance(e_bits, list) or \
                len(s_bits) != N_ITEMS or len(e_bits) != N_ITEMS:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: sweep/endpoint bits are not both "
                       f"{N_ITEMS} long — coverage failure")
            continue
        if not isinstance(s_c, list) or not isinstance(e_c, list) or \
                len(s_c) != N_ITEMS or len(e_c) != N_ITEMS:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: sweep/endpoint continuations are not "
                       f"both {N_ITEMS} long — coverage failure")
            continue
        bit_diff = sum(1 for a, b in zip(s_bits, e_bits) if int(bool(a)) != int(bool(b)))
        cont_diff = sum(1 for a, b in zip(s_c, e_c) if a != b)
        if bit_diff != 0:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: {bit_diff} bit diff(s) between the "
                       f"sweep's step{ENDPOINT_STEP_2M} record and the stage1_final endpoint "
                       f"record (re-derived from the bytes, not the attestation)")
        if cont_diff != 0:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: {cont_diff} continuation diff(s) "
                       f"(re-derived from the bytes, not the attestation)")
        if bd_att.get(r) != bit_diff:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: attested bit_diffs {bd_att.get(r)!r} "
                       f"disagrees with the re-derived {bit_diff}")
        if cd_att.get(r) != cont_diff:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: attested continuation_diffs "
                       f"{cd_att.get(r)!r} disagrees with the re-derived {cont_diff}")
        if nc_att.get(r) != N_ITEMS:
            bad.append(f"gate 1 smollm3_3b re-derive/{r}: attested continuations_compared "
                       f"{nc_att.get(r)!r} is not the full {N_ITEMS} — a zero diff count over "
                       f"a truncated comparison is not evidence")
    return bad


# ------------------------------------------------------------------ pins

# Every frozen module 2m executes on the verdict path or in a stage tool:
# 2l's 42 (which carry 2k's, 2j's, 2i's, 2g's, 2h's, 2d's, 2c's, exp3's)
# + 2l's four tag-bound blobs (2l is closed; frozen bytes to 2m) + 2m's
# own artifact writers. The four 2m blobs the prereg TAG binds are NOT
# here (2j's rule). `run/preflight_2m.py` and `verify_referents_2m.py`
# are pinned by `analyze_2m.IMPORTED_SHA256_2M` (Task 5).
FROZEN_FILES_2M = tuple(bl.FROZEN_SHA256_2L) + tuple(REPO / rel for rel in bl.INSTRUMENT_BLOBS_2L) + (
    EXP2M / "power_2m.py",
    EXP2M / "make_referents_2m.py",
)
FROZEN_SHA256_2M = {}   # Task 5: pinned as a literal from frozen_from_disk() (48 modules)


def frozen_from_disk(*, strict: bool = True) -> dict:
    if strict:
        return {p: bg.sha256_file(p) for p in FROZEN_FILES_2M}
    return {p: bg.sha256_file(p) for p in FROZEN_FILES_2M if p.is_file()}


def check_frozen_2m() -> None:
    if not FROZEN_SHA256_2M:
        raise RuntimeError("FROZEN_SHA256_2M is empty — not pinned (build incomplete)")
    for p, want in FROZEN_SHA256_2M.items():
        got = bg.sha256_file(p)
        if got != want:
            raise RuntimeError(f"frozen module drifted: {p} ({got[:12]} != {want[:12]})")


def require_prereg_2m(*, tag_exists=None, blob_sha=None) -> dict:
    """2k's blob binding: the tag must exist and each instrument blob's
    bytes on disk must equal the blob the tag carries."""
    from experiments.exp2g import predictor_2g as pr
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_2M):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_2M} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_2M:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_2M, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_2M} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_2M, "instrument_blobs": bound}


if __name__ == "__main__":
    if "--scan" in sys.argv:
        inv = refresh_inventory_3b()
        print(REPO_CKPT, len(inv[REPO_CKPT]), "revisions;", REPO_BASE, len(inv[REPO_BASE]))
        print("sha256", bg.sha256_file(HUB_INVENTORY_PATH))
    elif "--manifest" in sys.argv:
        inv = load_inventory_3b()
        manifest = build_manifest_3b(inv)
        write_manifest(CHECKPOINTS_PATH, manifest)
        e = entry_3b(manifest, ENDPOINT_STEP_2M)
        print("entries", len(manifest["entries_3b"]), "; endpoint commit", e["commit"],
              "; stage3_final commit", entry_stage3_3b(manifest)["commit"],
              "; base commit", entry_base_3b(manifest)["commit"],
              "; endpoint_duplicates", manifest["endpoint_duplicates"])
        print("sha256", bg.sha256_file(CHECKPOINTS_PATH))
    else:
        print("usage: python -m experiments.exp2m.battery_2m --scan | --manifest")
