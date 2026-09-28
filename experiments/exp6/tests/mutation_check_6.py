# experiments/exp6/tests/mutation_check_6.py
"""Mutation-test Exp 6's own modules (the mutants are in `mutants_6.py`).

NOTHING IS MUTATED IN PLACE. Each worker owns a private copy of
`experiments/exp6` with every other experiment symlinked beside it; a
mutant is written into the copy, the tests run there, and the copy's
file is restored from the working tree's bytes. The working tree is read
and never written: there is no backup to strand, no concurrent run to
collide with, and a killed run leaves nothing behind but a temporary
directory (2k, 4c, 5 and 5b mutated in place and each needed a protocol
for the crash that leaves a mutant in the tree).

    python -m experiments.exp6.tests.mutation_check_6 [--jobs 6] [--slow]
        [--only slug,slug] [--log PATH]

Pass 1 (always): every mutant against the FAST files mapped to its
target, first failure wins. Pass 2 (`--slow`): the survivors of pass 1
against the slow files, cheapest first — the mutant's own `hint`, the
worlds that refuse (a refusal costs seconds), the worlds that deliver a
verdict (a full analysis each), then totality. A mutant no test kills is OPEN and fails the run unless
`mutants_6.EQUIVALENT_6` carries its proof.

A timeout is not a kill. A mutant whose target text is not found exactly
once is an ERROR, never a survivor and never a kill.
"""
from __future__ import annotations

import ast
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
EXP6 = REPO / "experiments" / "exp6"
T = "experiments/exp6/tests/"
FAST_6 = {
    "battery": [T + f for f in ("test_verify_6.py", "test_spec_6.py", "test_data_6.py",
                                "test_generators_a_6.py", "test_generators_b_6.py",
                                "test_bbkeys_6.py", "test_battery_6.py")],
    "instrument": [T + f for f in ("test_records_6.py", "test_families_6.py",
                                   "test_referents_6.py", "test_pins_6.py",
                                   "test_common_6.py", "test_predict_6.py",
                                   "test_stages_6.py", "test_run_6.py",
                                   "test_analyze_unit_6.py", "test_preflight_6.py",
                                   "test_power_6.py")],
}
WORLDS, TOTALITY = T + "test_worlds_6.py", T + "test_totality_6.py"
# the tests of the worlds file that run a FULL analysis; every other one refuses
FULL = ("general or other_worlds or battery_bound or undetermined or "
        "another_convention or strict_json or what_each_secondary or abandoned or "
        "checked_again")
SLOW_6 = [([WORLDS], ["-k", f"not ({FULL})"]), ([WORLDS], ["-k", FULL]),
          ([TOTALITY], [])]
FAST_ARGS = ["-m", "not slow"]
SKIP_DIRS = {"__pycache__", "results", ".pytest_cache"}
TIMEOUT_FAST, TIMEOUT_SLOW = 900, 5400


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()[:72]


def make_tree(dst: Path) -> Path:
    """A private tree: `experiments/exp6` copied, its siblings linked."""
    exps = dst / "experiments"
    exps.mkdir(parents=True)
    for p in sorted((REPO / "experiments").iterdir()):
        if p.name == "exp6":
            shutil.copytree(p, exps / "exp6", ignore=lambda d, names: [
                n for n in names if n in SKIP_DIRS or n.endswith(".log")])
        elif p.name not in SKIP_DIRS:
            os.symlink(p, exps / p.name)
    return dst


def totality_mutants(path: Path) -> list:
    """One mutant per `collect_total(thunk, label)` call textually inside
    `run()`: the wrapper stripped, the thunk run uncaught. Labelled by a
    hash of the call's own source, stable under edits elsewhere."""
    src = path.read_text()
    fn = next(n for n in ast.parse(src).body
              if isinstance(n, ast.FunctionDef) and n.name == "run")
    out = []
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Call) and node.args):
            continue
        name = getattr(node.func, "id", getattr(node.func, "attr", None))
        if name != "collect_total":
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if not full or not thunk or src.count(full) != 1:
            continue
        label = ast.get_source_segment(src, node.args[1]) if len(node.args) > 1 else "?"
        out.append({"file": "analyze_6.py", "suite": "instrument",
                    "slug": "totality_" + hashlib.sha256(full.encode()).hexdigest()[:10],
                    "name": f"run(): collect_total stripped at {label}",
                    "old": full, "new": f"(({thunk})(), [])"})
    return out


def all_mutants() -> list:
    from experiments.exp6.tests import mutants_6 as m6
    out = []
    for m in m6.MUTANTS_6:
        m = dict(m)
        m.setdefault("slug", slug(m["name"]))
        out.append(m)
    out += totality_mutants(EXP6 / "analyze_6.py")
    for m in out:
        if m["name"] in m6.HINTS_6:
            m.setdefault("hint", m6.HINTS_6[m["name"]])
    lost = sorted(set(m6.HINTS_6) - {m["name"] for m in out})
    if lost:
        raise RuntimeError(f"HINTS_6 names no mutant: {lost}")
    slugs = [m["slug"] for m in out]
    dup = sorted({s for s in slugs if slugs.count(s) > 1})
    if dup:
        raise RuntimeError(f"mutant slugs are not unique: {dup}")
    return out


