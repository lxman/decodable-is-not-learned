"""Mutation-test the 3b fixture suite, in both directions.

Every gate gets at least a SOFTENING mutant (the gate stops firing — the
direction that lets an unwelcome outcome through) and, where a hardening
misread exists, a HARDENING mutant (the gate fires when it must not — the
direction that manufactures INSUFFICIENT_DATA or a dramatic zero). A
surviving mutant means the fixture suite would not notice that change to
the frozen analysis.

Runs under 3a's corrected harness: __pycache__ cleared and
PYTHONDONTWRITEBYTECODE=1 before every pytest invocation, because a
same-length same-second write leaves stale bytecode and the mutation never
reaches the interpreter (3a FREEZE_CHECKLIST, "A defect in the mutation
harness itself").
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/exp3b/analyze_3b.py"

M = [
    # ---- floors (ported from 3a) ----
    ("floor: use min instead of max",
     "src = max(eligible, key=lambda k: eligible[k])",
     "src = min(eligible, key=lambda k: eligible[k])"),
    ("floor: drop the copy_first floor entirely",
     '"copy_first": copy_first}', '"copy_first": 0.0}'),
    ("floor: re-include copy_first on a copy task",
     'if not (k == "copy_first" and copy_is_the_task)}', "if True}"),
    ("floor: declare copy_is_the_task always False",
     "copy_is_the_task = copy_whole > 0.5", "copy_is_the_task = False"),
    # ---- scoring (ported from 3a) ----
    ("scoring: drop unparseable items instead of failing them",
     "    return bool(got is not None and got == str(probe_label)[0].casefold())",
     "    return bool(got is None or got == str(probe_label)[0].casefold())"),
    ("scoring: do not strip leading whitespace",
     "    s = str(continuation).lstrip()", "    s = str(continuation)"),
    ("scoring: case-sensitive comparison",
     "    return bool(got is not None and got == str(probe_label)[0].casefold())",
     "    return bool(got is not None and got == str(probe_label)[0])"),
    ("scoring: silently allow a length mismatch",
     "    if len(continuations) != len(probe_labels):", "    if False:"),
    # ---- significance ----
    ("significance: drop the Bonferroni correction",
     "return bool(p * n_tests < alpha)", "return bool(p < alpha)"),
    ("significance: two-sided",
     "p = float(binom.sf(correct - 1, n, floor))",
     "p = float(binom.sf(correct - 1, n, floor)) / 2"),
    ("significance: verdict tests trained cells at n_tests=1",
     '            n_tests=n_tests if m == "trained" else 1, alpha=alpha)',
     "            n_tests=1, alpha=alpha)"),
    ("significance: verdict tests untrained twins at n_tests=8",
     '            n_tests=n_tests if m == "trained" else 1, alpha=alpha)',
     "            n_tests=n_tests, alpha=alpha)"),
    ("significance: count all 20 trained cells instead of the probe-size 8",
     "    n_tests = sum(1 for (r, s, m) in by_key\n"
     "                  if s in PROBE_SIZES and m == \"trained\")",
     "    n_tests = sum(1 for (r, s, m) in by_key\n"
     "                  if m == \"trained\")"),
    # ---- Clopper–Pearson ----
    ("cp: lower bound always 0",
     "    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))",
     "    lo = 0.0"),
    ("cp: upper bound always 1",
     "    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))",
     "    hi = 1.0"),
    ("cp: intervals always overlap",
     "    return bool(lo1 <= hi2 and lo2 <= hi1)", "    return True"),
    # ---- gate 1 (positive control) ----
    ("gate1: skip the positive-control gate",
     "    if not all(ctrl):", "    if False:"),
    ("gate1: either probe size suffices instead of both",
     "    if not all(ctrl):", "    if not any(ctrl):"),
    # ---- gate 2 (inclusion replication) ----
    ("gate2: skip the replication gate", "    if bad:", "    if False:"),
    ("gate2: check trained cells only",
     "    for k in sorted(inclusion):",
     '    for k in [q for q in sorted(inclusion) if q[2] == "trained"]:'),
    # ---- gate 3 (byte identity) ----
    ("gate3: tolerance so wide it never fires",
     "BYTE_TOLERANCE = 2", "BYTE_TOLERANCE = 500"),
    ("gate3: zero tolerance — an allowed tie flip kills the experiment",
     "BYTE_TOLERANCE = 2", "BYTE_TOLERANCE = 0"),
    ("gate3: diffs never disclosed", "        if diffs:", "        if False:"),
    ("gate3: continuations never compared",
     "                 if str(g) != str(w)]", "                 if False]"),
    # ---- gate 4 (contamination) and step 5 ----
    ("gate4: significance computed for eval-size cells too",
     "        if s not in PROBE_SIZES:\n            continue",
     "        if False:\n            continue"),
    ("gate4: contamination never recorded",
     "    contaminated = sorted({r for (r, s, m), v in sig.items()\n"
     "                           if v and m == \"untrained\"})",
     "    contaminated = []"),
    ("step5: contaminated rungs not excluded",
     "    eligible = [(r, s) for r in REVERSAL_RUNGS if r not in contaminated\n"
     "                for s in PROBE_SIZES]",
     "    eligible = [(r, s) for r in REVERSAL_RUNGS\n"
     "                for s in PROBE_SIZES]"),
    ("step5: vacuous quantifier allowed to adjudicate",
     "    if not eligible:", "    if False:"),
    ("step5: UNITS_ARTIFACT on any cell rather than all",
     "    if all(fired):", "    if any(fired):"),
    ("step5: DISSOCIATION even when a cell fired",
     "    if not any(fired):", "    if True:"),
    # ---- battery shape ----
    ("shape: missing cells accepted",
     "    if set(by_key) != want:", "    if False:"),
    ("shape: duplicate cells accepted",
     "        if k in by_key:", "        if False:"),
    ("loader: non-cell json ingested as data",
     '                if "continuations" not in rec or "probe_labels" not in rec:',
     "                if False:"),
    # ---- committed-referent pins ----
    ("floors: sha pin not checked",
     "    if got_sha != expected_sha:", "    if False:"),
    ("floors: recompute-assert dropped",
     "        if recomputed != committed.get(rung):", "        if False:"),
]


def run():
    for d in (ROOT / "experiments").rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "experiments/exp3b/tests/", "-q",
         "--no-header", "-x", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True, env=env).returncode


orig = A.read_text()
killed, survived = [], []
try:
    for name, old, new in M:
        if old not in orig:
            survived.append(f"{name} [PATTERN NOT FOUND]")
            continue
        A.write_text(orig.replace(old, new, 1))
        rc = run()
        A.write_text(orig)
        (killed if rc != 0 else survived).append(name)
finally:
    A.write_text(orig)
print(f"KILLED {len(killed)}/{len(M)}")
for k in killed:
    print("  ok  ", k)
if survived:
    print(f"\nSURVIVED {len(survived)}")
    for s in survived:
        print("  MISS", s)
print("\nbaseline:", "clean" if run() == 0 else "DIRTY")
