# experiments/exp2l/battery_2l.py
"""Experiment 2l — constants, the OLMo-2 13B inventory + manifest, the
13B loader family, paths, the rung-set rule, record stamps, the gate-1
checkers, the pins and the prereg binding (design `experiment-2l-
design.md` §3–§4). Everything not defined here is imported frozen and
sha-pinned (`FROZEN_SHA256_2L`, `check_frozen_2l`): 2k's tier readers,
2i's loaders/record shapes/tree, 2g's strata and statistics, 2d's bar,
2c's harness.

Deltas from `battery_2i`, all local to this module:

1. The outcome repo is `allenai/OLMo-2-1124-13B` — `battery_2i`'s
   loader family (`download_entry`/`clean_dir`/`load_checkpoint`/
   `free_checkpoint`) keys its cache by `_short(repo)`, which REFUSES any
   repo but 1B/7B, so 2l carries its own 13B-keyed copies of those four
   (`*_13b`). `load_thin`/`load_tokenizer`/`verify_downloads`/
   `_check_loading_info`/`check_tokenizer` take the repo explicitly and
   are reused.
2. The stage-1 branch has a REAL step 0 (`stage1-step0-tokens0B`): it is
   a manifest entry with weights and a commit, loaded in the sweep like
   a grid step, never in an outcome (`trained_steps_13b()` excludes
   it). No from_config twin.
3. The predictors are 2k's and 2i's sealed artifacts: nothing is
   sampled. `PREDICTOR_SHA_2L` (a composite of the two seal shas, both
   literal here and re-read from disk by every stage) is the
   `predictor_sha` every 2l record stamps.
4. The rung-set rule writes a PRIMARY set narrower than the design's
   wording (doc slip (a)): x_A^(256) exists only on 2k's nine, so
   `R_PRIMARY = R_13B ∩ R_CAP_2K`; the rest of the eleven and the rest
   of R_13B are printed, never in the verdict.

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

EXP2L = Path(__file__).resolve().parent
EXPERIMENTS = EXP2L.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import strata_2g  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402

RESULTS = EXP2L / "results"
HUB_INVENTORY_PATH = EXP2L / "hub_inventory_olmo13b.json"
CHECKPOINTS_PATH = EXP2L / "checkpoints_2l.json"
CHECKPOINTS_2L_SHA256 = "3dd466f5130c1406c84d8bc856e5f98b0db0f73782119a0b2c0dffa7e424b83c"

FAMILY = bi.FAMILY                          # "olmo2"
SIZE_OUT = "olmo13b"
REPO_13B = "allenai/OLMo-2-1124-13B"
REV_13B_ENDPOINT = "stage1-step596057-tokens5001B"
REV_13B_STEP0 = "stage1-step0-tokens0B"
REV_13B_MAIN = "main"
ENDPOINT_STEP_13B = 596057
STEP0 = 0

# design §3.4 / dial c: log head, every 64k, the endpoint — 16 trained points.
GRID_13B = (1000, 2000, 4000, 8000, 16000, 32000,
            64000, 128000, 192000, 256000, 320000, 384000, 448000, 512000, 576000,
            596057)

PREREG_TAG_2L = "exp2l-preregistered"
ENDPOINT_SEAL_TAG_2L = "exp2l-endpoint-sealed"
INSTRUMENT_BLOBS_2L = ("experiments/exp2l/analyze_2l.py",
                       "experiments/exp2l/battery_2l.py",
                       "experiments/exp2l/run/endpoint_2l.py",
                       "experiments/exp2l/run/sweep_2l.py")

N_ITEMS = bt.N_ITEMS
STRATA_RUNGS = tuple(strata_2g.COVARIATE_OF)       # 2g's eleven
R_CAP_2K = tuple(bk.R_CAP_DESIGN)                  # the nine with a 256-draw predictor
BATCH_SIZE_2L = 16                                 # the harness default, threaded explicitly

# The two predictor seals, as committed (2k close-out, 2i close-out).
SEAL_2K_SHA256 = "3c4778b06de20c38090ea0f488e4f1664019076d7015b447b30e57f95ae2be9a"
SEAL_2I_SHA256 = "d80ada5058b422645514c199046f00e9d5ab86a8139fb6a725f487ed8560be24"
PREDICTOR_TAGS_2L = f"{bk.SEAL_TAG_2K}+{bi.PREDICTOR_SEAL_TAG}"


def predictor_sha_2l(seal_2k_sha: str, seal_2i_sha: str) -> str:
    """The composite `predictor_sha` every 2l record stamps: both
    predictors are already sealed, so 2l's own predictor identity is a
    function of the two seals and nothing else."""
    return hashlib.sha256(f"{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()


PREDICTOR_SHA_2L = predictor_sha_2l(SEAL_2K_SHA256, SEAL_2I_SHA256)

_STAGE1_RE = re.compile(r"^stage1-step(\d+)-tokens\d+B$")


def trained_steps_13b() -> tuple:
    return tuple(GRID_13B)


def n_trained_13b() -> int:
    return len(trained_steps_13b())


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


def load_inventory_13b(path=HUB_INVENTORY_PATH) -> dict:
    inv = json.loads(Path(path).read_text())
    if REPO_13B not in inv or "main" not in inv[REPO_13B]:
        raise ValueError(f"inventory lacks {REPO_13B}/main")
    return inv


def refresh_inventory_13b(out_path=HUB_INVENTORY_PATH) -> dict:
    """NETWORK (metadata only) — the ONE Hub scan of the whole build:
    every branch of `REPO_13B` (the 646 stage-1 checkpoints, the stage-2
    ingredients, `main`), file lists with LFS sha256 + size and the
    branch commit. Refuses if `out_path` exists — this runs ONCE, ever."""
    p = Path(out_path)
    if p.exists():
        raise FileExistsError(f"{p} already exists — refresh_inventory_13b is the ONE scan "
                              f"of this build and refuses to overwrite a committed inventory")
    from huggingface_hub import HfApi
    api = HfApi()

    def _info(rev: str) -> dict:
        info = _retry(api.model_info, REPO_13B, revision=rev, files_metadata=True)
        files = {s.rfilename: [s.lfs.sha256, s.size] for s in info.siblings if s.lfs}
        return {"commit": info.sha, "files": files}

    refs = _retry(api.list_repo_refs, REPO_13B)
    revs = sorted({b.name for b in refs.branches} | {"main"})
    table = {rev: _info(rev) for rev in revs}
    out = {REPO_13B: table}
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    return out


# ------------------------------------------------------------- manifest

def _weight_entry(rev: str, table: dict, cands: dict) -> dict:
    c = cands.get(rev)
    if c is None:
        raise ValueError(f"{REPO_13B}/{rev}: no candidate weight file")
    files = table[rev]["files"]
    return {"revision": rev, "commit": table[rev]["commit"], "kind": c["kind"],
            "files": list(c["files"]),
            "lfs_sha256": {n: files[n][0] for n in c["lfs"]},
            "lfs_size": {n: int(files[n][1]) for n in c["lfs"]}}


def build_manifest_13b(inv: dict) -> dict:
    """`battery_2i.build_manifest`'s body for the 13B grid + the real
    step 0: `ck.candidate`/`ck.signature` directly (the shard regex
    accepts `model-000NN-of-00012.safetensors` unmodified — tested), the
    duplicate-signature refusal across ALL scanned revisions for every
    grid point AND step 0; the endpoint alone may duplicate (a stage-2
    ingredient copy), recorded under `final_duplicates`."""
    table = inv[REPO_13B]
    main_files = table[REV_13B_MAIN]["files"]
    cands = {rev: ck.candidate(rev, t["files"], main_files) for rev, t in table.items()}
    sigs = {rev: (ck.signature(table[rev]["files"], c) if c else None)
            for rev, c in cands.items()}

    def dups_of(rev: str) -> list:
        return sorted(r for r, s in sigs.items() if r != rev and s is not None and s == sigs[rev])

    entries = {}
    for step in trained_steps_13b() + (STEP0,):
        matches = [r for r in table if _STAGE1_RE.fullmatch(r)
                   and int(_STAGE1_RE.fullmatch(r).group(1)) == step]
        if len(matches) != 1:
            raise ValueError(f"{REPO_13B}: step {step} matches {matches} in the inventory — "
                             f"exactly one stage1 branch is expected")
        rev = matches[0]
        entry = _weight_entry(rev, table, cands)
        same = dups_of(rev)
        if step != ENDPOINT_STEP_13B and same:
            raise ValueError(f"{REPO_13B}/{rev}: candidate files duplicate {same} — not a "
                             f"trustworthy grid point")
        entries[str(step)] = entry
    endpoint_entry = entries[str(ENDPOINT_STEP_13B)]
    if endpoint_entry["revision"] != REV_13B_ENDPOINT:
        raise ValueError(f"{REPO_13B}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_13B_ENDPOINT!r}")
    if entries[str(STEP0)]["revision"] != REV_13B_STEP0:
        raise ValueError(f"{REPO_13B}: step-0 revision {entries[str(STEP0)]['revision']!r} is "
                         f"not the pinned {REV_13B_STEP0!r}")
    main_entry = _weight_entry(REV_13B_MAIN, table, cands)
    sig_equal_main = bool(sigs.get(REV_13B_ENDPOINT) is not None
                          and sigs[REV_13B_ENDPOINT] == sigs.get(REV_13B_MAIN))
    return {"repo_13b": REPO_13B, "grid_13b": list(GRID_13B),
            "trained_steps_13b": list(trained_steps_13b()), "step0": STEP0,
            "entries_13b": entries, "main": main_entry,
            "final_duplicates": dups_of(REV_13B_ENDPOINT),
            "signature_equals_main": sig_equal_main, "n_revisions": len(table)}


def write_manifest(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest_13b(path=CHECKPOINTS_PATH, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    if obj.get("grid_13b") != list(GRID_13B) or obj.get("step0") != STEP0:
        raise ValueError(f"{path}: manifest is not the frozen 13B grid")
    return obj


def entry_13b(manifest: dict, step) -> dict:
    e = manifest.get("entries_13b", {}).get(str(int(step)))
    if e is None:
        raise ValueError(f"13B step {step!r} is not a grid entry")
    return e


def entry_main_13b(manifest: dict) -> dict:
    e = manifest.get("main")
    if e is None:
        raise ValueError("manifest lacks a main entry")
    return e


# -------------------------------------------------------- loader family

CKPT_CACHE_2L = Path.home() / "emergence-lab" / "ckpt_cache_2l"


def _cache_dir_13b(key, cache_root) -> Path:
    return Path(cache_root) / SIZE_OUT / str(key)


def download_entry_13b(entry: dict, cache_root=CKPT_CACHE_2L) -> dict:
    """MODEL CONTACT (weight bytes, ≈ 55 GB per revision). Never
    executed by a test."""
    from huggingface_hub import hf_hub_download
    rev_dir = _cache_dir_13b(entry["revision"], cache_root)
    paths = {}
    for name in entry["files"]:
        p = hf_hub_download(REPO_13B, name, revision=entry["commit"], cache_dir=str(rev_dir))
        paths[name] = Path(p).resolve()
    return paths


def clean_dir_13b(rev_key, cache_root, paths: dict, *, config) -> Path:
    """`battery_2i.clean_dir` with the 13B cache key: the candidate files
    only, hardlinked, plus the entry's pinned `config` written as
    `config.json` (2i stop #1: transformers 5.x reads the generation
    config from the DIRECTORY after the weights). `config` REQUIRED."""
    d = _cache_dir_13b(rev_key, cache_root) / "clean"
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


def load_checkpoint_13b(entry: dict, *, cache_root=CKPT_CACHE_2L, device: str = "mps",
                        dtype="float16"):
    """MODEL CONTACT. `battery_2i.load_checkpoint`'s body against the 13B
    cache: candidate files hashed against the manifest, config pinned to
    the entry's own commit, loading info required empty, tensor digest
    via `ck.tensor_digest`. Never executed by a test."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    paths = download_entry_13b(entry, cache_root)
    shas = bi.verify_downloads(entry, paths)
    config = AutoConfig.from_pretrained(REPO_13B, revision=entry["commit"])
    d = clean_dir_13b(entry["revision"], cache_root, paths, config=config)
    dt = getattr(torch, dtype) if isinstance(dtype, str) else dtype
    model, li = AutoModelForCausalLM.from_pretrained(
        str(d), config=config, dtype=dt, low_cpu_mem_usage=True, output_loading_info=True)
    counts = bi._check_loading_info(li, f"{REPO_13B}@{entry['revision']} (candidate files)")
    model = model.to(device).eval()
    info = {"repo": REPO_13B, "revision": entry["revision"], "commit": entry["commit"],
            "kind": entry["kind"], "files": list(entry["files"]), "sha256": shas,
            "config_source": f"{REPO_13B}@{entry['commit']}", "loading_info": counts,
            "tensor_digest": ck.tensor_digest(model)}
    return model, info


