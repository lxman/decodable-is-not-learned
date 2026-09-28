# experiments/exp6/records_6.py
"""Exp 6 records: paths, writers, readers and the checks the analyzer
runs on every record it reads. One module, so the runners and the
synthetic worlds write through the SAME functions (2i F-1: a world must
carry the real shape, not a stub).

Layout under `<root>/results/`:

    predictor/<predictor>/<tier>/<rung>.json + .draws.jsonl.gz
    predictor/gate1p.json, predictor/predictor_6.json (the seal)
    predictor/HALTED                                a stage that failed its exit gate
    endpoint/<family>/stage1_final/<rung>.json      20 rungs
    endpoint/<family>/init/<rung>.json              20 rungs
    endpoint/<family>/_stage1_final.json, _init.json
    endpoint/gate1b.json, endpoint/rung_sets_6.json
    power_6.json
    hosts/<sha12>.json                              one per host
    sweep/<family>/gate1_<host12>.json              one per (family, host)
    sweep/<family>/gate1_<host12>/thin/<rung>.json, _thin.json
    sweep/<family>/gate1_<host12>/cand/<rung>.json, _cand.json
    sweep/<family>/step<N>/<rung>.json, _checkpoint.json
    sweep/<family>/HALTED, failed_steps/step<N>/    a gate that fired
    verdict.json

Nothing under results/ is ever overwritten or moved: a second host that
takes over a family's sweep writes its own gate directory.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path

from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import verify_6 as v6

PREREG_TAG_6 = "exp6-preregistered"
PREDICTOR_SEAL_TAG_6 = "exp6-predictor-sealed"
ENDPOINT_SEAL_TAG_6 = "exp6-endpoint-sealed"
STREAM_NAMESPACE = "exp3"          # exp3's sampler; one namespace since 3a
SAMPLING_DTYPE = "float32"
VERIFY_NOTE = ("verify_6: 2c normalize for number/word; whole line for "
               "span/sequence; first token for ipa; draw side total")

# ------------------------------------------------------------ predictors
# size: the label exp3's stream tag carries (the anchors' committed
# streams were drawn under exactly these labels)
PREDICTORS_6 = {
    "pythia_1b": {"size": "1b", "lineage": "pythia", "test": "A"},
    "pythia_410m": {"size": "410m", "lineage": "pythia", "test": None},
    "olmo2_1b": {"size": "olmo1b", "lineage": "olmo2", "test": "B"},
}
TEST_PREDICTOR = {"A": "pythia_1b", "B": "olmo2_1b"}
# tier -> shape. `rungs` names what the tier samples.
TIERS_6 = {
    "main": {"mode": "trained", "rungs": b6.RUNGS_6 + b6.ANCHORS_6},
    "pilot": {"mode": "trained", "rungs": b6.RUNGS_6, "seeds": (1000,), "dps": 8},
    "twin": {"mode": "untrained", "rungs": b6.RUNGS_6, "seeds": (0,), "dps": 64},
    "control": {"mode": "trained", "rungs": (b6.CONTROL_6,),
                "seeds": (0, 1, 2, 3), "dps": 8},
}
MAIN_SHAPE = {"pythia_1b": {"seeds": (0, 1, 2, 3), "dps": 64},
              "pythia_410m": {"seeds": (0, 1, 2, 3), "dps": 64},
              "olmo2_1b": {"seeds": (0,), "dps": 64}}
# which tiers each predictor runs
PREDICTOR_TIERS = {"pythia_1b": ("pilot", "main", "twin", "control"),
                   "pythia_410m": ("main", "control"),
                   "olmo2_1b": ("main",)}
LADDER_K = (64, 128, 192, 256)
ENDPOINT_WHICH_6 = ("stage1_final", "init")
# gate 1's two reads of the endpoint on a sweep host: `which` values
SWEEP_THIN, SWEEP_CAND = "sweep_thin", "sweep_cand"
GATE_READS_6 = {SWEEP_THIN: "thin", SWEEP_CAND: "cand"}


def tier_shape(predictor: str, tier: str) -> dict:
    if tier not in PREDICTOR_TIERS[predictor]:
        raise ValueError(f"{predictor} has no {tier!r} tier")
    t = dict(TIERS_6[tier])
    if tier == "main":
        t.update(MAIN_SHAPE[predictor])
    t["k"] = len(t["seeds"]) * t["dps"]
    return t


def predictor_units() -> list:
    """Every (predictor, tier, rung) the predictor stage samples."""
    return [(p, t, r) for p in PREDICTORS_6 for t in PREDICTOR_TIERS[p]
            for r in tier_shape(p, t)["rungs"]]


# ----------------------------------------------------------------- paths
def results(root) -> Path:
    return Path(root) / "results"


def tier_dir(root, predictor, tier) -> Path:
    return results(root) / "predictor" / predictor / tier


def tier_record_path(root, predictor, tier, rung) -> Path:
    return tier_dir(root, predictor, tier) / f"{rung}.json"


def tier_draws_path(root, predictor, tier, rung) -> Path:
    return tier_dir(root, predictor, tier) / f"{rung}.draws.jsonl.gz"


def tier_halt_path(root, predictor, tier, rung) -> Path:
    return tier_dir(root, predictor, tier) / f"{rung}.HALTED"


def predictor_halt_path(root) -> Path:
    return results(root) / "predictor" / "HALTED"


def gate1p_path(root) -> Path:
    return results(root) / "predictor" / "gate1p.json"


def seal_path(root) -> Path:
    return results(root) / "predictor" / "predictor_6.json"


def endpoint_dir(root, family, which) -> Path:
    if which not in ENDPOINT_WHICH_6:
        raise ValueError(which)
    return results(root) / "endpoint" / family / which


def endpoint_record_path(root, family, which, rung) -> Path:
    return endpoint_dir(root, family, which) / f"{rung}.json"


def endpoint_load_path(root, family, which) -> Path:
    return results(root) / "endpoint" / family / f"_{which}.json"


def gate1b_path(root) -> Path:
    return results(root) / "endpoint" / "gate1b.json"


def rung_sets_path(root) -> Path:
    return results(root) / "endpoint" / "rung_sets_6.json"


def power_path(root) -> Path:
    return results(root) / "power_6.json"


def sweep_dir(root, family) -> Path:
    return results(root) / "sweep" / family


def step_dir(root, family, step) -> Path:
    return sweep_dir(root, family) / f"step{int(step)}"


def sweep_record_path(root, family, step, rung) -> Path:
    return step_dir(root, family, step) / f"{rung}.json"


def checkpoint_path(root, family, step) -> Path:
    return step_dir(root, family, step) / "_checkpoint.json"


def gate1_path(root, family, host_sha256) -> Path:
    """One gate record per (family, host): every host that contributes
    sweep units to a family ran that family's gate itself."""
    return sweep_dir(root, family) / f"gate1_{host_sha256[:12]}.json"


