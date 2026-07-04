"""Checkpoint I/O and the checkpoint-cadence schedule.

Implementation plan §3/§5: save model checkpoints (not activations) with a cadence
dense around the transition -- log-spaced early, denser later -- so S1/S2 have
below-threshold checkpoints and S3 has enough pre-transition points to fit a precursor.
Activations are recomputed at analysis from a fixed probe set, so only weights persist.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch


def checkpoint_schedule(total_steps: int, n_points: int = 40) -> list[int]:
    """Steps at which to checkpoint: log-spaced over [1, total_steps], deduped.

    Log spacing puts most checkpoints early, where the pre-transition precursor lives
    (grokking/induction transitions are sudden and late-ish; the interesting readouts
    are the run-up). Always includes the final step.
    """
    if total_steps < 1:
        raise ValueError("total_steps must be >= 1")
    pts = np.unique(np.geomspace(1, total_steps, num=n_points).round().astype(int))
    steps = sorted(set(int(s) for s in pts) | {total_steps})
    return steps


def save_checkpoint(model, step: int, ckpt_dir: str | Path, extra: dict | None = None) -> Path:
    ckpt_dir = Path(ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    path = ckpt_dir / f"step_{step:07d}.pt"
    payload = {"step": step, "state_dict": model.state_dict()}
    if extra:
        payload.update(extra)
    torch.save(payload, path)
    return path


def list_checkpoints(ckpt_dir: str | Path) -> list[tuple[int, Path]]:
    ckpt_dir = Path(ckpt_dir)
    out = []
    for p in sorted(ckpt_dir.glob("step_*.pt")):
        step = int(p.stem.split("_")[1])
        out.append((step, p))
    return out


def load_checkpoint(model, path: str | Path, map_location="cpu") -> int:
    payload = torch.load(path, map_location=map_location, weights_only=False)
    model.load_state_dict(payload["state_dict"])
    return int(payload["step"])