def load_thin_13b(commit: str, *, device: str = "mps", dtype="float16"):
    """The second loader path: `battery_2i.load_thin` on the 13B repo
    (it takes the repo explicitly; no `_short` refusal). Never executed
    by a test."""
    return bi.load_thin(REPO_13B, commit, device=device, dtype=dtype)


def load_tokenizer_13b(commit: str):
    return bi.load_tokenizer(REPO_13B, commit)


def free_checkpoint_13b(rev_key, cache_root=CKPT_CACHE_2L) -> None:
    d = _cache_dir_13b(rev_key, cache_root)
    if d.exists():
        shutil.rmtree(d)


# ----------------------------------------------------------------- paths

def sweep_dir(root) -> Path:
    return Path(root) / "results" / "sweep" / SIZE_OUT


def record_path(root, step, rung: str) -> Path:
    return sweep_dir(root) / f"step{int(step)}" / f"{rung}.json"


def checkpoint_record_path(root, step) -> Path:
    return sweep_dir(root) / f"step{int(step)}" / "_checkpoint.json"


def gate1_path(root) -> Path:
    return sweep_dir(root) / "gate1.json"


def halt_marker_path(root) -> Path:
    return sweep_dir(root) / "HALTED"


def endpoint_dir(root) -> Path:
    return Path(root) / "results" / "endpoint"


