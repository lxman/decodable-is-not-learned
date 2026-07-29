"""Design §7: for the 12 survivors, the 2b fits ARE the 2c fits.
This manifest pins every reused artifact by path + SHA-256 so the
freeze commit declares exactly what is reused and verify() proves
nothing drifted. Survivors = scored_battery minus attrition."""

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


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _survivors():
    scored = json.loads((ITEMS / "scored_battery.json").read_text())
    att = set(json.loads((EXP2B / "results" / "m2_report.json")
                         .read_text())["attrition"])
    return [c for c in scored if c not in att]


def build(write=True) -> dict:
    m = {"source_tag": "exp2b-closed", "survivors": {}}
    for cap in _survivors():
        entry = {"item_file": {"path": str(ITEMS / f"{cap}.json"),
                               "sha256": _sha(ITEMS / f"{cap}.json")},
                 "fits": {}}
        for stage in STAGES:
            fits = []
            for size in SIZES:
                for s in range(5):
                    p = PROBES / stage / f"{size}_{cap}_seed{s}.json"
                    fits.append({"path": str(p), "sha256": _sha(p)})
            entry["fits"][stage] = fits
        m["survivors"][cap] = entry
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(m, indent=1))
    return m


def verify() -> bool:
    m = json.loads(OUT.read_text())
    for cap, e in m["survivors"].items():
        if _sha(Path(e["item_file"]["path"])) != e["item_file"]["sha256"]:
            return False
        for fits in e["fits"].values():
            for f in fits:
                if _sha(Path(f["path"])) != f["sha256"]:
                    return False
    return True
