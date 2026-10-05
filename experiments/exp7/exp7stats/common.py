"""Shared frozen constants, exact JSON and write-once stage publication."""
from contextlib import AbstractContextManager
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import os
from exp7core.contract import ARMS, FAMILIES, PREDICTORS, GRID, Refusal, require, pin, seed

SCHEMA = "exp7.statistics.v2"
KERNEL_VERSION = "numpy-PCG64DXSM-hypergeometric-exact-limbs-v1"
ALPHA = F(1, 200)
PERMUTATIONS = 10000
BOOTSTRAPS = 1000
POSITIVE_COUNTS = (20, 50, 125, 250)
COUNT_RANGES = (26, 3)
D_TARGETS = (F(1, 10), F(3, 20), F(1, 5))


@dataclass(frozen=True)
class Shape:
    n: int = 500
    grid: tuple = GRID
    permutations: int = PERMUTATIONS
    bootstraps: int = BOOTSTRAPS

    def __post_init__(self):
        require(type(self.n) is int and 2 <= self.n <= 500, "shape n")
        require(type(self.grid) is tuple and 1 <= len(self.grid) <= 26
                and len(set(self.grid)) == len(self.grid)
                and all(type(v) is int and v > 0 for v in self.grid), "shape grid")
        require(type(self.permutations) is int and 1 <= self.permutations <= PERMUTATIONS,
                "shape permutations")
        require(type(self.bootstraps) is int and 1 <= self.bootstraps <= BOOTSTRAPS,
                "shape bootstrap")


PRODUCTION = Shape()


def encode(value):
    if isinstance(value, F):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    if hasattr(value, "item"):
        return encode(value.item())
    if value is None or type(value) in (str, int, float, bool):
        return value
    raise Refusal(f"unserializable value {type(value).__name__}")


def decode(value):
    if type(value) is dict:
        if set(value) == {"numerator", "denominator"}:
            require(type(value["numerator"]) is int and type(value["denominator"]) is int
                    and value["denominator"] > 0, "rational JSON")
            return F(value["numerator"], value["denominator"])
        return {k: decode(v) for k, v in value.items()}
    if type(value) is list:
        return [decode(v) for v in value]
    return value