ENDPOINT_WHICH = ("stage1_final", "main")


def endpoint_record_path(root, which: str, rung: str) -> Path:
    if which not in ENDPOINT_WHICH:
        raise ValueError(f"{which!r} is not one of {ENDPOINT_WHICH}")
    return endpoint_dir(root) / which / f"{rung}.json"


def rung_set_path(root) -> Path:
    return endpoint_dir(root) / "rung_set_2l.json"


def power_path(root) -> Path:
    return endpoint_dir(root) / "power_2l.json"


# ----------------------------------------------------------- rung-set rule

def rung_set_from_counts_2l(counts: dict, floors: dict) -> dict:
    """§4 with doc slip (a): R_13B = the rungs clearing 2d's bar at the
    stage-1 endpoint; R_PRIMARY = R_13B ∩ R_CAP_2K (the nine that have a
    256-draw predictor — both tests run here); R_ELEVEN_EXTRA = the rest
    of 2g's eleven that clear (no 256-draw predictor: printed with the
    64-draw x_A and x_B, never in the verdict); R_EXTRA = the rest of
    R_13B (raw single-stratum D). Pure; sorted; a partition of R_13B."""
    from experiments.exp2d import stats_2d as st
    per_rung = {r: st.binomial_bar(int(k), N_ITEMS, float(floors[r])) for r, k in counts.items()}
    r_13b = tuple(r for r in sorted(counts) if per_rung[r]["significant"])
    r_primary = tuple(r for r in r_13b if r in R_CAP_2K)
    r_eleven_extra = tuple(r for r in r_13b if r in STRATA_RUNGS and r not in R_CAP_2K)
    r_extra = tuple(r for r in r_13b if r not in STRATA_RUNGS)
    return {"R_13B": list(r_13b), "R_PRIMARY": list(r_primary),
            "R_ELEVEN_EXTRA": list(r_eleven_extra), "R_EXTRA": list(r_extra),
            "primary_is_the_nine": tuple(r_primary) == tuple(sorted(R_CAP_2K)),
            "per_rung": per_rung}


