"""Re-fit every Exp 2b probe at EVERY candidate site, keeping all of them.

WHY. The campaign records store one accuracy per fit — the value at the site
the frozen rule selected (smallest Bonferroni-corrected permutation p, ties
broken by highest accuracy). That is a SELECTED value, and a selected value is
upward-biased as an estimate of what a representation contains, even though
the selection's significance test is correctly corrected: the null is
evaluated at the same site the selection picked. The correction protects the
claim that something is there. It does nothing to the number reported beside
it.

The paper prescribes reporting the whole profile instead. This script measures
what that prescription is worth on the paper's own two campaigns, rather than
on a synthetic system, by recovering the per-candidate accuracies the records
threw away.

WHAT IS AND IS NOT RE-COMPUTED. The permutation null is NOT re-run: it costs
2,500 refits per candidate and contributes nothing to a selection-bias
measurement. Only the observed accuracy at each candidate is recomputed, under
the identical starving split, from the identical stored activations.

THE VALIDITY CHECK IS MANDATORY AND NOT OPTIONAL. For every fit, the
recomputed accuracy at the record's own `best_layer`/`best_token` must equal
the record's stored `accuracy` exactly. If it does not, the replay has
diverged from the campaign and every per-candidate number is worthless. The
script refuses to emit a summary when any fit fails this check.

Nothing under experiments/exp2b/ is modified. Its modules are imported and its
activations read.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
EXP2B = REPO / "experiments" / "exp2b"
if str(EXP2B) not in sys.path:
    sys.path.insert(0, str(EXP2B))

from activations import activations_path, load_activation_map  # noqa: E402
from battery.base import load_items  # noqa: E402
from battery.generators import SPECS  # noqa: E402
from probe_starved import _make_starved_scorer  # noqa: E402
from run.run_probes_2b import thin_layers  # noqa: E402
from splits import starving_split  # noqa: E402

_SPEC = {s.name: s for s in SPECS}
OUT = REPO / "paper" / "per_candidate.json"


def stage_mode(stage: str) -> str:
    return "untrained" if stage == "known_absent" else "trained"


def refit(rec: dict) -> dict:
    """Recompute accuracy at every candidate for one stored fit record."""
    stage, size, cap, seed = (rec["stage"], rec["size"], rec["capability"],
                              rec["seed"])
    mode = stage_mode(stage)
    act, y, _meta = load_activation_map(activations_path(size, mode, cap))
    act = thin_layers(act)
    items = load_items(cap)["probe_items"]
    bases = [tuple(it["basis"]) for it in items]

    split_labels = None
    if stage == "shuffled":
        rng = np.random.default_rng(1000 + seed)
        split_labels = y
        y = rng.permutation(y)

    basis_labels = y if split_labels is None else np.asarray(split_labels)
    train_idx, val_idx, _info = starving_split(
        bases, basis_labels, seed, _SPEC[cap].split_params)

    keys = sorted(act.keys())
    accs = {}
    for key in keys:
        fit_fn = _make_starved_scorer(act[key], train_idx, val_idx)
        accs[f"{key[0]},{key[1]}"] = fit_fn(act[key], y)

    sel = accs[f"{rec['best_layer']},{rec['best_token']}"]
    return {
        "stage": stage, "size": size, "capability": cap, "seed": seed,
        "n_candidates": len(keys),
        "stored_accuracy": rec["accuracy"],
        "refit_at_selected_site": sel,
        "reproduces": abs(sel - rec["accuracy"]) < 1e-12,
        "accuracies": accs,
    }


def _job(path_str: str) -> dict:
    return refit(json.loads(Path(path_str).read_text()))


def main() -> int:
    from concurrent.futures import ProcessPoolExecutor, as_completed

    records = sorted((EXP2B / "results" / "probes").rglob("*_seed*.json"))
    print(f"{len(records)} stored fits to replay", flush=True)

    out, bad = [], []
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(_job, str(p)): p for p in records}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                r = fut.result()
            except Exception as exc:                      # noqa: BLE001
                bad.append((futs[fut].name, repr(exc)))
                continue
            out.append(r)
            if not r["reproduces"]:
                bad.append((futs[fut].name,
                            f"stored {r['stored_accuracy']!r} != refit "
                            f"{r['refit_at_selected_site']!r}"))
            if i % 50 == 0:
                print(f"  {i}/{len(records)}", flush=True)

    # Always persist, including on divergence: a replay that discovers a
    # mismatch should keep the evidence that shows WHICH fits mismatched, or
    # the next run has to pay the whole cost again to find out.
    OUT.write_text(json.dumps(out, indent=1))
    n_ok = sum(1 for r in out if r["reproduces"])
    print(f"\nreplayed {len(out)} fits; {n_ok} reproduce the stored accuracy "
          f"exactly at the record's own selected site")
    print(f"wrote {OUT}")
    if bad:
        print(f"\nREPLAY DIVERGED on {len(bad)} fits — no summary is emitted "
              f"from this run; adjudicate the divergence first:")
        for name, why in bad[:10]:
            print(f"  {name}: {why}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
