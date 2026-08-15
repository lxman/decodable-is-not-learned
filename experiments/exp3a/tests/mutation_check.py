"""Mutation-test the 3a fixture suite."""
import os
import shutil
import subprocess, sys
from pathlib import Path
ROOT=Path("/Users/michaeljordan/emergence-paper"); A=ROOT/"experiments/exp3a/analyze_3a.py"
M=[
 ("floor: use min instead of max", "src = max(eligible, key=lambda k: eligible[k])",
  "src = min(eligible, key=lambda k: eligible[k])"),
 ("floor: drop the copy_first floor entirely", '"copy_first": copy_first}',
  '"copy_first": 0.0}'),
 ("floor: re-include copy_first on a copy task",
  "if not (k == \"copy_first\" and copy_is_the_task)}", "if True}"),
 ("floor: declare copy_is_the_task always False", "copy_is_the_task = copy_whole > 0.5",
  "copy_is_the_task = False"),
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
 ("significance: drop the Bonferroni correction", "return bool(p * n_tests < alpha)",
  "return bool(p < alpha)"),
 ("significance: two-sided", "p = float(binom.sf(correct - 1, n, floor))",
  "p = float(binom.sf(correct - 1, n, floor)) / 2"),
 ("verdict: skip the positive-control gate", "    if sum(ctrl) < 2:", "    if False:"),
 ("verdict: skip the replication gate",
  '        if abs(float(c["full_string_acc"]) - float(c["committed_2c_acc"])) > 0.02:',
  "        if False:"),
 ("verdict: UNITS_ARTIFACT on any size rather than all",
  "    if all(all(v) for v in rev.values()):", "    if any(any(v) for v in rev.values()):"),
 ("verdict: DISSOCIATION even when a cell fired",
  "    if not any(any(v) for v in rev.values()):", "    if True:"),
 ("verdict: untrained fires no longer recorded",
  "    contaminated = sorted(k[0] for k, v in sig.items()\n                          if v and k[2] == \"untrained\")",
  "    contaminated = []"),
]
def run():
    for d in ROOT.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable,"-m","pytest","experiments/exp3a/tests/","-q","--no-header","-x","--tb=no"],cwd=ROOT,capture_output=True,text=True,env=env).returncode
orig=A.read_text(); killed=[]; survived=[]
try:
    for name,old,new in M:
        if old not in orig: survived.append(f"{name} [PATTERN NOT FOUND]"); continue
        A.write_text(orig.replace(old,new,1)); rc=run(); A.write_text(orig)
        (killed if rc!=0 else survived).append(name)
finally: A.write_text(orig)
print(f"KILLED {len(killed)}/{len(M)}")
for k in killed: print("  ok  ",k)
if survived:
    print(f"\nSURVIVED {len(survived)}")
    for s in survived: print("  MISS",s)
print("\nbaseline:", "clean" if run()==0 else "DIRTY")
