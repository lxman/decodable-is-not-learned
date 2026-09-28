# experiments/exp6/families_6.py
"""The four outcome families (design §3.4), each scored through the
loaders, tokenizer pins, render and stop id its own experiment froze
(2m, 2i, 2l, 2n). This module only DISPATCHES: no loader is rewritten.
torch / transformers are imported inside the frozen loaders, lazily.

Order is the sweep order: the smallest family first, so a battery that
is flat at 3 B is found at the least cost (design §7)."""
from __future__ import annotations

from pathlib import Path

FAMILIES_6 = ("smollm3_3b", "olmo7b", "olmo13b", "comma_7b")
LABEL_6 = {"smollm3_3b": "SmolLM3-3B", "olmo7b": "OLMo-2 7B",
           "olmo13b": "OLMo-2 13B", "comma_7b": "Comma v0.1-1T"}
SOURCE_EXPERIMENT = {"smollm3_3b": "exp2m", "olmo7b": "exp2i",
                     "olmo13b": "exp2l", "comma_7b": "exp2n"}
INIT_KIND = {"smollm3_3b": "twin", "olmo7b": "twin", "olmo13b": "step0",
             "comma_7b": "twin"}
RENDER_6 = {"smollm3_3b": "plain", "olmo7b": "plain", "olmo13b": "plain",
            "comma_7b": "bos"}
DTYPE_6 = "float16"
BATCH_SIZE_6 = 16
INIT = "init"                      # the step key of the init referent
CKPT_CACHE_6 = Path.home() / "emergence-lab" / "ckpt_cache_6"


def _mods():
    from experiments.exp2i import battery_2i as bi
    from experiments.exp2l import battery_2l as bl
    from experiments.exp2m import battery_2m as bm
    from experiments.exp2n import battery_2n as bn
    return bi, bl, bm, bn


def _check(family: str) -> None:
    if family not in FAMILIES_6:
        raise ValueError(f"{family!r} is not an Exp 6 outcome family")


def grid(family: str) -> tuple:
    _check(family)
    bi, bl, bm, bn = _mods()
    return {"smollm3_3b": bm.GRID_3B, "olmo7b": bi.GRID_7B,
            "olmo13b": bl.GRID_13B, "comma_7b": bn.GRID_COMMA}[family]


def endpoint_step(family: str) -> int:
    g = grid(family)
    return int(g[-1])


def repo(family: str) -> str:
    _check(family)
    bi, bl, bm, bn = _mods()
    return {"smollm3_3b": bm.REPO_CKPT, "olmo7b": bi.REPO_7B,
            "olmo13b": bl.REPO_13B, "comma_7b": bn.REPO_COMMA}[family]


def manifest(family: str) -> dict:
    """The family's committed checkpoint manifest, under its own sha pin."""
    _check(family)
    bi, bl, bm, bn = _mods()
    if family == "smollm3_3b":
        return bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    if family == "olmo7b":
        return bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    if family == "olmo13b":
        return bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    return bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)


def entry(family: str, man: dict, step) -> dict:
    """The manifest entry of a grid step, or of the init referent
    (`INIT`): the seeded twin, or OLMo-2 13B's real step 0."""
    _check(family)
    bi, bl, bm, bn = _mods()
    if step == INIT:
        step = bl.STEP0 if INIT_KIND[family] == "step0" else bi.TWIN
    elif int(step) not in grid(family):
        raise ValueError(f"{family}: step {step} is not on the grid")
    if family == "smollm3_3b":
        return bm.entry_3b(man, step)
    if family == "olmo7b":
        return bi.entry_7b(man, step)
    if family == "olmo13b":
        return bl.entry_13b(man, step)
    return bn.entry_comma(man, step)


def steps(family: str) -> tuple:
    """Every unit of a family's sweep, in run order: the endpoint first
    (gate 1), then the init referent, then the grid ascending."""
    g = grid(family)
    return (g[-1], INIT) + tuple(s for s in g[:-1])


def step_dir(step) -> str:
    return INIT if step == INIT else f"step{int(step)}"


# ------------------------------------------------------------- loaders
def load_thin(family: str, man: dict, *, device: str):
    """The stage-1 endpoint through the family's THIN loader.
    Returns (model, tok, info)."""
    bi, bl, bm, bn = _mods()
    e = entry(family, man, endpoint_step(family))
    if family == "smollm3_3b":
        return bm.load_thin_3b(e["repo"], e["commit"], device=device, dtype=DTYPE_6)
    if family == "olmo7b":
        return bi.load_thin(bi.REPO_7B, e["commit"], device=device, dtype=DTYPE_6)
    if family == "olmo13b":
        return bl.load_thin_13b(e["commit"], device=device, dtype=DTYPE_6)
    return bn.load_thin_comma(e["repo"], e["commit"], device=device, dtype=DTYPE_6)


