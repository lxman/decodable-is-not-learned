# experiments/exp5/tests/mutation_check.py
"""Mutation-test exp5's OWN modules — `battery_5.py` (the pins, the
spine substitution, the loaders' record checks, gate 1's tolerance,
`unit_complete_5`, `clears_5`), `slice_5.py` (the pure parts: `slice_
equal_5`, `loss_from_per_doc_5`), `search_5.py` (the deterministic
matching search: bisection, the crossing test), `stats_5.py` (the
primary statistic: the sign-flip null, the bar, the modifier, the
performability classes), `collect_5.py` (the unit pipeline: write
order, the prefetcher), `run/finals_5.py` (gate 1(a)'s loss-equality
check), `run/sweep_5.py`, `analyze_5.py` (the gates, `run()`'s verdict
path — every `collect_total_5` call site in `run()`'s own body,
AST-generated via a LOCAL `_totality_mutants_5`, exp4c's own `mutation_
check.py` with the name check changed to `collect_total_5` and the
walk restricted to the `run` FunctionDef — `test_totality_5.py`'s own
`_site_templates_5` is the same restriction, kept independent here
rather than imported so this file has no test-module dependency), and
`power_5.py` (the write-once guard, the power bar). Everything
imported from `experiments/exp2*` is FROZEN instrument and is not
re-targeted here.

Run each mutant against the FAST modules only (`test_battery_5.py`,
`test_slice_5.py`, `test_search_5.py`, `test_stats_5.py`, `test_
collect_5.py`, `test_stages_5.py`, `test_power_5.py`, `test_analyze_
5.py`, `test_verify_referents_5.py -m "not slow"`) — together under
three minutes. A mutant that survives the fast modules is either
closed with a new fast test (preferred) or, when only the slow worlds
can observe the behaviour it changes, recorded in `NON_FAST_KILLS_5`
below and confirmed by `--worlds-only` (against `test_totality_5.py`
first, `test_full_shape_5.py` second). The two reproducible records of
which mutants took which path are the committed `mutation_build.log`
(`main()`'s own fast-pass run) and `mutation_worlds.log` (`run_worlds_
only`'s non-fast pass) — both regenerated from the CURRENT source by
re-running this file, never hand-edited.

Mutates sources IN PLACE (with an exclusive `.mutation_backup`) and
restores them in `finally` — run alone, detached, never under a
foreground timeout, never concurrently with another mutation run."""
from __future__ import annotations

