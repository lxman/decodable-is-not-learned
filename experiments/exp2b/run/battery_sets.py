"""Torch-free battery-set constants shared by collection (GPU side) and the
probe runner (CPU side, incl. distributed workers with no torch install).

ctrl_next_letter dropped per Exp 2 M1; entity_track is the known-present gate
capability (2b's own M1-excluded task, 1b margin .688 — ledgered at M2 build).
"""

from __future__ import annotations

import json
from pathlib import Path

CONTROLS = ["ctrl_copy"]
GATE_CAPS = ["entity_track"]


def scored_battery() -> list[str]:
    from battery.base import ITEMS_DIR
    return json.loads((ITEMS_DIR / "scored_battery.json").read_text())
