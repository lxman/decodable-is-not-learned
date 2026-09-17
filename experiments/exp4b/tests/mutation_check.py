# experiments/exp4b/tests/mutation_check.py
"""Mutation-test exp4b's OWN modules -- battery_4b (the pin to Exp 4's
closed tree, the preregistration binding, the exp4-record loaders, the
design constants), placebo_4b (the leave-one-out trend/excess/
eligibility, the placebo batteries, `p_cal`/`T*`/`alpha_placebo`, S3-
S5/S8), power_ext_4b (gate (4)'s reproduction, the scaled zero-excess
arm, the extension arms), levels_4b (the site-family filter, the
per-item level, the CI machinery), and analyze_4b (the five gates, the
tree, `run()`'s verdict path -- every `collect_total_4b` call site in
`run()`, AST-generated via a LOCAL `_totality_mutants_4b`, exp4's own
`mutation_check.py::_totality_mutants_4` with the name check changed to
`collect_total_4b`). Everything imported from `experiments/exp2*`/
`experiments/exp3*`/`experiments/exp4/` is FROZEN instrument and is not
re-targeted here.

exp4's own precedent (this harness is that one, re-targeted): run each
mutant against the FAST modules only (`test_battery_4b.py`,
`test_placebo_4b.py`, `test_power_ext_4b.py`, `test_levels_4b.py`,
`test_analyze_4b.py -m "not slow"`) -- together a few seconds to a
couple of minutes, observing nothing a `--totality`/`--fullshape`
mutant changes. A mutant that survives the fast modules is either
closed with a new fast test (preferred) or, when only totality/full-
shape can observe the behaviour it changes, recorded as 'killed by
worlds/totality only' after one targeted confirmation run under
`--totality`/`--fullshape` -- see PROGRESS.md's Task 6 entry for which
mutants took that path.

Mutates sources IN PLACE (with an exclusive `.mutation_backup`) and
restores them in `finally` -- run alone, detached, never under a
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
    """exp4's `mutation_check.py::_slug` -- a stable, comma-free,
    CLI-selectable label derived from a mutant's own description text."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return s[:72]


L = ROOT / "experiments" / "exp4b"
BK4B = L / "battery_4b.py"
PL4B = L / "placebo_4b.py"
PE4B = L / "power_ext_4b.py"
LV4B = L / "levels_4b.py"
AN4B = L / "analyze_4b.py"


def _totality_mutants_4b(path: Path) -> list:
    """exp4's `_totality_mutants_4`, adapted: exp4b's refusal-collector
    is named `collect_total_4b`, not `collect_total_4`, so the AST name
    check is changed to match it. One mutant per `collect_total_4b(
    thunk, label)` call site: replaced VERBATIM at that exact source
    span by `(thunk(), [])` -- the thunk runs uncaught, reporting zero
    failures regardless of what it does. A site whose exact text is not
    unique in the source is skipped by main()'s own `count(old) != 1`
    guard, printed as a surviving SKIP rather than silently omitted.

    Every totality mutant carries a `label` -- a hash of the call
    site's own FULL source text (`full`: the thunk plus its message-
    label argument) -- stable across any edit that does not touch the
    site itself, independent of its line number or position in the
    walk (exp4's review round 2, IMPORTANT 1(a) lesson, carried
    forward)."""
    src = path.read_text()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total_4b" or not node.args:
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if full is None or thunk is None:
            continue
        label = "totality_" + hashlib.sha256(full.encode()).hexdigest()[:10]
        out.append((path, f"run(): totality -- collect_total_4b stripped at line "
                          f"{node.lineno} ({thunk.splitlines()[0][:60]}...)",
                   full, f"(({thunk})(), [])", label))
    return out


