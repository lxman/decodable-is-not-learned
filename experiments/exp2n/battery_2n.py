# experiments/exp2n/battery_2n.py
"""Experiment 2n — constants, the ONE-repo Comma v0.1-1T inventory +
manifest, the Comma loader family (its own tokenizer pins, the BOS
render, the EOS stop-id override, the seeded twin), paths, the rung-set
rule, record stamps, the gate-1 checkers, the pins and the prereg
binding (design `experiment-2n-design.md` §2–§3).
Everything not defined here is imported frozen and sha-pinned
(`FROZEN_SHA256_2N`, `check_frozen_2n`): 2m's instrument (four
tag-bound blobs, now frozen bytes), 2k's tier readers, 2i's record
shapes and seal machinery, 2g's strata and statistics, 2d's bar, 2c's
harness.

Deltas from `battery_2m`, all local to this module:

1. ONE repo: `common-pile/comma-v0.1-1t` carries the 46 stage-1
   revisions (`stage1-step<NNNNNN>-tokens<N>B`), the 9 stage-2
   cool-down revisions and a WEIGHT-BEARING `main` (the averaged
   release — unlike 2m's checkpoints repo, whose `main` was weightless).
   The manifest's duplicate-signature refusal runs over every scanned
   revision including `main` itself: a grid revision whose shards
   duplicate `main`'s is a stale copy, 2g's structural zero.
2. No step 0 exists: a seeded `from_config` TWIN of the stage-1 config
   at the endpoint's commit stands in (2i/2m's construction), loaded in
   the sweep after gate 1, never in an outcome.
3. A fourth tokenizer shape: Comma's own 64k BPE DECLARES its pad
   (`<pad>` 0) — the first outcome family whose tokenizer does — and the
   stack's plain render adds no special id, but the model trained with a
   BOS on every sequence. Dial n pins the render: the runner prepends
   `BOS_TOKEN_2N` to every prompt (`render_2n`, `BosRunner`), and
   `check_tokenizer_2n` asserts both the plain render's silence and the
   BOS render's single leading id.
4. The stop id (dial o): `config.json`'s `eos_token_id` is 2 — the
   tokenizer's OWN BOS, a LlamaConfig default, not Comma's real EOS (3).
   `set_eos_stop_2n` overrides `model.generation_config.eos_token_id` to
   3 after every load and asserts it reads back; every record carries
   `eos_stop_id` and `render`.
5. `DTYPE_2N` and `BATCH_SIZE_2N` are single pre-tag constants; every
   record's `dtype` is OVERRIDDEN to `DTYPE_2N` (2i's `item_record_2i`
   hard-codes "float16") and the analyzer requires it.
6. The predictors are 2k's and 2i's sealed artifacts: nothing is
   sampled. `PREDICTOR_SHA_2N` is a composite of the two seal shas with
   a "2n|" prefix — distinct from 2l's and 2m's composites of the same
   two seals.
7. Three endpoint whichs (stage1_final, stage2_final, main): the
   endpoint seal binds 3 × 34 records + the rung set + the power record.
8. The outcome grid is uniform on the 10k/20k lattice — {10,000} ∪
   {20,000·j : j = 1…23}, 24 points — with an every-40k 12-point SUBSET
   printed as a grid-density control (never a descriptive substitute).

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

EXP2N = Path(__file__).resolve().parent
EXPERIMENTS = EXP2N.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import strata_2g  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402

RESULTS = EXP2N / "results"
HUB_INVENTORY_PATH = EXP2N / "hub_inventory_comma.json"
CHECKPOINTS_PATH = EXP2N / "checkpoints_2n.json"
CHECKPOINTS_2N_SHA256 = "ff7996d141fe8e4f0791b143b573c538062bbd4be776fdcf27317d58e90943d5"

FAMILY = "comma"
SIZE_OUT = "comma_7b"
REPO_COMMA = "common-pile/comma-v0.1-1t"
REV_ENDPOINT_2N = "stage1-step460000-tokens965B"
ENDPOINT_STEP_2N = 460000
REV_STAGE2_FINAL_2N = "stage2-step018000-tokens1002B"
STAGE2_STEP_2N = 18000
REV_MAIN_2N = "main"                       # weight-bearing on this repo (the averaged release)
TOKENS_PER_STEP_2N = 2_097_152             # lingua batch 2 x seq 4096 x grad-acc 4 x 64 GPUs
TWIN = bi.TWIN                             # "twin"
TWIN_SEED = 0

# design §3.6 / dial c: the uniform grid on the branch's 10k lattice —
# {10,000} u {20,000 . j : j = 1 ... 23} — 24 trained points.
GRID_COMMA = (10000, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000,
              200000, 220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000, 380000,
              400000, 420000, 440000, 460000)
# design §5 / process note 3: the every-40k GRID-DENSITY CONTROL (12
# points, a strict subset) — never a descriptive substitute for the grid.
EVERY40K_SUBSET_2N = (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000,
                      400000, 440000, 460000)
if not set(EVERY40K_SUBSET_2N) < set(GRID_COMMA):
    raise RuntimeError("EVERY40K_SUBSET_2N must be a strict subset of GRID_COMMA")

PREREG_TAG_2N = "exp2n-preregistered"
ENDPOINT_SEAL_TAG_2N = "exp2n-endpoint-sealed"
INSTRUMENT_BLOBS_2N = ("experiments/exp2n/analyze_2n.py",
                       "experiments/exp2n/battery_2n.py",
                       "experiments/exp2n/run/endpoint_2n.py",
                       "experiments/exp2n/run/sweep_2n.py")

N_ITEMS = bt.N_ITEMS
STRATA_RUNGS = tuple(strata_2g.COVARIATE_OF)       # 2g's eleven
R_CAP_2K = tuple(bk.R_CAP_DESIGN)                  # the nine with a 256-draw predictor
BATCH_SIZE_2N = 16                                 # dial m — a pre-tag constant, threaded explicitly
DTYPE_2N = "float16"                               # dial l — a pre-tag constant; the fp32 fallback is a re-tag

# The tokenizer's facts (design §2, Hub metadata + the stack measurement
# 2026-09-06; dials n and o). Comma's own 64k BPE: <pad> 0 (DECLARED — the
# first outcome family with one), <unk> 1, <|begin_of_text|> 2,
# <|end_of_text|> 3; config.json's bos 1 / eos 2 are LlamaConfig defaults.
PAD_TOKEN_2N = "<pad>"
PAD_TOKEN_ID_2N = 0
UNK_TOKEN_ID_2N = 1
BOS_TOKEN_2N = "<|begin_of_text|>"
BOS_TOKEN_ID_2N = 2
EOS_TOKEN_2N = "<|end_of_text|>"
EOS_TOKEN_ID_2N = 3
CONFIG_EOS_TOKEN_ID_2N = 2          # what config.json says; disclosed, never used as a stop
EOS_STOP_ID_2N = EOS_TOKEN_ID_2N    # dial o: both loaders set generation_config.eos_token_id to this
RENDER_2N = "bos"                   # dial n: one BOS_TOKEN_2N prefix on every prompt (the training render)
VOCAB_LEN_2N = 64000                # len(tokenizer)
CONFIG_VOCAB_2N = 64256             # config.json vocab_size (padded rows; ids >= 64000 decode to '')

# The two predictor seals, as committed (2k close-out, 2i close-out) —
# the same two literals 2m carries; asserted equal to the seal files by
# test.
SEAL_2K_SHA256 = "3c4778b06de20c38090ea0f488e4f1664019076d7015b447b30e57f95ae2be9a"
SEAL_2I_SHA256 = "d80ada5058b422645514c199046f00e9d5ab86a8139fb6a725f487ed8560be24"
PREDICTOR_TAGS_2N = f"{bk.SEAL_TAG_2K}+{bi.PREDICTOR_SEAL_TAG}"


def predictor_sha_2n(seal_2k_sha: str, seal_2i_sha: str) -> str:
    """The composite `predictor_sha` every 2n record stamps: both
    predictors are already sealed, so 2n's own predictor identity is a
    function of the two seals — with a "2n|" prefix so it is distinct
    from 2l's and 2m's composites of the same two seals."""
    return hashlib.sha256(f"2n|{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()


PREDICTOR_SHA_2N = predictor_sha_2n(SEAL_2K_SHA256, SEAL_2I_SHA256)

_STAGE1_RE_2N = re.compile(r"^stage1-step(\d{6})-tokens(\d+)B$")


def trained_steps_comma() -> tuple:
    return tuple(GRID_COMMA)


def n_trained_comma() -> int:
    return len(trained_steps_comma())


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


def load_inventory_comma(path=HUB_INVENTORY_PATH) -> dict:
    inv = json.loads(Path(path).read_text())
    if REPO_COMMA not in inv or REV_MAIN_2N not in inv[REPO_COMMA] or REV_ENDPOINT_2N not in inv[REPO_COMMA]:
        raise ValueError(f"inventory lacks {REPO_COMMA}/{REV_MAIN_2N} or {REPO_COMMA}/{REV_ENDPOINT_2N}")
    return inv


def refresh_inventory_comma(out_path=HUB_INVENTORY_PATH) -> dict:
    """NETWORK (metadata only) — the ONE Hub scan of the whole build:
    every branch of `REPO_COMMA` (46 stage-1, the 9 stage-2 cool-down
    revisions, the weight-bearing `main`) EXCEPT pull-request refs
    (`pr/N`) — those are not checkpoints. Refuses if `out_path` exists —
    this runs ONCE, ever."""
    p = Path(out_path)
    if p.exists():
        raise FileExistsError(f"{p} already exists — refresh_inventory_comma is the ONE scan "
                              f"of this build and refuses to overwrite a committed inventory")
    from huggingface_hub import HfApi
    api = HfApi()

    def _info(repo: str, rev: str) -> dict:
        info = _retry(api.model_info, repo, revision=rev, files_metadata=True)
        files = {s.rfilename: [s.lfs.sha256, s.size] for s in info.siblings if s.lfs}
        return {"commit": info.sha, "files": files}

    refs = _retry(api.list_repo_refs, REPO_COMMA)
    revs = sorted({b.name for b in refs.branches if not b.name.startswith("pr/")} | {REV_MAIN_2N})
    table = {rev: _info(REPO_COMMA, rev) for rev in revs}
    out = {REPO_COMMA: table}
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


def build_manifest_comma(inv: dict) -> dict:
    """`battery_2m.build_manifest_3b`'s body over ONE repo whose `main`
    CARRIES weights (the averaged release): 2g's `ck.candidate`/
    `ck.signature` with `main_files = table["main"]["files"]`, the
    duplicate-signature refusal across ALL scanned revisions for every
    grid point and for the stage-2 endpoint and for `main` itself (a
    grid revision whose shards duplicate `main`'s is a stale copy, 2g's
    structural zero). The stage-1 endpoint alone may duplicate (recorded
    under `endpoint_duplicates`). The twin entry carries the endpoint's
    commit as `config_commit`."""
    table = inv[REPO_COMMA]
    if REV_MAIN_2N not in table:
        raise ValueError(f"{REPO_COMMA}: the main revision {REV_MAIN_2N!r} is not in the inventory")
    main_files = table[REV_MAIN_2N]["files"]
    cands = {rev: ck.candidate(rev, t["files"], main_files) for rev, t in table.items()}
    sigs = {rev: (ck.signature(table[rev]["files"], c) if c else None) for rev, c in cands.items()}

    def dups_of(rev: str) -> list:
        return sorted(r for r, s in sigs.items() if r != rev and s is not None and s == sigs[rev])

    entries = {}
    for step in trained_steps_comma():
        matches = [r for r in table if _STAGE1_RE_2N.fullmatch(r)
                   and int(_STAGE1_RE_2N.fullmatch(r).group(1)) == step]
        if len(matches) != 1:
            raise ValueError(f"{REPO_COMMA}: step {step} matches {matches} in the inventory — "
                             f"exactly one stage1 branch is expected")
        rev = matches[0]
        entry = _weight_entry(REPO_COMMA, rev, table, cands)
        same = dups_of(rev)
        if step != ENDPOINT_STEP_2N and same:
            raise ValueError(f"{REPO_COMMA}/{rev}: candidate files duplicate {same} — not a "
                             f"trustworthy grid point")
        entries[str(step)] = entry
    endpoint_entry = entries[str(ENDPOINT_STEP_2N)]
    if endpoint_entry["revision"] != REV_ENDPOINT_2N:
        raise ValueError(f"{REPO_COMMA}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_ENDPOINT_2N!r}")
    for name, rev in (("stage2_final", REV_STAGE2_FINAL_2N), ("main", REV_MAIN_2N)):
        if rev not in table:
            raise ValueError(f"{REPO_COMMA}: the {name} revision {rev!r} is not in the inventory")
        if dups_of(rev):
            raise ValueError(f"{REPO_COMMA}/{rev}: the {name} candidate files duplicate "
                             f"{dups_of(rev)} — not a trustworthy descriptive point")
    stage2 = _weight_entry(REPO_COMMA, REV_STAGE2_FINAL_2N, table, cands)
    main = _weight_entry(REPO_COMMA, REV_MAIN_2N, table, cands)
    twin = {"repo": REPO_COMMA, "revision": TWIN, "commit": None, "files": [], "kind": "from_config",
            "seed": TWIN_SEED, "config_commit": endpoint_entry["commit"]}
    return {"repo": REPO_COMMA, "grid_comma": list(GRID_COMMA),
            "trained_steps_comma": list(trained_steps_comma()),
            "every40k_subset": list(EVERY40K_SUBSET_2N), "tokens_per_step": TOKENS_PER_STEP_2N,
            "entries_comma": entries, "twin": twin, "stage2_final": stage2, "main": main,
            "endpoint_duplicates": dups_of(REV_ENDPOINT_2N), "n_revisions": len(table)}


def write_manifest(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest_comma(path=CHECKPOINTS_PATH, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    if obj.get("grid_comma") != list(GRID_COMMA) or obj.get("every40k_subset") != list(EVERY40K_SUBSET_2N) \
            or not isinstance(obj.get("twin"), dict) or obj["twin"].get("kind") != "from_config":
        raise ValueError(f"{path}: manifest is not the frozen Comma grid")
    return obj


def entry_comma(manifest: dict, step) -> dict:
    if step == TWIN:
        e = manifest.get("twin")
    else:
        e = manifest.get("entries_comma", {}).get(str(int(step)))
    if e is None:
        raise ValueError(f"Comma step {step!r} is not a grid entry")
    return e


def entry_stage2_comma(manifest: dict) -> dict:
    e = manifest.get("stage2_final")
    if e is None:
        raise ValueError("manifest lacks a stage2_final entry")
    return e


def entry_main_comma(manifest: dict) -> dict:
    e = manifest.get("main")
    if e is None:
        raise ValueError("manifest lacks a main entry")
    return e


def entry_which_comma(manifest: dict, which: str) -> dict:
    if which == "stage1_final":
        return entry_comma(manifest, ENDPOINT_STEP_2N)
    if which == "stage2_final":
        return entry_stage2_comma(manifest)
    if which == "main":
        return entry_main_comma(manifest)
    raise ValueError(f"{which!r} is not one of {ENDPOINT_WHICH_2N}")


# --------------------------------------------- render + stop id (dial n, o)

def eos_facts_2n(model) -> dict:
    """What the loaded model says about its ids, measured: config.json's
    bos/eos (LlamaConfig defaults on Comma, disclosed) and the generation
    config's eos AFTER `set_eos_stop_2n`."""
    return {"config_eos_token_id": getattr(model.config, "eos_token_id", None),
            "config_bos_token_id": getattr(model.config, "bos_token_id", None),
            "generation_eos_token_id": getattr(model.generation_config, "eos_token_id", None)}


