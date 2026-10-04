"""Fixed-scope descriptive reuse of Exp 5. CLI production is write-once.

--validate-only re-scores selected continuations and checks provenance, but
does not call summarize, form size comparisons, or draw a bootstrap sample.
No predecessor analyzer run(), model loader, or network call is used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.abc
import importlib.machinery
import json
import math
import re
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = "/opt/homebrew/bin/git"
SOURCE = "6deb2d55fd170cf76cae325ff41e4c750b2b775f"
SIZES = ("410m", "1b", "1.4b", "2.8b", "6.9b", "12b")
STEPS = (1000, 2000, 4000, 5000, 6000, 8000, 16000, 32000, 100000, 143000)
TOKENS_PER_STEP = 2_097_152
N_BOOT, SEED = 10_000, 20261004
TYPES = ("arithmetic", "option", "string")
OWN = tuple(f"analyses/matched-token/{name}" for name in
            ("analyze.py", "test_analyze.py", "verify_outputs.py", "PLAN.md"))


class Refusal(ValueError):
    """Missing, changed, malformed or inconsistent evidence; no partial analysis."""


def require(condition, message):
    if not condition:
        raise Refusal(message)


def require_clean(failures):
    require(not failures, "; ".join(failures))


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def git(root, *args):
    return subprocess.check_output([GIT, "-C", str(root), *args], stderr=subprocess.PIPE)


class Bindings:
    """Compare raw working bytes to the pinned Git tree; record SHA256 too.

    Git's blob object ID includes its type/length header. Comparing this locally
    avoids a subprocess for each of the 2,220 selected unit files. Every bound
    file is re-read at exit, independently of the cached entry hashes.
    """
    def __init__(self, root, commit):
        self.root = Path(root).resolve()
        self.commit = git(self.root, "rev-parse", f"{commit}^{{commit}}").decode().strip()
        self.tree = {}
        for entry in git(self.root, "ls-tree", "-rz", self.commit).split(b"\0"):
            if entry:
                meta, path = entry.split(b"\t", 1)
                mode, kind, oid = meta.decode().split()
                if kind == "blob" and mode in ("100644", "100755"):
                    self.tree[path.decode()] = oid
        self.files = {}

    def bind(self, path):
        p = Path(path).absolute()
        require(p.resolve() == p, f"binding refuses symlink: {p}")
        rel = p.relative_to(self.root).as_posix()
        require(rel in self.tree, f"binding: {rel} absent from {self.commit}")
        raw = p.read_bytes()
        oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(oid == self.tree[rel], f"binding mismatch: {rel} against {self.commit}")
        record = {"git_blob": oid, "sha256": sha256(raw), "bytes": len(raw)}
        if rel in self.files:
            require(record == self.files[rel], f"binding changed during run: {rel}")
        self.files[rel] = record
        return record

    def recheck(self):
        for rel in tuple(self.files):
            self.bind(self.root / rel)


@contextmanager
def pinned_imports(binding):
    """Bind repository source BEFORE exec, compile source rather than trust pyc."""
    class Loader(importlib.machinery.SourceFileLoader):
        def get_code(self, fullname):
            binding.bind(self.path)
            raw = Path(self.path).read_bytes()
            require(sha256(raw) == binding.files[Path(self.path).relative_to(binding.root).as_posix()]["sha256"],
                    f"module changed before compile: {self.path}")
            return compile(raw, self.path, "exec", dont_inherit=True)

    class Finder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            if spec and spec.origin and Path(spec.origin).is_relative_to(binding.root):
                require(spec.origin.endswith(".py"), f"non-source repository import: {spec.origin}")
                binding.bind(spec.origin)
                spec.loader = Loader(fullname, spec.origin)
            return spec

    finder = Finder()
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)


def check_imported(source, own):
    for mod in tuple(sys.modules.values()):
        filename = getattr(mod, "__file__", None)
        if not filename:
            continue
        p = Path(filename).absolute()
        if p.is_relative_to(source.root):
            rel = p.relative_to(source.root).as_posix()
            (own if rel in OWN else source).bind(p)


@dataclass
class Data:
    sizes: tuple
    steps: tuple
    rungs: tuple
    family_of: dict
    type_of: dict
    params: tuple
    floors: dict
    thresholds: dict
    bits: np.ndarray  # checkpoint, size, rung, item


def require_binary_record(rec, n):
    bits, conts = rec.get("bits"), rec.get("continuations")
    require(isinstance(bits, list) and len(bits) == n and
            all(type(b) is int and b in (0, 1) for b in bits), "bits must be binary integers with full coverage")
    require(isinstance(conts, list) and len(conts) == n and
            all(isinstance(c, str) for c in conts), "continuations must be strings with full coverage")
    require(type(rec.get("correct")) is int and rec["correct"] == sum(bits), "correct != sum(bits)")


def validate_unit(records, directory, *, size, step, entry, battery, verify, host):
    """One already byte-bound unit, using the frozen contracts plus cross-links."""
    from experiments.exp5 import battery_5 as b5
    from experiments.exp2d import battery_2d as bt
    unit, ck, loss = (records[n] for n in ("_unit.json", "_checkpoint.json", "_loss.json"))
    require_clean(b5.unit_record_failures_5(unit, directory))
    require_clean(b5.checkpoint_record_failures_5(ck, size=size, step=step, entry=entry))
    require_clean(b5._same_host(ck, host, f"{size}/step{step}/_checkpoint"))
    require_clean(b5.loss_record_failures_5(loss, size=size, step=step, host=host,
                  slice_sha=b5.SLICE_SHA256_5, require_finite=True))
    require(b5.loss_is_finite_5(loss) and loss.get("n_nonfinite") == 0 and
            all(isinstance(x, (int, float)) and math.isfinite(x) for x in loss["per_doc_loss"]),
            f"{size}/step{step}: nonfinite measured losses")
    require(len(loss["per_doc_loss"]) == loss["n_docs"], "per-doc loss coverage")
    for rec in (unit, loss):
        require(rec.get("size") == size and rec.get("step") == step, "unit/loss identity")
    require(unit.get("prereg_tag") == b5.PREREG_TAG_5 and unit.get("why") == ck.get("why")
            and bool(unit.get("why")), "unit/checkpoint purpose or tag mismatch")
    require(unit.get("host_sha256") == host["sha256"], "unit host mismatch")
    for k, want in (("digest", ck["digest"]), ("loss", loss["loss"]),
                    ("finite", True), ("n_nonfinite", 0)):
        require(unit.get(k) == want, f"unit {k} differs from measured record")
    require(re.fullmatch(r"[0-9a-f]{40}", unit.get("git_sha", "")) is not None,
            "unit collection git SHA missing")
    require(all(rec.get("git_sha") == unit["git_sha"] for rec in records.values()),
            "within-unit collection git SHA inconsistency")
    config = f"{b5.REPO_OF_5[size]}@{b5.MAIN_SHA_5[size]}"
    # Exp 5 hashes EVERY downloaded file, including non-LFS shard indices.
    # The frozen checkpoint contract above compares all LFS values to the manifest.
    require(ck.get("files") == entry["files"] and set(ck["sha256"]) == set(entry["files"]) and
            all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                for value in ck["sha256"].values()),
            "checkpoint payload manifest inconsistency")
    require(ck.get("config_source") == config and ck.get("tokenizer_source") == config,
            "checkpoint config/tokenizer provenance")
    require(type(ck["n_params"]) is int and ck["n_params"] > 0, "parameter count must be positive integer")
    bits = []
    for r in bt.RUNGS:
        rec = records[f"{r}.json"]
        require_binary_record(rec, bt.N_ITEMS)
        require_clean(b5.rung_record_failures_5(rec, size=size, step=step, rung=r,
                      cap=battery[r], entry=entry, verify_fn=verify, host=host))
        for k in ("revision", "kind", "files", "config_source", "tokenizer_source"):
            require(rec.get(k) == ck[k], f"{size}/{step}/{r}: {k} provenance mismatch")
        require(rec.get("weight_sha256") == ck["sha256"] and rec.get("gpu") == host["gpu"],
                "rung weight/GPU provenance mismatch")
        require(rec.get("verify") == "2c normalize + exact match under 3c's total wrapper",
                "rung criterion provenance mismatch")
        bits.append(rec["bits"])
    return bits


def load_selected(source):
    """ONLY the sixty named units. Frozen contracts rederive all 1,020,000 bits."""
    from experiments.exp5 import battery_5 as b5
    from experiments.exp2d import battery_2d as bt
    from experiments.exp2d import analyze_2d as a2d

    root = source.root / "experiments/exp5"
    for p in (b5.CHECKPOINTS_PATH_5, root / "results/host_5.json",
              source.root / "experiments/exp2d/results/verdict.json"):
        source.bind(p)
    for r in bt.RUNGS:
        source.bind(bt.items_path(r))
    manifest = b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    battery = bt.load_battery()
    floors = b5.load_floors_5()
    verify = a2d.load_verify()
    host = json.loads((root / "results/host_5.json").read_text())
    require_clean(b5.host_record_failures_5(host))
    require(host["device"] == "cuda", "selected records must be Exp 5 CUDA records")
    require(len(bt.RUNGS) == 34 and len(set(bt.FAMILY_OF.values())) == 16 and bt.N_ITEMS == 500,
            "unexpected frozen battery dimensions")
    require({t: sum(x == t for x in b5.RUNG_TYPE_5.values()) for t in TYPES} ==
            {"arithmetic": 25, "option": 4, "string": 5}, "unexpected type map")
    bits = np.empty((len(STEPS), len(SIZES), 34, 500), dtype=np.uint8)
    params, units = {}, []
    for ti, step in enumerate(STEPS):
        for si, size in enumerate(SIZES):
            d = b5.unit_dir_5(root, size, step)
            names = ("_unit.json",) + b5.unit_files_5()
            require(d.is_dir() and {p.name for p in d.iterdir()} == set(names),
                    f"{size}/step{step}: selected unit file coverage differs")
            for name in names:
                source.bind(d / name)
            records = {name: json.loads((d / name).read_text()) for name in names}
            unit, ck = records["_unit.json"], records["_checkpoint.json"]
            entry = b5.entry_5(manifest, size, step)
            bits[ti, si] = validate_unit(records, d, size=size, step=step, entry=entry,
                                         battery=battery, verify=verify, host=host)
            if size in params:
                require(params[size] == ck["n_params"], f"{size}: parameter count changes across checkpoints")
            params[size] = ck["n_params"]
            units.append({"size": size, "step": step, "collection_commit": unit["git_sha"],
                          "tensor_digest": ck["digest"], "n_params": ck["n_params"]})
    parameter_counts = tuple(params[s] for s in SIZES)
    require(all(x < y for x, y in zip(parameter_counts, parameter_counts[1:])), "parameter order not increasing")
    return Data(SIZES, STEPS, bt.RUNGS, bt.FAMILY_OF, b5.RUNG_TYPE_5, parameter_counts,
                floors, {}, bits), {"units": units, "host_sha256": host["sha256"]}


def frozen_thresholds(floors, n):
    """Encode the old reference-clear rule once; no new hypothesis test."""
    from experiments.exp5 import battery_5 as b5
    out = {}
    for r, floor in floors.items():
        lo, hi = 0, n + 1
        while lo < hi:
            mid = (lo + hi) // 2
            if mid <= n and b5.clears_5(mid, floor, n):
                hi = mid
            else:
                lo = mid + 1
        out[r] = lo
    return out


def paired_counts(smaller, larger):
    codes = 2 * np.asarray(smaller, dtype=int) + np.asarray(larger, dtype=int)
    return dict(zip(("n00", "n01", "n10", "n11"), map(int, np.bincount(codes, minlength=4))))


def texture(bits, params):
    from scipy.stats import rankdata
    bits = np.asarray(bits, dtype=int)
    counts = bits.sum(axis=1)
    x = np.log2(np.asarray(params, dtype=float))
    x -= x.mean()
    y = counts / bits.shape[1]
    slope = float(np.dot(x, y - y.mean()) / np.dot(x, x))
    ranks = rankdata(counts)
    rho = None if np.ptp(counts) == 0 else float(np.corrcoef(np.arange(len(counts)), ranks)[0, 1])
    losses = int(np.any(np.diff(bits, axis=0) < 0, axis=0).sum())
    ever = int(np.any(bits, axis=0).sum())
    codes = (bits * (2 ** np.arange(len(params)))[:, None]).sum(axis=0)
    return {"slope_accuracy_per_doubling": slope, "spearman": rho,
            "adjacent_decreases": int((np.diff(counts) < 0).sum()),
            "nondecreasing": bool(np.all(np.diff(counts) >= 0)), "any_loss": losses,
            "n_items": bits.shape[1], "ever_correct": ever, "all_wrong": bits.shape[1] - ever,
            "loss_fraction_all": losses / bits.shape[1],
            "loss_fraction_ever": losses / ever if ever else None,
            "size_pattern_counts": np.bincount(codes, minlength=2 ** len(params)).tolist()}


def bootstrap_means(values, family_labels, draws):
    """One value per rung; repeated family draws keep their complete rung blocks."""
    values = np.asarray(values, dtype=float)
    families = list(dict.fromkeys(family_labels))
    indices = [np.flatnonzero(np.array(family_labels) == f) for f in families]
    sums = np.array([values[i].sum() for i in indices])
    sizes = np.array([len(i) for i in indices])
    return {"all_rung": sums[draws].sum(axis=1) / sizes[draws].sum(axis=1),
            "equal_family": (sums / sizes)[draws].mean(axis=1)}


def contrast(values, data, draws):
    values = np.asarray(values) * 100  # percentage points throughout
    labels = [data.family_of[r] for r in data.rungs]
    families = list(dict.fromkeys(labels))
    out = {"all_rung_pp": float(values.mean()),
           "equal_family_pp": float(np.mean([values[np.array(labels) == f].mean() for f in families]))}
    boot = bootstrap_means(values, labels, draws)
    for name in ("all_rung", "equal_family"):
        low, high = np.quantile(boot[name], [.025, .975], method="linear")
        out.update({f"{name}_ci_low_pp": float(low), f"{name}_ci_high_pp": float(high)})
    for kind in TYPES:
        out[f"{kind}_pp"] = float(np.mean([v for r, v in zip(data.rungs, values) if data.type_of[r] == kind]))
    return out


def summarize(data, draws):
    """Pure analysis. Tests pass miniature synthetic tensors and explicit draws."""
    nt, ns, nr, n = data.bits.shape
    require((nt, ns, nr) == (len(data.steps), len(data.sizes), len(data.rungs)), "tensor coverage")
    require(np.isin(data.bits, [0, 1]).all(), "nonbinary tensor")
    require(len(data.params) == ns and all(x < y for x, y in zip(data.params, data.params[1:])), "parameter ordering")
    families = list(dict.fromkeys(data.family_of[r] for r in data.rungs))
    require(draws.ndim == 2 and draws.shape[1] == len(families) and
            np.issubdtype(draws.dtype, np.integer) and draws.min() >= 0 and draws.max() < len(families),
            "family draw shape/range")
    counts = data.bits.sum(axis=-1)
    acc = counts / n
    clear = counts >= np.array([data.thresholds[r] for r in data.rungs])
    tables = {name: [] for name in ("counts", "accuracy", "contrasts", "transitions", "texture", "time_averages")}
    nesting = []
    for ti, step in enumerate(data.steps):
        base = {"step": step, "training_tokens": step * TOKENS_PER_STEP}
        for si, size in enumerate(data.sizes):
            for ri, r in enumerate(data.rungs):
                tables["counts"].append({**base, "size": size, "n_params": data.params[si], "rung": r,
                    "family": data.family_of[r], "type": data.type_of[r], "n_items": n,
                    "correct": int(counts[ti, si, ri]), "accuracy": float(acc[ti, si, ri]),
                    "floor": data.floors[r], "reference_clear": bool(clear[ti, si, ri])})
            tables["accuracy"].append({**base, "size": size, "n_rungs": nr, "n_items": nr * n,
                "correct": int(counts[ti, si].sum()), "mean_accuracy": float(acc[ti, si].mean()),
                "clearing_rungs": int(clear[ti, si].sum())})
        for lo, hi in combinations(range(ns), 2):
            pair = {**base, "smaller": data.sizes[lo], "larger": data.sizes[hi]}
            gain = loss = clear_gain = clear_loss = 0
            for ri, r in enumerate(data.rungs):
                p = paired_counts(data.bits[ti, lo, ri], data.bits[ti, hi, ri])
                cg, cl = int(not clear[ti, lo, ri] and clear[ti, hi, ri]), int(clear[ti, lo, ri] and not clear[ti, hi, ri])
                diff = int(counts[ti, hi, ri]) - int(counts[ti, lo, ri])
                require(p["n01"] - p["n10"] == diff, "paired-count identity")
                tables["transitions"].append({**pair, "rung": r, "n_items": n, **p,
                    "correct_difference": diff, "clear_gain": cg, "clear_loss": cl})
                gain += p["n01"]
                loss += p["n10"]
                clear_gain += cg
                clear_loss += cl
            tables["contrasts"].append({**pair, "n_rungs": nr, "n_families": len(families),
                "n_items": nr * n, **contrast(acc[ti, hi] - acc[ti, lo], data, draws),
                "gross_gains": gain, "gross_losses": loss, "clear_gains": clear_gain, "clear_losses": clear_loss})
        rows = []
        for ri, r in enumerate(data.rungs):
            row = {**base, "rung": r, **texture(data.bits[ti, :, ri], data.params)}
            tables["texture"].append(row)
            rows.append(row)
        lost, ever = sum(r["any_loss"] for r in rows), sum(r["ever_correct"] for r in rows)
        nesting.append({**base, "any_loss": lost, "n_items": nr * n, "ever_correct": ever,
                        "loss_fraction_all": lost / (nr * n), "loss_fraction_ever": lost / ever if ever else None,
                        "nondecreasing_rungs": sum(r["nondecreasing"] for r in rows), "n_rungs": nr})
    for grid, indices in (("all_steps", list(range(nt))),
                          ("shared_spine", [i for i, step in enumerate(data.steps) if step not in (5000, 6000)])):
        require(bool(indices), "empty time grid")
        for lo, hi in combinations(range(ns), 2):
            tables["time_averages"].append({"grid": grid, "n_checkpoints": len(indices),
                "smaller": data.sizes[lo], "larger": data.sizes[hi], "n_rungs": nr,
                "n_families": len(families), "n_item_observations": len(indices) * nr * n,
                **contrast((acc[indices, hi] - acc[indices, lo]).mean(axis=0), data, draws)})
    displayed = {(data.sizes[0], data.sizes[-1]), *zip(data.sizes, data.sizes[1:])}
    summary = {"schema_version": 1, "analysis": "known-data descriptive matched-token size association",
        "limitations": LIMITATIONS,
        "scope": {"sizes": list(data.sizes), "steps": list(data.steps), "n_rungs": nr,
                  "n_families": len(families), "n_items_per_rung": n},
        "parameter_counts": dict(zip(data.sizes, data.params)), "tokens_per_step": TOKENS_PER_STEP,
        "rungs": [{"rung": r, "family": data.family_of[r], "type": data.type_of[r],
                   "floor": data.floors[r], "minimum_clear_count": data.thresholds[r]} for r in data.rungs],
        "families": [{"family": f, "n_rungs": sum(data.family_of[r] == f for r in data.rungs),
                      "all_rung_weight": sum(data.family_of[r] == f for r in data.rungs) / nr,
                      "equal_family_weight": 1 / len(families)} for f in families],
        "types": [{"type": t, "n_rungs": sum(data.type_of[r] == t for r in data.rungs)} for t in TYPES],
        "bootstrap": {"n_draws": len(draws), "seed": SEED, "family_order": families,
                      "draws_sha256": sha256(draws.astype("<i8").tobytes()), "percentiles": [2.5, 97.5],
                      "quantile_method": "linear", "shared_across_all_conditions": True},
        "table_rows": {k: len(rows) for k, rows in tables.items()},
        "accuracy": tables["accuracy"], "displayed_contrasts": [r for r in tables["contrasts"]
                      if (r["smaller"], r["larger"]) in displayed],
        "time_averages": tables["time_averages"], "nesting": nesting}
    return summary, tables


LIMITATIONS = """## Interpretation and limits

