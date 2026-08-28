# experiments/exp2j/tests/mutation_check.py
"""Mutation-test exp2j's OWN modules — functionals_2j (the bucket rule,
the four functionals, the density-matched thinner) and analyze_2j (the
tree, the pin/comparison machinery, t_only, the block gate,
_load_power_2j, a1_density, rederive_2i/rederive_2g2h, and every
`collect_total` call site in `run()`, AST-generated via 2i's own
`_totality_mutants`, imported verbatim rather than re-implemented).
2i/2g/2h/2d/2c/exp3/exp3c are frozen instrument, pinned by
`FROZEN_SHA256_2J`, and are not re-targeted here.

Task 4's ruling: run each mutant against the FAST modules only
(`test_functionals_2j.py`, `test_analyze_2j.py` — a few seconds each);
the world/totality modules take ~14 minutes each and would make a
60-mutant run a many-hour one. A mutant that survives the fast modules
is either closed with a new fast test (preferred) or, when only a
world/totality shape can observe the behaviour it changes, recorded as
'killed by worlds only' after one targeted confirmation run — see
PROGRESS.md's Task 4 entry for which mutants took that path, and for
`matched_k`'s upper clip (64 -> 65), which is a documented EQUIVALENT
mutant (proved in the ledger, not merely asserted): the pre-clip value
can never exceed 64 given the function's own `sparse <= dense`
invariant, for any (rate_a, rate_b), so the clip's upper bound is dead
code and no test — fast or otherwise — can distinguish it.

Mutates sources IN PLACE (with a `.mutation_backup` copy) and restores
them in `finally` — run alone, detached (nohup), never under a
foreground timeout."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.exp2i.tests.mutation_check import _totality_mutants  # noqa: E402

J = ROOT / "experiments/exp2j"
FN = J / "functionals_2j.py"
AN = J / "analyze_2j.py"

M = [
    # ---------------------------------------------------- functionals_2j.py
    (FN, "bucket: first branch '>' loosened to '>=' (median branch)",
     "    b = [int(v > med) for v in arr]",
     "    b = [int(v >= med) for v in arr]"),
    (FN, "bucket: tie_fallback branch disabled (always dropped_after_fallback)",
     '    b = [int(v >= med) for v in arr]\n    if len(set(b)) == 2:\n        return b, "tie_fallback"',
     '    b = [int(v >= med) for v in arr]\n    if False:\n        return b, "tie_fallback"'),
    (FN, "bucket: constant-drop bar loosened (< 2 -> < 1, dropped_constant no "
         "longer fires on a genuinely constant array)",
     '    """design \xa75.2 / dial b: 1[F > med]; if constant, 1[F >= med]; if\n'
     "    still constant, dropped. 2i's `_median_bucket` is the strict first\n"
     '    branch alone (ties fall in bucket 0)."""\n'
     "    arr = np.asarray(values, dtype=np.float64)\n"
     "    if len(set(arr.tolist())) < 2:",
     '    """design \xa75.2 / dial b: 1[F > med]; if constant, 1[F >= med]; if\n'
     "    still constant, dropped. 2i's `_median_bucket` is the strict first\n"
     '    branch alone (ties fall in bucket 0)."""\n'
     "    arr = np.asarray(values, dtype=np.float64)\n"
     "    if len(set(arr.tolist())) < 1:"),
    (FN, "wrong_target_propensity: loo/non-loo branches swapped",
     "        if loo:\n"
     "            num, den = total[a] - per_item[i][a], n_total - DRAWS_PER_ITEM\n"
     "        else:\n"
     "            num, den = total[a] - by_answer[a][0][a], n_total - by_answer[a][1]",
     "        if loo:\n"
     "            num, den = total[a] - by_answer[a][0][a], n_total - by_answer[a][1]\n"
     "        else:\n"
     "            num, den = total[a] - per_item[i][a], n_total - DRAWS_PER_ITEM"),
    (FN, "wrong_target_propensity: non-loo numerator no longer excludes "
         "same-answer draws (by_answer[a][0][a] -> 0)",
     "            num, den = total[a] - by_answer[a][0][a], n_total - by_answer[a][1]",
     "            num, den = total[a] - 0, n_total - by_answer[a][1]"),
    (FN, "input_overlap: question no longer lowercased before matching",
     '        q = str(it["question"]).lower()',
     '        q = str(it["question"])'),
    (FN, "repeated_char: '<' loosened to '<=' (every answer reads as repeated)",
     "    return [int(len(set(a)) < len(a)) for a in normalized_answers(cap)]",
     "    return [int(len(set(a)) <= len(a)) for a in normalized_answers(cap)]"),
    (FN, "answer_length: raw answer instead of normalized",
     "def answer_length(cap) -> list:\n"
     "    return [len(a) for a in normalized_answers(cap)]",
     "def answer_length(cap) -> list:\n"
     '    return [len(str(it["answer"])) for it in cap["eval_items"]]'),
    (FN, "matched_k: floor(...+0.5) replaced by int() truncation",
     "    k = int(np.floor(DRAWS_PER_ITEM * sparse / dense + 0.5))",
     "    k = int(DRAWS_PER_ITEM * sparse / dense)"),
    (FN, "matched_k: clip upper bound 64 -> 65 — DOCUMENTED EQUIVALENT: "
         "sparse <= dense by construction, so the pre-clip value can never "
         "exceed DRAWS_PER_ITEM (64) for any (rate_a, rate_b); the upper "
         "bound is dead code (ledgered, PROGRESS.md Task 4)",
     "    k = min(DRAWS_PER_ITEM, max(1, k))",
     "    k = min(65, max(1, k))"),
    (FN, "thinned_counts: slice start off by one (block * k -> block * k + 1)",
     "    return [int(sum(b[block * k:(block + 1) * k])) for b in bits]",
     "    return [int(sum(b[block * k + 1:(block + 1) * k])) for b in bits]"),
    (FN, "zero_fraction_k: '<' loosened to '<=' (ties prefer the larger k)",
     "        if best is None or d < best[0]:",
     "        if best is None or d <= best[0]:"),
    (FN, "composite_strata: join order reversed",
     '        out[r] = {"strata": ["|".join(p) for p in zip(*parts)]}',
     '        out[r] = {"strata": ["|".join(p) for p in zip(*list(reversed(parts)))]}'),
    # -------------------------------------------------------- analyze_2j.py
    (AN, "verdict_tree_2j: the firing branch reports ABSORBED instead of RESIDUAL",
     '        return {"verdict": "RESIDUAL", "declared_status": status,',
     '        return {"verdict": "ABSORBED", "declared_status": status,'),
    (AN, "_licensed: the plain POWERED branch returns the UNDERPOWERED licence",
     '            if s == "POWERED":\n                licensed = LICENSED_2J["ABSORBED"]',
     '            if s == "POWERED":\n                licensed = LICENSED_2J["ABSORBED_UNDERPOWERED"]'),
    (AN, "check_pin: exact != loosened to abs(...) > 1e-6",
     "        if k not in rederived or rederived[k] != on_disk.get(k):",
     "        if k not in rederived or abs(rederived[k] - on_disk.get(k)) > 1e-6:"),
    (AN, "check_pin: the on-disk-vs-literal check removed",
     "    if {k: on_disk.get(k) for k in literal} != literal:\n"
     '        bad.append(f"{label}: verdict.json {on_disk} != the literal pin {literal}")',
     "    if False:\n"
     '        bad.append(f"{label}: verdict.json {on_disk} != the literal pin {literal}")'),
    (AN, "t_only: mean -> median",
     '    return {"T": float(np.mean(list(per_rung.values()))), "per_rung": per_rung,',
     '    return {"T": float(np.median(list(per_rung.values()))), "per_rung": per_rung,'),
    (AN, "t_only: the degeneracy pre-check removed (dropped always empty)",
     "    dropped = list(an2i._degenerate_rungs(counts, strata, rungs))",
     "    dropped = []"),
    (AN, "run()/_core: the block gate '!=' flipped to '==' (raises on a "
         "correct reproduction instead of a drifted one) — world/totality only",
     '            if t64 != _T_of(comparison["rederived_2i"]["within_alone"]):',
     '            if t64 == _T_of(comparison["rederived_2i"]["within_alone"]):'),
    (AN, "_load_power_2j: rung-set equality relaxed to a subset check",
     '    if set(prim.get("rungs", [])) != set(r_cap):',
     '    if not set(r_cap).issubset(set(prim.get("rungs", []))):'),
    (AN, "a1_density: gap_fraction_closed denominator sign flipped — world/totality only",
     '            gap = float((t_b64 - matched_b["T"]) / (t_b64 - t_a64))',
     '            gap = float((t_b64 - matched_b["T"]) / (t_a64 - t_b64))'),
    # controller ruling (fix round 1): the brief's "gap >= 0.5 -> > 0.5
    # (boundary, keep)" meant KEEP THE MUTANT, not exclude it — at
    # gap == 0.5 exactly, `>=` reads DENSITY while `>` reads MIXED.
    (AN, "a1_density: DENSITY boundary tightened (gap >= 0.5 -> gap > 0.5)",
     "    elif all(g >= 0.5 for g in readings):",
     "    elif all(g > 0.5 for g in readings):"),
    (AN, "rederive_2i: 'B' uses _composite_strata_median instead of the zero "
         "cut (_composite_strata) — world/totality only",
     '        "B": _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x_a, r_cap),\n'
     "                       r_cap, **kw),",
     '        "B": _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata_median(strata, x_a, r_cap),\n'
     "                       r_cap, **kw),"),
    (AN, "rederive_2g2h: 'primary' reads R_28 instead of R_69 — world/totality only",
     '            "primary": _run_test(x_a_full, "1b", py["6.9b"], strata, tuple(bh.R_69), **kw)}',
     '            "primary": _run_test(x_a_full, "1b", py["6.9b"], strata, tuple(bg.R_28), **kw)}'),
]

