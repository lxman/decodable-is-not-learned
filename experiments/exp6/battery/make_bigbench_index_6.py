# experiments/exp6/battery/make_bigbench_index_6.py
"""The collision index (design §2): sha256 of every BIG-bench string a
generated item could reproduce, at ONE pinned commit of google/BIG-bench.
Hashes only — no BIG-bench text is vendored. Built once; the generators
read `data/bigbench_index_6.json` (sha-pinned in collisions_6.py)."""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
OUT = DATA / "bigbench_index_6.json"
BIGBENCH_COMMIT = "092b196c1f8f14a54bbc62f24759d43bde46dd3b"
RAW = ("https://raw.githubusercontent.com/google/BIG-bench/{commit}/bigbench/"
       "benchmark_tasks/{path}/task.json")
# task id -> (collision kind, task.json paths)
SOURCES = {
    "modified_arithmetic": ("input", (
        "modified_arithmetic/three_digit_addition_plus_one",
        "modified_arithmetic/three_digit_subtraction_plus_one",
        "modified_arithmetic/two_digit_multiplication_plus_one")),
    "word_unscrambling": ("input", ("word_unscrambling",)),
    "word_sorting": ("input", ("word_sorting",)),
    "international_phonetic_alphabet_transliterate": (
        "input", ("international_phonetic_alphabet_transliterate",)),
    "logical_deduction": ("input", ("logical_deduction/three_objects",
                                    "logical_deduction/five_objects")),
    "ascii_word_recognition": ("target", ("ascii_word_recognition",)),
    "geometric_shapes": ("input", ("geometric_shapes",)),
    "temporal_sequences": ("input", ("temporal_sequences",)),
    "cs_algorithms": ("input", ("cs_algorithms/lcs",)),
    "unit_interpretation": ("input", ("unit_interpretation/lv1",
                                      "unit_interpretation/lv2")),
}


def local_name(path: str) -> str:
    return path.replace("/", "__") + ".json"


def fetch(dest: Path, commit: str = BIGBENCH_COMMIT) -> None:
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for _, paths in SOURCES.values():
        for path in paths:
            out = dest / local_name(path)
            if out.exists():
                continue
            with urllib.request.urlopen(RAW.format(commit=commit, path=path)) as r:
                out.write_bytes(r.read())


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build(src: Path, out: Path = OUT) -> dict:
    src = Path(src)
    tasks = {}
    for task, (kind, paths) in SOURCES.items():
        keys, files = set(), {}
        for path in paths:
            raw = (src / local_name(path)).read_bytes()
            files[path] = hashlib.sha256(raw).hexdigest()
            for ex in json.loads(raw)["examples"]:
                if kind == "input":
                    keys.add(_sha(ex["input"]))
                else:
                    t = ex["target"]
                    for one in (t if isinstance(t, list) else [t]):
                        keys.add(_sha(one))
        tasks[task] = {"kind": kind, "files": files, "n_keys": len(keys),
                       "keys": sorted(keys)}
    rec = {"repo": "google/BIG-bench", "commit": BIGBENCH_COMMIT, "tasks": tasks}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rec, indent=0, sort_keys=True) + "\n"
    Path(out).write_text(text)
    return {"sha256": hashlib.sha256(text.encode()).hexdigest(),
            "n_keys": {t: v["n_keys"] for t, v in tasks.items()}}


if __name__ == "__main__":
    src = Path(sys.argv[1])
    fetch(src)
    print(json.dumps(build(src), indent=1))
