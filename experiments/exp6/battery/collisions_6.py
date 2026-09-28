# experiments/exp6/battery/collisions_6.py
"""The collision gate's index, sha-checked at load."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

INDEX_PATH = Path(__file__).resolve().parent / "data" / "bigbench_index_6.json"
INDEX_6_SHA256 = "0970e986315d09946951683b056228629e821bbeeebec8fb565b60ef9297d94c"
BIGBENCH_COMMIT = "092b196c1f8f14a54bbc62f24759d43bde46dd3b"


@lru_cache(maxsize=1)
def load_index() -> dict:
    raw = INDEX_PATH.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != INDEX_6_SHA256:
        raise ValueError(f"{INDEX_PATH} hashes to {got}, pinned {INDEX_6_SHA256}")
    rec = json.loads(raw)
    if rec["commit"] != BIGBENCH_COMMIT:
        raise ValueError(f"index built at {rec['commit']}, pinned {BIGBENCH_COMMIT}")
    for task, t in rec["tasks"].items():
        if t["n_keys"] != len(t["keys"]) or len(set(t["keys"])) != len(t["keys"]):
            raise ValueError(f"index entry {task} is inconsistent")
    return rec


def for_spec(spec) -> frozenset:
    t = load_index()["tasks"].get(spec.task)
    if t is None:
        raise ValueError(f"{spec.name}: task {spec.task!r} has no index entry")
    if t["kind"] != spec.collision_kind:
        raise ValueError(f"{spec.name}: collision kind {spec.collision_kind!r} "
                         f"against the index's {t['kind']!r}")
    return frozenset(t["keys"])
