"""Design §7: for the 12 survivors, the 2b fits ARE the 2c fits.
This manifest pins every reused artifact by path + SHA-256 so the
freeze commit declares exactly what is reused. Survivors =
scored_battery minus attrition. Pinned paths are repo-relative and
verify() returns (ok, drifted_paths) (Michael's ruling 2026-07-29)."""

import hashlib
import json
from pathlib import Path

EXP2B = Path(__file__).resolve().parent.parent.parent / "exp2b"
ITEMS = EXP2B / "battery" / "items"
PROBES = EXP2B / "results" / "probes"
OUT = (Path(__file__).resolve().parent.parent / "results" /
       "reuse_manifest.json")
STAGES = ("known_absent", "m3", "shuffled")
SIZES = ("410m", "1b")
ROOT = Path(__file__).resolve().parents[3]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _pin(p: Path) -> dict:
    return {"path": str(p.relative_to(ROOT)), "sha256": _sha(p)}


def _survivors():
    scored = json.loads((ITEMS / "scored_battery.json").read_text())
    att = set(json.loads((EXP2B / "results" / "m2_report.json")
                         .read_text())["attrition"])
    return [c for c in scored if c not in att]


def build(write=True) -> dict:
    m = {"source_tag": "exp2b-closed", "survivors": {}}
    for cap in _survivors():
        entry = {"item_file": _pin(ITEMS / f"{cap}.json"), "fits": {}}
        for stage in STAGES:
            fits = []
            for size in SIZES:
                for s in range(5):
                    p = PROBES / stage / f"{size}_{cap}_seed{s}.json"
                    fits.append(_pin(p))
            entry["fits"][stage] = fits
        m["survivors"][cap] = entry
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(m, indent=1))
    return m


def verify():
    """Returns (ok, drifted): ok is True iff every pinned artifact
    exists and matches its SHA-256; drifted lists every offending
    repo-relative path (missing counts as drift, never a crash)."""
    m = json.loads(OUT.read_text())
    drifted = []

    def _check(rec):
        p = ROOT / rec["path"]
        if not p.exists() or _sha(p) != rec["sha256"]:
            drifted.append(rec["path"])

    for e in m["survivors"].values():
        _check(e["item_file"])
        for fits in e["fits"].values():
            for f in fits:
                _check(f)
    return (not drifted, drifted)