import ast
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _slug(text: str) -> str:
    """exp4c's `mutation_check.py::_slug` — a stable, comma-free,
    CLI-selectable label derived from a mutant's own description text."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return s[:72]


L = ROOT / "experiments" / "exp5"
BAT5 = L / "battery_5.py"
SL5 = L / "slice_5.py"
SE5 = L / "search_5.py"
ST5 = L / "stats_5.py"
CL5 = L / "collect_5.py"
FIN5 = L / "run" / "finals_5.py"
SW5 = L / "run" / "sweep_5.py"
AN5 = L / "analyze_5.py"
PW5 = L / "power_5.py"


def _run_function_node(path: Path):
    src = path.read_text()
    tree = ast.parse(src, filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            return node, src
    raise RuntimeError(f"{path}: no top-level run() found")


def _totality_mutants_5(path: Path) -> list:
    """One mutant per `collect_total_5(thunk, label)` call site
    TEXTUALLY INSIDE `run()`'s own body (the same AST restriction
    `test_totality_5.py::_site_templates_5` uses — `secondaries_5`,
    a separate top-level function `run()` merely calls, is excluded):
    replaced VERBATIM at that exact source span by `((thunk)(), [])` —
    the thunk runs uncaught, reporting zero failures regardless of
    what it does. A site whose exact text is not unique in the source
    is skipped by `main()`'s own `count(old) != 1` guard.

    Every totality mutant carries a `label` — a hash of the call
    site's own FULL source text — stable across any edit that does
    not touch the site itself, independent of its line number
    (exp4's/exp4c's review lesson, carried forward)."""
    fn_node, src = _run_function_node(path)
    out = []
    for node in ast.walk(fn_node):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total_5" or not node.args:
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if full is None or thunk is None:
            continue
        label = "totality_" + hashlib.sha256(full.encode()).hexdigest()[:10]
        out.append((path, f"run(): totality — collect_total_5 stripped at line "
                          f"{node.lineno} ({thunk.splitlines()[0][:60]}...)",
                   full, f"(({thunk})(), [])", label))
    return out


M = [
    # -------------------------------------------------------------- stats_5.py
    (ST5, "tree_5: the bar T >= T_BAR_5 widened to T > T_BAR_5",
     "T >= b5.T_BAR_5", "T > b5.T_BAR_5"),
    (ST5, "tree_5: the alpha comparison p < ALPHA_5 widened to p <= ALPHA_5",
     "p < b5.ALPHA_5", "p <= b5.ALPHA_5"),
    (ST5, "sign_flip_p_5: the enumerated null's identity row (all +1 signs) dropped",
     "        signs = (((np.arange(2 ** k, dtype=np.int64)[:, None] >> np.arange(k)) & 1) * 2 - 1)",
     "        signs = (((np.arange(2 ** k - 1, dtype=np.int64)[:, None] >> np.arange(k)) & 1) * 2 - 1)"),
    (ST5, "cell_5: P = mean(sides) becomes P = sum(sides)",
     "    P = (sum(sides) / len(sides)) if sides else None",
     "    P = sum(sides) if sides else None"),
    (ST5, "cell_5: R = abs(a - f) drops the abs",
     "    R = abs(a - f)", "    R = a - f"),
    (ST5, "cell_5: live = any(...) widened to all(...)",
     "    live = any(clears[k] for k in seven)", "    live = all(clears[k] for k in seven)"),
    (ST5, "modifier_5: the two-sided binomial test narrowed to one-sided",
     'p = float(binomtest(n_pos, n, 0.5, alternative="two-sided").pvalue)',
     'p = float(binomtest(n_pos, n, 0.5, alternative="greater").pvalue)'),

    # ------------------------------------------------------------- search_5.py
    (SE5, "bisect_step_5: the tie-break flipped toward the HIGHER step",
     "    return min(inside, key=lambda s: (abs(s - mid), s))",
     "    return min(inside, key=lambda s: (abs(s - mid), -s))"),
    (SE5, "plan_5: the crossing test losses[a] >= target > losses[b] operators swapped",
     "        if losses[a] >= target > losses[b]:",
     "        if losses[a] > target >= losses[b]:"),

    # ------------------------------------------------------------ battery_5.py
    (BAT5, "spine_5: the substitution picks the step BELOW the excluded point, not above",
     "        above = [a for a in avail if a > s]",
     "        above = [a for a in avail if a < s]"),
    (BAT5, "clears_5: the binomial significance bar replaced by a plain rate >= floor reading",
     '    return bool(st.binomial_bar(int(count), n, floor)["significant"])',
     "    return bool((int(count) / n) >= floor)"),
    (BAT5, "MODIFIER_MIN_CELLS_5 (THIN threshold): 8 -> 7",
     "MODIFIER_MIN_CELLS_5 = 8", "MODIFIER_MIN_CELLS_5 = 7"),
    (BAT5, "MIN_LIVE_CELLS_5: 20 -> 19",
     "MIN_LIVE_CELLS_5 = 20", "MIN_LIVE_CELLS_5 = 19"),
    (BAT5, "N_WINDOW_SIDE_5: 2 -> 1",
     "N_WINDOW_SIDE_5 = 2", "N_WINDOW_SIDE_5 = 1"),
    (BAT5, "unit_complete_5: the per-file sha comparison dropped (existence-only)",
     "    return all((d / name).is_file() and bg.sha256_file(d / name) == sha\n"
     "               for name, sha in files.items())",
     "    return all((d / name).is_file()\n"
     "               for name, sha in files.items())"),
    (BAT5, "tolerance_failures_5: the per-rung tolerance widened from > to >=",
     "        if d > GATE1_TOL_PER_RUNG_5:", "        if d >= GATE1_TOL_PER_RUNG_5:"),

    # ------------------------------------------------------------- collect_5.py
    (CL5, "run_unit_5: _unit.json written BEFORE the 34 rung records, not after",
     '        for rung in b5.RUNGS:\n'
     '            t = time.time()\n'
     '            ev = evaluate_items(runner, battery[rung], verify_fn)\n'
     '            _write(b5.rung_record_path_5(root, size, step, rung),\n'
     '                   rung_record_5(size=size, step=step, rung=rung, cap=battery[rung], ev=ev,\n'
     '                                 ckpt=ckpt, host=host, git_sha=git_sha, t_s=time.time() - t))\n'
     '        files = {name: bg.sha256_file(d / name) for name in b5.unit_files_5()}\n'
     '        _write(b5.unit_record_path_5(root, size, step),\n'
     '               {"size": size, "step": int(step), "why": why, "files": files, "digest": digest,\n'
     '                "loss": loss["loss"], "git_sha": git_sha, "host_sha256": host["sha256"],\n'
     '                "prereg_tag": b5.PREREG_TAG_5, "seconds": round(time.time() - t0, 1),\n'
     '                "written_utc": datetime.now(timezone.utc).isoformat()})',
     '        files = {name: bg.sha256_file(d / name) for name in b5.unit_files_5()}\n'
     '        _write(b5.unit_record_path_5(root, size, step),\n'
     '               {"size": size, "step": int(step), "why": why, "files": files, "digest": digest,\n'
     '                "loss": loss["loss"], "git_sha": git_sha, "host_sha256": host["sha256"],\n'
     '                "prereg_tag": b5.PREREG_TAG_5, "seconds": round(time.time() - t0, 1),\n'
     '                "written_utc": datetime.now(timezone.utc).isoformat()})\n'
     '        for rung in b5.RUNGS:\n'
     '            t = time.time()\n'
     '            ev = evaluate_items(runner, battery[rung], verify_fn)\n'
     '            _write(b5.rung_record_path_5(root, size, step, rung),\n'
     '                   rung_record_5(size=size, step=step, rung=rung, cap=battery[rung], ev=ev,\n'
     '                                 ckpt=ckpt, host=host, git_sha=git_sha, t_s=time.time() - t))'),
    (CL5, "Prefetcher.wait: a background prefetch failure is never even printed",
     '            if self._err is not None:\n'
     '                print(f"[5 prefetch] failed ({self._err}); the unit\'s own download will '
     'retry",\n'
     '                      flush=True)',
     '            if False:\n'
     '                print(f"[5 prefetch] failed ({self._err}); the unit\'s own download will '
     'retry",\n'
     '                      flush=True)'),

    # ---------------------------------------------------------- run/finals_5.py
    (FIN5, "gate1a: loss_equal ignores per_doc_loss (aggregate-only)",
     '           "loss_equal": (repr(loss_a["loss"]) == repr(loss_b["loss"])\n'
     '                          and loss_a["per_doc_loss"] == loss_b["per_doc_loss"]),',
     '           "loss_equal": (repr(loss_a["loss"]) == repr(loss_b["loss"])),'),

    # ----------------------------------------------------------- run/sweep_5.py
    (SW5, "run(): the halted-size refusal dropped (a halted size resumes anyway)",
     '    if b5.halt_marker_path_5(root, size).exists():\n'
     '        raise RuntimeError(f"refusing: {size} is halted ({b5.halt_marker_path_5(root, size)})")',
     '    if False:\n'
     '        raise RuntimeError(f"refusing: {size} is halted ({b5.halt_marker_path_5(root, size)})")'),

    # ------------------------------------------------------------- analyze_5.py
    (AN5, "replay_pairs_5: the replay target reads the LOGGED target, not the small final's loss",
     "        rep = se5.replay_5(losses, available, spine_expected, target)",
     "        rep = se5.replay_5(losses, available, spine_expected, logged_target)"),
    (AN5, "_gate4: an orphan unit (units_unnamed) is never turned into a failure",
     '            if unnamed:\n'
     '                pf = pf + [f"gate 4 {size}: step{s} on disk but never requested (nothing else "\n'
     '                          f"loaded)" for s in unnamed]',
     '            if False:\n'
     '                pf = pf + [f"gate 4 {size}: step{s} on disk but never requested (nothing else "\n'
     '                          f"loaded)" for s in unnamed]'),
    (AN5, "projection_failures_5: the final step is no longer excluded from the ancestry check",
     "        for step, sha in git_shas.items():\n"
     "            if int(step) == b5.FINAL_STEP_5:\n"
     "                continue\n"
     "            if not is_ancestor(projection_commit, sha):",
     "        for step, sha in git_shas.items():\n"
     "            if not is_ancestor(projection_commit, sha):"),
    (AN5, "power_failures_5: n_sim provenance never compared",
     '    if rec.get("n_sim") != pw.N_SIM_5:\n'
     "        bad.append(f\"power record: n_sim {rec.get('n_sim')!r} != power_5.N_SIM_5 \"\n"
     '                   f"{pw.N_SIM_5!r} — provenance is measured, not attested")',
     '    if False:\n'
     "        bad.append(f\"power record: n_sim {rec.get('n_sim')!r} != power_5.N_SIM_5 \"\n"
     '                   f"{pw.N_SIM_5!r} — provenance is measured, not attested")'),

    # -------------------------------------------------------------- power_5.py
    (PW5, "main: the write-once refusal dropped (a second write silently overwrites)",
     '    if out.is_file():\n'
     '        raise RuntimeError(f"power_5.main: {out} exists — the power record is written ONCE")',
     '    if False:\n'
     '        raise RuntimeError(f"power_5.main: {out} exists — the power record is written ONCE")'),
    (PW5, "POWER_BAR_5: 0.75 -> 0.5",
     "POWER_BAR_5 = 0.75", "POWER_BAR_5 = 0.5"),

    # -------------------------------------------------------------- slice_5.py
    (SL5, "slice_equal_5: the set_index array comparison dropped",
     '    for k in ("ids", "offsets", "set_index"):',
     '    for k in ("ids", "offsets"):'),
    (SL5, "loss_from_per_doc_5: a per-set n_tokens count zeroed instead of measured",
     '        per_set[name] = {"loss": float(sums[m].sum() / n_k) if n_k else None, "n_tokens": n_k}',
     '        per_set[name] = {"loss": float(sums[m].sum() / n_k) if n_k else None, "n_tokens": 0}'),

    # ----------------------------------------------- the freeze's closures (F-1..F-6)
    (SW5, "freeze F-1: the spine loaded for a size that is never a large side",
     "    for s in (spine if is_large else ()):", "    for s in spine:"),
    (AN5, "freeze F-2: gate1a per_doc_diffs never re-derived",
     '    if rec.get("per_doc_diffs") != 0:', '    if False:'),
    (AN5, "freeze F-2: gate1a loss_2c_path vs loss_candidate_path never re-derived",
     "    if not (isinstance(la, float) and isinstance(lb, float) and repr(la) == repr(lb)):",
     "    if not (isinstance(la, float) and isinstance(lb, float)):"),
    (AN5, "freeze F-2: the candidate path's loss never tied to the 2.8b final unit",
     '    if repr(rec.get("loss_candidate_path")) != repr(final_2p8b.get("loss")):',
     '    if False:'),
    (BAT5, "freeze F-3: the stack pins never checked in the host record",
     "    bad += stack_pin_failures_5(rec)\n", "    bad += []\n"),
    (AN5, "freeze F-3: the checkpoint record's host attestation never compared",
     '            bad += b5._same_host(ck_rec, host, f"{size}/step{step}/_checkpoint")',
     '            bad += []'),
    (BAT5, "freeze F-4: a NaN loss passes the measured finiteness check",
     "    if not (isinstance(lv, float) and math.isfinite(lv)):",
     "    if not isinstance(lv, float):"),
    (AN5, "freeze F-4: a torn step directory is never turned into a failure",
     '            if torn:\n                pf = pf + [f"gate 3 {size}',
     '            if False:\n                pf = pf + [f"gate 3 {size}'),
    (BAT5, "freeze F-5: later commits touching projection.md never listed",
     "            for c in later.stdout.split() if c]", "            for c in [] if c]"),
    (AN5, "freeze F-6: drop_kind never_reaches mislabelled",
     '        return "never_reaches"', '        return "crosses_before_spine"'),
]

# Every hand mutant above is a 4-tuple (path, name, old, new); every
# AST-generated totality mutant is already a 5-tuple with its own
# hash-derived label. Normalize the hand mutants to 5-tuples by
# deriving their label from the description text (`_slug`), THEN
# append the totality mutants — so hand-mutant labels are always
# `_slug(name)`, never a totality hash.
M = [(p, name, old, new, _slug(name)) for p, name, old, new in M]
M += _totality_mutants_5(AN5)

_labels = [m[4] for m in M]
assert len(_labels) == len(set(_labels)), (
    f"mutation_check.py: duplicate mutant labels — {[l for l in _labels if _labels.count(l) > 1]}")


FAST_TESTS = [str(L / "tests" / "test_battery_5.py"), str(L / "tests" / "test_slice_5.py"),
             str(L / "tests" / "test_search_5.py"), str(L / "tests" / "test_stats_5.py"),
             str(L / "tests" / "test_collect_5.py"), str(L / "tests" / "test_stages_5.py"),
             str(L / "tests" / "test_power_5.py"), str(L / "tests" / "test_analyze_5.py"),
             str(L / "tests" / "test_verify_referents_5.py")]
FAST_EXTRA_ARGS = ["-m", "not slow"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_5.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_5.py")]
WORLDS_TESTS = TOTALITY_TESTS + FULLSHAPE_TESTS

# Mutants killed ONLY by a slow (totality/full-shape) test — populated
# as fast-pass survivors are individually confirmed against the slow
# suites via `--worlds-only`; see PROGRESS.md's Task 6 entry for the
# transcript. Each value names the exact killing test.
NON_FAST_KILLS_5 = {
    "freeze_f_4_a_torn_step_directory_is_never_turned_into_a_failure":
        "test_full_shape_5.py::test_refusal_routes_deliver_insufficient_data",
    "gate4_an_orphan_unit_units_unnamed_is_never_turned_into_a_failure":
        "test_full_shape_5.py::test_refusal_routes_deliver_insufficient_data",
    "totality_1007afd168": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_138a23d00f": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_1bc33db24b": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_223e38694e": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_2c46608367": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_3339204c5a": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_33f9851f81": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_3ec118fa91": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_40ef758834": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_456c3066bc": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_49618d9fb5": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_4f95d553d7": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_5b3140592f": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_71c7feae97": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_71da69b926": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_7226035f79": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_7a4d35f5a0": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_7e528df1ad": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_95697235f9": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_ad39e59a5f": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_b2fb2be78d": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_b47686f67d": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_bed8157518": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_ca59f913cb": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_dbe9455868": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_ed13262569": "test_totality_5.py::test_site_template_count_matches_the_brief",
    "totality_f7541f99c2": "test_totality_5.py::test_every_runner_leavable_tree_shape_gives_"
                           "insufficient_data",
    "totality_fdf4511a43": "test_totality_5.py::test_site_template_count_matches_the_brief",
}
# Process note (disclosed): most `totality_*` labels are "killed" by
# `test_site_template_count_matches_the_brief` — a STRUCTURAL check
# (removing any collect_total_5 call drops the AST-detected site count
# below 28), not a behavioural one. This is a legitimate kill under the
# usual mutation-testing convention (some test in the covering suite
# fails), and every totality mutant is ALSO exercised behaviourally by
# `test_every_runner_leavable_tree_shape_gives_insufficient_data`'s own
# corruption shapes and by the 27/28-site census test, which run first
# in file order — but only 6 of the 29 sites here have a shape in the
# 9-shape list that actually drives that specific site to a raise
# (halt/torn-unit/orphan/no-search-log/no-power/bad-ancestor); the
# other 23 (loaders, gate 1(b), the primary/modifier/cells pipeline,
# import-surface, referents) are not independently exercised by a
# corruption scenario that would fail WITHOUT the site-count check.
# PROGRESS.md's Task 6 entry carries this finding forward.

# Mutants that survive BOTH the fast and slow suites, with a DOCUMENTED
# reason the mutation is behaviourally equivalent on every input this
# instrument's own tests can construct — never added without a proof
# in the comment beside the entry.
EQUIVALENT_MUTANTS = set()


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp5" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """exp4c's/2k's Finding 3 lesson: a stray `.mutation_backup`
    anywhere under `experiments/exp5` means either a concurrent run is
    already in flight or a previous run crashed without restoring —
    refuse before the baseline check even starts."""
    found = sorted((ROOT / "experiments" / "exp5").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp5 (a concurrent run, or a previous crash that "
                           f"never restored) — resolve by hand before starting a new run: {found}")


def _acquire_backup(path):
    backup = path.with_suffix(path.suffix + ".mutation_backup")
    try:
        with open(backup, "xb") as f:
            f.write(path.read_bytes())
    except FileExistsError:
        raise RuntimeError(f"refusing: {backup} already exists — a concurrent mutation_check.py "
                           f"run may be in flight against {path.name} (or a previous run crashed "
                           f"without restoring); resolve it by hand before retrying")
    return backup


def run_suite(tests, extra_args=None, timeout=None, extra_env=None):
    """Returns `(ok, out, timed_out, no_tests_collected)`. A timeout is
    NOT a kill: `subprocess.run(..., timeout=...)` kills the child
    itself on expiry and raises `TimeoutExpired`, caught here and
    reported as `timed_out=True` — the caller must never fold this
    into either `ok` or `survived`. pytest exits 5 ("no tests ran")
    when a `-k` pattern selects nothing — NOT `returncode == 0`, so
    already never `ok`, but folding it into `survived` would silently
    read a stale mapping as a kill; `no_tests_collected` lets the
    caller route it to a SKIP instead."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(extra_env or {})}
    args = list(extra_args or [])
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                            *tests, *args], cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode == 0, r.stdout[-600:], False, r.returncode == 5
    except subprocess.TimeoutExpired as e:
        partial = e.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode(errors="replace")
        return False, partial[-600:], True, False