# Review finding 4's lesson, one experiment later: one mutant per
# collect_total(...) call site in analyze_2j.py's run(), generated from
# the real, current source at import time rather than hand-picked.
M += _totality_mutants(AN)

# Task 4 ruling: fast modules only by default — the world/totality
# modules (test_full_shape_2j.py, test_totality_2j.py) take ~10-14
# minutes each. Fix round 1 (Finding 2): a `--totality` flag switches
# the covering suite to TOTALITY_TESTS so a totality-only kill (the
# block gate, `_cmp`, and the seven refusal-path mutants closed this
# round) is reproducible from the COMMITTED harness, not a scratch
# script — every number in the tally must be derivable from a
# committed log.
TESTS = [str(J / "tests" / "test_functionals_2j.py"), str(J / "tests" / "test_analyze_2j.py")]
TOTALITY_TESTS = [str(J / "tests" / "test_totality_2j.py")]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2j" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def run_suite(tests):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        *tests], cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode == 0, r.stdout[-600:]


def _parse_only(argv) -> set:
    """`--only N[,N,...]` — 1-based mutant indices (M's own numbering,
    printed by every run) to restrict this run to. Returns None (no
    restriction) if `--only` is absent."""
    for a in argv:
        if a.startswith("--only="):
            return {int(x) for x in a[len("--only="):].split(",") if x}
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 < len(argv):
            return {int(x) for x in argv[i + 1].split(",") if x}
    return None


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    totality = "--totality" in argv
    tests = TOTALITY_TESTS if totality else TESTS
    only = _parse_only(argv)

    clear_pycache()
    ok, out = run_suite(tests)
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    print(f"baseline OK ({'totality' if totality else 'fast'} pass, "
         f"{'all' if only is None else sorted(only)} mutants)\n", flush=True)

    survivors = []
    considered = 0
    for i, (path, name, old, new) in enumerate(M, 1):
        if only is not None and i not in only:
            continue
        considered += 1
        src = path.read_text()
        if src.count(old) != 1:
            print(f"[{i:2d}] SKIP  {name}: target text not found exactly once in {path.name} "
                  f"(count={src.count(old)})")
            survivors.append((i, name, "target-not-found"))
            continue
        backup = path.with_suffix(path.suffix + ".mutation_backup")
        shutil.copy2(path, backup)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out = run_suite(tests)
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        print(f"[{i:2d}] {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((i, name, "survived"))
    print(f"\n{considered - len(survivors)}/{considered} killed; survivors: {survivors}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