Known-data descriptive reuse; no sealed forecast, p-value, effect-threshold
world or PASS/FAIL verdict. Positive size association is conditional on these
Pythia models and this older synthetic battery. It is not a causal parameter-only
effect: architecture, recipe and size-specific learning rates vary. Equal tokens
fix schedule position, not learning rate, FLOPs or held-out loss.

The ten checkpoints are equally weighted in the across-time average, not a time
integral or ten independent replications. The eight-point shared-spine sensitivity
excludes exactly the search-added 5k/6k points. No interpolation, 64k/65k mixing,
seventh-size endpoint, or outcome-selected rung exclusion is used.

Family-cluster percentile intervals describe sensitivity to resampling represented
task families, not randomly sampled tasks. They do not quantify training-seed,
model-population, checkpoint measurement-noise or extrapolation uncertainty.
Whole families, all their rungs/items and every condition travel together in the
same draws. Equal-rung replicates divide by repeated rung count; equal-family
replicates average the selected family means. Type readings are point estimates.

Gains/losses are recorded paired fp16 greedy reads without repeated-read noise
correction; nonnesting does not establish irreversible capability loss. All-wrong
items are vacuously nested; ever-correct denominators are printed separately.
Zero correct is an observation at finite resolution, not a zero capability
probability or an absence verdict. Reference-clear transitions reuse the frozen
per-rung binomial rule; they are not a new multiplicity-controlled capability test.
The frozen criterion includes first-digit-run matching on base12_digitsum/base13.
This does not test the old sampled predictor's size-axis forecast, identify a
learning mechanism, or establish capability birth versus resolution.

