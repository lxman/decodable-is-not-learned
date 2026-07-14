"""Collect probe-side activations (design §3), durable and resumable.

Usage:
    python -m run.collect_activations <size> <trained|untrained> [capability ...]

size            410m | 1b  (probe side only — the two-stage lock forbids 2.8b+
                            until Stage 1 is committed and tagged)
Default capabilities: the FIXED scored battery + both positive controls.

One .npz per (size, mode, capability); existing files are skipped. The model
loads lazily on the first miss. Shuffled-label controls need no collection of
their own — they reuse the trained activations with permuted labels.
"""

from __future__ import annotations

import sys

from activations import activations_path, collect_capability, save_activations
from battery.base import load_items
from models import PROBE_SIZES, PYTHIA_SHAS, load_pythia

UNTRAINED_SEED = 0  # same control model as M1's chance floors, ledgered
CONTROLS = ["ctrl_copy", "ctrl_next_letter"]


def scored_battery() -> list[str]:
    import json
    from battery.base import ITEMS_DIR
    return json.loads((ITEMS_DIR / "scored_battery.json").read_text())


def main() -> None:
    size, mode = sys.argv[1], sys.argv[2]
    assert size in PROBE_SIZES, f"probe side only, not {size!r}"
    assert mode in ("trained", "untrained")
    caps = sys.argv[3:] or (scored_battery() + CONTROLS)

    model = tok = None
    for name in caps:
        path = activations_path(size, mode, name)
        if path.exists():
            print(f"[collect] skip {size}/{mode}/{name} (exists)", flush=True)
            continue
        if model is None:
            tok, model = load_pythia(size, untrained=(mode == "untrained"),
                                     seed=UNTRAINED_SEED)
        arrays = collect_capability(model, tok, load_items(name))
        save_activations(path, arrays, {
            "size": size, "mode": mode, "capability": name,
            "sha": PYTHIA_SHAS[size],
            "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None,
            "n_items": int(arrays["X"].shape[0]),
            "n_layers": int(arrays["X"].shape[1]),
        })
        print(f"[collect] DONE {size}/{mode}/{name} shape={arrays['X'].shape}", flush=True)


if __name__ == "__main__":
    main()