# ------------------------------------------------------- endpoint sha

def composite_sha(files: dict) -> str:
    lines = "\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))
    return hashlib.sha256(lines.encode()).hexdigest()


def endpoint_files(root) -> dict:
    """{relpath: sha256} over the 68 endpoint records + the rung set +
    the power record — the content `ENDPOINT_SEAL_TAG_2L` binds. A
    missing file is a hard error (a composite over fewer files would be
    a different, silently weaker claim)."""
    root = Path(root)
    paths = [rung_set_path(root), power_path(root)]
    for which in ENDPOINT_WHICH:
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

def item_record_2l(*, rung, cap, ev, ckpt, step, endpoint_sha, t_s) -> dict:
    """A sweep record: 2i's `item_record_2i` (frozen, imported) with 2l's
    family/size, `seal_tag = ENDPOINT_SEAL_TAG_2L`, `predictor_sha =
    PREDICTOR_SHA_2L`, plus `endpoint_sha256` — the composite the
    analyzer re-derives from the committed endpoint files (design §3.7:
    the sweep records are read through the endpoint seal's sha)."""
    from experiments.exp2i.run.endpoint_2i import item_record_2i
    rec = item_record_2i(rung=rung, family=FAMILY, size=SIZE_OUT, cap=cap, ev=ev, ckpt=ckpt,
                         seal={"tag": ENDPOINT_SEAL_TAG_2L, "sha256": PREDICTOR_SHA_2L},
                         t_s=t_s, step=int(step))
    rec["endpoint_sha256"] = endpoint_sha
    return rec