def set_eos_stop_2n(model) -> dict:
    """Dial o: the harness (2c's `HFRunner.generate`, frozen) stops on the
    loaded model's `generation_config.eos_token_id`, which Comma's config
    sets to 2 — the tokenizer's BOS. Set it to the tokenizer's EOS and
    REQUIRE it to read back; called by every 2n loader. Returns the facts."""
    model.generation_config.eos_token_id = EOS_STOP_ID_2N
    facts = eos_facts_2n(model)
    if facts["generation_eos_token_id"] != EOS_STOP_ID_2N:
        raise RuntimeError(f"generation_config.eos_token_id reads {facts['generation_eos_token_id']!r} "
                           f"after setting {EOS_STOP_ID_2N} — the stop id cannot be pinned")
    return facts


def render_2n(prompts) -> list:
    """Dial n: one `BOS_TOKEN_2N` prefix on every prompt string — the
    tokenizer resolves it to the single added-token id 2, first, after the
    pads (left padding). Pure."""
    return [BOS_TOKEN_2N + p for p in prompts]


class BosRunner:
    """The production runner: 2c's `HFRunner` (frozen) behind the BOS
    render. `evaluate_items` (2g, frozen) renders the prompt text itself,
    so the prefix has to go on here, between it and `generate`. Every
    stage builds its runner through this class; `batch_size` is exposed
    for the record."""

    def __init__(self, inner):
        self.inner = inner
        self.batch_size = getattr(inner, "batch_size", None)

    def generate(self, prompts, max_new_tokens: int) -> list:
        return self.inner.generate(render_2n(prompts), max_new_tokens)