OLS slopes are accuracy units per doubling of measured parameters; Spearman uses
size ranks and average ranks for tied counts, with null for constant counts.
Texture histograms encode size i in bit i (smallest size is the low bit).
"""


def report(summary):
    scope = summary["scope"]
    lines = ["# Matched-token Pythia size analysis", "", "Descriptive existing-data analysis.", "",
             f"Source `{summary['provenance']['source_commit']}`; launch `{summary['provenance']['launch_commit']}`.", "",
             f"Coverage: {len(scope['steps'])} checkpoints × {len(scope['sizes'])} sizes × {scope['n_rungs']} rungs × {scope['n_items_per_rung']} items.",
             f"Bootstrap: {summary['bootstrap']['n_draws']} shared family draws; seed {SEED}; percentile 95% intervals (pp).",
             "", "## Per-checkpoint accuracy", "", "Accuracy is the equally weighted rung mean; clear denominator is all rungs.", "",
             "| Step | Tokens | Size | Correct / items | Mean accuracy | Clear / rungs |",
             "|---:|---:|---|---:|---:|---:|"]
    for r in summary["accuracy"]:
        lines.append(f"| {r['step']} | {r['training_tokens']} | {r['size']} | {r['correct']}/{r['n_items']} | {r['mean_accuracy']:.6f} | {r['clearing_rungs']}/{r['n_rungs']} |")
    lines += ["", "## Widest and adjacent size contrasts", "",
              "Larger minus smaller. All 15 pairs at every checkpoint are in contrasts.csv.",
              "143000 is the fixed final comparison, not a selected peak. Gains/losses count paired item observations; clear changes count rungs.", "",
              "| Step | Larger − smaller | All-rung pp [95%] | Equal-family pp [95%] | Arithmetic / option / string pp | Gains / losses / items | Clear gains / losses / rungs |",
              "|---:|---|---:|---:|---:|---:|---:|"]
    def effect(r, name):
        return f"{r[name + '_pp']:.6f} [{r[name + '_ci_low_pp']:.6f}, {r[name + '_ci_high_pp']:.6f}]"
    for r in summary["displayed_contrasts"]:
        lines.append(f"| {r['step']} | {r['larger']} − {r['smaller']} | {effect(r, 'all_rung')} | {effect(r, 'equal_family')} | "
                     f"{r['arithmetic_pp']:.6f} / {r['option_pp']:.6f} / {r['string_pp']:.6f} | "
                     f"{r['gross_gains']} / {r['gross_losses']} / {r['n_items']} | {r['clear_gains']} / {r['clear_losses']} / {r['n_rungs']} |")
    lines += ["", "## Equally weighted checkpoint averages", "",
              "These are paired time averages, not independent replications. all_steps uses ten points; shared_spine uses eight.", "",
              "| Grid | Points | Larger − smaller | All-rung pp [95%] | Equal-family pp [95%] | Arithmetic / option / string pp |",
              "|---|---:|---|---:|---:|---:|"]
    for r in summary["time_averages"]:
        lines.append(f"| {r['grid']} | {r['n_checkpoints']} | {r['larger']} − {r['smaller']} | {effect(r, 'all_rung')} | {effect(r, 'equal_family')} | "
                     f"{r['arithmetic_pp']:.6f} / {r['option_pp']:.6f} / {r['string_pp']:.6f} |")
    lines += ["", "## Size-order nesting", "",
              "Any loss means at least one adjacent 1→0 along the size axis. Per-rung slopes and rank associations are in texture.csv.", "",
              "| Step | Any loss / all items | Any loss / ever-correct | Nondecreasing count rungs / all rungs |",
              "|---:|---:|---:|---:|"]
    for r in summary["nesting"]:
        lines.append(f"| {r['step']} | {r['any_loss']}/{r['n_items']} | {r['any_loss']}/{r['ever_correct']} | {r['nondecreasing_rungs']}/{r['n_rungs']} |")
    lines += ["", "## Battery weights", "", "| Family | Rungs | All-rung weight | Equal-family weight |", "|---|---:|---:|---:|"]
    for r in summary["families"]:
        lines.append(f"| {r['family']} | {r['n_rungs']} | {r['all_rung_weight']:.6f} | {r['equal_family_weight']:.6f} |")
    lines += ["", "Type counts: " + "; ".join(f"{r['type']} {r['n_rungs']}/{scope['n_rungs']}" for r in summary["types"]) + ".",
              "", LIMITATIONS]
    return "\n".join(lines) + "\n"


def reserve_output(path):
    try:
        Path(path).mkdir(parents=True, exist_ok=False)
    except FileExistsError as e:
        raise Refusal(f"results directory exists; write-once refusal: {path}") from e


def write_outputs(dest, summary, tables, provenance):
    dest = Path(dest)
    require(not any(dest.iterdir()), "reserved output directory is not empty")
    for name, rows in tables.items():
        with (dest / f"{name}.csv").open("x", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in rows)
    with (dest / "summary.json").open("xb") as f:
        f.write(json_bytes(summary))
    with (dest / "REPORT.md").open("x") as f:
        f.write(report(summary))
    hashes = {p.name: sha256(p.read_bytes()) for p in sorted(dest.iterdir())}
    with (dest / "provenance.json").open("xb") as f:
        f.write(json_bytes({**provenance, "outputs_sha256": hashes, "state": "complete"}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    dest, reserved = HERE / "results", False
    try:
        if not args.validate_only:
            reserve_output(dest)
            reserved = True
        source = Bindings(ROOT, SOURCE)
        own = Bindings(ROOT, "HEAD")
        for rel in OWN:
            own.bind(ROOT / rel)
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        check_imported(source, own)
        with pinned_imports(source):
            data, receipt = load_selected(source)
            check_imported(source, own)
            source.recheck()
            own.recheck()
            if args.validate_only:
                print(json.dumps({"state": "validated", "units": 60, "rung_records": 2040,
                                  "rederived_bits": int(data.bits.size), "bound_source_files": len(source.files),
                                  "bound_launch_files": len(own.files)}))
                return 0
            data.thresholds = frozen_thresholds(data.floors, 500)
            draws = np.random.default_rng(SEED).integers(0, 16, size=(N_BOOT, 16), dtype=np.int64)
            summary, tables = summarize(data, draws)
            check_imported(source, own)
            source.recheck()
            own.recheck()
            provenance = {"source_commit": source.commit, "launch_commit": own.commit,
                          "source_files": source.files, "launch_files": own.files,
                          "source_manifest_sha256": sha256(json_bytes(source.files)),
                          "launch_manifest_sha256": sha256(json_bytes(own.files)),
                          "completed_utc": datetime.now(timezone.utc).isoformat(),
                          "runtime": {"python": sys.version, "numpy": np.__version__}, **receipt}
            summary["provenance"] = {k: provenance[k] for k in
                ("source_commit", "launch_commit", "source_manifest_sha256", "launch_manifest_sha256")}
            write_outputs(dest, summary, tables, provenance)
            check_imported(source, own)
            source.recheck()
            own.recheck()
        print(json.dumps({"state": "written", "directory": str(dest), "table_rows": summary["table_rows"]}))
        return 0
    except (ValueError, OSError, RuntimeError, KeyError, TypeError, AttributeError, ImportError,
            EOFError, subprocess.SubprocessError) as e:
        message = f"REFUSED: {type(e).__name__}: {e}"
        if reserved:
            with (dest / "REFUSAL.json").open("x") as f:
                json.dump({"state": "refused", "reason": message}, f)
        print(message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