def checkpoint_record_2l(*, step, ckpt: dict, info: dict, seconds: float) -> dict:
    """`_common_2i.checkpoint_record`'s payload with 2l's size (that
    helper hard-codes `bi.SIZE_OUT`)."""
    return {"family": FAMILY, "size": SIZE_OUT, "step": int(step),
            "revision": ckpt["revision"], "commit": ckpt["commit"],
            "sha256": dict(info.get("sha256", {})), "loading_info": info.get("loading_info"),
            "digest": ckpt["weight_sha256"], "download_seconds": round(seconds, 1)}


# ---------------------------------------------------------------- gate 1

GATE1_FIELDS_2L = ("rungs", "bit_diffs", "continuation_diffs", "continuations_compared",
                   "digest_sweep", "digest_endpoint", "commit_sweep", "commit_endpoint",
                   "prereg_tag")


def gate1_failures_13b(rec: dict, endpoint_records: dict) -> list:
    """`analyze_2i.gate1_failures_7b`'s body on the 13B labels: the
    runner's ATTESTED fields against the rule (coverage 500/rung
    required, both digests and commits equal, the prereg tag stamped)."""
    bad = []
    rungs = tuple(bt.RUNGS)
    if list(rec.get("rungs", [])) != list(rungs):
        bad.append("gate 1 olmo13b: rung list is not the full 34-rung sweep set")
    cs, ce = rec.get("commit_sweep"), rec.get("commit_endpoint")
    if not cs or not ce or cs != ce:
        bad.append(f"gate 1 olmo13b: commit through the sweep loader ({cs}) != through the "
                   f"endpoint loader ({ce})")
    dg_s, dg_e = rec.get("digest_sweep"), rec.get("digest_endpoint")
    if not dg_s or not dg_e or dg_s != dg_e:
        bad.append(f"gate 1 olmo13b: tensor digest through the sweep loader ({dg_s}) != "
                   f"through the endpoint loader ({dg_e}) — the checkpoint loader path is "
                   f"not the production path")
    bd, cd, nc = rec.get("bit_diffs", {}), rec.get("continuation_diffs", {}), \
        rec.get("continuations_compared", {})
    for r in rungs:
        if r not in endpoint_records:
            bad.append(f"gate 1 olmo13b/{r}: no stage1_final endpoint record to compare against")
            continue
        if bd.get(r) != 0:
            bad.append(f"gate 1 olmo13b/{r}: {bd.get(r)} bit diffs between the sweep's "
                       f"step{ENDPOINT_STEP_13B} record and the endpoint's stage1_final record")
        if cd.get(r) != 0:
            bad.append(f"gate 1 olmo13b/{r}: {cd.get(r)} continuation diffs")
        if nc.get(r) != N_ITEMS:
            bad.append(f"gate 1 olmo13b/{r}: {nc.get(r)} continuation pairs compared, not the "
                       f"full {N_ITEMS} — a zero diff count over a truncated comparison is "
                       f"not evidence")
    if rec.get("prereg_tag") != PREREG_TAG_2L:
        bad.append(f"gate 1 olmo13b: prereg_tag {rec.get('prereg_tag')!r} is not "
                   f"{PREREG_TAG_2L!r}")
    return bad