def check_tokenizer_2n(tok_like) -> None:
    """The pure assertions every 2n load applies (design §3.2, dials n, o):
    left padding; Comma's OWN declared pad 0 (the loader sets nothing);
    unk 1, bos 2, eos 3; 64,000 entries; the plain render of 'Q:' begins
    with a NON-special id (the stack adds nothing — the measured fact);
    the BOS render begins with exactly one id 2 followed by the plain
    render's first id. Raises `RuntimeError` naming the offending field."""
    side = getattr(tok_like, "padding_side", None)
    if side != "left":
        raise RuntimeError(f"padding_side is {side!r}, not 'left'")
    for name, want in (("pad_token_id", PAD_TOKEN_ID_2N), ("eos_token_id", EOS_TOKEN_ID_2N),
                       ("bos_token_id", BOS_TOKEN_ID_2N), ("unk_token_id", UNK_TOKEN_ID_2N)):
        got = getattr(tok_like, name, None)
        if got != want:
            raise RuntimeError(f"{name} is {got!r}, not {want} — Comma's own {name}")
    n = len(tok_like)
    if n != VOCAB_LEN_2N:
        raise RuntimeError(f"len(tokenizer) is {n}, not {VOCAB_LEN_2N}")
    plain = list(tok_like("Q:")["input_ids"])
    specials = set(tok_like.all_special_ids)
    if not plain or plain[0] in specials:
        raise RuntimeError(f"the plain render of 'Q:' begins with {plain[:1]} — a special id; the stack "
                           f"must add nothing on its own (dial n pins the prefix explicitly)")
    bos = list(tok_like(BOS_TOKEN_2N + "Q:")["input_ids"])
    if bos[:2] != [BOS_TOKEN_ID_2N, plain[0]] or (len(bos) > 2 and bos[1] == BOS_TOKEN_ID_2N):
        raise RuntimeError(f"the BOS render of 'Q:' begins {bos[:3]}, not [{BOS_TOKEN_ID_2N}, {plain[0]}] — "
                           f"exactly one BOS, first (dial n)")