M = [
    # --------------------------------------------------------- battery_4b.py
    (BK4B, "ALPHA_4B = 0.01 -> 0.05", "ALPHA_4B = 0.01", "ALPHA_4B = 0.05"),
    (BK4B, "MARGINAL_4B = 0.05 -> 0.1", "MARGINAL_4B = 0.05", "MARGINAL_4B = 0.1"),
    (BK4B, "MIN_PLACEBO_TOTAL_4B = 8 -> 7", "MIN_PLACEBO_TOTAL_4B = 8", "MIN_PLACEBO_TOTAL_4B = 7"),
    (BK4B, "MIN_PLACEBO_PER_TRAJ_4B = 3 -> 2",
     "MIN_PLACEBO_PER_TRAJ_4B = 3", "MIN_PLACEBO_PER_TRAJ_4B = 2"),
    (BK4B, "check_exp4_closed_4b: the per-file pin comparison skipped",
     '''        if got != want:
            bad.append(f"{rel}: {got} != {want}")''',
     '''        if False:
            bad.append(f"{rel}: {got} != {want}")'''),
    (BK4B, "require_prereg_4b: the tag_exists check skipped",
     '''    if not tag_exists(PREREG_TAG_4B):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_4B} does not exist")''',
     '''    if False:
        raise RuntimeError(f"preregistration tag {PREREG_TAG_4B} does not exist")'''),
    (BK4B, "require_prereg_4b: the blob-binding equality check skipped",
     '''        want, got = blob_sha(PREREG_TAG_4B, rel), bg.sha256_file(p)
        if want != got:''',
     '''        want, got = blob_sha(PREREG_TAG_4B, rel), bg.sha256_file(p)
        if False:'''),

    # --------------------------------------------------------- placebo_4b.py
    (PL4B, "loo_trend_4b: leave-one-out pool keeps ONLY the rung itself (!= inverted to ==)",
     '''    pool = [r for r in flat if r != f]
    if not pool:
        raise ValueError(f"4b: leave-one-out pool empty for {f}")
    return an.trend_4(a, pool, steps)''',
     '''    pool = [r for r in flat if r == f]
    if not pool:
        raise ValueError(f"4b: leave-one-out pool empty for {f}")
    return an.trend_4(a, pool, steps)'''),
    (PL4B, "placebo_pool_4b: the eligibility bar compares with > instead of >=",
     '        eligible = x_end >= an.SE_MULTIPLE_4 * se',
     '        eligible = x_end > an.SE_MULTIPLE_4 * se'),
    (PL4B, "draw_batteries_4b: placebo rungs drawn without replacement (integers -> choice)",
     "            picks = rng.integers(0, len(P[t]), size=n)",
     "            picks = rng.choice(len(P[t]), size=n, replace=False)"),
    (PL4B, "draw_batteries_4b: the clear-index assignment is not permuted",
     "            order = rng.permutation(n)",
     "            order = np.arange(n)"),
    (PL4B, "alpha_placebo_4b: the LEADS count condition inverted",
     '        if world == "LEADS":',
     '        if world != "LEADS":'),
    (PL4B, "p_cal_4b: the add-one smoothing dropped from p_cal's numerator",
     "    p_cal = (1 + int(np.sum(T_b >= T4 - eps))) / (B + 1)",
     "    p_cal = int(np.sum(T_b >= T4 - eps)) / (B + 1)"),
    (PL4B, "p_cal_4b: the >= comparison direction flipped to <=",
     "    p_cal = (1 + int(np.sum(T_b >= T4 - eps))) / (B + 1)",
     "    p_cal = (1 + int(np.sum(T_b <= T4 - eps))) / (B + 1)"),
    (PL4B, "p_cal_4b: p_low's tolerance comparison weakened from <= to <",
     "    p_low = (1 + int(np.sum(T_b <= T4 + eps))) / (B + 1)",
     "    p_low = (1 + int(np.sum(T_b < T4 + eps))) / (B + 1)"),
    (PL4B, "t_star_4b: T_star's sign flipped (T4 - null_mean -> T4 + null_mean)",
     '"T_star": float(T4 - null_mean)', '"T_star": float(T4 + null_mean)'),
    (PL4B, "t_star_4b: the interval's lo/hi swapped",
     '"interval": [float(T4 - hi), float(T4 - lo)]',
     '"interval": [float(T4 - lo), float(T4 - hi)]'),

    # ------------------------------------------------------- power_ext_4b.py
    (PE4B, "reproduce_power_record_4b: gate (4)'s byte-equality short-circuited to True",
     "    identical = reproduced_bytes == committed_bytes",
     "    identical = True"),
    (PE4B, "simulate_zero_excess_scaled: the flat-rung noise draw's per-trajectory scale dropped",
     '                noise = rng.normal(0.0, ti["flat_se"][r] * scale_by_traj[traj], size=G)',
     '                noise = rng.normal(0.0, ti["flat_se"][r], size=G)'),
    (PE4B, "simulate_zero_excess_scaled: the pool-rung noise draw's per-trajectory scale dropped",
     '            noise = rng.normal(0.0, info["se_r"] * scale_by_traj[traj], size=info["G"])',
     '            noise = rng.normal(0.0, info["se_r"], size=info["G"])'),
    (PE4B, "simulate_zero_excess_scaled: the eligibility bar compares with > instead of >=",
     '                ok = excess[rung][-1] >= an.SE_MULTIPLE_4 * info["se_r"]',
     '                ok = excess[rung][-1] > an.SE_MULTIPLE_4 * info["se_r"]'),

    # ----------------------------------------------------------- levels_4b.py
    (LV4B, "kept_positions_4b: the site-family exclusion inverted (keeps ONLY the excluded site)",
     "    return [i for i, s in enumerate(int(x) for x in sites) if s not in bad]",
     "    return [i for i, s in enumerate(int(x) for x in sites) if s in bad]"),
    (LV4B, "level_ci_4b: the CI percentiles widened from [2.5, 97.5] to [5.0, 95.0]",
     "    lo, hi = np.percentile(boots, [2.5, 97.5])",
     "    lo, hi = np.percentile(boots, [5.0, 95.0])"),

    # ---------------------------------------------------------- analyze_4b.py
    (AN4B, "verdict_tree_4b: the CALIBRATED bar weakened from < to <=",
     "    if p_cal < battery_4b.ALPHA_4B:",
     "    if p_cal <= battery_4b.ALPHA_4B:"),
    (AN4B, "verdict_tree_4b: the MARGINAL bar weakened from < to <=",
     "    if p_cal < battery_4b.MARGINAL_4B:",
     "    if p_cal <= battery_4b.MARGINAL_4B:"),
    (AN4B, "run(): the stop_before validation removed",
     '''    if stop_before not in (None, "placebo"):
        raise ValueError(f"4b: stop_before must be None or 'placebo', got {stop_before!r}")''',
     '''    if False:
        raise ValueError(f"4b: stop_before must be None or 'placebo', got {stop_before!r}")'''),
    (AN4B, "run(): the stop_before='placebo' early return condition inverted",
     '    if stop_before == "placebo":',
     '    if stop_before != "placebo":'),
    (AN4B, "gate1_rederive_4b: T equality short-circuited to True",
     '    t_match = primary1["T"] == T4',
     '    t_match = True'),
    (AN4B, "gate2_rederive_4b: the pass flag short-circuited to True regardless of diffs",
     'return {"pass": not diffs, "diffs": diffs[:5]}',
     'return {"pass": True, "diffs": diffs[:5]}'),
    (AN4B, "gate3_rederive_4b: the lambda_hat mismatch check disabled",
     '''        if got != want:
            diffs.append(f"{traj}: {got!r} != {want!r}")
    return {"pass": not diffs and bool(cal_re["per_traj"]), "diffs": diffs,''',
     '''        if False:
            diffs.append(f"{traj}: {got!r} != {want!r}")
    return {"pass": not diffs and bool(cal_re["per_traj"]), "diffs": diffs,'''),
    (AN4B, "gate5_rederive_4b: the fraction_below mismatch check disabled",
     '''        if got != want:
            ok_all = False
    return {"pass": ok_all, "per_traj": detail}''',
     '''        if False:
            ok_all = False
    return {"pass": ok_all, "per_traj": detail}'''),
    (AN4B, "_s7: the clears-and-stays known-answer gate against the committed T disabled",
     "                if committed_cas_T is not None and cas_T != committed_cas_T:",
     "                if False:"),
]