def gate1_rederive_13b(sweep_endpoint_records: dict, stage1_final_records: dict,
                       gate_record: dict) -> list:
    """`analyze_2i.gate1_rederive_7b`'s body on the 13B labels: bit and
    continuation diffs RE-DERIVED from the two committed record sets,
    required zero AND equal to the attestation, coverage 500 on both
    sides and in the attestation."""
    bad = []
    g = gate_record if isinstance(gate_record, dict) else {}
    bd_att, cd_att, nc_att = g.get("bit_diffs", {}), g.get("continuation_diffs", {}), \
        g.get("continuations_compared", {})
    for r in bt.RUNGS:
        if r not in sweep_endpoint_records:
            bad.append(f"gate 1 olmo13b re-derive/{r}: no sweep step{ENDPOINT_STEP_13B} record "
                       f"to re-derive against")
            continue
        if r not in stage1_final_records:
            bad.append(f"gate 1 olmo13b re-derive/{r}: no stage1_final endpoint record to "
                       f"re-derive against")
            continue
        s_bits, e_bits = sweep_endpoint_records[r].get("bits"), stage1_final_records[r].get("bits")
        s_c, e_c = sweep_endpoint_records[r].get("continuations"), \
            stage1_final_records[r].get("continuations")
        if not isinstance(s_bits, list) or not isinstance(e_bits, list) or \
                len(s_bits) != N_ITEMS or len(e_bits) != N_ITEMS:
            bad.append(f"gate 1 olmo13b re-derive/{r}: sweep/endpoint bits are not both "
                       f"{N_ITEMS} long — coverage failure")
            continue
        if not isinstance(s_c, list) or not isinstance(e_c, list) or \
                len(s_c) != N_ITEMS or len(e_c) != N_ITEMS:
            bad.append(f"gate 1 olmo13b re-derive/{r}: sweep/endpoint continuations are not "
                       f"both {N_ITEMS} long — coverage failure")
            continue
        bit_diff = sum(1 for a, b in zip(s_bits, e_bits) if int(bool(a)) != int(bool(b)))
        cont_diff = sum(1 for a, b in zip(s_c, e_c) if a != b)
        if bit_diff != 0:
            bad.append(f"gate 1 olmo13b re-derive/{r}: {bit_diff} bit diff(s) between the "
                       f"sweep's step{ENDPOINT_STEP_13B} record and the stage1_final endpoint "
                       f"record (re-derived from the bytes, not the attestation)")
        if cont_diff != 0:
            bad.append(f"gate 1 olmo13b re-derive/{r}: {cont_diff} continuation diff(s) "
                       f"(re-derived from the bytes, not the attestation)")
        if bd_att.get(r) != bit_diff:
            bad.append(f"gate 1 olmo13b re-derive/{r}: attested bit_diffs {bd_att.get(r)!r} "
                       f"disagrees with the re-derived {bit_diff}")
        if cd_att.get(r) != cont_diff:
            bad.append(f"gate 1 olmo13b re-derive/{r}: attested continuation_diffs "
                       f"{cd_att.get(r)!r} disagrees with the re-derived {cont_diff}")
        if nc_att.get(r) != N_ITEMS:
            bad.append(f"gate 1 olmo13b re-derive/{r}: attested continuations_compared "
                       f"{nc_att.get(r)!r} is not the full {N_ITEMS} — a zero diff count over "
                       f"a truncated comparison is not evidence")
    return bad


# ------------------------------------------------------------------ pins