def load_tokenizer_comma(repo: str, commit: str):
    """MODEL-ADJACENT NETWORK (tokenizer files). Left padding, then
    `check_tokenizer_2n` — nothing is set on the tokenizer (Comma declares
    its own pad; a tokenizer declaring another one is refused). Never
    executed by a test."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, revision=commit)
    tok.padding_side = "left"
    check_tokenizer_2n(tok)
    return tok


# -------------------------------------------------------- loader family

CKPT_CACHE_2N = Path.home() / "emergence-lab" / "ckpt_cache_2n"


def _cache_dir_comma(key, cache_root) -> Path:
    return Path(cache_root) / SIZE_OUT / str(key)


def download_entry_comma(entry: dict, cache_root=CKPT_CACHE_2N) -> dict:
    """MODEL CONTACT (weight bytes, ≈ 14.0 GB per revision). Never
    executed by a test."""
    from huggingface_hub import hf_hub_download
    rev_dir = _cache_dir_comma(entry["revision"], cache_root)
    paths = {}
    for name in entry["files"]:
        p = hf_hub_download(entry["repo"], name, revision=entry["commit"], cache_dir=str(rev_dir))
        paths[name] = Path(p).resolve()
    return paths


def clean_dir_comma(rev_key, cache_root, paths: dict, *, config) -> Path:
    """`battery_2m.clean_dir_3b` with the 2n cache key: the candidate
    files only, hardlinked, plus the entry's pinned `config` written as
    `config.json` (2i stop #1). `config` REQUIRED."""
    d = _cache_dir_comma(rev_key, cache_root) / "clean"
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


def load_checkpoint_comma(entry: dict, *, cache_root=CKPT_CACHE_2N, device: str = "mps", dtype=DTYPE_2N):
    """MODEL CONTACT. `battery_2m.load_checkpoint_3b`'s body with the
    repo read from the entry: candidate files hashed against the
    manifest, config pinned to the entry's own commit, loading info
    required empty, tensor digest via `ck.tensor_digest`, then dial o's
    `set_eos_stop_2n` applied and its facts merged into `info`. Never
    executed by a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    repo = entry["repo"]
    paths = download_entry_comma(entry, cache_root)
    shas = bi.verify_downloads(entry, paths)
    config = AutoConfig.from_pretrained(repo, revision=entry["commit"])
    d = clean_dir_comma(entry["revision"], cache_root, paths, config=config)
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(
        str(d), config=config, dtype=dt, low_cpu_mem_usage=True, output_loading_info=True)
    counts = bi._check_loading_info(li, f"{repo}@{entry['revision']} (candidate files)")
    model = model.to(device).eval()
    facts = set_eos_stop_2n(model)
    info = {"repo": repo, "revision": entry["revision"], "commit": entry["commit"],
            "kind": entry["kind"], "files": list(entry["files"]), "sha256": shas,
            "config_source": f"{repo}@{entry['commit']}", "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    info.update(facts)
    return model, info


def load_thin_comma(repo: str, commit: str, *, device: str = "mps", dtype=DTYPE_2N):
    """The second loader path: `battery_2i.load_thin`'s body (plain
    `from_pretrained` through the ordinary HF cache) with THIS module's
    tokenizer loader (2i's applies OLMo-2's pad check), then dial o's
    `set_eos_stop_2n`. Never executed by a test."""
    import torch
    from transformers import AutoModelForCausalLM
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(repo, revision=commit, dtype=dt,
                                                      output_loading_info=True)
    counts = bi._check_loading_info(li, f"{repo}@{commit} (thin load)")
    model = model.to(device).eval()
    facts = set_eos_stop_2n(model)
    tok = load_tokenizer_comma(repo, commit)
    info = {"repo": repo, "commit": commit, "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    info.update(facts)
    return model, tok, info


def load_twin_comma(*, config_commit: str, device: str = "mps", dtype=DTYPE_2N, seed: int = TWIN_SEED):
    """The init referent (design §3.1, dial i): no step 0 exists on the
    branch, so a seeded `from_config` twin stands in — the stage-1
    config pinned at the endpoint's commit, `torch.manual_seed(seed)`
    immediately before construction, then dial o's `set_eos_stop_2n`.
    Descriptive only, never in an outcome. Never executed by a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    config = AutoConfig.from_pretrained(REPO_COMMA, revision=config_commit)
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    torch.manual_seed(int(seed))
    model = AutoModelForCausalLM.from_config(config, dtype=dt)
    model = model.to(device).eval()
    facts = set_eos_stop_2n(model)
    info = {"repo": REPO_COMMA, "revision": TWIN, "seed": int(seed),
            "config_source": f"{REPO_COMMA}@{config_commit}", "tensor_digest": ck.tensor_digest(model)}
    info.update(facts)
    return model, info


