# experiments/exp2i/battery_2i.py
"""The Exp 2i battery: the sampler confirmation carried cross-family,
Pythia-1b/6.9b's instrument re-run on OLMo-2 1B/7B (design
`experiment-2i-design.md` §3-§4). Everything not defined here is
imported frozen and re-asserted by sha256 (`FROZEN_SHA256`,
`check_frozen_2i()`): exp2h's 6.9b sampler-confirmation shape,
exp2g's strata/statistics/rung-set rule, exp2d's row format and
binomial bar, exp2c's harness, exp3's sampler contract, exp3c's total
verify wrapper.

Four deltas from that stack, all local to this module:

1. **A second model family.** `allenai/OLMo-2-0425-1B` (predictor) and
   `allenai/OLMo-2-1124-7B` (outcome) replace Pythia's repos. The Hub
   inventory (`hub_inventory_olmo.json`, `refresh_inventory`) is the
   ONE network call in this build — everything else reads that
   committed file. `checkpoints_2g.candidate`/`.signature` are reused
   directly (their shard-name regex matches OLMo's
   `model-0000N-of-00006.safetensors` naming without modification —
   confirmed against the real scan in Step 4), never copied or
   re-implemented.
2. **Two loader paths + a twin**, generalized from `battery_2h`'s
   single-size shape to take `repo` explicitly (2i spans two repos and
   22 sizes-of-one: the 7B grid's 21 trained points plus `main`, and
   the 1B's endpoint and `main`): `load_checkpoint` (the candidate-file
   clean-dir path, config pinned to the entry's OWN commit — unlike
   2h's one size-wide config pin, 2i has no single commit that covers
   every revision it loads), `load_thin` (plain `from_pretrained`
   through the ordinary HF cache — stage 2 and the preflight), and
   `load_twin_7b` (a seeded `from_config` referent: the 7B branch
   publishes no true step0).
3. **Tokenizer deltas** (design §3.1): OLMo-2 pads left with its own
   `<|pad|>` (id 100277, asserted) and adds no BOS (asserted on
   `tok("Q:")`). The pure assertions are factored into
   `check_tokenizer` so they are testable without a network call;
   `load_tokenizer` itself touches the Hub and is never executed by a
   test.
4. **The predictor readers.** `sampler_counts_pythia` re-exports
   `battery_2h.sampler_counts` unchanged (x_A, 2d's committed 1b/410m
   draws). `sampler_counts_olmo` is the same per-item verified-count
   body pointed at 2i's OWN sealed draws (x_B, `results/predictor/
   olmo1b/<rung>.draws.jsonl.gz`, `analyze_2d.read_rows`'s row format).
   The rung-set rule (`rung_set_from_counts`) is 2d's binomial bar
   applied to whatever count table it is handed, split against 2g's
   eleven-rung strata table (`strata_2g.COVARIATE_OF`) — pure, and the
   one piece of §4 logic genuinely new to this module (2h reused
   `battery_2g.rising_by_bar` for a single known rung set; 2i's R_OLMO
   is not known until the 7B endpoint stage runs, so the rule itself,
   not just its inputs, has to live here).

Zero model contact, zero network beyond the one committed scan: the
loader family (`download_entry`/`clean_dir`/`load_checkpoint`/
`load_thin`/`load_twin_7b`/`load_tokenizer`/`free_checkpoint`) imports
`huggingface_hub`/`torch`/`transformers` lazily inside each function
body, never at module import, and nothing here calls them."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

EXP2I = Path(__file__).resolve().parent
EXPERIMENTS = EXP2I.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import strata_2g  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402

EXP2H = EXPERIMENTS / "exp2h"
EXP2G = EXPERIMENTS / "exp2g"
EXP2D = EXPERIMENTS / "exp2d"
EXP2C = EXPERIMENTS / "exp2c"
EXP3 = EXPERIMENTS / "exp3"
EXP3C = EXPERIMENTS / "exp3c"

RESULTS = EXP2I / "results"
HUB_INVENTORY_PATH = EXP2I / "hub_inventory_olmo.json"
CHECKPOINTS_PATH = EXP2I / "checkpoints_2i.json"

# checkpoints_2i.json's sha256 (Task 1's committed manifest, written by
# `--manifest` from the committed inventory) — Task 3 imports this same
# literal from here rather than re-deriving it, per ruling 2.
CHECKPOINTS_2I_SHA256 = \
    "029b1cca0529bba6da629229d8fd352c6f118d3eba7d82b4526170c65822325a"

FAMILY = "olmo2"
SIZE_PRED = "olmo1b"
SIZE_OUT = "olmo7b"
REPO_1B = "allenai/OLMo-2-0425-1B"
REPO_7B = "allenai/OLMo-2-1124-7B"
REV_1B_ENDPOINT = "stage1-step1907359-tokens4001B"
REV_1B_MAIN = "main"
REV_7B_ENDPOINT = "stage1-step928646-tokens3896B"
REV_7B_MAIN = "main"
TWIN = "twin"
TWIN_SEED = 0
ENDPOINT_STEP_7B = 928646

# design §3.4 / Global Constraints: 21 trained points, endpoint last —
# log-spaced head, every 64k from 64k to 896k, the endpoint.
GRID_7B = (1000, 2000, 4000, 8000, 16000, 32000,
           64000, 128000, 192000, 256000, 320000, 384000, 448000,
           512000, 576000, 640000, 704000, 768000, 832000, 896000,
           928646)

PREREG_TAG = "exp2i-preregistered"
PREDICTOR_SEAL_TAG = "exp2i-predictor-sealed"
ENDPOINT_SEAL_TAG = "exp2i-endpoint-sealed"

N_ITEMS = bt.N_ITEMS
DRAWS_PER_ITEM = 64
SAMPLING_SEED = 0
STRATA_RUNGS = tuple(strata_2g.COVARIATE_OF)         # 2g's eleven

_STAGE1_RE = re.compile(r"^stage1-step(\d+)-tokens\d+B$")


def trained_steps_7b() -> tuple:
    """The 7B stage-1 branch has no step0 — every grid point is
    trained; the twin (§3.1) stands in for the step-0 referent
    separately, never on this tuple."""
    return tuple(GRID_7B)


def n_trained_7b() -> int:
    return len(trained_steps_7b())


def revision_of_7b(step) -> str:
    """The exact branch name for a 7B grid step, read from the
    committed manifest — the token-count suffix
    (`stage1-step{N}-tokens{M}B`) is data, never computed. Raises on a
    step off `GRID_7B` before touching any file."""
    step_i = int(step)
    if step_i not in GRID_7B:
        raise ValueError(f"step {step_i} is not on GRID_7B")
    manifest = load_manifest(CHECKPOINTS_PATH, sha_pin=CHECKPOINTS_2I_SHA256)
    return manifest["entries_7b"][str(step_i)]["revision"]


# ------------------------------------------------------------ inventory

def _retry(fn, *args, tries: int = 3, sleep: float = 5.0, **kwargs):
    """A small retry for transient Hub HTTP errors (5xx, timeouts) —
    ~1,000 metadata calls make one flaky response likely; this must
    not lose 20 minutes to it."""
    last = None
    for i in range(tries):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 — deliberately broad, retried
            last = exc
            if i < tries - 1:
                time.sleep(sleep)
    raise last


def load_inventory(path=HUB_INVENTORY_PATH) -> dict:
    inv = json.loads(Path(path).read_text())
    for repo in (REPO_1B, REPO_7B):
        if repo not in inv or "main" not in inv[repo]:
            raise ValueError(f"inventory lacks {repo}/main")
    return inv


def refresh_inventory(out_path=HUB_INVENTORY_PATH) -> dict:
    """NETWORK (metadata only) — the ONE Hub scan of the whole build.
    `REPO_7B`: every branch (the 928 stage-1 + stage-2 ingredient +
    main). `REPO_1B`: the endpoint, `main`, and `stage1-step0-tokens0B`
    only. Refuses if `out_path` already exists — this call runs ONCE,
    ever, and every later step reads the committed file it wrote."""
    p = Path(out_path)
    if p.exists():
        raise FileExistsError(
            f"{p} already exists — refresh_inventory is the ONE scan of "
            f"this build and refuses to overwrite a committed inventory")
    from huggingface_hub import HfApi
    api = HfApi()

    def _info(repo: str, rev: str) -> dict:
        info = _retry(api.model_info, repo, revision=rev, files_metadata=True)
        files = {s.rfilename: [s.lfs.sha256, s.size] for s in info.siblings if s.lfs}
        return {"commit": info.sha, "files": files}

    refs = _retry(api.list_repo_refs, REPO_7B)
    revs_7b = sorted({b.name for b in refs.branches} | {"main"})
    table_7b = {rev: _info(REPO_7B, rev) for rev in revs_7b}

    revs_1b = (REV_1B_ENDPOINT, REV_1B_MAIN, "stage1-step0-tokens0B")
    table_1b = {rev: _info(REPO_1B, rev) for rev in revs_1b}

    out = {REPO_7B: table_7b, REPO_1B: table_1b}
    Path(out_path).write_text(json.dumps(out, indent=1, sort_keys=True))
    return out


# ------------------------------------------------------------- manifest

def _weight_entry(repo: str, rev: str, table: dict, cands: dict) -> dict:
    c = cands.get(rev)
    if c is None:
        raise ValueError(f"{repo}/{rev}: no candidate weight file")
    files = table[rev]["files"]
    return {
        "revision": rev, "commit": table[rev]["commit"], "kind": c["kind"],
        "files": list(c["files"]),
        "lfs_sha256": {n: files[n][0] for n in c["lfs"]},
        "lfs_size": {n: int(files[n][1]) for n in c["lfs"]},
    }


def build_manifest(inv: dict) -> dict:
    """Mirrors `checkpoints_2g.build_manifest`'s body for the 7B grid,
    using `ck.candidate`/`ck.signature` directly (their shard-name
    regex accepts OLMo's `model-0000N-of-00006.safetensors` naming
    unmodified). The duplicate-signature refusal runs across ALL
    scanned 7B revisions, as 2g — not just the 21 grid points."""
    table_7b, table_1b = inv[REPO_7B], inv[REPO_1B]
    main_files_7b = table_7b[REV_7B_MAIN]["files"]
    main_files_1b = table_1b[REV_1B_MAIN]["files"]

    cands_7b = {rev: ck.candidate(rev, t["files"], main_files_7b)
                for rev, t in table_7b.items()}
    sigs_7b = {rev: (ck.signature(table_7b[rev]["files"], c) if c else None)
               for rev, c in cands_7b.items()}

    def dups_of_7b(rev: str) -> list:
        return sorted(r for r, s in sigs_7b.items()
                      if r != rev and s is not None and s == sigs_7b[rev])

    entries_7b = {}
    for step in trained_steps_7b():
        matches = [r for r in table_7b if _STAGE1_RE.fullmatch(r)
                   and int(_STAGE1_RE.fullmatch(r).group(1)) == step]
        if len(matches) != 1:
            raise ValueError(
                f"{REPO_7B}: step {step} matches {matches} in the inventory "
                f"— exactly one stage1 branch is expected")
        rev = matches[0]
        entry = _weight_entry(REPO_7B, rev, table_7b, cands_7b)
        same = dups_of_7b(rev)
        if step != ENDPOINT_STEP_7B and same:
            raise ValueError(f"{REPO_7B}/{rev}: candidate files duplicate "
                             f"{same} — not a trustworthy grid point")
        entries_7b[str(step)] = entry

    endpoint_entry = entries_7b[str(ENDPOINT_STEP_7B)]
    if endpoint_entry["revision"] != REV_7B_ENDPOINT:
        raise ValueError(
            f"{REPO_7B}: endpoint revision {endpoint_entry['revision']!r} is "
            f"not the pinned {REV_7B_ENDPOINT!r}")

    entries_7b[TWIN] = {"revision": TWIN, "commit": None, "files": [],
                        "kind": "from_config", "seed": TWIN_SEED,
                        "config_commit": endpoint_entry["commit"]}

    main_entry_7b = _weight_entry(REPO_7B, REV_7B_MAIN, table_7b, cands_7b)
    sig_equal_main = bool(sigs_7b.get(REV_7B_ENDPOINT) is not None
                          and sigs_7b[REV_7B_ENDPOINT] == sigs_7b.get(REV_7B_MAIN))
    final_duplicates = dups_of_7b(REV_7B_ENDPOINT)

    cands_1b = {rev: ck.candidate(rev, t["files"], main_files_1b)
                for rev, t in table_1b.items()}
    entry_1b_endpoint_obj = _weight_entry(REPO_1B, REV_1B_ENDPOINT, table_1b, cands_1b)
    main_entry_1b = _weight_entry(REPO_1B, REV_1B_MAIN, table_1b, cands_1b)

    return {
        "repo_1b": REPO_1B, "repo_7b": REPO_7B,
        "grid_7b": list(GRID_7B), "trained_steps_7b": list(trained_steps_7b()),
        "entries_7b": entries_7b,
        "entry_1b_endpoint": entry_1b_endpoint_obj,
        "main": {REPO_1B: main_entry_1b, REPO_7B: main_entry_7b},
        "final_duplicates": final_duplicates,
        "signature_equals_main": sig_equal_main,
        "n_revisions": {REPO_1B: len(table_1b), REPO_7B: len(table_7b)},
    }


def write_manifest(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest(path=CHECKPOINTS_PATH, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    if obj.get("grid_7b") != list(GRID_7B):
        raise ValueError(f"{path}: manifest is not the frozen 7B grid")
    return obj


def entry_7b(manifest: dict, step) -> dict:
    key = TWIN if step == TWIN else str(int(step))
    e = manifest.get("entries_7b", {}).get(key)
    if e is None:
        raise ValueError(f"7B step {step!r} is not a grid entry")
    return e


def entry_1b_endpoint(manifest: dict) -> dict:
    e = manifest.get("entry_1b_endpoint")
    if e is None:
        raise ValueError("manifest lacks entry_1b_endpoint")
    return e


def entry_main(manifest: dict, repo: str) -> dict:
    e = manifest.get("main", {}).get(repo)
    if e is None:
        raise ValueError(f"manifest lacks a main entry for {repo!r}")
    return e


# ---------------------------------------------------- loader (stage 2)

CKPT_CACHE = Path.home() / "emergence-lab" / "ckpt_cache_2i"
_SIZE_OF_REPO = {REPO_1B: SIZE_PRED, REPO_7B: SIZE_OUT}


def _short(repo: str) -> str:
    if repo not in _SIZE_OF_REPO:
        raise ValueError(f"{repo!r} is not an exp2i repo")
    return _SIZE_OF_REPO[repo]


def _cache_dir(repo: str, key, cache_root) -> Path:
    return Path(cache_root) / _short(repo) / str(key)


def download_entry(repo: str, entry: dict, cache_root=CKPT_CACHE) -> dict:
    """MODEL CONTACT (weight bytes). Never executed by a test."""
    from huggingface_hub import hf_hub_download
    rev_dir = _cache_dir(repo, entry["revision"], cache_root)
    paths = {}
    for name in entry["files"]:
        p = hf_hub_download(repo, name, revision=entry["commit"],
                            cache_dir=str(rev_dir))
        paths[name] = Path(p).resolve()
    return paths


def verify_downloads(entry: dict, paths: dict) -> dict:
    shas = {}
    for name, p in paths.items():
        got = bg.sha256_file(p)
        want = entry["lfs_sha256"].get(name)
        if want is not None and got != want:
            raise ValueError(f"{name}: downloaded sha256 {got} against the "
                             f"manifest's {want} — not the pinned weights")
        shas[name] = got
    return shas


def clean_dir(repo: str, rev_key, cache_root, paths: dict) -> Path:
    """A fresh directory holding only the candidate files, hardlinked
    (falling back to a copy across filesystems) — no stray Hub file
    can leak into what `from_pretrained` loads. `rev_key` is the
    caller's own label for the revision (an int step, `TWIN`, or a
    repo's `main`), independent of `download_entry`'s own Hub-derived
    cache path, so a sweep can key its clean dirs by grid step while
    the raw HF cache is keyed by branch name."""
    d = _cache_dir(repo, rev_key, cache_root) / "clean"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for name, src in paths.items():
        dst = d / name
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    return d


_LOADING_INFO_FIELDS = ("missing_keys", "unexpected_keys", "mismatched_keys")


def _check_loading_info(li: dict, label: str) -> dict:
    """The shared shape check both loader paths apply to
    `output_loading_info`: every field must be empty, or the load did
    not fill the pinned architecture exactly. Raises `ValueError`
    naming `label` (the caller's own repo/revision description) with
    the offending fields; returns the per-field counts either way, for
    the caller's own `info` record. Pure — no torch, no network,
    tested directly on a stub dict."""
    bad = {k: list(li.get(k, [])) for k in _LOADING_INFO_FIELDS if li.get(k)}
    if bad:
        raise ValueError(f"{label}: the load does not fill the pinned "
                         f"architecture exactly: {bad}")
    return {k: len(li.get(k, [])) for k in _LOADING_INFO_FIELDS}


def load_checkpoint(repo: str, entry: dict, *, cache_root=CKPT_CACHE,
                    device: str = "mps", dtype="float16"):
    """MODEL CONTACT. The candidate files only, hashed, into a config
    pinned to the ENTRY'S OWN commit — 2h's `load_checkpoint_69` shape,
    generalized: 2h had one commit for the whole size (2c's pin); 2i
    has no single commit that covers the 7B grid's 21 revisions plus
    `main` plus the 1B endpoint, so the config is fetched fresh per
    entry rather than written once by `clean_dir`. `dtype` is fp16 for
    the 7B sweep (2c/2g/2h convention). `low_cpu_mem_usage=True`;
    loading info must be empty (`_check_loading_info`); tensor digest
    via `ck.tensor_digest` (reused, not redefined). Never executed by
    a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    paths = download_entry(repo, entry, cache_root)
    shas = verify_downloads(entry, paths)
    d = clean_dir(repo, entry["revision"], cache_root, paths)
    config = AutoConfig.from_pretrained(repo, revision=entry["commit"])
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(
        str(d), config=config, dtype=dt, low_cpu_mem_usage=True,
        output_loading_info=True)
    counts = _check_loading_info(li, f"{repo}@{entry['revision']} (candidate files)")
    model = model.to(device).eval()
    info = {"repo": repo, "revision": entry["revision"], "commit": entry["commit"],
            "kind": entry["kind"], "files": list(entry["files"]), "sha256": shas,
            "config_source": f"{repo}@{entry['commit']}",
            "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    return model, info


def load_thin(repo: str, revision_commit: str, *, device: str = "mps",
             dtype="float16"):
    """The second loader path (§3): plain `from_pretrained` through
    the ordinary HF cache, no candidate-file selection — `main`'s
    descriptive reading and the preflight use it. Never executed by a
    test."""
    import torch
    from transformers import AutoModelForCausalLM
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(
        repo, revision=revision_commit, dtype=dt, output_loading_info=True)
    counts = _check_loading_info(li, f"{repo}@{revision_commit} (thin load)")
    model = model.to(device).eval()
    tok = load_tokenizer(repo, revision_commit)
    info = {"repo": repo, "commit": revision_commit,
            "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    return model, tok, info


def load_twin_7b(*, device: str = "mps", dtype="float16", seed: int = TWIN_SEED):
    """The step-0 referent (§3.1): the 7B branch publishes no true
    step0, so a seeded `from_config` twin stands in — the 7B config
    pinned at `REV_7B_ENDPOINT`'s commit, `torch.manual_seed(seed)`
    immediately before construction. Descriptive only, never in an
    outcome. Never executed by a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    config = AutoConfig.from_pretrained(REPO_7B, revision=REV_7B_ENDPOINT)
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    torch.manual_seed(int(seed))
    model = AutoModelForCausalLM.from_config(config, dtype=dt)
    model = model.to(device).eval()
    info = {"repo": REPO_7B, "revision": TWIN, "seed": int(seed),
            "config_source": f"{REPO_7B}@{REV_7B_ENDPOINT}",
            "tensor_digest": ck.tensor_digest(model)}
    return model, info


PAD_TOKEN_ID = 100277   # OLMo-2's own <|pad|> (facts, 2026-08-25 scan)


def check_tokenizer(tok_like) -> None:
    """The pure assertions `load_tokenizer` applies (design §3.1):
    left padding, OLMo-2's own pad id, no BOS prefix on a plain
    render. Raises `RuntimeError` naming the offending field — factored
    out of `load_tokenizer` so it is testable on a stub, with no
    network call."""
    side = getattr(tok_like, "padding_side", None)
    if side != "left":
        raise RuntimeError(f"padding_side is {side!r}, not 'left'")
    pad_id = getattr(tok_like, "pad_token_id", None)
    if pad_id != PAD_TOKEN_ID:
        raise RuntimeError(f"pad_token_id is {pad_id!r}, not {PAD_TOKEN_ID} "
                           f"— OLMo-2's own <|pad|>")
    first_id = tok_like("Q:")["input_ids"][0]
    specials = set(tok_like.all_special_ids)
    if first_id in specials:
        raise RuntimeError(f"a special id {first_id} is prepended to 'Q:' — "
                           f"OLMo-2 adds no BOS")


def load_tokenizer(repo: str, commit: str):
    """MODEL-ADJACENT NETWORK (tokenizer files). Left padding, then
    `check_tokenizer`'s assertions. Never executed by a test."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, revision=commit)
    tok.padding_side = "left"
    check_tokenizer(tok)
    return tok


def free_checkpoint(repo: str, rev_key, cache_root=CKPT_CACHE) -> None:
    d = _cache_dir(repo, rev_key, cache_root)
    if d.exists():
        shutil.rmtree(d)


# ------------------------------------------------------- predictor readers

# x_A, re-exported (not copied, not wrapped): `battery_2h.sampler_counts`,
# 2d's committed main-tier draws at `size` ("1b" or "410m").
sampler_counts_pythia = bh.sampler_counts


def predictor_draws_path(root, rung: str) -> Path:
    return Path(root) / "results" / "predictor" / SIZE_PRED / f"{rung}.draws.jsonl.gz"


def predictor_record_path(root, rung: str) -> Path:
    return Path(root) / "results" / "predictor" / SIZE_PRED / f"{rung}.json"


def sampler_counts_olmo(rungs, *, root=EXP2I, battery, verify_fn) -> dict:
    """x_B: the same per-item verified-count body as
    `battery_2h.sampler_counts`, pointed at 2i's own sealed draws
    (`predictor_draws_path`) in `analyze_2d.read_rows`'s row format.
    `n_items`/`dps` are threaded from this module's own `N_ITEMS`/
    `DRAWS_PER_ITEM` at call time (not `analyze_2d`'s defaults), so a
    test can shrink them for a small fixture. Refuses a missing draws
    file with `FileNotFoundError` carrying the path."""
    from experiments.exp2d import analyze_2d as a2d
    out = {}
    for rung in rungs:
        path = predictor_draws_path(root, rung)
        if not Path(path).is_file():
            raise FileNotFoundError(str(path))
        cap = battery[rung]
        rows = a2d.read_rows(path, seed=SAMPLING_SEED, dps=DRAWS_PER_ITEM,
                             n_items=N_ITEMS)
        counts = [0] * N_ITEMS
        for row in rows:
            ans = cap["eval_items"][row["item"]]["answer"]
            counts[row["item"]] = sum(
                1 for d in row["draws"][str(SAMPLING_SEED)]
                if verify_fn(d, ans, cap["answer_type"]))
        out[rung] = counts
    return out


# ----------------------------------------------------------- rung-set rule

def rung_set_from_counts(counts: dict, floors: dict) -> dict:
    """§4: R_OLMO is whichever rungs in `counts` clear `floors`' bar
    (2d's one-sided exact binomial, `stats_2d.binomial_bar`, at N_ITEMS
    evaluations); R_CAP is R_OLMO's intersection with 2g's eleven
    strata rungs (`STRATA_RUNGS`); R_EXTRA is the rest — printed as a
    raw-D descriptive, never in the verdict. Pure: no file, no
    network."""
    from experiments.exp2d import stats_2d as st
    per_rung = {r: st.binomial_bar(int(k), N_ITEMS, float(floors[r]))
                for r, k in counts.items()}
    r_olmo = tuple(r for r in sorted(counts) if per_rung[r]["significant"])
    r_cap = tuple(r for r in r_olmo if r in STRATA_RUNGS)
    r_extra = tuple(r for r in r_olmo if r not in STRATA_RUNGS)
    return {"R_OLMO": list(r_olmo), "R_CAP": list(r_cap),
            "R_EXTRA": list(r_extra), "per_rung": per_rung}


# ----------------------------------------------------------------- paths

def sweep_dir(root) -> Path:
    return Path(root) / "results" / "sweep" / SIZE_OUT


def record_path(root, step, rung: str) -> Path:
    key = TWIN if step == TWIN else f"step{int(step)}"
    return sweep_dir(root) / key / f"{rung}.json"


def checkpoint_record_path(root, step) -> Path:
    key = TWIN if step == TWIN else f"step{int(step)}"
    return sweep_dir(root) / key / "_checkpoint.json"


def gate1_path(root) -> Path:
    return sweep_dir(root) / "gate1.json"


def halt_marker_path(root) -> Path:
    return sweep_dir(root) / "HALTED"


def endpoint_dir(root) -> Path:
    return Path(root) / "results" / "endpoint"


_ENDPOINT_WHICH = ("stage1_final", "main")


def endpoint_record_path(root, which: str, rung: str) -> Path:
    if which not in _ENDPOINT_WHICH:
        raise ValueError(f"{which!r} is not one of {_ENDPOINT_WHICH}")
    return endpoint_dir(root) / which / f"{rung}.json"


def rung_set_path(root) -> Path:
    return endpoint_dir(root) / "rung_set_2i.json"


def predictor_seal_path(root) -> Path:
    return Path(root) / "results" / "predictor" / "predictor_2i.json"


def power_path(root) -> Path:
    return endpoint_dir(root) / "power_2i.json"


# ------------------------------------------------------- frozen imports

# Every frozen module 2i imports or whose logic it mirrors, plus the one
# frozen DATA file (2d's committed floor verdict, §4's bar). The
# battery/verify modules `bt` (battery_2d) itself resolves dynamically
# (`harness`, `experiments.exp2c.battery.family_map`) are pinned here
# too — I-1's lesson (2h): pins must be ASSERTED on every surface that
# touches this code, not merely listed once upstream.
FROZEN_SHA256 = {
    EXP2H / "battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    EXP2H / "analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    EXP2G / "battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    EXP2G / "stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    EXP2G / "strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    EXP2G / "labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    EXP2G / "analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    EXP2G / "checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    EXP2D / "battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    EXP2D / "analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    EXP2D / "stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    EXP2D / "results" / "verdict.json":
        "d5b1b28bf70f4be1a5acf73df8ad03d8c57349ce4acf15e26f690c6dc1347b61",
    EXP2C / "harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    EXP2C / "battery" / "family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    EXP3 / "sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    EXP3C / "analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    # whole-branch review fix wave (I-2): four instrument modules that
    # were imported/mirrored but never pinned. The last two are 2i's
    # OWN files — a self-pin of a non-tag-bound module is fine (ruling,
    # review): a post-tag edit to either refuses everywhere
    # `check_frozen_2i` runs, exactly like any other frozen module.
    EXP2G / "predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    EXP2G / "run" / "sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    EXP2I / "run" / "_common_2i.py":
        "5cc7c97f68b45656d6dbbb5fbf6d7d895d7b1d96e104df543f8c9f1691e5ad4f",
    EXP2I / "make_referents_2i.py":
        "c296f9912e1135dc9a79e0a13659e1316d5457aaa0094a0ea7912aa6f75c0760",
}


def check_frozen_2i() -> None:
    for path, want in FROZEN_SHA256.items():
        got = bg.sha256_file(path)
        if got != want:
            raise ValueError(f"frozen file {path} has sha256 {got}, expected "
                             f"{want} — exp2h/exp2g/exp2d/exp2c/exp3/exp3c are "
                             f"closed and their code is 2i's instrument")


# 2d's committed main-tier draws files (1b, 410m; 34 rungs each) —
# x_A's real input, sha-pinned so a stale or drifted committed draws
# file fails loudly rather than silently changing the predictor.
PYTHIA_PREDICTOR_FILES = {
    ("1b", "add3_mid"): "8968bce191eaecbf6c7b69112f7246517b61b97242b9df53a75d87962c319150",
    ("1b", "add4_mid"): "74703d01c5872857cdf91c4dfa0c880cd9a54b06507dd9608618c27586366d40",
    ("1b", "add_base8"): "d59499f40c0e2953222ae4d4ab30972264a207feb78d346142ce5e29666f4b02",
    ("1b", "antonym"): "983a56cc09c653b291483c47ac74199dddfc7ede8c30237e1b7dc2565c1f0052",
    ("1b", "antonym6"): "1423f7b44bffed2f017ed73e24515ab083961b7afe7479d346b9feb7187c701a",
    ("1b", "arith_next"): "2a528aa15aba477cef3b41791582c8a19b4cc0a6c56b1c12ad016bc3a126095d",
    ("1b", "base12_digitsum"): "b8f78ed7f6a9f69da366e4c2d92494643ef733f4d9865ef47e35bd5aa2aebf26",
    ("1b", "base13"): "5d9af297faff94bdc177aba734c56150117a5d31f8559ec6482a1ebfbff7e87e",
    ("1b", "base7"): "72c587b422324b91c8a5c10821eee8173659acc0fede658218c0af3258411b6b",
    ("1b", "caesar"): "e4e78cbd9c594277139f90a04c1069e8a246c91d57ca94d7fea7ab9da62af04b",
    ("1b", "caesar_len8"): "40ef2135f3dd4c6ba9f8c2368576258dab7c272911e21a5eb1346fdf4c6fa34f",
    ("1b", "clock24"): "617d7a0388c21caf8e960c26fb6745ecfd457bf1cb768bdb07a4d5fccb1f87db",
    ("1b", "clock24_d999"): "6551aef74722b8ddd277163468d64ac9dbfaa77781845bd136bb4156d9126251",
    ("1b", "collatz_step2"): "fdeae4be17049004a7634c0050907297e6bfc789d5f0060797632e307ef577e3",
    ("1b", "count_div13"): "bd792ac4de209efcefb0aada85402b796e20883f7b75fc925642fb86a73ddc7a",
    ("1b", "count_div7"): "61338d376ccb0fc1e31a78847f483f0eebf0b3abbf4f11a588122593380aebb6",
    ("1b", "hamming12"): "97782d19fa324a8886aef24b11fce71ff9a1bd5aa64a885144617deb1e3479b1",
    ("1b", "isqrt_gap"): "54162d09d2743699f2b7801a82eaf3817ee8e76e8ee5a52f523d17d01cac1a55",
    ("1b", "median5"): "fc624384ced8f5d12ec8730fee8addb7dd729ab416eb9651b57bbc7b6e20ae63",
    ("1b", "median7"): "83dc934558ac219334175032433fb77292bd4a27777a7ccefccf4590cbd5c4ba",
    ("1b", "mod13"): "48a8f81ecbeb6b8746b5ae6673d7856d1531400850d681c78d10c465e29dfae1",
    ("1b", "mod13_comp"): "fe356ec539aff19c325e6b4ae737711c983f33bd05705b1aa71defe741c41791",
    ("1b", "mod17"): "f5c121406905c8d734c0552409fb4ae6bcb3f0bdbb62be05d59a58e73902b6c9",
    ("1b", "mod19"): "e893f575e6ecc2c086e885ddf4757a00c465f86239fc414561016751fc95191f",
    ("1b", "oct2dec"): "c84e99844750d8028580f0574a96bf6e46869ea44c366f7af67aab9c84dfef86",
    ("1b", "odd6"): "d737fea80951516a872f21b6008a613662e98695222d1687df5a014937dfc21c",
    ("1b", "odd_one_out"): "ff45542516d96ee53f9ca58f5325b5ff2f0c0c94bfea6e8141a49275c6edd301",
    ("1b", "quad_next"): "e2be9b13f5e4b3f58e3c48b631cfbd5d0121759b624723180358704a78900c7c",
    ("1b", "rev_string7"): "977672e4493c8c7105871b116136f03c31dcdf974100d36f7cc11220fbf39635",
    ("1b", "reverse_string"): "ba907c2c7d773cc8689d7ba5c8c138588546278cc2679bd583bd6e91217b0a99",
    ("1b", "roman_sum7"): "2ffafc011088ad5795b801b9ffc6ac60df414ad5ac3b5476cd6e78bda473b85c",
    ("1b", "sub3_mid"): "1d6e0d989a94ace41e55fc57a82bbe338b740d39137246378c5419d5d8948914",
    ("1b", "sub4_mid"): "d45b0c09bd832b6cde00d8937f46c27bbb4c7381f48b47e3d3591dd26a26801b",
    ("1b", "sub_base8"): "4eb6ff0a626ca2b045d45dcfbb0f34b60d9e39a3e2163a904a106ee80b9052e2",
    ("410m", "add3_mid"): "7d50ff235cc6a2d84b1d7152b9062ef1f78e1366f8a35e5c5d4e09213527b620",
    ("410m", "add4_mid"): "6bdba6a7b51265d36d15bb4259b18f493e7b18a641115875ca3951023ace79c7",
    ("410m", "add_base8"): "afad3a5871c29f1ba60af5a272afc7bb6c9c57bcef691b16222e73cbf56df062",
    ("410m", "antonym"): "7480c22572f3ce96941da32e0f5ff1e35b7f3cc9b988cd07e88a1b013edcf8d6",
    ("410m", "antonym6"): "c29696d7d9a4da8bb7c3e9a7867757511059475504da7c22f2a741b1a64c4fa5",
    ("410m", "arith_next"): "6398288f5a0a501bde0545d9d7254fc2a4c129fdb809d8ecf6b3c8bc40d76e0a",
    ("410m", "base12_digitsum"): "af65ef9115142ffc65bff376dddc92e16de5d5888d095a946f69e300d28c606a",
    ("410m", "base13"): "45fa0536d5a2246ac43c2849fc178f5fc7f189ebc03af26912507328a7cdb18f",
    ("410m", "base7"): "113fefd21f44b569ed895911adc0b62ea1ac5c83003252ca8804cc3eef9f2e95",
    ("410m", "caesar"): "dd533acd7d30576e1b53c1222fff0b9b4882c39dcddda0ec2ab299920cda1c78",
    ("410m", "caesar_len8"): "ae6c2978bef03111d9501e97af365c0824cc34a21ff21691091cd1af510ea782",
    ("410m", "clock24"): "eb26a7758f9356bc3ac092554fe1d861c8a58f812c028ff37724814c26337c1b",
    ("410m", "clock24_d999"): "ad7fe6defa822bc7bb8b1725dd523793906e578f762d5feb9e44d7f5c18342f6",
    ("410m", "collatz_step2"): "06854fcfe19fc96d2352aadbe001156aad4f81d60623ce3be820f7fb7f02082a",
    ("410m", "count_div13"): "c4dc02e10e1c400d1ddc4071f251761477e33b658a238a8b6e163ebff94d18bd",
    ("410m", "count_div7"): "03116e3b825126e388d87e7fb3e2f08a4410bc2aa20a6e0d8549ab8576bae765",
    ("410m", "hamming12"): "18ea699fc95923df35ca95b128baf2703b8a18ddcc10e2223679460f21e24cd6",
    ("410m", "isqrt_gap"): "eff7d08e7babfeac0c609edbad9a63076f4596c227e8220b380f95b47913692e",
    ("410m", "median5"): "b182881bdb5920829c09629d73dda18907716d7b82cdbcacbe300125d2850ce1",
    ("410m", "median7"): "684a7a8deb8ad75dc97087e1304ddaf17adfffe8bff2cf0abf68098eb90e1e58",
    ("410m", "mod13"): "fe033773db4df4cf6d954bc01ba6ec7ac5b71b28005db18182fccffa35380812",
    ("410m", "mod13_comp"): "ffa48feb258111f7fed4b5059f56e320394d6cac94420230df4bc90874ab4a6f",
    ("410m", "mod17"): "b0a31c315a78c69ced9a856a84678b49c36d5e58d55ad12f0082a17c4cfc3ca8",
    ("410m", "mod19"): "fa5f8b407213e2edcffc013c2c747e233d7232d3f815b1c55a41b79e07dce560",
    ("410m", "oct2dec"): "76b88e800f7632b6d69b1553535603c50925495393f18448f173668146a1fbea",
    ("410m", "odd6"): "a0fd57f45aa5d3c0c5f747c913437c9374206aeeb8a6d840e3e1b90c266304a0",
    ("410m", "odd_one_out"): "79ad32a1e1bbbb446cd2addd76aaa035290adee9daf932409067b477823bbc6f",
    ("410m", "quad_next"): "f71b90a4afa14648e4c61122a542e5802614d4529a54a6d7333a9723235aea67",
    ("410m", "rev_string7"): "5b703296907f075b2219cfd799e7d43e9d97e437e900d94f9a963fa1057956d6",
    ("410m", "reverse_string"): "e9a23fc7e850ff738f7d15cd47c19159cc0b6cc087123f4f47c239f51d4ed2cb",
    ("410m", "roman_sum7"): "2eb1b8d5ff7ffb835760d079a1a570d00acd4d8ad292a6b1a1bc7cd3f2dd1f9d",
    ("410m", "sub3_mid"): "444d48f380efb148ec45af8f97236808013b92f067c234ba20fe7727b7c2e85e",
    ("410m", "sub4_mid"): "6ae4a2862b9b3ff94db73932f7d498263226827a7ba5a58c1ba64e237a00ecf2",
    ("410m", "sub_base8"): "9423aef5fb2357494500328b354f64bda331ef1b5d43bab4e187c496328ac0f2",
}


# --------------------------------------------------------- blob binding

def blobs_bound(tag: str, paths, *, repo_root=REPO) -> list:
    """2h's F-3 primitive, generalized to any tag/path set (ruling 3):
    the subset of `paths` (relative to `repo_root`, the git top level
    the tag's blobs are resolved against — `git rev-parse <tag>:<path>`
    reads `<path>` relative to the repository root regardless of `cwd`,
    verified empirically against a real temp repo) whose working-tree
    blob (`git hash-object`) differs from the blob `tag` carries at
    that path, or that the tag does not carry at all. Empty list =
    every path is bound to the tag — both sides are content-addressed,
    so no file bytes are read directly by this function on either
    side. Used by `run/endpoint_2i.py` to bind the predictor seal
    (`predictor_2i.json` + its draws AND record files) to
    `PREDICTOR_SEAL_TAG`."""
    repo_root = Path(repo_root)
    drift = []
    for rel in paths:
        p = repo_root / rel
        got = subprocess.run(["git", "hash-object", str(p)], cwd=repo_root,
                             capture_output=True, text=True)
        if got.returncode != 0:
            drift.append(rel)
            continue
        want = subprocess.run(["git", "rev-parse", f"{tag}:{rel}"], cwd=repo_root,
                              capture_output=True, text=True)
        if want.returncode != 0 or want.stdout.strip() != got.stdout.strip():
            drift.append(rel)
    return drift


def check_pythia_predictor_files() -> None:
    """Re-asserts x_A's real input (2d's committed main-tier draws)
    against `PYTHIA_PREDICTOR_FILES`."""
    from experiments.exp2d import analyze_2d as a2d
    for (size, rung), want in PYTHIA_PREDICTOR_FILES.items():
        p = a2d.tier_draws_path(a2d.EXP2D, "main", size, rung)
        got = bg.sha256_file(p)
        if got != want:
            raise ValueError(f"{p} has sha256 {got}, pinned {want} — 2d's "
                             f"committed draws have drifted")


if __name__ == "__main__":
    if "--scan" in sys.argv:
        inv = refresh_inventory()
        print(REPO_7B, len(inv[REPO_7B]), "revisions;", REPO_1B,
              len(inv[REPO_1B]), "revisions")
        print("sha256", bg.sha256_file(HUB_INVENTORY_PATH))
    elif "--manifest" in sys.argv:
        check_frozen_2i()
        inv = load_inventory()
        manifest = build_manifest(inv)
        write_manifest(CHECKPOINTS_PATH, manifest)
        print("7B entries", len(manifest["entries_7b"]), "; final_duplicates",
              manifest["final_duplicates"], "; signature_equals_main:",
              manifest["signature_equals_main"])
        print("sha256", bg.sha256_file(CHECKPOINTS_PATH))
    else:
        print("usage: python -m experiments.exp2i.battery_2i --scan | --manifest")