# Every frozen module 2l executes on the verdict path or in a stage tool:
# 2k's 36 (which carry 2j's, 2i's, 2g's, 2h's, 2d's, 2c's, exp3's) + 2k's
# three tag-bound blobs (2k is closed; frozen bytes to 2l) + 2i's
# `run/endpoint_2i.py` (imported for `item_record_2i`) + 2l's own
# artifact writers. The four 2l blobs the prereg TAG binds are NOT here
# (2j's rule: a sha literal on them would kill every mutant trivially).
# `run/preflight_2l.py` and `verify_referents_2l.py` are deliberately not
# pinned (2i's convention, disclosed: neither writes on the verdict path).
FROZEN_FILES_2L = tuple(bk.FROZEN_SHA256_2K) + tuple(REPO / rel for rel in bk.INSTRUMENT_BLOBS_2K) + (
    EXPERIMENTS / "exp2i" / "run" / "endpoint_2i.py",
    EXP2L / "power_2l.py",
    EXP2L / "make_referents_2l.py",
)
FROZEN_SHA256_2L = {   # Task 5: pinned as a literal from frozen_from_disk() (42 modules)
    REPO / "experiments/exp2h/battery_2h.py":
        "2d721cf85bbd85937f45a1135e8b5e102685ab424d8ab0dfada527bd8ab4e80a",
    REPO / "experiments/exp2h/analyze_2h.py":
        "52733e8d4280fb41b76cda2dcac024299ce7dd61090f856ba3147c8098b871bf",
    REPO / "experiments/exp2g/battery_2g.py":
        "aca79dd71ee7dead3c0ce065945bb38eaf1b0b72b5d5f40698dabb0f5a9cf3c1",
    REPO / "experiments/exp2g/stats_2g.py":
        "cf3c4c89c86fa43c5ba49d5c4be12eabad28ac65d9d12a43b1e31ef6e4bc195f",
    REPO / "experiments/exp2g/strata_2g.py":
        "ea0acbbdfde13655a6b89d3afcc981f348ee6312b4448b70d437f1e4d3f7f594",
    REPO / "experiments/exp2g/labels_2g.py":
        "d86e7cdb4dcc10257986e8a85824365972a75ba993be5a8fde8a825d68e3077d",
    REPO / "experiments/exp2g/analyze_2g.py":
        "eab7c5b91d57351ee2a7adb0e85d71cb92cb4d6ed15d0bb90150c95c2076050e",
    REPO / "experiments/exp2g/checkpoints_2g.py":
        "155fee3ec3933db33930d7ddadb99c02604d893205a8f8c037016cc18609fb10",
    REPO / "experiments/exp2d/battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    REPO / "experiments/exp2d/analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    REPO / "experiments/exp2d/stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    REPO / "experiments/exp2d/results/verdict.json":
        "d5b1b28bf70f4be1a5acf73df8ad03d8c57349ce4acf15e26f690c6dc1347b61",
    REPO / "experiments/exp2c/harness.py":
        "3e72fb3c18772096e8c520ade93e154dd8bc6765c3c473390a9b32a6b24ae111",
    REPO / "experiments/exp2c/battery/family_map.py":
        "46477b37683c8ea0e1f2f219dce96858a0dcf91710b15cae45a8cf4c4c7ab375",
    REPO / "experiments/exp3/sampler.py":
        "e33c50d3985b1d6205d886e53726860f364cce1c6cd943ec460524e9110a03ea",
    REPO / "experiments/exp3c/analyze_3c.py":
        "66b78ffbedb808625ed33019f29d2ef8ec9d0f31a1115eb7cb08ad3e67d42d84",
    REPO / "experiments/exp2g/predictor_2g.py":
        "3381b43a34fd1fb1f7ef57eb9d02a6a9e9ec41b3ffcadea425c37b86c1e92a4e",
    REPO / "experiments/exp2g/run/sweep_2g.py":
        "850db5831adeffc46a888ca185ef3f1ad819a8db104c9eafd1df69c470c91a87",
    REPO / "experiments/exp2i/run/_common_2i.py":
        "5cc7c97f68b45656d6dbbb5fbf6d7d895d7b1d96e104df543f8c9f1691e5ad4f",
    REPO / "experiments/exp2i/make_referents_2i.py":
        "6de0278cfe85d9efefa11d0b2549afa78dd8836e1ef2b947d00c8709acc3977b",
    REPO / "experiments/exp2i/power_2i.py":
        "0e5e449ac420e40243ae86eb84e576256e857581ad3c7e000fcea5e08666119d",
    REPO / "experiments/exp2i/run/seal_2i.py":
        "f20132aed4c0b7e995745972abeddec4ba1d7a269147b5d034bff06a3157f078",
    REPO / "experiments/exp2i/analyze_2i.py":
        "85e482fea17e0706476243a0a98a7d2c32efebd6536c5255ae48e729b494c252",
    REPO / "experiments/exp2i/battery_2i.py":
        "e0a8d10cb4dde8a3af1a3e9b32447c407b43201513dc758d6cd9a8c38b5cdfcf",
    REPO / "experiments/exp2j/power_2j.py":
        "19b80593d091663183b7394b101ee5f97c832b5f0dd7dc4227c9b1107721ab1a",
    REPO / "experiments/exp2j/make_referents_2j.py":
        "ac4064ccc0e2a210c6eee720578f2b4c31846cf00d76668070adac5e9ebe1678",
    REPO / "experiments/exp2j/analyze_2j.py":
        "976f1ff1f91affa2fc66d635e6b6d9a8aabfd21bdc7ccc38abfe87482ea09b13",
    REPO / "experiments/exp2j/functionals_2j.py":
        "39375f01de4b5bf06787175e25f7f85394844c005c3c4ea66f69954b1fe8bfce",
    REPO / "experiments/exp3d/rederive_3d.py":
        "8421433ffe328e7e2ad8d2877150f9bfc0279c9337576fd5860e917dc8690870",
    REPO / "experiments/exp3/run/run_cell.py":
        "5c018457d9eb999079b4b0426dc0ecadf10baed6339d32b5eb914f280da35b46",
    REPO / "experiments/exp2i/run/sample_2i.py":
        "6cf3cdfac2f940f12c0365694758578a3655afbf74498f7c7c549ac221b55fe4",
    REPO / "experiments/exp2b/models.py":
        "a4c5eed26cc92044aeb9ed7b68b177035de3ac2615dbba09a6d21eeb191a55a4",
    REPO / "experiments/exp2k/power_2k.py":
        "318ec4266513200e6a018285184cdae5c1fe5cc78400fe07671a9f45bc92ed4e",
    REPO / "experiments/exp2k/make_referents_2k.py":
        "6921feb194bd5971a74af1c25899146c70e5a9b402546be413321b3edee882d4",
    REPO / "experiments/exp2k/run/seal_2k.py":
        "0cbdd982a55075e8c8567acb82d7264ce87c88320d2fa4568a5b419f7ca4b2fb",
    REPO / "experiments/exp2k/run/campaign_2k.py":
        "75f2b4c4f66d3d683d875e2a569bc2ec2b7c72fafa3ca1071c103d54df1337e5",
    REPO / "experiments/exp2k/analyze_2k.py":
        "27ea6f7b4dcf18894061363a7d7d64d2a63e867946797a5306a695c9d0e86f1a",
    REPO / "experiments/exp2k/battery_2k.py":
        "1066265d689573cc009c73df1b036a9453be7a807d79e153b53ccf52177eec0a",
    REPO / "experiments/exp2k/run/tier_2k.py":
        "4729ece9592b27c9aaa1183e8570dc787d4a945edafb82f036bc05b9bee50510",
    REPO / "experiments/exp2i/run/endpoint_2i.py":
        "8c3718341b22fcdd99c799e45d43ac883f076c2d2080789aa323626c4d808cf2",
    REPO / "experiments/exp2l/power_2l.py":
        "99e4c8f978608db64ec0cf3ea00de98e4c43d4447d033ec836c45b82c198b5e9",
    REPO / "experiments/exp2l/make_referents_2l.py":
        "b7e3cdc5a60f1c94aed98c7f77c73221e1c0fac9e78b0870bbbfd549473373a0",
}


