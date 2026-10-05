"""Strict immutable normalized adapter boundary; no repository imports."""
from dataclasses import dataclass
from hashlib import sha256
import json
import re

FAMILIES = ("unscrambling", "deduction", "units", "shapes")
ARMS = ("q0", "q1", "q0s", "q1s")
PREDICTORS = ("pythia_1b", "olmo2_1b")
GRID = (40000, 80000, 120000, 160000, 200000, 240000, 280000,
        320000, 360000, 400000, 600000, 800000, 1000000, 1200000,
        1400000, 1600000, 1800000, 2000000, 2200000, 2400000,
        2600000, 2800000, 3000000, 3200000, 3400000, 3440000)
CAPS = {"number": 8, "word": 12, "span": 12}
TRAIN_SEED = 700100
TWIN_SEED = 700200
SEED_ROOT = "exp7/instrument/v1"


class Refusal(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Refusal(message)


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def digest(data):
    return sha256(data).hexdigest()


def pin(value):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value)
            and value != "0" * 64, "unset or invalid SHA256 pin")
    return value


def integer(value, lo, hi, label):
    require(type(value) is int and lo <= value <= hi, label)
    return value


def text(value, label):
    require(type(value) is str and bool(value.strip()) and "\x00" not in value,
            label)
    return value


def seed(namespace, *parts):
    """Length-delimited canonical JSON avoids separator/name collisions."""
    text(namespace, "empty seed namespace")
    return int.from_bytes(sha256(canonical([SEED_ROOT, namespace, list(parts)]))
                          .digest()[:16], "big")


def sampler_stream(family, arm, predictor, index, twin=False):
    require(family in FAMILIES and arm in ARMS, "unknown family/arm")
    require(predictor in PREDICTORS, "unknown predictor")
    require(not twin or predictor == "pythia_1b", "OLMo twin forbidden")
    integer(index, 0, 499, "item index")
    size = "1b" if predictor == "pythia_1b" else "olmo1b"
    mode = "untrained" if twin else "trained"
    s = TWIN_SEED if twin else TRAIN_SEED
    rung = f"exp7/{family}/{arm}"
    tag = f"exp3|{rung}|{size}|{mode}|s{s}|i{index}"
    stream = int.from_bytes(sha256(tag.encode()).digest()[:8], "big") & ((1 << 63) - 1)
    return {"rung": rung, "size": size, "mode": mode, "item_idx": index,
            "seeds": (s,), "draws_per_seed": 16 if twin else 64,
            "stream_seed": stream}


@dataclass(frozen=True)
class Pair:
    family: str
    index: int
    pair_id: str
    questions: tuple
    prompts: tuple
    targets: tuple
    answer_type: str
    nominal: str
    ordinal: int
    source_ids: tuple
    metadata_json: str


@dataclass(frozen=True)
class Battery:
    pairs: tuple
    certificate_sha256: str
    levels_sha256: str
    bytes_sha256: str

    def family(self, name):
        require(name in FAMILIES, "unknown family")
        return tuple(p for p in self.pairs if p.family == name)


def decode_battery(data, *, expected_sha256, certificate_sha256, levels_sha256,
                   expected_per_family=500):
    """Only production entry should call with literal 500; miniature API is explicit.

    This validates the normalized interface, NOT the independent oracles or
    mappings from feasibility artifacts. Those remain separate mandatory gates.
    """
    from .scoring import answer
    require(type(data) is bytes, "battery must be bytes")
    require(digest(data) == pin(expected_sha256), "battery hash mismatch")
    integer(expected_per_family, 1, 500, "pair count")
    obj = json.loads(data)
    require(type(obj) is dict and set(obj) == {
        "schema", "certificate_sha256", "levels_sha256", "pairs"}, "battery keys")
    require(obj["schema"] == "exp7.normalized-pairs.v1", "battery schema")
    require(obj["certificate_sha256"] == pin(certificate_sha256), "certificate pin")
    require(obj["levels_sha256"] == pin(levels_sha256), "levels pin")
    require(type(obj["pairs"]) is list, "pairs list")
    pairs, ids, questions, sources = [], set(), set(), set()
    keys = {"family", "index", "pair_id", "questions", "prompts", "targets",
            "answer_type", "nominal", "ordinal", "source_ids", "metadata"}
    for row in obj["pairs"]:
        require(type(row) is dict and set(row) == keys, "pair schema")
        f = row["family"]
        require(f in FAMILIES, "family")
        i = integer(row["index"], 0, expected_per_family - 1, "pair index")
        pid = text(row["pair_id"], "pair ID")
        require(pid == f"{f}:{i:04d}" and pid not in ids, "pair identity")
        ids.add(pid)
        require(type(row["questions"]) is dict and set(row["questions"]) == set(ARMS),
                "four questions required")
        require(type(row["prompts"]) is dict and set(row["prompts"]) == set(ARMS),
                "four prompts required")
        qs = tuple(text(row["questions"][a], "question") for a in ARMS)
        ps = tuple(text(row["prompts"][a], "prompt") for a in ARMS)
        require(len(set(qs)) == 4 and not set(qs) & questions, "duplicate question")
        require(len(set(ps)) == 4, "duplicate prompt within pair")
        questions.update(qs)
        require(type(row["targets"]) is list and len(row["targets"]) == 2,
                "two targets required")
        kind = row["answer_type"]
        require(kind in CAPS, "answer type")
        targets = tuple(text(a, "target") for a in row["targets"])
        normalized = tuple(answer(a, kind) for a in targets)
        require(len(set(normalized)) == 2, "normalized targets collide")
        require(type(row["source_ids"]) is list and len(row["source_ids"]) > 0,
                "source IDs required")
        ss = tuple(text(s, "source ID") for s in row["source_ids"])
        require(len(set(ss)) == len(ss), "duplicate source within pair")
        require(not {(f, s) for s in ss} & sources, "base sources reused")
        sources.update((f, s) for s in ss)
        require(type(row["metadata"]) is dict and row["metadata"], "metadata required")
        pairs.append(Pair(f, i, pid, qs, ps, targets, kind,
                          text(row["nominal"], "nominal signature"),
                          integer(row["ordinal"], 0, 1000000, "ordinal level"),
                          ss, canonical(row["metadata"]).decode("ascii")))
    expected = {(f, i) for f in FAMILIES for i in range(expected_per_family)}
    require({(p.family, p.index) for p in pairs} == expected and len(pairs) == len(expected),
            "battery coverage")
    require(len({s for p in pairs for s in p.prompts}) == len(pairs) * 4,
            "duplicate rendered prompt")
    return Battery(tuple(sorted(pairs, key=lambda p: (FAMILIES.index(p.family), p.index))),
                   certificate_sha256, levels_sha256, digest(data))
