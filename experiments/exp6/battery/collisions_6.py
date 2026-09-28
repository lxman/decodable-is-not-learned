# experiments/exp6/battery/collisions_6.py
"""The collision gate's index, sha-checked at load."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

INDEX_PATH = Path(__file__).resolve().parent / "data" / "bigbench_index_6.json"
INDEX_6_SHA256 = "d47c4a4c4057b7dfe7d0ef0feb789625ef1fda81307a30788bcc067e45ef2525"
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
        x = t.get("extra", [])
        if t.get("n_extra", 0) != len(x) or len(set(x)) != len(x):
            raise ValueError(f"index entry {task}: its extra table is inconsistent")
    return rec


def for_spec(spec) -> frozenset:
    t = load_index()["tasks"].get(spec.task)
    if t is None:
        raise ValueError(f"{spec.name}: task {spec.task!r} has no index entry")
    if t["kind"] != spec.collision_kind:
        raise ValueError(f"{spec.name}: collision kind {spec.collision_kind!r} "
                         f"against the index's {t['kind']!r}")
    return frozenset(t["keys"])


def extra_for_spec(spec) -> frozenset:
    """The task's extra table (the hashes of the parts of each BIG-bench
    input that are questions in their own right); empty for a task that
    has none."""
    t = load_index()["tasks"].get(spec.task)
    if t is None:
        raise ValueError(f"{spec.name}: task {spec.task!r} has no index entry")
    return frozenset(t.get("extra", []))
