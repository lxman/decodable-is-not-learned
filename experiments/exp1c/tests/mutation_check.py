"""Mutation-test the 1c fixture suite: break the implementation on purpose and
confirm the suite notices. A suite that passes on a broken instrument is not a
gate, it is decoration."""
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/michaeljordan/emergence-paper")
A = ROOT / "experiments/exp1c/analyze_1c.py"
P = ROOT / "experiments/exp1c/run/profile_lib.py"
R = ROOT / "experiments/exp1c/records.py"

MUTATIONS = [
    ("site_fires: drop the floor gate (null only)", A,
     "return bool(null_admits and floor_admits)",
     "return bool(null_admits)"),
    ("site_fires: drop the null gate (floor only)", A,
     "return bool(null_admits and floor_admits)",
     "return bool(floor_admits)"),
    ("site_fires: drop the Bonferroni correction", A,
     'null_admits = float(_field(trained_site, "null_p_raw")) * n_sites < alpha',
     'null_admits = float(_field(trained_site, "null_p_raw")) < alpha'),
    ("site_fires: admit a tie with the twin", A,
     '    floor_admits = (float(_field(trained_site, "accuracy"))\n'
     '                    > float(_field(twin_site, "accuracy")))',
     '    floor_admits = (float(_field(trained_site, "accuracy"))\n'
     '                    >= float(_field(twin_site, "accuracy")))'),
    ("margins: max instead of mean", A,
     "    return sum(diffs) / len(diffs)",
     "    return max(diffs)"),
    ("classify: invert the precedence", A,
     "    if n_depth:\n        cls = \"depth\"\n    elif n_l0:\n        cls = \"L0-only\"",
     "    if n_l0:\n        cls = \"L0-only\"\n    elif n_depth:\n        cls = \"depth\""),
    ("verdict: raise the live-block floor to 9", A,
     "MIN_LIVE_BLOCKS = 8", "MIN_LIVE_BLOCKS = 9"),
    ("verdict: let the diagnostic arm force a PASS", A,
     '    if test["p"] < alpha and test["slope"] > 0:',
     '    if (test["p"] < alpha and test["slope"] > 0) or natural_l0_tracks_pool:'),
    ("verdict: skip the 0.50 p_c consistency check", A,
     "    if not below_silent:", "    if False and not below_silent:"),
    ("verdict: skip the stage A gate", A,
     '    if not stage_a.get("pass"):', "    if False:"),
    ("slope: two-sided instead of one-sided", A,
     "    p = (int(np.sum(null >= obs - _TIE_TOL)) + 1) / (n_draw + 1)",
     "    p = (int(np.sum(np.abs(null) >= abs(obs) - _TIE_TOL)) + 1) / (n_draw + 1)"),
    ("slope: relabel across blocks, not within", A,
     "    idx = rng.integers(0, xp.shape[0], size=(n_draw, len(blocks)))",
     "    idx = np.repeat(rng.integers(0, xp.shape[0], size=(n_draw, 1)),\n"
     "                    len(blocks), axis=1)"),
    ("stage A: population sd instead of sample sd", A,
     "np.std(np.asarray(xs, dtype=float), ddof=1)",
     "np.std(np.asarray(xs, dtype=float), ddof=0)"),
    ("stage A: lower the present-row bar to 3", A,
     "    if n_positive < 8:", "    if n_positive < 3:"),
    ("subsample: silently shrink an underfull class", P,
     "            raise ValueError(\n"
     "                f\"class {int(c)} has only {members.size} entities, below the \"\n"
     "                f\"{per_class}/class quota — the stratified subsample cannot be \"\n"
     "                f\"built and must not be silently shrunk\")",
     "            picked.append(members); continue"),
    ("subsample: make it seed-independent", P,
     "    rng = np.random.default_rng(seed)\n    picked = []",
     "    rng = np.random.default_rng(0)\n    picked = []"),
    ("probe: give every site its own split", P,
     "        fit_fn = _val_scorer(X, train_idx, val_idx)",
     "        ti, vi = split_indices(n, val_frac, seed + i)\n"
     "        fit_fn = _val_scorer(X, ti, vi)"),
    ("checkpoint: drop the 1M size suffix", P,
     '_SUFFIX = {"1M": "_m1M", "10M": ""}',
     '_SUFFIX = {"1M": "", "10M": ""}'),
    ("records: let the natural arm carry a null", R,
     '        if self.arm == "natural" and any(has_null):',
     "        if False:"),
    ("records: accept a profile with missing sites", R,
     "        if len(self.sites) != N_SITES:",
     "        if False:"),
]


def run_suite():
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "experiments/exp1c/tests/", "-q",
         "--no-header", "-x", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True)
    return r.returncode


originals = {f: f.read_text() for f in (A, P, R)}
survived, killed = [], []
try:
    for name, target, old, new in MUTATIONS:
        src = originals[target]
        if old not in src:
            survived.append(f"{name}  [PATTERN NOT FOUND — mutation not applied]")
            continue
        target.write_text(src.replace(old, new, 1))
        rc = run_suite()
        target.write_text(src)
        (killed if rc != 0 else survived).append(name)
finally:
    for f, s in originals.items():
        f.write_text(s)

print(f"KILLED   {len(killed)}/{len(MUTATIONS)}")
for k in killed:
    print(f"  ok   {k}")
if survived:
    print(f"\nSURVIVED {len(survived)}  <-- the suite does not catch these")
    for s in survived:
        print(f"  MISS {s}")
print("\nbaseline after restore:",
      "clean" if run_suite() == 0 else "DIRTY — restore failed")
