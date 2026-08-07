"""M2 trained-side campaign (design §6): m3 + shuffled + known-present
fits over the frozen 34-rung battery's NEW-POOL rungs.

The 12 reused 2b survivors are never refit here: their m3 and shuffled
fits carry from the tagged 2b record (design §7, declared at freeze).
This module fits the 22 new-pool rungs plus the known-present controls.

Stages (per size; one JSON per (stage, size, cap, seed), skip-if-exists,
resumable — exp2b's run_probes_2b.py conventions carried verbatim):

  m3             trained activations, scored new-pool rungs
                 -> results/probes/m3/
  shuffled       trained activations, labels permuted with rng(1000+seed)
                 AFTER the split is built from the true labels
                 (split_labels=y; gate 2's corrected ordering, canonical
                 per design §4) -> results/probes/shuffled/
  known_present  entity_track (2b committed items + the local 2b trained
                 npz caches — the instrument is bit-deterministic, so
                 fits on identical inputs are exact) + ctrl_copy (2c's
                 own M1 items) -> results/probes/known_present/

Collection: the trained model loaded by pinned SHA (fp16, MPS), npz
cached under results/activations/{size}_trained/ — identical harvest
path to the untrained screen's (run/screen.py), model weights the only
difference. Two-stage lock: probe sizes (410m/1b) only; nothing here
names an eval-side model.

Usage:
    python -m run.campaign_m2 collect <size>
    python -m run.campaign_m2 probes <stage> <size> [cap ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

try:  # experiments.exp2c.run.campaign_m2 (pytest / absolute import)
    from . import screen
    from ..battery import family_map
except ImportError:  # pragma: no cover - `python -m run.campaign_m2` from exp2c/
    import sys as _sys
    from run import screen
    _exp2c = str(Path(__file__).resolve().parent.parent)
    if _exp2c in _sys.path:
        _sys.path.remove(_exp2c)
    _sys.path.insert(0, _exp2c)
    _sys.modules.pop("battery", None)
    _sys.modules.pop("battery.family_map", None)
    from battery import family_map

HERE = Path(__file__).resolve().parent.parent      # experiments/exp2c
EXP2B = HERE.parent / "exp2b"
RESULTS = HERE / "results"
SEEDS = (0, 1, 2, 3, 4)
SIZES = ("410m", "1b")
STAGES = ("m3", "shuffled", "known_present")
KNOWN_PRESENT_CAPS = ("entity_track", "ctrl_copy")


# ------------------------------------------------------------- battery sets

def survivors() -> set[str]:
    m = json.loads((RESULTS / "reuse_manifest.json").read_text())
    return set(m["survivors"])

def new_pool_rungs() -> list[str]:
    """The 22 scored rungs whose fits this campaign owns: the frozen
    scored battery (family_map is tier-1- and M1-adjudication-aware;
    the map is rung -> family) minus the 12 reused survivors whose
    record carries from 2b."""
    rung_to_family = family_map.scored_battery_families()
    carry = survivors()
    return sorted(r for r in rung_to_family if r not in carry)

def stage_caps(stage: str) -> list[str]:
    if stage == "known_present":
        return list(KNOWN_PRESENT_CAPS)
    return new_pool_rungs()


# --------------------------------------------------------------- activations

def _trained_path(size: str, name: str) -> Path:
    return RESULTS / "activations" / f"{size}_trained" / f"{name}.npz"

def _load_trained_pythia(size: str):
    """Trained weights at the pinned SHA (the run-code-loads-by-SHA rule)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    repo = f"EleutherAI/pythia-{size}"
    sha = screen.PYTHIA_SHAS[size]
    tok = AutoTokenizer.from_pretrained(repo, revision=sha)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        repo, revision=sha, dtype=torch.float16)
    return tok, model.to("mps").eval()

def collect_size(size: str) -> None:
    """Collect trained activations for every cap this campaign fits whose
    npz is missing. entity_track is excluded: its cache is 2b's, asserted
    present at fit time, never recollected (identical items, design §7)."""
    todo = [c for c in new_pool_rungs() + ["ctrl_copy"]
            if not _trained_path(size, c).exists()]
    print(f"[m2-collect] {size}: {len(todo)} to collect", flush=True)
    if not todo:
        return
    tok, model = _load_trained_pythia(size)
    for name in todo:
        payload = screen._load_item_file(name)
        arrays = screen._collect_capability(model, tok, payload)
        meta = {"size": size, "mode": "trained", "capability": name,
                "sha": screen.PYTHIA_SHAS[size],
                "n_items": int(arrays["X"].shape[0]),
                "n_layers": int(arrays["X"].shape[1])}
        screen._save_activations(_trained_path(size, name), arrays, meta)
        print(f"[m2-collect] {size}/{name}: {meta['n_items']} items", flush=True)


