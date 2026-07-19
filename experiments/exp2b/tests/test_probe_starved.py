"""probe_starved end-to-end on synthetic activations: generalizing structure
must fire, a pure lookup world must NOT (the reservoir scenario that killed
Exp 2, replayed against the new instrument), shuffles must kill, and the
frozen-primitive imports must not shadow exp2b's own modules."""

import numpy as np
import pytest

from probe_starved import probe_starved
from splits import SplitParams


def _world(kind, n=1200, d=32, n_vals=40, n_cls=4, seed=0):
    """Two (layer, slot) candidates; candidate (1, 1) carries the signal.

    kind='structure': the label is linearly encoded in X independent of basis
    value -> generalizes across the starving split.
    kind='lookup': X encodes ONLY the basis value's identity (a random fixed
    embedding per value); labels are a fixed function of value -> perfectly
    decodable in-distribution, chance on starved validation.
    """
    rng = np.random.default_rng(seed)
    vals = [str(v) for v in range(n_vals)]
    bases = [(vals[int(rng.integers(n_vals))],) for _ in range(n)]
    table = {v: str(i % n_cls) for i, v in enumerate(vals)}
    y = np.array([table[b[0]] for b in bases], dtype=object)
    X = rng.normal(size=(n, 2, 2, d)).astype(np.float32)
    if kind == "structure":
        for i in range(n):
            X[i, 1, 1, int(y[i])] += 4.0
    elif kind == "lookup":
        emb = {v: rng.normal(size=d) * 3.0 for v in vals}
        for i in range(n):
            X[i, 1, 1, :] += emb[bases[i][0]]
    act = {(l, s): X[:, l, s, :] for l in range(2) for s in range(2)}
    return act, y, bases


PARAMS = SplitParams(holdout_frac=0.2, min_holdout_values=5, min_val_items=100)


def test_structure_fires_and_generalizes():
    act, y, bases = _world("structure")
    r = probe_starved(act, y, bases, split_params=PARAMS, checkpoint_id="t",
                      seed=0, n_perm=500)
    assert r["present"] and r["margin"] > 0.5
    assert (r["best_layer"], r["best_token"]) == (1, 1)


def test_lookup_world_is_silent():
    """THE test: the world that scored margin 1.0 on Exp 2's instrument must
    score 0 here — its lookup embedding is starved out of validation."""
    act, y, bases = _world("lookup")
    r = probe_starved(act, y, bases, split_params=PARAMS, checkpoint_id="t",
                      seed=0, n_perm=500)
    assert not r["present"] and r["margin"] == 0.0
    # and the in-distribution accuracy WOULD have been high: verify the lookup
    # world is genuinely decodable, so the silence above is the split's doing
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X = act[(1, 1)]
    rng = np.random.default_rng(1)
    perm = rng.permutation(len(y))
    tr, va = perm[300:], perm[:300]
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=200))
    clf.fit(X[tr], y[tr])
    assert (clf.predict(X[va]) == y[va]).mean() > 0.9


def test_shuffled_labels_are_silent():
    act, y, bases = _world("structure", seed=2)
    rng = np.random.default_rng(1002)
    r = probe_starved(act, rng.permutation(y), bases, split_params=PARAMS,
                      checkpoint_id="t", seed=0, n_perm=500)
    assert not r["present"]


def test_null_std_recorded_for_floor_signature_check():
    act, y, bases = _world("structure", seed=3)
    r = probe_starved(act, y, bases, split_params=PARAMS, checkpoint_id="t",
                      seed=1, n_perm=200)
    assert r["null_std"] > 0
    assert r["split"]["n_val"] >= 100 and r["split"]["n_train"] > 0


def test_split_determinism_per_seed():
    act, y, bases = _world("structure", seed=4)
    r1 = probe_starved(act, y, bases, split_params=PARAMS, checkpoint_id="t",
                       seed=2, n_perm=200)
    r2 = probe_starved(act, y, bases, split_params=PARAMS, checkpoint_id="t",
                       seed=2, n_perm=200)
    assert r1 == r2


def test_alias_import_does_not_shadow_exp2b_modules():
    """Exp 2's shadowing-abort regression, fresh interpreter."""
    import subprocess
    import sys as _sys
    from pathlib import Path
    code = ("import probe_starved\n"
            "from battery.generators import SPECS\n"
            "from splits import SplitParams\n"
            "assert len(SPECS) == 30\n"
            "print('CLEAN')\n")
    r = subprocess.run([_sys.executable, "-c", code], capture_output=True,
                       text=True,
                       cwd=str(Path(__file__).resolve().parent.parent))
    assert r.returncode == 0 and "CLEAN" in r.stdout, r.stderr


def test_analyze_thresholds_and_schema():
    from analyze import ALPHA_PERM, MIN_N, analyze
    assert MIN_N == 20 and ALPHA_PERM == 0.01
    probe = {f"c{i}": {"probe_margin": i / 24} for i in range(24)}
    evals = {f"c{i}": {m: i / 48 for m in ("2.8b", "6.9b", "12b")} for i in range(24)}
    r = analyze(probe, evals, list(probe.keys()))
    assert r.verdict == "PASS" and r.n == 24
    r2 = analyze({k: probe[k] for k in list(probe)[:19]},
                 evals, list(probe.keys())[:19])
    assert r2.verdict == "INSUFFICIENT_DATA"