def free_checkpoint_comma(rev_key, cache_root=CKPT_CACHE_2N) -> None:
    d = _cache_dir_comma(rev_key, cache_root)
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


ENDPOINT_WHICH_2N = ("stage1_final", "stage2_final", "main")


def endpoint_record_path(root, which: str, rung: str) -> Path:
    if which not in ENDPOINT_WHICH_2N:
        raise ValueError(f"{which!r} is not one of {ENDPOINT_WHICH_2N}")
    return endpoint_dir(root) / which / f"{rung}.json"


def rung_set_path(root) -> Path:
    return endpoint_dir(root) / "rung_set_2n.json"


def power_path(root) -> Path:
    return endpoint_dir(root) / "power_2n.json"


# ----------------------------------------------------------- rung-set rule

def rung_set_from_counts_2n(counts: dict, floors: dict) -> dict:
    """§4: R_Comma = the rungs clearing 2d's bar at the stage-1 endpoint;
    R_PRIMARY = R_Comma ∩ R_CAP_2K (the nine with a 256-draw predictor —
    both tests run here); R_ELEVEN_EXTRA = the rest of 2g's eleven that
    clear (printed with the 64-draw x_A and x_B, never in the verdict);
    R_EXTRA = the rest of R_Comma (raw single-stratum D). Pure; sorted; a
    partition of R_Comma."""
    from experiments.exp2d import stats_2d as st
    per_rung = {r: st.binomial_bar(int(k), N_ITEMS, float(floors[r])) for r, k in counts.items()}
    r_comma = tuple(r for r in sorted(counts) if per_rung[r]["significant"])
    r_primary = tuple(r for r in r_comma if r in R_CAP_2K)
    r_eleven_extra = tuple(r for r in r_comma if r in STRATA_RUNGS and r not in R_CAP_2K)
    r_extra = tuple(r for r in r_comma if r not in STRATA_RUNGS)
    return {"R_COMMA": list(r_comma), "R_PRIMARY": list(r_primary),
            "R_ELEVEN_EXTRA": list(r_eleven_extra), "R_EXTRA": list(r_extra),
            "primary_is_the_nine": tuple(r_primary) == tuple(sorted(R_CAP_2K)),
            "per_rung": per_rung}


# ------------------------------------------------------- endpoint sha

def composite_sha(files: dict) -> str:
    lines = "\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))
    return hashlib.sha256(lines.encode()).hexdigest()


def endpoint_files(root) -> dict:
    """{relpath: sha256} over the 102 endpoint records + the rung set +
    the power record — the content `ENDPOINT_SEAL_TAG_2N` binds. A
    missing file is a hard error."""
    root = Path(root)
    paths = [rung_set_path(root), power_path(root)]
    for which in ENDPOINT_WHICH_2N:
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

def item_record_2n(*, rung, cap, ev, ckpt, step, endpoint_sha, t_s) -> dict:
    """A sweep record: 2i's `item_record_2i` (frozen, imported) with 2n's
    family/size, `seal_tag = ENDPOINT_SEAL_TAG_2N`, `predictor_sha =
    PREDICTOR_SHA_2N`, plus `endpoint_sha256`, the `dtype` OVERRIDE
    (`item_record_2i` hard-codes "float16"; `DTYPE_2N` is the truth) and
    the render/stop-id pins (dials n, o). `step` is an int or `TWIN`."""
    from experiments.exp2i.run.endpoint_2i import item_record_2i
    rec = item_record_2i(rung=rung, family=FAMILY, size=SIZE_OUT, cap=cap, ev=ev, ckpt=ckpt,
                         seal={"tag": ENDPOINT_SEAL_TAG_2N, "sha256": PREDICTOR_SHA_2N},
                         t_s=t_s, step=(TWIN if step == TWIN else int(step)))
    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec


