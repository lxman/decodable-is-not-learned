"""Re-derivation from raw strings against an INDEPENDENT expected unit.

The trusted construction of ExpectedUnit from tag-bound battery/model/host
receipts is intentionally a separate, still-missing production task.
"""
from dataclasses import dataclass
import json
from .contract import ARMS, canonical, digest, integer, pin, require
from .scoring import answer, normalize


def strict_json(data):
    def pairs(values):
        out = {}
        for key, value in values:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError(f"nonfinite JSON number {value}")
    return json.loads(data, object_pairs_hook=pairs, parse_constant=nonfinite)


@dataclass(frozen=True)
class Address:
    family: str
    pair_id: str
    index: int
    arm: str
    prompt_sha256: str
    stream_seed: object
    targets: tuple
    answer_type: str

    def __post_init__(self):
        require(self.arm in ARMS, "address arm")
        integer(self.index, 0, 499, "address index")
        pin(self.prompt_sha256)
        require(self.stream_seed is None or
                (type(self.stream_seed) is int and 0 <= self.stream_seed < (1 << 63)), "stream seed")
        require(len(self.targets) == 2 and
                answer(self.targets[0], self.answer_type) != answer(self.targets[1], self.answer_type),
                "address distinct normalized targets")

    def public(self):
        return {"family": self.family, "pair_id": self.pair_id, "index": self.index,
                "arm": self.arm, "prompt_sha256": self.prompt_sha256,
                "stream_seed": self.stream_seed}


CONTEXT_KEYS = {"battery_sha256", "normalizer_sha256", "source_manifest_sha256",
                "code_manifest_sha256", "host_receipt_sha256", "host_id",
                "launch_git_commit", "prereg_tag_object", "projection_commit",
                "predictor_seal_sha256", "power_sha256", "model"}
MODEL_KEYS = {"repo", "revision_commit", "tensor_digest", "config_sha256",
              "tokenizer_files_sha256", "render", "terminal_ids", "dtype", "init_seed"}


@dataclass(frozen=True)
class ExpectedUnit:
    kind: str
    unit_id: str
    addresses: tuple
    k: int
    context_json: str

    def __post_init__(self):
        require(self.kind in ("trained", "twin", "outcome"), "unit kind")
        require(self.k == {"trained": 64, "twin": 16, "outcome": 1}[self.kind], "unit budget")
        require(type(self.unit_id) is str and self.unit_id, "unit identity")
        require(self.addresses and all(isinstance(a, Address) for a in self.addresses), "unit addresses")
        require(len({canonical(a.public()) for a in self.addresses}) == len(self.addresses),
                "duplicate expected address")
        if self.kind != "outcome":
            streams = [a.stream_seed for a in self.addresses]
            require(None not in streams and len(set(streams)) == len(streams), "shared sampling stream")
        else:
            require(all(a.stream_seed is None for a in self.addresses), "greedy stream must be null")
        ctx = strict_json(self.context_json)
        require(type(ctx) is dict and set(ctx) == CONTEXT_KEYS, "context schema")
        for key in CONTEXT_KEYS - {"model", "predictor_seal_sha256", "power_sha256",
                                   "host_id", "launch_git_commit", "prereg_tag_object", "projection_commit"}:
            pin(ctx[key])
        for key in ("host_id", "launch_git_commit", "prereg_tag_object", "projection_commit"):
            require(type(ctx[key]) is str and ctx[key], f"missing {key}")
        for key in ("predictor_seal_sha256", "power_sha256"):
            if self.kind == "outcome":
                pin(ctx[key])
            else:
                require(ctx[key] is None, f"premature {key}")
        m = ctx["model"]
        require(type(m) is dict and set(m) == MODEL_KEYS, "model context schema")
        for key in ("tensor_digest", "config_sha256", "tokenizer_files_sha256"):
            pin(m[key])
        require(m["dtype"] == ("float16" if self.kind == "outcome" else "float32"), "dtype")
        require(m["render"] == "plain", "render")
        require(type(m["terminal_ids"]) is list and m["terminal_ids"] and
                all(type(i) is int and i >= 0 for i in m["terminal_ids"]), "terminal IDs")
        require(len(set(m["terminal_ids"])) == len(m["terminal_ids"]), "duplicate terminal ID")
        require(type(m["repo"]) is str and m["repo"] and
                type(m["revision_commit"]) is str and m["revision_commit"], "model identity")
        if self.kind == "twin":
            integer(m["init_seed"], 0, (1 << 63) - 1, "twin initialization seed")
        else:
            require(m["init_seed"] is None, "trained init seed")


def rederive(raw, expected):
    require(isinstance(expected, ExpectedUnit) and type(raw) is bytes, "raw unit types")
    lines = raw.splitlines()
    require(len(lines) == len(expected.addresses) and raw.endswith(b"\n"), "raw row coverage")
    counts = []
    for line, address in zip(lines, expected.addresses):
        row = strict_json(line)
        fields = address.public()
        require(type(row) is dict and set(row) == set(fields) | {"draws"}, "raw row schema")
        require(canonical({k: row[k] for k in fields}) == canonical(fields),
                "raw address/provenance/order mismatch")
        draws = row["draws"]
        require(type(draws) is list and len(draws) == expected.k
                and all(type(s) is str for s in draws), "raw draw coverage")
        a0, a1 = (answer(a, address.answer_type) for a in address.targets)
        ns = [normalize(v, address.answer_type) for v in draws]
        counts.append((ns.count(a0), ns.count(a1)))
    return {"rows": len(lines), "n_draws": len(lines) * expected.k,
            "raw_sha256": digest(raw), "counts_sha256": digest(canonical(counts)),
            "address_sha256": digest(canonical([a.public() for a in expected.addresses]))}


def build_record(raw, expected):
    return {"schema": "exp7.raw-unit.v1", "kind": expected.kind, "unit_id": expected.unit_id,
            "k": expected.k, "context": strict_json(expected.context_json),
            **rederive(raw, expected)}


def validate_record(raw, record, expected):
    require(type(record) is dict and canonical(record) == canonical(build_record(raw, expected)),
            "record does not rederive against independently bound expectation")