def gate1_dir(root, family, host_sha256) -> Path:
    return sweep_dir(root, family) / f"gate1_{host_sha256[:12]}"


def gate_record_path(root, family, host_sha256, which, rung) -> Path:
    """A sweep host's own read of the endpoint through one loader path
    (`SWEEP_THIN` or `SWEEP_CAND`), kept so the analyzer re-derives the
    gate from bytes."""
    return gate1_dir(root, family, host_sha256) / GATE_READS_6[which] / f"{rung}.json"


def gate_load_path(root, family, host_sha256, which) -> Path:
    return gate1_dir(root, family, host_sha256) / f"_{GATE_READS_6[which]}.json"


def endpoint_halt_path(root) -> Path:
    return results(root) / "endpoint" / "HALTED"


def sweep_halt_path(root, family) -> Path:
    return sweep_dir(root, family) / "HALTED"


def halted_step_dir(root, family, step) -> Path:
    """Where a step that FAILED its anchor gate leaves its records: the
    evidence is kept, and the step directory stays incomplete. (Not
    `halted/`: beside the marker `HALTED` that name is the same name on
    a case-insensitive filesystem, and the Mac's is one.)"""
    return sweep_dir(root, family) / "failed_steps" / f"step{int(step)}"


def verdict_path(root) -> Path:
    return results(root) / "verdict.json"


def halt_markers(root) -> list:
    base = results(root)
    found = set(base.glob("predictor/*/*/*.HALTED"))
    found |= set(base.glob("predictor/*/*/*.HALTED.jsonl.gz"))
    found |= set(base.glob("predictor/HALTED"))
    found |= set(base.glob("sweep/*/HALTED"))
    found |= set(base.glob("sweep/*/failed_steps"))   # evidence, marker not yet
    found |= set(base.glob("endpoint/HALTED"))
    return sorted(found)