# Review round 2, IMPORTANT 1(a) (exp4's precedent): give every hand-
# authored mutant above a stable label too, derived from its own
# (already unique, already content-stable) description text -- never
# from its position in this list.
M = [(path, desc, old, new, _slug(desc)) for (path, desc, old, new) in M]

# One mutant per collect_total_4b(...) call site in analyze_4b.py's
# run(), generated from the real, current source at import time.
# ------------------------------------------------- the freeze's own closures
#
# NB-1/NB-2 and F-1..F-5. Every one of these is killed by the FAST
# suite (the new fast tests in `test_placebo_4b.py`/
# `test_analyze_4b.py`); the gate-6 totality site is an AST mutant
# below and is also fast-killed, since `test_gate6_wrapper_collects_a_
# raise_into_insufficient_data` reaches that site on an EMPTY root4.
_FREEZE_M = [
    (PL4B, "NB-1: the n/(n-1) rescale reinstated on S4's flat side",
     """        flat_incs = []
        for f in flat:
            loo = loo_excess_4b(a, flat, steps, f)
            flat_incs.extend(np.diff(loo).tolist())""",
     """        flat_incs = []
        for f in flat:
            loo = loo_excess_4b(a, flat, steps, f)
            flat_incs.extend((np.diff(loo) / (loo_scale_factor or 1.0)).tolist())"""),
    (PL4B, "NB-1: rms_flat_loo decoupled from rms_flat (the disclosure field faked)",
     "        rms_flat_loo = rms_flat",
     "        rms_flat_loo = rms_flat if rms_flat is None else rms_flat * 1.001"),
    (PL4B, "NB-2: s3_pooled_rising_4b's tolerance dropped (any rise reads rising)",
     '    out.update({"rising": bool(delta > S1_SHAPE_TOL_4B), "first_bin": live[0][0],',
     '    out.update({"rising": bool(delta > 0.0), "first_bin": live[0][0],'),
    (PL4B, "NB-2: s3_pooled_rising_4b decides on ONE bin (the >= 2 guard dropped)",
     "    if len(live) < 2:",
     "    if len(live) < 1:"),
    (PL4B, "F-2: p_cal's Monte Carlo SE formula loses its 1/B",
     "    return float(np.sqrt(max(p * (1.0 - p), 0.0) / B))",
     "    return float(np.sqrt(max(p * (1.0 - p), 0.0)))"),
    (PL4B, "F-2: bar_margins_4b's 2-SE band widened to 0 (no bar ever flagged)",
     "            if abs(p_cal - bar) <= 2.0 * se:",
     "            if abs(p_cal - bar) <= 0.0 * se:"),
    (AN4B, "NB-2: s1_reading_4b's above-iid branch removed (two-sided again, r2's defect)",
     '''    elif placebo_null_mean > iid_null_mean + tol:
        reading = "above-iid"
    elif rising.get("rising"):''',
     '''    elif rising.get("rising"):'''),
    (AN4B, "NB-2: s1_reading_4b's S3 conjunct dropped",
     '    elif rising.get("rising"):',
     '    elif True:'),
    (AN4B, "F-1: gate 6 drops the tensor_digest agreement",
     "        if not (sets_ok and act_ok and att_ok and g[\"digest_equal\"]):",
     "        if not (sets_ok and act_ok and att_ok):"),
    (AN4B, "F-1: gate 6 drops the per-rung sets byte agreement",
     "        if not (sets_ok and act_ok and att_ok and g[\"digest_equal\"]):",
     "        if not (act_ok and att_ok and g[\"digest_equal\"]):"),
    (AN4B, "F-1: gate 6's failure no longer refuses the verdict",
     '''    if not gate6_ok:
        failures.append(f"4b gate 6: the endpoint units' bytes disagree, so the placebo ''',
     '''    if False:
        failures.append(f"4b gate 6: the endpoint units' bytes disagree, so the placebo '''),
    (AN4B, "F-3: interval_covers_zero_4b always reads True",
     "    return bool(interval[0] <= 0.0 <= interval[1])",
     "    return True"),
]
M += [(path, desc, old, new, _slug(desc)) for (path, desc, old, new) in _FREEZE_M]