def dumps(value):
    return (json.dumps(encode(value), ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value):
    return sha256(value if type(value) is bytes else dumps(value)).hexdigest()


def receipt(value, key):
    require(type(value) is dict and key in value, f"missing {key} receipt")
    pin(value[key])
    require("pass" not in value, "attested pass is not verification")
    if "bindings" in value:
        require(type(value["bindings"]) is dict and value["bindings"], "empty bindings")
        for name, sha in value["bindings"].items():
            require(type(name) is str and name and not Path(name).is_absolute()
                    and ".." not in Path(name).parts, "binding path")
            pin(sha)
    return value


def entry_receipt(value):
    receipt(value, "provenance_sha256")
    require(type(value.get("input_sha256")) is dict and value["input_sha256"], "input pins")
    for sha in value["input_sha256"].values():
        pin(sha)
    return value


def require_protocol(campaign, methods):
    require(campaign is not None, "empty campaign injection")
    for name in methods:
        require(callable(getattr(campaign, name, None)), f"missing verifiedCampaign.{name}")
    require(getattr(campaign, "root", None) is not None and
            getattr(campaign, "repo", None) is not None, "campaign root/repo")


def require_preoutcome(root):
    root = Path(root)
    # Canonical interface path plus historical layouts: even an empty outcome
    # tree is a sequencing ambiguity, so it refuses instead of guessing.
    for name in ("units/outcome", "units/endpoint", "units/outcome-anchors", "contacts/outcome", "outcomes", "outcome", "results/outcomes",
                 "results/outcome", "results/sweep", "contact-receipts/outcome", "probes/outcome",
                 "grants/outcome.json", "phases/outcome.json", "operations/outcome"):
        require(not (root / name).exists() and not (root / name).is_symlink(), f"power requires absent outcome tree: {name}")


CONTACT_ROOTS = ("units/outcome", "units/endpoint", "units/outcome-anchors", "contacts", "contact-receipts", "probes", "grants", "phases", "operations", "claims", "loads")


def require_preoutcome_inventory(provenance):
    """Adapter MUST independently enumerate/validate receipts at entry AND exit.

    Directory absence alone cannot certify that an outcome probe or grant-phase
    contact has not happened. Unknown phases refuse rather than defaulting safe.
    """
    inv = provenance.get("contact_inventory")
    require(type(inv) is dict and set(inv) == {"schema", "covered_roots", "entries"}
            and inv["schema"] == "exp7.contact-inventory.v1", "verified contact inventory required")
    require(type(inv["covered_roots"]) in (list, tuple) and
            set(CONTACT_ROOTS) <= set(inv["covered_roots"]), "contact inventory missing required roots")
    require(type(inv["entries"]) in (list, tuple), "contact inventory entries")
    require(digest(inv) == pin(provenance["input_sha256"].get("contact_inventory")),
            "contact inventory independent binding")
    seen = set()
    for row in inv["entries"]:
        require(type(row) is dict and set(row) == {"path", "phase", "kind", "sha256"}, "contact receipt schema")
        require(type(row["path"]) is str and row["path"] and not Path(row["path"]).is_absolute()
                and ".." not in Path(row["path"]).parts and row["path"] not in seen, "contact receipt path")
        seen.add(row["path"])
        pin(row["sha256"])
        require(row["kind"] in ("unit", "endpoint", "probe", "grant", "phase", "contact", "operation"), "contact receipt kind")
        require(row["phase"] in ("generation", "predictor", "calibration", "power"),
                f"outcome/unknown phase before power: {row['path']}")
        require(not row["path"].startswith(("units/outcome/", "units/endpoint/", "units/outcome-anchors/", "contacts/outcome/")), "outcome unit mislabeled as predictor")
    return inv


def write_once(path, data):
    require(type(data) is bytes, "write bytes")
    path = Path(path)
    require(not path.is_symlink(), "output symlink")
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def stage(campaign, name, operation, *, production=True):
    """Consume claim before any data read; exit gate before final publication.

    Entry/exit authorization is supplied by verifiedCampaign, never a pass
    field. The once-only claim also remains consumed on every refusal.
    """
    failures, directory, claimed, result = [], None, False, None
    try:
        require_protocol(campaign, ("entryexit",))
        require(name in ("analysis", "power", "calibration"), "stage name")
        root = Path(campaign.root)
        require(root.is_dir() and not root.is_symlink(), "campaign root")
        stats = root / "statistics"
        require(not stats.is_symlink(), "statistics symlink")
        stats.mkdir(exist_ok=True)
        require(not (stats / "HALTED.json").exists(), "statistics already HALTED")
        directory = stats / name
        directory.mkdir()  # exclusive; existing complete/torn/claim all refuse
        write_once(directory / "CLAIM.json", dumps({"schema": SCHEMA, "stage": name,
                                                    "production": production}))
        claimed = True
        ctx = campaign.entryexit(name)
        require(hasattr(ctx, "__enter__") and hasattr(ctx, "__exit__"), "entryexit context")
        with ctx as provenance:
            provenance = entry_receipt(provenance)
            if name == "power":
                require_preoutcome(root)
                require_preoutcome_inventory(provenance)
            result = operation(provenance)
            require(type(result) is dict and result.get("schema") == SCHEMA, "stage result schema")
            result = {**result, "provenance": provenance, "production": production}
            payload = dumps(result)
            if name == "power":
                require_preoutcome(root)
                require_preoutcome_inventory(provenance)
        # Context exit has now reverified source/input pins. No result before it.
        require(not (stats / "HALTED.json").exists(), "HALTED before success")
        if name == "power":
            require_preoutcome(root)
            require_preoutcome_inventory(provenance)
        text = render_report(result)
        if result.get("state") == "CALIBRATION-FAILED":
            write_once(stats / "HALTED.json", dumps({"schema": SCHEMA, "stage": name,
                                                       "state": "INSUFFICIENT_DATA",
                                                       "reason": "calibration defect or generator failure"}))
        write_once(directory / f"{name}.json", payload)
        write_once(directory / "REPORT.md", text.encode())
        marker = "REFUSED.json" if result.get("state") == "CALIBRATION-FAILED" else "COMPLETE.json"
        write_once(directory / marker, dumps({"files": {
            f"{name}.json": digest(payload), "REPORT.md": digest(text.encode())}}))
        return result
    except BaseException as e:
        failures.append(f"{type(e).__name__}: {e}")
    terminal = {"schema": SCHEMA, "state": "INSUFFICIENT_DATA", "stage": name,
                 "failures": failures, "production": production,
                 "baseline_missing": [v for v in failures if "baseline_missing:" in v]}
    if claimed:
        try:
            halted = directory.parent / "HALTED.json"
            if not halted.exists():
                write_once(halted, dumps(terminal))
            write_once(directory / "REFUSED.json", dumps(terminal))
        except BaseException as e:
            terminal["failures"].append(f"could not persist terminal: {type(e).__name__}: {e}")
    return terminal


def render_report(result):
    """Complete machine values also present in human report; no omitted secondary."""
    title = result.get("stage", "statistics")
    lines = [f"# Experiment 7 — {title}", "", f"State: {result.get('state', 'COMPLETE')}", ""]
    if title == "analysis":
        for p, r in result["primary"].items():
            lines += [f"## {p}: {r['state']}", r["licence"], ""]
        for name, value in result["secondaries"].items():
            lines += [f"## {name}", "```json", json.dumps(encode(value), sort_keys=True, indent=2), "```", ""]
    lines += ["## Complete record", "```json", json.dumps(encode(result), sort_keys=True, indent=2), "```", ""]
    return "\n".join(lines)