def endpoint_item_record_2n(*, rung, cap, ev, ckpt, which, seal, t_s) -> dict:
    """An endpoint record: `item_record_2i(which=…)` with the `dtype`
    override and the render/stop-id pins — used by the endpoint stage
    and every fixture."""
    from experiments.exp2i.run.endpoint_2i import item_record_2i
    rec = item_record_2i(rung=rung, family=FAMILY, size=SIZE_OUT, which=which, cap=cap, ev=ev,
                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec


def checkpoint_record_2n(*, step, ckpt: dict, info: dict, seconds: float) -> dict:
    """`_common_2i.checkpoint_record`'s payload with 2n's size and the
    repo (that helper hard-codes 2i's size), plus the stop-id facts
    (dial o)."""
    return {"family": FAMILY, "size": SIZE_OUT, "step": int(step), "repo": info.get("repo"),
            "revision": ckpt["revision"], "commit": ckpt["commit"],
            "sha256": dict(info.get("sha256", {})), "loading_info": info.get("loading_info"),
            "digest": ckpt["weight_sha256"], "download_seconds": round(seconds, 1),
            "config_eos_token_id": info.get("config_eos_token_id"),
            "generation_eos_token_id": info.get("generation_eos_token_id")}


def twin_checkpoint_record_2n(*, info: dict) -> dict:
    """The twin's bespoke checkpoint record (2i's `run_twin` shape):
    no commit, no files, the seed, the config source and the stop-id
    facts (dial o)."""
    return {"family": FAMILY, "size": SIZE_OUT, "step": TWIN, "repo": info.get("repo", REPO_COMMA),
            "revision": TWIN, "commit": None, "kind": "from_config", "seed": int(info["seed"]),
            "digest": info["tensor_digest"], "config_source": info["config_source"],
            "config_eos_token_id": info.get("config_eos_token_id"),
            "generation_eos_token_id": info.get("generation_eos_token_id")}


# ---------------------------------------------------------------- gate 1

GATE1_FIELDS_2N = ("rungs", "bit_diffs", "continuation_diffs", "continuations_compared",
                   "digest_sweep", "digest_endpoint", "commit_sweep", "commit_endpoint",
                   "prereg_tag")


def gate1_failures_comma(rec: dict, endpoint_records: dict) -> list:
    """`battery_2m.gate1_failures_3b`'s body on the 2n labels: the
    runner's ATTESTED fields against the rule (coverage 500/rung
    required, both digests and commits equal, the prereg tag stamped)."""
    bad = []
    rungs = tuple(bt.RUNGS)
    if list(rec.get("rungs", [])) != list(rungs):
        bad.append("gate 1 comma_7b: rung list is not the full 34-rung sweep set")
    cs, ce = rec.get("commit_sweep"), rec.get("commit_endpoint")
    if not cs or not ce or cs != ce:
        bad.append(f"gate 1 comma_7b: commit through the sweep loader ({cs}) != through the "
                   f"endpoint loader ({ce})")
    dg_s, dg_e = rec.get("digest_sweep"), rec.get("digest_endpoint")
    if not dg_s or not dg_e or dg_s != dg_e:
        bad.append(f"gate 1 comma_7b: tensor digest through the sweep loader ({dg_s}) != "
                   f"through the endpoint loader ({dg_e}) — the checkpoint loader path is "
                   f"not the production path")
    # FREEZE F-2 (2m's lineage): `digest_endpoint`/`commit_endpoint` are
    # attested by the runner from `stage1_final[rungs[0]]` — ONE rung's
    # record. Measure them against the digest and commit all 34 stage1_final
    # records carry, so a which assembled from two loads cannot pass gate 1
    # on the one record the runner happened to read.
    for field, att, label in (("weight_sha256", dg_e, "tensor digest"),
                              ("commit", ce, "commit")):
        vals = sorted({str(endpoint_records[r].get(field)) for r in rungs
                       if r in endpoint_records})
        if len(vals) > 1:
            bad.append(f"gate 1 comma_7b: the stage1_final endpoint records carry "
                       f"{len(vals)} different {label}s {vals} — they did not come from one load")
        elif vals and att is not None and vals[0] != str(att):
            bad.append(f"gate 1 comma_7b: attested {label} through the endpoint loader "
                       f"{att!r} is not the {label} every stage1_final record carries "
                       f"({vals[0]!r}) — the attestation was read from one rung")
    bd, cd, nc = rec.get("bit_diffs", {}), rec.get("continuation_diffs", {}), \
        rec.get("continuations_compared", {})
    for r in rungs:
        if r not in endpoint_records:
            bad.append(f"gate 1 comma_7b/{r}: no stage1_final endpoint record to compare against")
            continue
        if bd.get(r) != 0:
            bad.append(f"gate 1 comma_7b/{r}: {bd.get(r)} bit diffs between the sweep's "
                       f"step{ENDPOINT_STEP_2N} record and the endpoint's stage1_final record")
        if cd.get(r) != 0:
            bad.append(f"gate 1 comma_7b/{r}: {cd.get(r)} continuation diffs")
        if nc.get(r) != N_ITEMS:
            bad.append(f"gate 1 comma_7b/{r}: {nc.get(r)} continuation pairs compared, not the "
                       f"full {N_ITEMS} — a zero diff count over a truncated comparison is "
                       f"not evidence")
    if rec.get("prereg_tag") != PREREG_TAG_2N:
        bad.append(f"gate 1 comma_7b: prereg_tag {rec.get('prereg_tag')!r} is not "
                   f"{PREREG_TAG_2N!r}")
    return bad


def gate1_rederive_comma(sweep_endpoint_records: dict, stage1_final_records: dict,
                         gate_record: dict) -> list:
    """`battery_2m.gate1_rederive_3b`'s body on the 2n labels: bit and
    continuation diffs RE-DERIVED from the two committed record sets,
    required zero AND equal to the attestation, coverage 500 on both
    sides and in the attestation."""
    bad = []
    g = gate_record if isinstance(gate_record, dict) else {}
    bd_att, cd_att, nc_att = g.get("bit_diffs", {}), g.get("continuation_diffs", {}), \
        g.get("continuations_compared", {})
    # FREEZE F-2 (the sweep side): `digest_sweep`/`commit_sweep` are the
    # runner's attestation of its OWN load. Measure them against the
    # digest and commit all 34 sweep step-ENDPOINT records carry, so the
    # gate's two halves are both tied to committed bytes rather than to
    # each other.
    for field, att, label in (("weight_sha256", g.get("digest_sweep"), "tensor digest"),
                              ("commit", g.get("commit_sweep"), "commit")):
        vals = sorted({str(sweep_endpoint_records[r].get(field)) for r in bt.RUNGS
                       if r in sweep_endpoint_records})
        if len(vals) > 1:
            bad.append(f"gate 1 comma_7b re-derive: the sweep's step{ENDPOINT_STEP_2N} records "
                       f"carry {len(vals)} different {label}s {vals} — they did not come from one "
                       f"load")
        elif vals and att is not None and vals[0] != str(att):
            bad.append(f"gate 1 comma_7b re-derive: attested {label} through the sweep loader "
                       f"{att!r} is not the {label} every step{ENDPOINT_STEP_2N} record carries "
                       f"({vals[0]!r})")
    for r in bt.RUNGS:
        if r not in sweep_endpoint_records:
            bad.append(f"gate 1 comma_7b re-derive/{r}: no sweep step{ENDPOINT_STEP_2N} record "
                       f"to re-derive against")
            continue
        if r not in stage1_final_records:
            bad.append(f"gate 1 comma_7b re-derive/{r}: no stage1_final endpoint record to "
                       f"re-derive against")
            continue
        s_bits, e_bits = sweep_endpoint_records[r].get("bits"), stage1_final_records[r].get("bits")
        s_c, e_c = sweep_endpoint_records[r].get("continuations"), \
            stage1_final_records[r].get("continuations")
        if not isinstance(s_bits, list) or not isinstance(e_bits, list) or \
                len(s_bits) != N_ITEMS or len(e_bits) != N_ITEMS:
            bad.append(f"gate 1 comma_7b re-derive/{r}: sweep/endpoint bits are not both "
                       f"{N_ITEMS} long — coverage failure")
            continue
        if not isinstance(s_c, list) or not isinstance(e_c, list) or \
                len(s_c) != N_ITEMS or len(e_c) != N_ITEMS:
            bad.append(f"gate 1 comma_7b re-derive/{r}: sweep/endpoint continuations are not "
                       f"both {N_ITEMS} long — coverage failure")
            continue
        bit_diff = sum(1 for a, b in zip(s_bits, e_bits) if int(bool(a)) != int(bool(b)))
        cont_diff = sum(1 for a, b in zip(s_c, e_c) if a != b)
        if bit_diff != 0:
            bad.append(f"gate 1 comma_7b re-derive/{r}: {bit_diff} bit diff(s) between the "
                       f"sweep's step{ENDPOINT_STEP_2N} record and the stage1_final endpoint "
                       f"record (re-derived from the bytes, not the attestation)")
        if cont_diff != 0:
            bad.append(f"gate 1 comma_7b re-derive/{r}: {cont_diff} continuation diff(s) "
                       f"(re-derived from the bytes, not the attestation)")
        if bd_att.get(r) != bit_diff:
            bad.append(f"gate 1 comma_7b re-derive/{r}: attested bit_diffs {bd_att.get(r)!r} "
                       f"disagrees with the re-derived {bit_diff}")
        if cd_att.get(r) != cont_diff:
            bad.append(f"gate 1 comma_7b re-derive/{r}: attested continuation_diffs "
                       f"{cd_att.get(r)!r} disagrees with the re-derived {cont_diff}")
        if nc_att.get(r) != N_ITEMS:
            bad.append(f"gate 1 comma_7b re-derive/{r}: attested continuations_compared "
                       f"{nc_att.get(r)!r} is not the full {N_ITEMS} — a zero diff count over "
                       f"a truncated comparison is not evidence")
    return bad


# ------------------------------------------------------------------ pins

# Every frozen module 2n executes on the verdict path or in a stage tool:
# 2m's 48 (which carry 2l's, 2k's, 2j's, 2i's, 2g's, 2h's, 2d's, 2c's,
# exp3's) + 2m's four tag-bound blobs (2m is closed; frozen bytes to 2n)
# + 2n's own artifact writers. The four 2n blobs the prereg TAG binds are
# NOT here (2j's rule). `run/preflight_2n.py` and `verify_referents_2n.py`
# are pinned by `analyze_2n.IMPORTED_SHA256_2N` (a later task).
FROZEN_FILES_2N = tuple(bm.FROZEN_SHA256_2M) + tuple(REPO / rel for rel in bm.INSTRUMENT_BLOBS_2M) + (
    EXP2N / "power_2n.py",
    EXP2N / "make_referents_2n.py",
)
FROZEN_SHA256_2N = {
    REPO / "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    REPO / "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    REPO / "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    REPO / "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    REPO / "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    REPO / "experiments/exp2d/results/verdict.json":
        "d5b1b28bf70f4be1a5acf73df8ad03d8c57349ce4acf15e26f690c6dc1347b61",
    REPO / "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    REPO / "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    REPO / "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    REPO / "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    REPO / "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    REPO / "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    REPO / "experiments/exp2g/run/sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    REPO / "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    REPO / "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    REPO / "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    REPO / "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    REPO / "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    REPO / "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    REPO / "experiments/exp2i/make_referents_2i.py":
        "6de0278cfe85d9efefa11d0b2549afa78dd8836e1ef2b947d00c8709acc3977b",
    REPO / "experiments/exp2i/power_2i.py":
        "0e5e449ac420e40243ae86eb84e576256e857581ad3c7e000fcea5e08666119d",
    REPO / "experiments/exp2i/run/_common_2i.py":
        "5cc7c97f68b45656d6dbbb5fbf6d7d895d7b1d96e104df543f8c9f1691e5ad4f",
    REPO / "experiments/exp2i/run/endpoint_2i.py":
        "8c3718341b22fcdd99c799e45d43ac883f076c2d2080789aa323626c4d808cf2",
    REPO / "experiments/exp2i/run/sample_2i.py":
        "6cf3cdfac2f940f12c0365694758578a3655afbf74498f7c7c549ac221b55fe4",
    REPO / "experiments/exp2i/run/seal_2i.py":
        "f20132aed4c0b7e995745972abeddec4ba1d7a269147b5d034bff06a3157f078",
    REPO / "experiments/exp2j/analyze_2j.py":
        "976f1ff1f91affa2fc66d635e6b6d9a8aabfd21bdc7ccc38abfe87482ea09b13",
    REPO / "experiments/exp2j/functionals_2j.py":
        "39375f01de4b5bf06787175e25f7f85394844c005c3c4ea66f69954b1fe8bfce",
    REPO / "experiments/exp2j/make_referents_2j.py":
        "ac4064ccc0e2a210c6eee720578f2b4c31846cf00d76668070adac5e9ebe1678",
    REPO / "experiments/exp2j/power_2j.py":
        "19b80593d091663183b7394b101ee5f97c832b5f0dd7dc4227c9b1107721ab1a",
    REPO / "experiments/exp2k/analyze_2k.py":
        "27ea6f7b4dcf18894061363a7d7d64d2a63e867946797a5306a695c9d0e86f1a",
    REPO / "experiments/exp2k/battery_2k.py":
        "1066265d689573cc009c73df1b036a9453be7a807d79e153b53ccf52177eec0a",
    REPO / "experiments/exp2k/make_referents_2k.py":
        "6921feb194bd5971a74af1c25899146c70e5a9b402546be413321b3edee882d4",
    REPO / "experiments/exp2k/power_2k.py":
        "318ec4266513200e6a018285184cdae5c1fe5cc78400fe07671a9f45bc92ed4e",
    REPO / "experiments/exp2k/run/campaign_2k.py":
        "75f2b4c4f66d3d683d875e2a569bc2ec2b7c72fafa3ca1071c103d54df1337e5",
    REPO / "experiments/exp2k/run/seal_2k.py":
        "0cbdd982a55075e8c8567acb82d7264ce87c88320d2fa4568a5b419f7ca4b2fb",
    REPO / "experiments/exp2k/run/tier_2k.py":
        "4729ece9592b27c9aaa1183e8570dc787d4a945edafb82f036bc05b9bee50510",
    REPO / "experiments/exp2l/analyze_2l.py":
        "a76d26031abc73df0757c9fa20ac5b5254a06128d5fc6897c0cd5876106441b6",
    REPO / "experiments/exp2l/battery_2l.py":
        "c85726b9909dfe11dd6481b96e773ce27aa507d83ac05348e0125f79aae50b8b",
    REPO / "experiments/exp2l/make_referents_2l.py":
        "4b7e0b9660a4bf057af7976e7ca64d8f0a2396f8fce959d9f0285103ed5bacd7",
    REPO / "experiments/exp2l/power_2l.py":
        "99e4c8f978608db64ec0cf3ea00de98e4c43d4447d033ec836c45b82c198b5e9",
    REPO / "experiments/exp2l/run/endpoint_2l.py":
        "714c8db8b2ab99a7e04a0ff169e821015caa9cad2e2c47e198beccaf383ad6ad",
    REPO / "experiments/exp2l/run/sweep_2l.py":
        "d24babe784d465deea35c3ed06802bd2210a6dd471b01cb7d31b2d17ba1093bd",
    REPO / "experiments/exp2m/analyze_2m.py":
        "034c8a7359a275a2835c31e31fcb27b7d37ffb7144b53d49cfcc3e95ceab275e",
    REPO / "experiments/exp2m/battery_2m.py":
        "0c5e1f07f8881c537304b496240605b95027306962ec2e4f389b42843323bffd",
    REPO / "experiments/exp2m/make_referents_2m.py":
        "36340a89d3086e25b35377065e714803ccc33ff9821a696312a02d8a11e221c9",
    REPO / "experiments/exp2m/power_2m.py":
        "71ce8601bb633411d91ab595d6d5adbf979c16ed50ffddab4e7359a8ff31878f",
    REPO / "experiments/exp2m/run/endpoint_2m.py":
        "52bd2fe173e56007ccc6de407530a7ef79e7049237973536c6ac720d5d2bae91",
    REPO / "experiments/exp2m/run/sweep_2m.py":
        "30fa4b4f73cff09aac0200ee15269a8b6b61b75d85e56c660fbca91a0b72b636",
    REPO / "experiments/exp2n/make_referents_2n.py":
        "98eb723c9284aa47b2b9f0905cb9500a93ca168f36db0c738042f3bbccb4ba4a",   # re-pinned Task 5 Step 3 (N_FILES_2N set)
    REPO / "experiments/exp2n/power_2n.py":
        "9c7d71b0a4d1133358f2c1d198af308caf6abb904549c8f27738798c68e9f58f",
    REPO / "experiments/exp3/run/run_cell.py":
        "5c018457d9eb999079b4b0426dc0ecadf10baed6339d32b5eb914f280da35b46",
    REPO / "experiments/exp3/sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    REPO / "experiments/exp3c/analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    REPO / "experiments/exp3d/rederive_3d.py":
        "8421433ffe328e7e2ad8d2877150f9bfc0279c9337576fd5860e917dc8690870",
}   # pinned as a literal from frozen_from_disk() at Task 5 (54 modules)


def frozen_from_disk(*, strict: bool = True) -> dict:
    if strict:
        return {p: bg.sha256_file(p) for p in FROZEN_FILES_2N}
    return {p: bg.sha256_file(p) for p in FROZEN_FILES_2N if p.is_file()}


def check_frozen_2n() -> None:
    if not FROZEN_SHA256_2N:
        raise RuntimeError("FROZEN_SHA256_2N is empty — not pinned (build incomplete)")
    for p, want in FROZEN_SHA256_2N.items():
        got = bg.sha256_file(p)
        if got != want:
            raise RuntimeError(f"frozen module drifted: {p} ({got[:12]} != {want[:12]})")


def require_prereg_2n(*, tag_exists=None, blob_sha=None) -> dict:
    """2k's blob binding: the tag must exist and each instrument blob's
    bytes on disk must equal the blob the tag carries."""
    from experiments.exp2g import predictor_2g as pr
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_2N):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_2N} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_2N:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_2N, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_2N} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_2N, "instrument_blobs": bound}


if __name__ == "__main__":
    if "--scan" in sys.argv:
        inv = refresh_inventory_comma()
        print(REPO_COMMA, len(inv[REPO_COMMA]), "revisions")
        print("sha256", bg.sha256_file(HUB_INVENTORY_PATH))
    elif "--manifest" in sys.argv:
        inv = load_inventory_comma()
        manifest = build_manifest_comma(inv)
        write_manifest(CHECKPOINTS_PATH, manifest)
        e = entry_comma(manifest, ENDPOINT_STEP_2N)
        print("entries", len(manifest["entries_comma"]), "; endpoint commit", e["commit"],
              "; stage2_final commit", entry_stage2_comma(manifest)["commit"],
              "; main commit", entry_main_comma(manifest)["commit"],
              "; endpoint_duplicates", manifest["endpoint_duplicates"])
        print("sha256", bg.sha256_file(CHECKPOINTS_PATH))
    else:
        print("usage: python -m experiments.exp2n.battery_2n --scan | --manifest")