def run_pytest(tree: Path, tests, args, timeout) -> dict:
    empty = str(Path(tree) / "no-models")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1",
           "TRANSFORMERS_OFFLINE": "1", "HF_HOME": empty,
           "HF_HUB_CACHE": empty + "/hub"}
    env["PYTHONPATH"] = os.pathsep.join(
        [str(tree)] + [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep)
                       if p and Path(p).resolve() != REPO.resolve()])
    cmd = [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
           *tests, *args]
    try:
        r = subprocess.run(cmd, cwd=tree, env=env, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"state": "timeout", "by": None, "tail": ""}
    text = r.stdout + r.stderr
    if r.returncode == 0:
        return {"state": "passed", "by": None, "tail": text[-300:]}
    if r.returncode == 5:
        return {"state": "no-tests", "by": None, "tail": text[-300:]}
    by = next((ln.split(" ")[1] for ln in text.splitlines()
               if ln.startswith(("FAILED ", "ERROR "))), None)
    return {"state": "failed", "by": by or "(unidentified)", "tail": text[-600:]}


def apply(tree: Path, m: dict):
    """Write the mutant into the tree; returns the restore thunk, or the
    reason it could not be applied."""
    rel = Path("experiments/exp6") / m["file"]
    src = (REPO / rel).read_text(encoding="utf-8")
    if src.count(m["old"]) != 1:
        return None, f"target text found {src.count(m['old'])} times in {m['file']}"
    if m["old"] == m["new"]:
        return None, "the mutant changes nothing"
    (tree / rel).write_text(src.replace(m["old"], m["new"]), encoding="utf-8")
    return (lambda: (tree / rel).write_text(src, encoding="utf-8")), None


def judge(tree: Path, m: dict, *, slow: bool) -> dict:
    restore, err = apply(tree, m)
    if restore is None:
        return {"outcome": "ERROR", "detail": err}
    try:
        got = run_pytest(tree, FAST_6[m.get("suite", "instrument")], FAST_ARGS,
                         TIMEOUT_FAST)
        if got["state"] == "failed":
            return {"outcome": "killed", "detail": f"fast: {got['by']}"}
        if got["state"] != "passed":
            return {"outcome": "ERROR", "detail": f"fast suite: {got['state']}"}
        if not slow:
            return {"outcome": "survived-fast", "detail": ""}
        routes = ([([T + m["hint"].split("::")[0]],
                    ["-k", m["hint"].split("::")[1]])] if m.get("hint") else [])
        routes += SLOW_6
        for tests, args in routes:
            got = run_pytest(tree, tests, ["-m", "slow or not slow", *args],
                             TIMEOUT_SLOW)
            if got["state"] == "failed":
                return {"outcome": "killed", "detail": f"slow: {got['by']}"}
            if got["state"] == "timeout":
                return {"outcome": "ERROR", "detail": "slow suite: timeout"}
        return {"outcome": "OPEN", "detail": "no test fails"}
    finally:
        restore()


def main(argv=None) -> int:
    from experiments.exp6.tests import mutants_6 as m6
    argv = list(sys.argv[1:] if argv is None else argv)

    def opt(name, default=None):
        for i, a in enumerate(argv):
            if a == name and i + 1 < len(argv):
                return argv[i + 1]
            if a.startswith(name + "="):
                return a.split("=", 1)[1]
        return default
    jobs, slow = int(opt("--jobs", "6")), "--slow" in argv
    only = set(filter(None, (opt("--only") or "").split(",")))
    log_path = opt("--log")
    lines, lock = [], threading.Lock()

    def say(text):
        with lock:
            lines.append(text)
            print(text, flush=True)

    mutants = [m for m in all_mutants() if not only or m["slug"] in only]
    missing = only - {m["slug"] for m in mutants}
    if missing:
        raise SystemExit(f"no such mutant(s): {sorted(missing)}")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="exp6-mutation-") as tmp:
        tmp = Path(tmp)
        base = make_tree(tmp / "baseline")
        for suite, tests in FAST_6.items():
            if any(m.get("suite", "instrument") == suite for m in mutants):
                got = run_pytest(base, tests, FAST_ARGS, TIMEOUT_FAST)
                if got["state"] != "passed":
                    say(f"BASELINE {suite}: {got['state']} — fix the suite first\n"
                        f"{got['tail']}")
                    return 2
                say(f"baseline OK ({suite}, fast)")
        trees = [make_tree(tmp / f"w{i}") for i in range(jobs)]
        free = list(trees)

        def work(m):
            with lock:
                tree = free.pop()
            try:
                res = judge(tree, m, slow=slow)
            finally:
                with lock:
                    free.append(tree)
            if res["outcome"] == "OPEN" and m["slug"] in m6.EQUIVALENT_6:
                res = {"outcome": "equivalent", "detail": m6.EQUIVALENT_6[m["slug"]]}
            say(f"[{m['slug']}] {res['outcome']:14s} {m['file']}: {m['name']}"
                + (f"  — {res['detail']}" if res["detail"] else ""))
            return m["slug"], res["outcome"]
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            done = dict(pool.map(work, mutants))
    tally = {}
    for v in done.values():
        tally[v] = tally.get(v, 0) + 1
    stale = sorted(set(m6.EQUIVALENT_6) - {m["slug"] for m in all_mutants()})
    say(f"\n=== {len(done)} mutants in {time.time() - t0:.0f} s: "
        + ", ".join(f"{k} {v}" for k, v in sorted(tally.items()))
        + (f"; EQUIVALENT_6 names no mutant: {stale}" if stale else ""))
    if log_path:
        Path(log_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    bad = [s for s, v in done.items() if v in ("OPEN", "ERROR")]
    if not slow:
        bad = [s for s, v in done.items() if v == "ERROR"]
    return 1 if (bad or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