def load_checkpoint(family: str, man: dict, step, *, device: str,
                    cache_root=CKPT_CACHE_6):
    """A grid step (or OLMo-2 13B's step 0) through the family's
    CANDIDATE-FILE loader. Returns (model, tok, info)."""
    bi, bl, bm, bn = _mods()
    e = entry(family, man, step)
    if e.get("kind") == "from_config":
        raise ValueError(f"{family}: {step} is a twin; use load_init")
    if family == "smollm3_3b":
        model, info = bm.load_checkpoint_3b(e, cache_root=cache_root, device=device,
                                            dtype=DTYPE_6)
        tok = bm.load_tokenizer_3b(e["repo"], e["commit"])
    elif family == "olmo7b":
        model, info = bi.load_checkpoint(bi.REPO_7B, e, cache_root=cache_root,
                                         device=device, dtype=DTYPE_6)
        tok = bi.load_tokenizer(bi.REPO_7B, e["commit"])
    elif family == "olmo13b":
        model, info = bl.load_checkpoint_13b(e, cache_root=cache_root, device=device,
                                             dtype=DTYPE_6)
        tok = bl.load_tokenizer_13b(e["commit"])
    else:
        model, info = bn.load_checkpoint_comma(e, cache_root=cache_root, device=device,
                                               dtype=DTYPE_6)
        tok = bn.load_tokenizer_comma(e["repo"], e["commit"])
    return model, tok, info


def load_init(family: str, man: dict, *, device: str, cache_root=CKPT_CACHE_6):
    """The init referent: the seeded `from_config` twin, or for OLMo-2
    13B the real step 0. Returns (model, tok, info)."""
    bi, bl, bm, bn = _mods()
    e = entry(family, man, INIT)
    if INIT_KIND[family] == "step0":        # a real checkpoint, off the grid
        return load_checkpoint(family, man, INIT, device=device,
                               cache_root=cache_root)
    if family == "smollm3_3b":
        model, info = bm.load_twin_3b(config_commit=e["config_commit"], device=device,
                                      dtype=DTYPE_6)
        tok = bm.load_tokenizer_3b(e["repo"], e["config_commit"])
    elif family == "olmo7b":
        model, info = bi.load_twin_7b(device=device, dtype=DTYPE_6)
        tok = bi.load_tokenizer(bi.REPO_7B, e["config_commit"])
    else:
        model, info = bn.load_twin_comma(config_commit=e["config_commit"],
                                         device=device, dtype=DTYPE_6)
        tok = bn.load_tokenizer_comma(e["repo"], e["config_commit"])
    return model, tok, info


def runner(family: str, tok, model):
    """2c's frozen HFRunner; Comma's prompts go through 2n's BosRunner."""
    from experiments.exp6 import verify_6 as v6
    h = v6.harness_2c()
    inner = h.HFRunner(tok, model, BATCH_SIZE_6)
    if RENDER_6[family] == "bos":
        _, _, _, bn = _mods()
        return bn.BosRunner(inner)
    return inner


def free(family: str, man: dict, step, *, cache_root=CKPT_CACHE_6) -> None:
    bi, bl, bm, bn = _mods()
    e = entry(family, man, step)
    if e.get("kind") == "from_config":
        return
    if family == "smollm3_3b":
        bm.free_checkpoint_3b(e["revision"], cache_root)
    elif family == "olmo7b":
        bi.free_checkpoint(bi.REPO_7B, e["revision"], cache_root)
    elif family == "olmo13b":
        bl.free_checkpoint_13b(e["revision"], cache_root)
    else:
        bn.free_checkpoint_comma(e["revision"], cache_root)


def release(model) -> None:
    """Drop the model and empty the allocator's cache on either backend
    (the frozen `release` empties MPS only)."""
    if model is None:
        return
    try:
        import gc
        import torch
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:      # noqa: BLE001 — fakes in tests
        pass


# ------------------------------------------- the Mac's committed records
def committed_root(family: str) -> Path:
    from experiments.exp6 import battery_6 as b6
    return b6.EXPERIMENTS / SOURCE_EXPERIMENT[family]


def committed_sweep_record(family: str, step, rung: str) -> Path:
    """The Mac's committed record of `rung` at `step` on 2c's battery
    (the anchors' referent)."""
    d = "twin" if (step == INIT and INIT_KIND[family] == "twin") else (
        "step0" if step == INIT else f"step{int(step)}")
    return committed_root(family) / "results" / "sweep" / family / d / f"{rung}.json"


def committed_endpoint_record(family: str, rung: str) -> Path:
    return (committed_root(family) / "results" / "endpoint" / "stage1_final" /
            f"{rung}.json")
