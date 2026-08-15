"""Recompute the per-size m3 probe margins from the committed seed records
and write `probe_margins.json` (design §3, open item 4).

The probe side of 3b is NOT re-run. These are means over the five committed
probe seeds per (rung, size), read from exp2c's m3 records (rev_string7)
and exp2b's (reverse_string). The design doc quotes .6263/.7725 and
.5731/.6749; this script asserts the recompute matches those quotes to
4 decimal places — a mismatch means the design doc misquoted the record and
must be surfaced, not overwritten.

The pooled .699/.624 of the paper's §8 is deliberately not computed here
and appears nowhere in this tree: citing a mean over two models was part of
the original confound (design §3).
"""

from __future__ import annotations

import json
from pathlib import Path

EXP3B = Path(__file__).resolve().parent
EXPERIMENTS = EXP3B.parent
OUT = EXP3B / "probe_margins.json"

M3_TREES = {"rev_string7": EXPERIMENTS / "exp2c" / "results" / "probes" / "m3",
            "reverse_string": EXPERIMENTS / "exp2b" / "results" / "probes" / "m3"}
SIZES = ("410m", "1b")
SEEDS = range(5)

# design §3's quoted table, asserted against the recompute
DESIGN_QUOTES = {("rev_string7", "410m"): 0.6263, ("rev_string7", "1b"): 0.7725,
                 ("reverse_string", "410m"): 0.5731,
                 ("reverse_string", "1b"): 0.6749}


def main() -> dict:
    out = {}
    for rung, tree in M3_TREES.items():
        out[rung] = {}
        for size in SIZES:
            per_seed = {}
            for seed in SEEDS:
                p = tree / f"{size}_{rung}_seed{seed}.json"
                rec = json.loads(p.read_text())
                assert rec["capability"] == rung and rec["size"] == size, p
                per_seed[f"seed{seed}"] = rec["margin"]
            mean = sum(per_seed.values()) / len(per_seed)
            quoted = DESIGN_QUOTES[(rung, size)]
            assert abs(mean - quoted) < 5e-5, (
                f"{rung}/{size}: recomputed mean {mean:.6f} does not match "
                f"the design doc's {quoted} — surface this, do not overwrite")
            out[rung][size] = {"mean": mean, "per_seed": per_seed,
                               "n_seeds": len(per_seed),
                               "source": str(tree.relative_to(EXPERIMENTS))}
    OUT.write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    r = main()
    for rung, sizes in r.items():
        for size, d in sizes.items():
            print(f"{rung} {size}: mean margin {d['mean']:.4f} "
                  f"({d['n_seeds']} seeds, {d['source']})")
    print(f"wrote {OUT}")
