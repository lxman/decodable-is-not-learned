"""Within-family correlation nuisance parameter (design §5), estimated
from the 2b record's sibling pairs — closed-record probe data, touches
no outcome quantity (design §7). The seed-margin vectors of siblings
share split-draw structure; their correlation across seeds and sizes is
the plug-in estimate for the MC calibration model."""

import json
from pathlib import Path

import numpy as np

EXP2B_PROBES = (Path(__file__).resolve().parent.parent / "exp2b" /
                "results" / "probes" / "m3")
PAIRS = (("add3_mid", "sub3_mid"), ("base7", "oct2dec"))
SIZES = ("410m", "1b")
OUT = Path(__file__).resolve().parent / "results" / "family_corr.json"


def _seed_margins(cap, size):
    return [json.loads((EXP2B_PROBES / f"{size}_{cap}_seed{s}.json")
                       .read_text())["margin"] for s in range(5)]


def estimate(write=True):
    pairs = []
    rs = []
    for a, b in PAIRS:
        for size in SIZES:
            va, vb = _seed_margins(a, size), _seed_margins(b, size)
            if np.std(va) > 0 and np.std(vb) > 0:
                r = float(np.corrcoef(va, vb)[0, 1])
                rs.append(r)
            else:
                r = None  # zero-variance vectors carry no estimate
            pairs.append({"pair": (a, b), "size": size,
                          "seed_margins_a": va, "seed_margins_b": vb,
                          "r": r})
    valid = [r for r in rs if r is not None]
    rho = float(np.clip(np.mean(valid) if valid else 0.5, 0.0, 0.9))
    d = {"pairs": pairs, "rho_family": rho,
         "note": "fallback 0.5 if all sibling vectors are degenerate; "
                 "ledger the outcome either way"}
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(d, indent=1))
    return d