M += _totality_mutants_4b(AN4B)

_labels = [m[4] for m in M]
assert len(_labels) == len(set(_labels)), (
    f"mutation_check.py: duplicate mutant labels -- {[l for l in _labels if _labels.count(l) > 1]}")

FAST_TESTS = [str(L / "tests" / "test_battery_4b.py"), str(L / "tests" / "test_placebo_4b.py"),
             str(L / "tests" / "test_power_ext_4b.py"), str(L / "tests" / "test_levels_4b.py"),
             str(L / "tests" / "test_analyze_4b.py")]
FAST_EXTRA_ARGS = ["-m", "not slow"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_4b.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_4b.py")]

# --------------------------------------------------------- --fullshape mode
#
# Controller ruling (Task 6, review of the first fast-mode pass): the
# 33+ survivors only totality/worlds can observe each map to ONE
# specific test already written for exactly that site -- running the
# WHOLE of `test_totality_4b.py` per mutant (as `--totality` does) is
# not affordable here the way it is for exp4's own totality suite:
# exp4's totality base is a cheap `stage="reference_only"` tree, but
# exp4b's totality tests need a COMPLETE exp4 verdict (a `stage="full"`
# 92-point sweep), so even with `EXP4B_WORLD_CACHE` removing the sweep-
# generation cost, running the full ~25-test slow suite once PER
# mutant would still cost about an hour per mutant. `--fullshape`
# instead runs `test_totality_4b.py` filtered to the ONE test (`-k`)
# that targets each mutant's site, with `EXP4B_WORLD_CACHE` set so
# `full_shape_4b.build_world_4b` copies a pre-built world instead of
# re-running the sweep. A mutant with no entry here falls back to the
# WHOLE totality file (still correct, just slower) -- every mutant
# below was mapped by reading which test corrupts/monkeypatches
# exactly that `collect_total_4b` call site or gate function.
FULLSHAPE_MUTANT_TEST_4B = {
    "run_the_stop_before_placebo_early_return_condition_inverted": None,  # already killed, fast
    "totality_957a6ce94e": "test_frozen_check_raise_gives_insufficient_data",
    "totality_cab6e140cf": "test_prereg_tag_missing_gives_insufficient_data",
    "totality_a1b6f9d618": "test_battery_items_raise_gives_insufficient_data",
    "totality_3b119f6978": "test_floors_raise_gives_insufficient_data",
    "totality_2f5ee2baca": "test_import_surface_entry_check_raise_gives_insufficient_data",
    "totality_cf7a1c9dd6": "test_import_surface_exit_check_raise_gives_insufficient_data",
    "totality_0ec22598ad": "test_t4_from_verdict_non_numeric_gives_insufficient_data",
    "totality_ef3e324a80": "test_cells_from_verdict_off_grid_t_clear_gives_insufficient_data",
    "totality_3f47837ddb": "test_stage_tables_torn_json_gives_insufficient_data",
    "totality_a15c461d59": "test_gate1_wrapper_catches_a_raise_from_gate1_rederive_4b",
    "totality_59861cd925": "test_gate2_wrapper_catches_a_raise_from_gate2_rederive_4b",
    "totality_18ae809c1b": "test_gate3_wrapper_catches_a_raise_from_gate3_rederive_4b",
    "totality_5262dd7e57": "test_gate5_wrapper_catches_a_raise_from_gate5_rederive_4b",
    "totality_aea9103fb7": "4b_draw_batteries",
    "totality_fddb16c7c4": "4b_p_cal",
    "totality_faf87ceb9f": "4b_t_star",
    # Final review r3: alpha_placebo_4b's call site text changed (the
    # new `real_regime=real_regime` argument), so its AST-derived
    # totality label changed too (content-hashed, per _totality_
    # mutants_4b's own docstring) -- the old label 3405d51a5d can never
    # recur; re-confirmed via --fullshape, mutation_worlds_pass3.log.
    "totality_305f5deb91": "4b_alpha_placebo",
    "totality_04f188936b": "4b_per_traj",
    "totality_ccbbb8079f": "4b_per_type",
    "totality_b99147fc28": "4b_S3",
    "totality_510f35ee2f": "4b_S4",
    "totality_56d7e2591c": "4b_S5",
    "totality_e6cbbab111": "4b_S8",
    "totality_4b4d957203": "4b_S1",
    "totality_3a1bba5455": "4b_S6",
    "totality_440b0c76f3": "4b_S7",
    "totality_3072ba3f6c": "test_referent_manifest_bad_pin_gives_insufficient_data",
    "totality_fa4043337a": "test_real_design_raise_gives_insufficient_data",
    "totality_244e7e8111": "test_outcome_raise_gives_insufficient_data",
    "totality_8c87362f51": "test_sweep_unit_missing_gives_insufficient_data",
    "totality_e0971c8f19": "test_ref_tables_raise_gives_insufficient_data",
    "totality_9dbaf2e5a8": "test_alignment_series_raise_gives_insufficient_data",
    "totality_f6819c9e67": "test_placebo_pool_raise_gives_insufficient_data",
    "totality_2e4f7f4de5": "test_rung_sets_raise_gives_insufficient_data",
    # FREEZE F-1's gate-6 site. Mapped for completeness only: it is
    # killed by the FAST suite (`test_gate6_wrapper_collects_a_raise_
    # into_insufficient_data`, which reaches the site on an EMPTY
    # root4 -- `gate1_rederive_4` raises when the files are not there),
    # so --fullshape never sees it.
    "totality_7764f70ca9": "test_gate5_wrapper_catches_a_raise_from_gate5_rederive_4b",
    "s7_the_clears_and_stays_known_answer_gate_against_the_committed_t_disabl":
        "test_s7_known_answer_gate_catches_a_corrupted_committed_t",
}


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp4b" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """2k's Finding 3 lesson (exp4's own carry-forward): a stray
    `.mutation_backup` anywhere under `experiments/exp4b` means either
    a concurrent run is already in flight or a previous run crashed
    without restoring -- refuse before the baseline check even starts."""
    found = sorted((ROOT / "experiments" / "exp4b").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp4b (a concurrent run, or a previous crash that "
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
    NOT a kill (exp4's own ruling): `subprocess.run(..., timeout=...)`
    kills the child itself on expiry and raises `TimeoutExpired`,
    caught here and reported as `timed_out=True` — the caller must
    never fold this into either `ok` or `survived`. Review finding 4:
    pytest exits 5 ("no tests ran") when a `-k` pattern selects
    nothing — that is NOT `returncode == 0`, so it was already never
    `ok`, but it was being folded into `survived` (a kill requires the
    covering test to FAIL, and "no test ran" trivially satisfies
    `returncode != 0` the same shape a real failure does) — a typo in
    `FULLSHAPE_MUTANT_TEST_4B` would silently read as a kill.
    `no_tests_collected` (`returncode == 5`) lets the caller route this
    to a SKIP instead. `extra_env` (e.g. `EXP4B_WORLD_CACHE` for
    `--fullshape`) is merged in on top of the inherited environment."""
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