def frozen_from_disk(*, strict: bool = True) -> dict:
    if strict:
        return {p: bg.sha256_file(p) for p in FROZEN_FILES_2L}
    return {p: bg.sha256_file(p) for p in FROZEN_FILES_2L if p.is_file()}


def check_frozen_2l() -> None:
    if not FROZEN_SHA256_2L:
        raise RuntimeError("FROZEN_SHA256_2L is empty — not pinned (build incomplete)")
    for p, want in FROZEN_SHA256_2L.items():
        got = bg.sha256_file(p)
        if got != want:
            raise RuntimeError(f"frozen module drifted: {p} ({got[:12]} != {want[:12]})")


def require_prereg_2l(*, tag_exists=None, blob_sha=None) -> dict:
    """2k's blob binding: the tag must exist and each instrument blob's
    bytes on disk must equal the blob the tag carries."""
    from experiments.exp2g import predictor_2g as pr
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_2L):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_2L} does not exist")
    bound = {}
    for rel in INSTRUMENT_BLOBS_2L:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_2L, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_2L} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_2L, "instrument_blobs": bound}


if __name__ == "__main__":
    if "--scan" in sys.argv:
        inv = refresh_inventory_13b()
        print(REPO_13B, len(inv[REPO_13B]), "revisions")
        print("sha256", bg.sha256_file(HUB_INVENTORY_PATH))
    elif "--manifest" in sys.argv:
        inv = load_inventory_13b()
        manifest = build_manifest_13b(inv)
        write_manifest(CHECKPOINTS_PATH, manifest)
        e = entry_13b(manifest, ENDPOINT_STEP_13B)
        print("entries", len(manifest["entries_13b"]), "; endpoint commit", e["commit"],
              "; main commit", entry_main_13b(manifest)["commit"],
              "; final_duplicates", manifest["final_duplicates"],
              "; signature_equals_main:", manifest["signature_equals_main"])
        print("sha256", bg.sha256_file(CHECKPOINTS_PATH))
    else:
        print("usage: python -m experiments.exp2l.battery_2l --scan | --manifest")
