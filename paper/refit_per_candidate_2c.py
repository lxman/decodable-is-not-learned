"""Re-fit every Exp 2c probe at EVERY candidate site, keeping all of them.

Two questions in one run.

1. REPRODUCTION. 2c's probe fits have never been re-derived from their stored
   activations. exp2b's were (731 of 731 Mac-computed fits reproduced exactly,
   the 15 mismatches all from two x86 workers and explained by BLAS
   accumulation order). This closes the same gap for 2c.

2. SELECTION. The campaign stored one accuracy per fit — the value at the site
   the frozen rule selected. On 2b that value runs 1.28x the candidate mean on
   untrained networks, positive in 246 of 247 fits, which is selection and not
   signal. 2c's primary statistic is a rank correlation over exactly those
   selected values, so the same measurement here says whether the artifact was
   carrying part of rho = .368.

Neither can touch 2c's frozen verdict, which is closed. Both are disclosed
descriptives, the same standing this program gave the chance-floor correction.

The permutation null is NOT re-run: it costs N_PERM_FULL refits per candidate
and contributes nothing to either question. Only the observed accuracy at each
candidate is recomputed, under the identical starving split.

THE VALIDITY CHECK IS MANDATORY. For every fit, the recomputed accuracy at the
record's own best_layer/best_token must equal its stored accuracy exactly. A
divergence means the replay is not reproducing the campaign, and the
per-candidate numbers from that fit are worthless.

Nothing under experiments/exp2c/ or experiments/exp2b/ is modified.
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
EXP2C = REPO / "experiments" / "exp2c"
# Order matters and is not cosmetic: BOTH trees carry a `run` package, a
# `harness` and a `screen`. sys.path.insert(0) puts the LAST inserted first,
# so exp2b goes in first and exp2c ends up ahead of it — 2c's own run/screen/
# harness win, while exp2b still supplies probe_starved and splits, which 2c
# does not redefine. Inserting these the other way round silently replays 2c's
# records through 2b's code.
for _p in (REPO / "experiments" / "exp2b", EXP2C):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

OUT = REPO / "paper" / "per_candidate_2c.json"


def refit(rec: dict) -> dict:
    from run import screen
    from run.campaign_m2 import (_activation_source, _split_params_for,
                                 shuffled_labels)
    from probe_starved import _make_starved_scorer
    from splits import starving_split

    stage, size, cap, seed = (rec["stage"], rec["size"], rec["capability"],
                              rec["seed"])

    # Route by stage. known_absent fits are the tier-2 screening fits and read
    # the UNTRAINED activation cache via screen._load_untrained_activations;
    # every other stage reads the trained cache via campaign_m2's
    # _activation_source, whose checkpoint_id is hardcoded ":trained". Using
    # one source for both silently replays untrained records against trained
    # activations — which is exactly what the mandatory reproduction check
    # caught on the first smoke test.
    if stage == "known_absent":
        act, y, bases, _meta = screen._load_untrained_activations(cap, size)
    else:
        npz, payload = _activation_source(cap, size)
        act, y, _meta = screen._load_activation_map(npz)
        act = screen._thin_layers(act)
        bases = [tuple(it["basis"]) for it in payload["probe_items"]]

    split_labels = None
    if stage == "shuffled":
        split_labels, y = shuffled_labels(y, seed)
    basis_labels = y if split_labels is None else np.asarray(split_labels)
    train_idx, val_idx, _info = starving_split(
        bases, basis_labels, seed, _split_params_for(cap))

    accs = {}
    for key in sorted(act.keys()):
        fit_fn = _make_starved_scorer(act[key], train_idx, val_idx)
        accs[f"{key[0]},{key[1]}"] = fit_fn(act[key], y)

    sel = accs.get(f"{rec['best_layer']},{rec['best_token']}")
    return {
        "stage": stage, "size": size, "capability": cap, "seed": seed,
        "n_candidates": len(accs),
        "stored_accuracy": rec["accuracy"],
        "refit_at_selected_site": sel,
        "reproduces": sel is not None and abs(sel - rec["accuracy"]) < 1e-12,
        "host": rec.get("host"),
        "accuracies": accs,
    }


def _job(path_str: str) -> dict:
    return refit(json.loads(Path(path_str).read_text()))


def main() -> int:
    from concurrent.futures import ProcessPoolExecutor, as_completed

    records = sorted((EXP2C / "results" / "probes").rglob("*_seed*.json"))
    print(f"{len(records)} stored 2c fits to replay", flush=True)

    out, bad = [], []
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(_job, str(p)): p for p in records}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                r = fut.result()
            except Exception as exc:                       # noqa: BLE001
                bad.append((futs[fut].name, repr(exc)))
                continue
            out.append(r)
            if not r["reproduces"]:
                bad.append((futs[fut].name,
                            f"stored {r['stored_accuracy']!r} != refit "
                            f"{r['refit_at_selected_site']!r}"))
            if i % 100 == 0:
                print(f"  {i}/{len(records)}", flush=True)

    OUT.write_text(json.dumps(out, indent=1))
    n_ok = sum(1 for r in out if r["reproduces"])
    print(f"\nreplayed {len(out)} fits; {n_ok} reproduce exactly")
    print(f"wrote {OUT}")
    if bad:
        print(f"\n{len(bad)} did not reproduce:")
        for name, why in bad[:15]:
            print(f"  {name}: {why}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