# ------------------------------------------------------------------- io
def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj) -> None:
    """Whole or not at all: written beside the path and renamed over it,
    so a kill leaves the file that was there, or none, never a torn one."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    os.replace(tmp, path)


def whole(path) -> bool:
    """Is the record there? A file that exists and does not parse as a
    JSON object is a TORN record: it is refused, and no unit is resumed
    over it (a completeness check that asked only whether the file
    exists would have resumed past it)."""
    path = Path(path)
    if not path.exists():
        return False
    try:
        ok = isinstance(json.loads(path.read_text(encoding="utf-8")), dict)
    except (OSError, ValueError):
        ok = False
    if not ok:
        raise RuntimeError(f"{path}: torn record — a unit is not resumed over it")
    return True


def read_json(path) -> dict:
    return json.loads(Path(path).read_text())


def write_draws(path, rows) -> None:
    """exp3's draws format: one JSON line per item, keys sorted, gzip
    with mtime 0 so the same rows give the same bytes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
            for row in rows:
                f.write((json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))


def read_draws(path, *, seeds, dps, n_items=b6.N_ITEMS) -> list:
    """Rows in item order with coverage PINNED: exactly `n_items` items,
    exactly the seed set, exactly `dps` strings per seed."""
    rows = []
    with gzip.open(Path(path), "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    want_seeds = {str(s) for s in seeds}
    if [r.get("item") for r in rows] != list(range(n_items)):
        raise ValueError(f"{path}: items are not 0..{n_items - 1} in order")
    for r in rows:
        if set(r["draws"]) != want_seeds:
            raise ValueError(f"{path}: item {r['item']} seeds {sorted(r['draws'])} "
                             f"against {sorted(want_seeds)}")
        for s in want_seeds:
            d = r["draws"][s]
            if len(d) != dps or not all(isinstance(x, str) for x in d):
                raise ValueError(f"{path}: item {r['item']} seed {s} carries "
                                 f"{len(d)} draws against {dps}")
    return rows


# ------------------------------------------------------- predictor side
def bits_of(rows, cap, *, seeds) -> list:
    """N_ITEMS lists of verified bits in SEED ORDER (every ladder prefix
    and every 64-draw block reads this order)."""
    at = cap["answer_type"]
    out = []
    for row in rows:
        ans = cap["eval_items"][row["item"]]["answer"]
        b = []
        for s in seeds:
            b.extend(int(v6.verify_6(d, ans, at)) for d in row["draws"][str(s)])
        out.append(b)
    return out


def counts_of(bits, k=None) -> list:
    return [int(sum(b if k is None else b[:k])) for b in bits]


def block_counts(bits, block: int, dps: int = 64) -> list:
    return [int(sum(b[block * dps:(block + 1) * dps])) for b in bits]


def tallies_from_bits(bits, *, seeds, dps: int) -> dict:
    """Per-seed tallies from bits in SEED ORDER (`bits_of`'s output)."""
    out = {}
    for j, s in enumerate(seeds):
        out[str(s)] = {"verified": int(sum(sum(b[j * dps:(j + 1) * dps])
                                           for b in bits)),
                       "n_draws": len(bits) * dps}
    return out


def tallies_of(rows, cap, *, seeds) -> dict:
    dps = len(rows[0]["draws"][str(seeds[0])]) if rows else 0
    return tallies_from_bits(bits_of(rows, cap, seeds=seeds), seeds=seeds, dps=dps)


TIER_RECORD_PINS = ("rung", "predictor", "tier", "size", "mode", "n_items",
                    "answer_type", "n_shots", "dtype", "items_sha256",
                    "stream_namespace", "seeds", "draws_per_seed", "k_total",
                    "max_new_tokens", "temperature", "truncation", "prereg_tag",
                    "draws_file")


def tier_record_expected(predictor, tier, rung, cap) -> dict:
    t = tier_shape(predictor, tier)
    return {"rung": rung, "predictor": predictor, "tier": tier,
            "size": PREDICTORS_6[predictor]["size"], "mode": t["mode"],
            "n_items": b6.N_ITEMS, "answer_type": cap["answer_type"],
            "n_shots": b6.N_SHOTS, "dtype": SAMPLING_DTYPE,
            "items_sha256": cap["items_sha256"],
            "stream_namespace": STREAM_NAMESPACE, "seeds": list(t["seeds"]),
            "draws_per_seed": t["dps"], "k_total": t["k"],
            "max_new_tokens": b6.max_new_tokens_6(rung), "temperature": 1.0,
            "truncation": "none", "prereg_tag": PREREG_TAG_6,
            "draws_file": tier_draws_path("", predictor, tier, rung).name}


def tier_record(*, predictor, tier, rung, cap, rows, model, stack, git_sha,
                seconds, draws_sha256, bits=None) -> dict:
    """`model`: {"repo","commit","model_sha"} as the loader measured it."""
    t = tier_shape(predictor, tier)
    rec = tier_record_expected(predictor, tier, rung, cap)
    if bits is None:
        bits = bits_of(rows, cap, seeds=t["seeds"])
    rec.update({"answers": [str(it["answer"]) for it in cap["eval_items"]],
                "repo": model["repo"], "commit": model["commit"],
                "model_sha": model["model_sha"],
                "untrained_seed": 0 if t["mode"] == "untrained" else None,
                "per_seed_tallies": tallies_from_bits(bits, seeds=t["seeds"],
                                                      dps=t["dps"]),
                "draws_sha256": draws_sha256, "verify": VERIFY_NOTE,
                "stack": stack, "git_sha": git_sha,
                "seconds": round(float(seconds), 1)})
    return rec


def tier_record_failures(rec, *, predictor, tier, rung, cap, bits, model_pin,
                         draws_sha256) -> list:
    """Every field of a tier record MEASURED against what it must be:
    the shape against the frozen tables, the answers against the item
    file, the tallies against the draws (`bits` = `bits_of` the draws on
    disk), the model against its pin, the draws' sha against the file
    on disk (2i F-1)."""
    bad = []
    label = f"6 predictor {predictor}/{tier}/{rung}"
    want = tier_record_expected(predictor, tier, rung, cap)
    for k in TIER_RECORD_PINS:
        if rec.get(k) != want[k]:
            bad.append(f"{label}: {k} {rec.get(k)!r} against {want[k]!r}")
    if rec.get("answers") != [str(it["answer"]) for it in cap["eval_items"]]:
        bad.append(f"{label}: the answers column is not the item file's")
    t = tier_shape(predictor, tier)
    if rec.get("per_seed_tallies") != tallies_from_bits(bits, seeds=t["seeds"],
                                                        dps=t["dps"]):
        bad.append(f"{label}: the tallies do not re-derive from the draws")
    for k in ("repo", "commit"):
        if rec.get(k) != model_pin[k]:
            bad.append(f"{label}: {k} {rec.get(k)!r} against the pin {model_pin[k]!r}")
    if model_pin.get("model_sha") is not None and \
            rec.get("model_sha") != model_pin["model_sha"]:
        bad.append(f"{label}: model_sha {rec.get('model_sha')!r} against the pin")
    if not rec.get("model_sha"):
        bad.append(f"{label}: no model_sha")
    if rec.get("draws_sha256") != draws_sha256:
        bad.append(f"{label}: draws_sha256 is not the draws file's")
    want_seed = 0 if t["mode"] == "untrained" else None
    if rec.get("untrained_seed") != want_seed:
        bad.append(f"{label}: untrained_seed {rec.get('untrained_seed')!r}")
    return bad


def diff_draws(rows, committed, *, seeds) -> dict:
    """Byte identity of two row sets over `seeds`, with coverage:
    returns {"items_compared","draws_compared","n_diffs","first"}."""
    by_item = {r["item"]: r for r in committed}
    n_items = n_draws = n_diffs = 0
    first = None
    for r in rows:
        c = by_item.get(r["item"])
        if c is None:
            raise ValueError(f"item {r['item']} has no committed row")
        n_items += 1
        for s in seeds:
            a, b = r["draws"][str(s)], c["draws"][str(s)]
            if len(a) != len(b):
                raise ValueError(f"item {r['item']} seed {s}: {len(a)} draws "
                                 f"against the committed {len(b)}")
            for j, (x, y) in enumerate(zip(a, b)):
                n_draws += 1
                if x != y:
                    n_diffs += 1
                    if first is None:
                        first = {"item": r["item"], "seed": s, "draw": j}
    return {"items_compared": n_items, "draws_compared": n_draws,
            "n_diffs": n_diffs, "first": first}


# --------------------------------------------------------- outcome side
def evaluate_items_6(runner, cap: dict) -> dict:
    """2g's `evaluate_items` with Exp 6's budgets and criterion (the
    frozen one reads 2c's MAX_NEW_TOKENS by answer type and knows two
    types). On an anchor it is the frozen function's arithmetic: same
    prompts, same budget, same normalizer."""
    h = v6.harness_2c()
    rung = cap["name"]
    shots = [tuple(s) for s in cap["shots"]][:b6.N_SHOTS]
    prompts = [h.render_prompt(it["question"], shots) for it in cap["eval_items"]]
    preds = runner.generate(prompts, b6.max_new_tokens_6(rung))
    if len(preds) != len(cap["eval_items"]):
        raise RuntimeError("generate returned the wrong number of continuations")
    bits = [int(v6.verify_6(p, it["answer"], cap["answer_type"]))
            for p, it in zip(preds, cap["eval_items"])]
    return {"correct": int(sum(bits)), "bits": bits, "continuations": list(preds)}


UNIT_RECORD_PINS = ("rung", "family", "items_sha256", "n", "max_new_tokens",
                    "n_shots", "dtype", "batch_size", "render", "answer_type",
                    "prereg_tag")


def unit_record_expected(family, rung, cap) -> dict:
    return {"rung": rung, "family": family, "items_sha256": cap["items_sha256"],
            "n": b6.N_ITEMS, "max_new_tokens": b6.max_new_tokens_6(rung),
            "n_shots": b6.N_SHOTS, "dtype": fm.DTYPE_6,
            "batch_size": fm.BATCH_SIZE_6, "render": fm.RENDER_6[family],
            "answer_type": cap["answer_type"], "prereg_tag": PREREG_TAG_6}


def unit_record(*, family, rung, cap, ev, load, host_sha256, seal_sha256,
                stack, git_sha, seconds, step=None, which=None,
                endpoint_sha256=None) -> dict:
    """One rung at one checkpoint. Exactly one of `step` (a sweep unit)
    and `which` (an endpoint-stage unit). `load` is the loader's
    measured record (`load_record`)."""
    if (step is None) == (which is None):
        raise ValueError("unit_record: exactly one of step and which")
    rec = unit_record_expected(family, rung, cap)
    rec.update({"repo": load["repo"], "revision": load["revision"],
                "commit": load["commit"], "kind": load["kind"],
                "weight_sha256": load["digest"],
                "correct": int(ev["correct"]), "bits": list(ev["bits"]),
                "continuations": list(ev["continuations"]),
                "verify": VERIFY_NOTE, "host_sha256": host_sha256,
                "predictor_sha256": seal_sha256, "stack": stack,
                "git_sha": git_sha, "seconds": round(float(seconds), 2)})
    if step is not None:
        rec["step"] = int(step)
    else:
        rec["which"] = which
    if step is not None or which in GATE_READS_6:
        rec["endpoint_sha256"] = endpoint_sha256
    return rec


def load_record(*, family, key, entry, info, device, host_sha256, seconds,
                n_nonfinite) -> dict:
    """What the loader MEASURED for one model load (`_checkpoint.json`
    in a sweep step; `_stage1_final.json` / `_init.json` at the endpoint
    stage). `key` is the step, "stage1_final" or "init"."""
    rec = {"family": family, "key": key, "repo": fm.repo(family),
           "revision": entry.get("revision"), "commit": entry.get("commit"),
           "config_commit": entry.get("config_commit"),
           "kind": entry.get("kind", "thin-loader"),
           "sha256": dict(info.get("sha256", {})),
           "loading_info": info.get("loading_info"),
           "digest": info.get("tensor_digest"), "device": device,
           "dtype": fm.DTYPE_6, "host_sha256": host_sha256,
           "n_nonfinite_logits": int(n_nonfinite),
           "download_seconds": round(float(seconds), 1)}
    for k in ("config_eos_token_id", "generation_eos_token_id", "seed"):
        if k in info:
            rec[k] = info[k]
    return rec


def unit_record_failures(rec, *, family, rung, cap, load, seal_sha256,
                         host_sha256=None, step=None, which=None,
                         endpoint_sha256=None) -> list:
    bad = []
    where = which if which is not None else f"step{step}"
    label = f"6 outcome {family}/{where}/{rung}"
    want = unit_record_expected(family, rung, cap)
    for k in UNIT_RECORD_PINS:
        if rec.get(k) != want[k]:
            bad.append(f"{label}: {k} {rec.get(k)!r} against {want[k]!r}")
    bits, conts = rec.get("bits"), rec.get("continuations")
    if not isinstance(bits, list) or len(bits) != b6.N_ITEMS or \
            not isinstance(conts, list) or len(conts) != b6.N_ITEMS:
        return bad + [f"{label}: bits/continuations are not {b6.N_ITEMS} long"]
    if not all(isinstance(c, str) for c in conts):
        return bad + [f"{label}: a continuation is not a string"]
    redo = [int(v6.verify_6(c, it["answer"], cap["answer_type"]))
            for c, it in zip(conts, cap["eval_items"])]
    if redo != bits:
        bad.append(f"{label}: the bits do not re-derive from the continuations")
    if rec.get("correct") != sum(redo):
        bad.append(f"{label}: correct {rec.get('correct')!r} against {sum(redo)}")
    for k, lk in (("commit", "commit"), ("revision", "revision"),
                  ("weight_sha256", "digest"), ("repo", "repo"), ("kind", "kind")):
        if rec.get(k) != load.get(lk):
            bad.append(f"{label}: {k} {rec.get(k)!r} against the load record's "
                       f"{load.get(lk)!r}")
    if not rec.get("weight_sha256"):
        bad.append(f"{label}: no tensor digest")
    if rec.get("predictor_sha256") != seal_sha256:
        bad.append(f"{label}: predictor_sha256 is not the predictor seal's")
    if host_sha256 is not None and rec.get("host_sha256") != host_sha256:
        bad.append(f"{label}: host_sha256 is not the host record's")
    if step is not None:
        if rec.get("step") != int(step) or "which" in rec:
            bad.append(f"{label}: step {rec.get('step')!r}")
    else:
        if rec.get("which") != which or "step" in rec:
            bad.append(f"{label}: which {rec.get('which')!r}")
    if step is not None or which in GATE_READS_6:
        if rec.get("endpoint_sha256") != endpoint_sha256:
            bad.append(f"{label}: endpoint_sha256 is not the sealed endpoint's")
    return bad


def load_record_failures(rec, *, family, key, entry, host_sha256=None) -> list:
    bad = []
    label = f"6 load {family}/{key}"
    want = {"family": family, "key": key, "repo": fm.repo(family),
            "revision": entry.get("revision"), "commit": entry.get("commit"),
            "dtype": fm.DTYPE_6}
    for k, v in want.items():
        if rec.get(k) != v:
            bad.append(f"{label}: {k} {rec.get(k)!r} against {v!r}")
    if not rec.get("digest"):
        bad.append(f"{label}: no tensor digest")
    if host_sha256 is not None and rec.get("host_sha256") != host_sha256:
        bad.append(f"{label}: host_sha256 is not the host record's")
    if not isinstance(rec.get("n_nonfinite_logits"), int):
        bad.append(f"{label}: finiteness was not measured")
    if entry.get("kind") == "from_config":
        if rec.get("seed") != entry.get("seed"):
            bad.append(f"{label}: twin seed {rec.get('seed')!r}")
    else:
        li = rec.get("loading_info") or {}
        if any(li.get(k) for k in ("missing_keys", "unexpected_keys",
                                   "mismatched_keys")):
            bad.append(f"{label}: loading_info reports key mismatches {li}")
        shas = rec.get("sha256") or {}
        for name, sha in (entry.get("lfs_sha256") or {}).items():
            if rec.get("kind") != "thin-loader" and shas.get(name) != sha:
                bad.append(f"{label}: {name} sha is not the manifest's")
    if fm.RENDER_6[family] == "bos":
        from experiments.exp2n import battery_2n as bn
        if rec.get("generation_eos_token_id") != bn.EOS_STOP_ID_2N:
            bad.append(f"{label}: the stop id was not overridden "
                       f"({rec.get('generation_eos_token_id')!r})")
    return bad


def composite_sha(files: dict) -> str:
    """The seal's sha over a {relative path: sha256} table."""
    lines = "\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))
    return hashlib.sha256(lines.encode()).hexdigest()