def _extract_failed_test(stdout: str) -> str:
    """The pytest node id of the first FAILED test in a `-x` run's
    FULL stdout (never the 600-char-truncated `run_suite` tail)."""
    for line in stdout.splitlines():
        if line.startswith("FAILED "):
            return line[len("FAILED "):].split(" ")[0].strip()
    return None


def _run_suite_full(tests, extra_args=None, timeout=None, extra_env=None):
    """`run_suite`'s body, returning the FULL stdout (not the last 600
    chars) so `_extract_failed_test` can find the summary line — used
    only by `run_worlds_only`."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(extra_env or {})}
    args = list(extra_args or [])
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                            *tests, *args], cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode == 0, r.stdout, False, r.returncode == 5
    except subprocess.TimeoutExpired as e:
        partial = e.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode(errors="replace")
        return False, partial, True, False


WORLD_ONLY_LABELS = sorted(NON_FAST_KILLS_5)


def run_worlds_only(argv) -> int:
    """Executes every label in `WORLD_ONLY_LABELS` against `test_
    totality_5.py` first, `test_full_shape_5.py` second if totality
    alone doesn't catch it (`-m slow` both times). Prints one line per
    label with the identified killing test (or OPEN if every route
    survives) and a final tally; writes nothing to `NON_FAST_KILLS_5`
    itself — the caller reads this run's own stdout log and updates
    that table by hand, so the committed record is never wider than
    what was actually observed."""
    only = _parse_only(argv)
    labels = [lbl for lbl in WORLD_ONLY_LABELS if only is None or lbl in only]
    by_label = {m[4]: m for m in M}
    missing = [lbl for lbl in labels if lbl not in by_label]
    if missing:
        raise RuntimeError(f"run_worlds_only: label(s) not found in M: {missing}")

    _refuse_if_any_backup_exists()
    clear_pycache()

    killed_by, open_survivors, errors = {}, [], []
    for n, label in enumerate(labels, 1):
        path, name, old, new, mlabel = by_label[label]
        sequence = [("totality", TOTALITY_TESTS, ["-m", "slow"]),
                    ("fullshape", FULLSHAPE_TESTS, ["-m", "slow"])]

        src = path.read_text()
        if src.count(old) != 1:
            print(f"[{label}] ({n}/{len(labels)}) SKIP: target text not found exactly once "
                 f"(count={src.count(old)})", flush=True)
            errors.append((label, "target-not-found"))
            continue

        found = False
        for mode_name, tests, extra in sequence:
            backup = _acquire_backup(path)
            try:
                path.write_text(src.replace(old, new))
                clear_pycache()
                ok, out, timed_out, no_tests = _run_suite_full(tests, extra, timeout=900)
            finally:
                shutil.copy2(backup, path)
                backup.unlink()
                clear_pycache()
            if timed_out:
                print(f"[{label}] ({n}/{len(labels)}) {mode_name}: TIMEOUT", flush=True)
                continue
            if no_tests:
                print(f"[{label}] ({n}/{len(labels)}) {mode_name}: no tests collected", flush=True)
                continue
            if not ok:
                test_id = _extract_failed_test(out) or "(unidentified — see full stdout)"
                print(f"[{label}] ({n}/{len(labels)}) KILLED by {mode_name}: {test_id}", flush=True)
                killed_by[label] = f"{mode_name}:{test_id}"
                found = True
                break
            print(f"[{label}] ({n}/{len(labels)}) survived {mode_name}", flush=True)
        if not found:
            print(f"[{label}] ({n}/{len(labels)}) OPEN SURVIVOR — every route tried failed to "
                 f"kill it: {name}", flush=True)
            open_survivors.append(label)

    print(f"\n=== run_worlds_only tally === considered={len(labels)} "
         f"killed={len(killed_by)} open_survivors={len(open_survivors)} errors={len(errors)}")
    print(f"killed_by = {killed_by}")
    print(f"open_survivors = {open_survivors}")
    print(f"errors = {errors}")
    return 1 if (open_survivors or errors) else 0


def _parse_only(argv) -> set:
    for a in argv:
        if a.startswith("--only="):
            return {x for x in a[len("--only="):].split(",") if x}
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 < len(argv):
            return {x for x in argv[i + 1].split(",") if x}
    return None


def _parse_timeout(argv):
    for a in argv:
        if a.startswith("--timeout="):
            return float(a[len("--timeout="):])
    if "--timeout" in argv:
        i = argv.index("--timeout")
        if i + 1 < len(argv):
            return float(argv[i + 1])
    return None


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--worlds-only" in argv:
        return run_worlds_only(argv)
    totality = "--totality" in argv
    fullshape = "--fullshape" in argv
    if fullshape:
        tests, extra = FULLSHAPE_TESTS, ["-m", "slow"]
    elif totality:
        tests, extra = TOTALITY_TESTS, ["-m", "slow"]
    else:
        tests, extra = FAST_TESTS, FAST_EXTRA_ARGS
    only = _parse_only(argv)
    timeout = _parse_timeout(argv)

    _refuse_if_any_backup_exists()
    clear_pycache()
    # The baseline always runs the WHOLE file set (no `-k`): a real,
    # unmutated confirmation that every covering test still passes.
    ok, out, timed_out, _ = run_suite(tests, extra, timeout=timeout)
    if timed_out:
        print(f"BASELINE TIMED OUT after {timeout}s — investigate before trusting any mutant "
             f"result from this run\n", out)
        return 3
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    label = "totality/fullshape" if (totality or fullshape) else "fast"
    print(f"baseline OK ({label} pass, "
         f"{'all' if only is None else sorted(only)} mutants"
         f"{f', timeout={timeout}s' if timeout else ''})\n", flush=True)

    survivors = []
    timeouts = []
    considered = 0
    n_killed_slow = 0
    n_equivalent = 0
    for i, (path, name, old, new, mlabel) in enumerate(M, 1):
        if only is not None and mlabel not in only and str(i) not in only:
            continue
        considered += 1
        src = path.read_text()
        if src.count(old) != 1:
            print(f"[{mlabel}] (#{i}) SKIP  {name}: target text not found exactly once in "
                 f"{path.name} (count={src.count(old)})")
            survivors.append((mlabel, i, name, "target-not-found"))
            continue
        backup = _acquire_backup(path)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out, timed_out, no_tests = run_suite(tests, extra, timeout=timeout)
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        if timed_out:
            print(f"[{mlabel}] (#{i}) TIMEOUT  {name}  (no verdict — not counted as killed or "
                 f"survived; a timeout is not a kill)", flush=True)
            timeouts.append((mlabel, i, name, "timeout"))
            continue
        if no_tests:
            print(f"[{mlabel}] (#{i}) SKIP  {name}  (collected 0 tests against the MUTATED "
                 f"source — not counted as killed or survived)", flush=True)
            survivors.append((mlabel, i, name, "no-tests-collected"))
            continue
        if ok and mlabel in NON_FAST_KILLS_5:
            print(f"[{mlabel}] (#{i}) survived-fast, killed by the slow suite — "
                 f"{NON_FAST_KILLS_5[mlabel]} (individually re-confirmed, see PROGRESS.md)  "
                 f"{name}", flush=True)
            n_killed_slow += 1
            continue
        if ok and mlabel in EQUIVALENT_MUTANTS:
            print(f"[{mlabel}] (#{i}) survived, EQUIVALENT (documented reasoning in "
                 f"mutation_check.py)  {name}", flush=True)
            n_equivalent += 1
            continue
        print(f"[{mlabel}] (#{i}) {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((mlabel, i, name, "survived"))
    skipped = [s for s in survivors if s[3] in ("target-not-found", "no-tests-collected")]
    real = [s for s in survivors if s[3] == "survived"]
    killed_fast = considered - len(survivors) - len(timeouts) - n_killed_slow - n_equivalent
    print(f"\n{killed_fast} killed by the fast suite directly; "
          f"{n_killed_slow} killed by the slow suite (each individually re-confirmed via "
          f"--worlds-only, not inferred — see mutation_worlds.log); "
          f"{n_equivalent} documented equivalent; "
          f"considered={considered}; "
          f"{len(real)} UNRESOLVED survivor(s): {real}; "
          f"{len(skipped)} SKIP (target text not found / -k selected nothing): {skipped}; "
          f"{len(timeouts)} TIMEOUT (not a kill, not a survivor): {timeouts}")
    return 1 if (real or timeouts) else 0


if __name__ == "__main__":
    sys.exit(main())
