"""Exp 2g checkpoints (design §4; build findings A–E): the Hub
inventory, the candidate-weight rule, the grid manifest with every
candidate's sha pinned, and the loader that builds a CLEAN directory
holding only the candidate files and loads them into 2c's pinned
config with 2b's pinned tokenizer.

The Hub's Pythia branches are not trustworthy by label (finding A):
a branch may carry `main`'s files beside its own, or another step's
files. Nothing here loads a revision "as published"; every weight
file is chosen by rule, hashed after download, and compared to the
manifest; every grid point's candidate must be unique across all 155
revisions (the final point's duplicates are listed, not refused)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402

CKPT_CACHE = Path.home() / "emergence-lab" / "ckpt_cache_2g"
_ST_SHARD = re.compile(r"model-\d+-of-\d+\.safetensors")
_BIN_SHARD = re.compile(r"pytorch_model-\d+-of-\d+\.bin")
INDEX_OF = {"safetensors-shards": "model.safetensors.index.json",
            "bin-shards": "pytorch_model.bin.index.json"}


def _pythia_shas() -> dict:
    from models import PYTHIA_SHAS   # exp2b's, via battery_2d's sys.path
    return PYTHIA_SHAS


# ------------------------------------------------------------ inventory

def load_inventory(path=bg.HUB_INVENTORY_PATH) -> dict:
    inv = json.loads(Path(path).read_text())
    for size, repo in bg.REPO_OF.items():
        if repo not in inv or "main" not in inv[repo]:
            raise ValueError(f"inventory lacks {repo}/main")
    return inv


def refresh_inventory(sizes=bg.SWEEP_SIZES, out_path=bg.HUB_INVENTORY_PATH) -> dict:
    """NETWORK (metadata only): rebuild the inventory from the Hub."""
    from huggingface_hub import HfApi
    api = HfApi()
    out = {}
    for size in sizes:
        repo = bg.REPO_OF[size]
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


# ------------------------------------------------------ candidate rule

def candidate(rev: str, files: dict, main_files: dict) -> dict | None:
    """Finding A's rule: shards if present; else the single safetensors
    if its sha is the branch's own (≠ main's) or the branch IS main;
    else bin shards; else the single bin; else None."""
    st = sorted(n for n in files if _ST_SHARD.fullmatch(n))
    if st:
        return {"kind": "safetensors-shards",
                "files": st + [INDEX_OF["safetensors-shards"]], "lfs": st}
    single = files.get("model.safetensors")
    main_single = main_files.get("model.safetensors", [None])[0]
    if single is not None and (rev == "main" or single[0] != main_single):
        return {"kind": "safetensors-single", "files": ["model.safetensors"],
                "lfs": ["model.safetensors"]}
    bins = sorted(n for n in files if _BIN_SHARD.fullmatch(n))
    if bins:
        return {"kind": "bin-shards", "files": bins + [INDEX_OF["bin-shards"]],
                "lfs": bins}
    if "pytorch_model.bin" in files:
        return {"kind": "bin", "files": ["pytorch_model.bin"],
                "lfs": ["pytorch_model.bin"]}
    return None


def signature(files: dict, cand: dict) -> tuple:
    return tuple(files[n][0] for n in cand["lfs"])


# ------------------------------------------------------------- manifest

def build_manifest(size: str, inv: dict) -> dict:
    repo = bg.REPO_OF[size]
    table = inv[repo]
    main_files = table["main"]["files"]
    cands = {rev: candidate(rev, t["files"], main_files) for rev, t in table.items()}
    sigs = {rev: (signature(table[rev]["files"], c) if c else None)
            for rev, c in cands.items()}

    def dups_of(rev):
        return sorted((r for r, s in sigs.items()
                       if r != rev and s is not None and s == sigs[rev]),
                      key=lambda r: (r == "main", int(r[4:]) if r.startswith("step") else 0))

    entries, evidence = {}, {}
    excluded = {int(k): v for k, v in bg.EXCLUDED_GRID[size].items()}
    # visit the grid AND the excluded steps: an excluded step must carry
    # executable evidence for its exclusion (GRID itself omits it)
    for step in sorted(set(bg.GRID[size]) | set(excluded)):
        rev = bg.revision_of(step)
        if rev not in table:
            raise ValueError(f"{repo}: revision {rev} is not in the inventory")
        c = cands[rev]
        if c is None:
            raise ValueError(f"{repo}/{rev}: no candidate weight file")
        same = dups_of(rev)
        if step in excluded:
            if not same:
                raise ValueError(f"{repo}/{rev}: exclusion {excluded[step]!r} is "
                                 f"unjustified — its candidate files are unique")
            evidence[str(step)] = {"kind": c["kind"], "duplicates": same,
                                   "lfs_sha256": {n: table[rev]["files"][n][0]
                                                  for n in c["lfs"]}}
            continue
        if step != bg.FINAL_STEP and same:
            raise ValueError(f"{repo}/{rev}: candidate files duplicate {same} — "
                             f"not a trustworthy grid point")
        entries[str(step)] = {
            "revision": rev, "commit": table[rev]["commit"], "kind": c["kind"],
            "files": list(c["files"]),
            "lfs_sha256": {n: table[rev]["files"][n][0] for n in c["lfs"]},
            "lfs_size": {n: int(table[rev]["files"][n][1]) for n in c["lfs"]},
        }
    for step in excluded:
        if str(step) not in evidence:
            raise ValueError(f"excluded step {step} is not on the grid")
    main_entry = entries.get(str(bg.FINAL_STEP))
    if main_entry is None or main_entry["commit"] != _pythia_shas()[size]:
        raise ValueError(f"{repo}: the final grid point is not 2c's pinned "
                         f"main commit {_pythia_shas()[size]}")
    hub = table.get(f"step{bg.FINAL_STEP}")
    hub_c = cands.get(f"step{bg.FINAL_STEP}")
    main_bins = tuple(v[0] for n, v in sorted(main_files.items())
                      if n.startswith("pytorch_model") and n.endswith(".bin"))
    hub_bins = tuple(v[0] for n, v in sorted(hub["files"].items())
                     if n.startswith("pytorch_model") and n.endswith(".bin")) if hub else ()
    hub_rec = {
        "commit": hub["commit"] if hub else None,
        "kind": hub_c["kind"] if hub_c else None,
        "lfs_sha256": ({n: hub["files"][n][0] for n in hub_c["lfs"]} if hub_c else {}),
        "signature_equals_main": bool(hub_c and sigs[f"step{bg.FINAL_STEP}"] == sigs["main"]
                                      or (hub_bins and hub_bins == main_bins)),
        "duplicates": dups_of(f"step{bg.FINAL_STEP}") if hub else [],
    }
    stale = {
        "model.safetensors": sum(1 for r, t in table.items() if r != "main"
                                 and t["files"].get("model.safetensors", [None])[0]
                                 == main_files.get("model.safetensors", [None])[0]),
        "pytorch_model.bin": sum(1 for r, t in table.items() if r != "main"
                                 and t["files"].get("pytorch_model.bin", [None])[0]
                                 == main_files.get("pytorch_model.bin", [None])[0]),
    }
    return {"size": size, "repo": repo, "main_commit": table["main"]["commit"],
            "grid": list(bg.GRID[size]), "trained_steps": list(bg.trained_steps(size)),
            "entries": entries, "excluded": {str(k): v for k, v in excluded.items()},
            "exclusion_evidence": evidence, "final_duplicates": dups_of("main"),
            "hub_step143000": hub_rec, "stale_main_copies": stale,
            "n_revisions": len(table)}


def build_all(inv: dict) -> dict:
    return {size: build_manifest(size, inv) for size in bg.SWEEP_SIZES}


def write_manifest(path, obj: dict) -> None:
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True))


def load_manifest(path=bg.CHECKPOINTS_PATH, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    obj = json.loads(raw)
    for size in bg.SWEEP_SIZES:
        m = obj.get(size)
        if not m or m.get("grid") != list(bg.GRID[size]) or \
                set(m.get("excluded", {})) != {str(k) for k in bg.EXCLUDED_GRID[size]}:
            raise ValueError(f"{path}: {size} manifest is not the frozen grid")
        if m["main_commit"] != _pythia_shas()[size]:
            raise ValueError(f"{path}: {size} main commit is not 2c's pin")
    return obj


def entry_for(manifest: dict, size: str, step: int) -> dict:
    e = manifest[size]["entries"].get(str(int(step)))
    if e is None:
        raise ValueError(f"{size} step {step} is not a grid entry")
    return e


# ---------------------------------------------------- loader (stage 2)

def _rev_dir(size, step, cache_root) -> Path:
    return Path(cache_root) / size / f"step{int(step)}"


def download_entry(size: str, entry: dict, cache_root=CKPT_CACHE) -> dict:
    from huggingface_hub import hf_hub_download
    rev_dir = _rev_dir(size, _step_of(entry), cache_root)
    paths = {}
    for name in entry["files"]:
        p = hf_hub_download(bg.REPO_OF[size], name, revision=entry["commit"],
                            cache_dir=str(rev_dir))
        paths[name] = Path(p).resolve()
    return paths


def _step_of(entry: dict) -> int:
    rev = entry["revision"]
    return bg.FINAL_STEP if rev == "main" else int(rev[4:])


def verify_downloads(entry: dict, paths: dict) -> dict:
    shas = {}
    for name, p in paths.items():
        got = bg.sha256_file(p)
        want = entry["lfs_sha256"].get(name)
        if want is not None and got != want:
            raise ValueError(f"{name}: downloaded sha256 {got} against the manifest's "
                             f"{want} — not the pinned weights")
        shas[name] = got
    return shas


def pinned_config(size: str):
    from transformers import AutoConfig
    return AutoConfig.from_pretrained(bg.REPO_OF[size], revision=_pythia_shas()[size])


def clean_dir(size: str, step: int, cache_root, paths: dict) -> Path:
    d = _rev_dir(size, step, cache_root) / "clean"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for name, src in paths.items():
        dst = d / name
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    pinned_config(size).to_json_file(str(d / "config.json"))
    return d


def load_checkpoint(size: str, step: int, entry: dict, *, cache_root=CKPT_CACHE,
                    device: str = "mps"):
    """MODEL CONTACT. The candidate files only, hashed, into 2c's pinned
    config; loading info must be empty; fp16 on `device`."""
    import torch
    from transformers import AutoModelForCausalLM
    paths = download_entry(size, entry, cache_root)
    shas = verify_downloads(entry, paths)
    d = clean_dir(size, step, cache_root, paths)
    model, li = AutoModelForCausalLM.from_pretrained(
        str(d), config=pinned_config(size), dtype=torch.float16,
        output_loading_info=True)
    bad = {k: list(li.get(k, [])) for k in ("missing_keys", "unexpected_keys",
                                             "mismatched_keys") if li.get(k)}
    if bad:
        raise ValueError(f"{size} step {step}: the candidate files do not fill "
                         f"2c's architecture exactly: {bad}")
    model = model.to(device).eval()
    info = {"size": size, "step": int(step), "revision": entry["revision"],
            "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry["files"]), "sha256": shas,
            "config_source": f"{bg.REPO_OF[size]}@{_pythia_shas()[size]}",
            "tokenizer_source": f"{bg.REPO_OF[size]}@{_pythia_shas()[size]}",
            "loading_info": {k: len(li.get(k, [])) for k in
                             ("missing_keys", "unexpected_keys", "mismatched_keys")}}
    return model, info


def tensor_digest(model) -> str:
    h = hashlib.sha256()
    for k, t in sorted(model.state_dict().items()):
        a = t.detach().to("cpu").contiguous()
        h.update(k.encode())
        h.update(str(tuple(a.shape)).encode())
        h.update(str(a.dtype).encode())
        h.update(a.numpy().tobytes())
    return h.hexdigest()


def free_checkpoint(size: str, step: int, cache_root=CKPT_CACHE) -> None:
    d = _rev_dir(size, step, cache_root)
    if d.exists():
        shutil.rmtree(d)


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh_inventory()
    inv = load_inventory()
    obj = build_all(inv)
    write_manifest(bg.CHECKPOINTS_PATH, obj)
    for size, m in obj.items():
        print(size, len(m["entries"]), "entries; excluded", m["excluded"],
              "; hub step143000 == main:", m["hub_step143000"]["signature_equals_main"])
    print("sha256", bg.sha256_file(bg.CHECKPOINTS_PATH))