def _activation_source(cap: str, size: str) -> tuple[Path, dict]:
    """(npz path, item payload). entity_track reads the 2b tree for both."""
    if cap == "entity_track":
        path = EXP2B / "results" / "activations" / f"{size}_trained" / \
            "entity_track.npz"
        assert path.exists(), (
            f"2b trained entity_track cache missing at {path}; the "
            "known-present gate reuses it by design (§7) — restore it "
            "rather than recollecting")
        payload = json.loads(
            (EXP2B / "battery" / "items" / "entity_track.json").read_text())
        return path, payload
    return _trained_path(size, cap), screen._load_item_file(cap)


def _entity_track_split_params():
    """entity_track's SplitParams live in exp2b's frozen spec registry.
    Both trees ship a top-level `battery` package, so exp2b's must be
    forced ahead of exp2c's for this one import (the mirror image of
    screen._split_plan's fallback) and the module cache cleared both
    ways so neither tree sees the other's battery afterward."""
    import sys as _sys
    saved = [p for p in _sys.path]
    for mod in [m for m in _sys.modules if m == "battery" or
                m.startswith("battery.")]:
        _sys.modules.pop(mod)
    _sys.path.insert(0, str(EXP2B))
    try:
        from battery.generators import SPECS as SPECS_2B
        return {s.name: s for s in SPECS_2B}["entity_track"].split_params
    finally:
        _sys.path[:] = saved
        for mod in [m for m in _sys.modules if m == "battery" or
                    m.startswith("battery.")]:
            _sys.modules.pop(mod)

def _split_params_for(cap: str):
    if cap == "entity_track":
        return _entity_track_split_params()
    return screen._split_plan(cap)


# --------------------------------------------------------------------- fits

def probe_result_path(stage: str, size: str, cap: str, seed: int) -> Path:
    return RESULTS / "probes" / stage / f"{size}_{cap}_seed{seed}.json"

def shuffled_labels(y: np.ndarray, seed: int):
    """Gate 2's corrected ordering (design §4, canonical): the split is
    built from the TRUE labels; only the fit labels are permuted."""
    rng = np.random.default_rng(1000 + seed)
    return y, rng.permutation(y)

def fit_one(stage: str, size: str, cap: str, seed: int) -> dict:
    out = probe_result_path(stage, size, cap, seed)
    if out.exists():
        return json.loads(out.read_text())

    npz, payload = _activation_source(cap, size)
    act, y, meta = screen._load_activation_map(npz)
    act = screen._thin_layers(act)
    items = payload["probe_items"]
    bases = [tuple(it["basis"]) for it in items]
    assert len(bases) == len(y), f"{cap}/{size}: basis/label count mismatch"

    split_labels = None
    if stage == "shuffled":
        split_labels, y = shuffled_labels(y, seed)

    r = screen.probe_starved(
        act, y, bases,
        split_params=_split_params_for(cap),
        checkpoint_id=f"pythia-{size}:{screen.PYTHIA_SHAS[size][:8]}:trained",
        n_perm=screen.N_PERM_FULL,
        seed=seed,
        split_labels=split_labels,
    )
    import socket
    d = {"stage": stage, "size": size, "capability": cap,
         "host": socket.gethostname(), **r}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, indent=1))
    return d


def _worker(args):
    import os
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    return fit_one(*args)

def run_stage(stage: str, size: str, caps: list[str] | None = None,
              processes: int = 8) -> None:
    caps = caps or stage_caps(stage)
    jobs = [(stage, size, cap, seed) for cap in caps for seed in SEEDS
            if not probe_result_path(stage, size, cap, seed).exists()]
    print(f"[m2-probe] {stage}/{size}: {len(jobs)} to fit, "
          f"{len(caps) * len(SEEDS) - len(jobs)} cached", flush=True)

    def report(d):
        print(f"[m2-probe] {d['stage']}/{d['size']}/{d['capability']}"
              f"/seed{d['seed']}: present={d['present']} "
              f"p={d['null_p']:.4g} acc={d['accuracy']:.4f} "
              f"margin={d['margin']:.4f}", flush=True)

    if processes <= 1:
        for job in jobs:
            report(_worker(job))
        return
    from multiprocessing import Pool
    with Pool(processes=processes) as pool:
        for d in pool.imap_unordered(_worker, jobs):
            report(d)


def main(argv=None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0]
    if cmd == "collect":
        collect_size(argv[1])
    elif cmd == "probes":
        stage, size = argv[1], argv[2]
        assert stage in STAGES, f"stage must be one of {STAGES}"
        assert size in SIZES, f"size must be one of {SIZES}"
        run_stage(stage, size, list(argv[3:]) or None)
    else:
        raise SystemExit(f"unknown command {cmd!r}; use collect|probes")


if __name__ == "__main__":
    main()