def _k_selects_something(tests, k_pattern, *, extra_env=None) -> bool:
    """Review finding 4's second half: BEFORE a mutant is applied,
    confirm its `-k` selector matches at least one test on the REAL,
    unmutated source via `--collect-only` — a typo'd mapping value is
    caught here, as a SKIP with a clear reason, rather than only
    showing up (or not) as a `no_tests_collected` result from the timed
    mutant run itself."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(extra_env or {})}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        "--collect-only", *tests, "-k", k_pattern],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode == 0


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
    totality = "--totality" in argv
    fullshape = "--fullshape" in argv
    if fullshape:
        # See FULLSHAPE_MUTANT_TEST_4B's docstring: the mapped tests
        # live in test_totality_4b.py (test_full_shape_4b.py's own
        # `--fullshape`-flag tests, FULLSHAPE_TESTS, are the completion/
        # boundary suite, not where the per-mutant map points), run
        # per mutant filtered to just its own mapped test where one
        # exists. `EXP4B_WORLD_CACHE`, if set in THIS process's own
        # environment, is inherited by every subprocess automatically
        # (`run_suite`'s `{**os.environ, ...}`) -- nothing here sets it.
        tests, extra = TOTALITY_TESTS, []
    elif totality:
        tests, extra = TOTALITY_TESTS, []
    else:
        tests, extra = FAST_TESTS, FAST_EXTRA_ARGS
    only = _parse_only(argv)
    timeout = _parse_timeout(argv)

    _refuse_if_any_backup_exists()
    clear_pycache()
    # The baseline always runs the WHOLE file (no `-k`): a real,
    # unmutated confirmation that every mapped test still passes, not
    # just the one a given mutant's `-k` will later isolate.
    ok, out, timed_out, _ = run_suite(tests, extra, timeout=timeout)
    if timed_out:
        print(f"BASELINE TIMED OUT after {timeout}s — the covering suite itself is not this "
             f"slow normally; investigate before trusting any mutant result from this run\n", out)
        return 3
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    label = "fullshape" if fullshape else ("totality" if totality else "fast")
    print(f"baseline OK ({label} pass, "
         f"{'all' if only is None else sorted(only)} mutants"
         f"{f', timeout={timeout}s' if timeout else ''})\n", flush=True)

    survivors = []
    timeouts = []
    considered = 0
    for i, (path, name, old, new, mlabel) in enumerate(M, 1):
        if only is not None and mlabel not in only and str(i) not in only:
            continue
        considered += 1
        mutant_extra = extra
        if fullshape:
            mapped = FULLSHAPE_MUTANT_TEST_4B.get(mlabel)
            if mapped:
                mutant_extra = ["-k", mapped]
                # Review finding 4: confirm the `-k` selector matches
                # at least one test on the REAL, unmutated source
                # BEFORE the mutant is ever applied — a typo'd mapping
                # value is a SKIP with a clear reason, never silently
                # folded into a "kill" once the mutant's own run also
                # collects nothing.
                if not _k_selects_something(tests, mapped):
                    print(f"[{mlabel}] (#{i}) SKIP  {name}: -k {mapped!r} selects no test in "
                         f"{tests} (stale FULLSHAPE_MUTANT_TEST_4B entry)", flush=True)
                    survivors.append((mlabel, i, name, "k-selects-nothing"))
                    continue
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
            ok, out, timed_out, no_tests = run_suite(tests, mutant_extra, timeout=timeout)
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
            # pytest exit 5 ("no tests ran"): `ok` is already False
            # here (5 != 0), which would otherwise read as a "kill" —
            # the pre-check above should have caught a stale mapping,
            # but this is the defense-in-depth backstop (e.g. a
            # selector that matches on the real tree but not after
            # some OTHER, unrelated mutation's side effect).
            print(f"[{mlabel}] (#{i}) SKIP  {name}  (-k {mutant_extra[1]!r} collected 0 tests "
                 f"against the MUTATED source — not counted as killed or survived)", flush=True)
            survivors.append((mlabel, i, name, "no-tests-collected"))
            continue
        via = f"  (-k {mutant_extra[1]!r})" if fullshape and mutant_extra != extra else ""
        print(f"[{mlabel}] (#{i}) {'killed' if not ok else 'SURVIVED'}  {name}{via}", flush=True)
        if ok:
            survivors.append((mlabel, i, name, "survived"))
    skipped = [s for s in survivors if s[3] in ("target-not-found", "k-selects-nothing", "no-tests-collected")]
    real = [s for s in survivors if s[3] == "survived"]
    killed = considered - len(survivors) - len(timeouts)
    print(f"\n{killed}/{considered} killed; "
          f"{len(real)} survivor(s): {real}; "
          f"{len(skipped)} SKIP (target text not found / stale mutant / -k selected nothing): "
          f"{skipped}; "
          f"{len(timeouts)} TIMEOUT (not a kill, not a survivor): {timeouts}")
    return 1 if (survivors or timeouts) else 0


if __name__ == "__main__":
    sys.exit(main())
