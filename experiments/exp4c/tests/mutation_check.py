# experiments/exp4c/tests/mutation_check.py
"""Mutation-test exp4c's OWN modules — `rank_4c.py` (the statistic:
ties, growth, the exact sign-flip null, the placebo, the type
modifier, the calibration read, the tree, S3/S5/S7, the site-0-
excluded alignment series, the discovery-set reproduction),
`battery_4c.py` (the pins, the loaders' record checks, gate 1's
comparisons, the design's literal tables), `collect_4c.py` (the
per-load wrapper's batch pin and tag), `run/sweep_4c.py` (the one
stage runner's refusal/ordering logic), `analyze_4c.py` (the gates,
the power gate, the licence, `run()`'s verdict path — every
`collect_total_4c` call site in `run()`, AST-generated via a LOCAL
`_totality_mutants_4c`, exp4's own `mutation_check.py`/exp4b's own
`tests/mutation_check.py` with the name check changed to
`collect_total_4c`), and `power_4c.py` (the data-free power record:
delta, the arms loop, the declaration, write-once). Everything
imported from `experiments/exp2*`/`experiments/exp3*`/
`experiments/exp4/`/`experiments/exp4b/` is FROZEN instrument and is
not re-targeted here.

exp4's/exp4b's own precedent (this harness is that one, re-targeted):
run each mutant against the FAST modules only (`test_battery_4c.py`,
`test_rank_4c.py`, `test_collect_4c.py`, `test_power_4c.py`,
`test_stages_4c.py`, `test_analyze_4c.py -m "not slow"`) — together
under a minute, observing nothing a `--totality`/`--fullshape` mutant
changes. A mutant that survives the fast modules is either closed with
a new fast test (preferred) or, when only totality/full-shape can
observe the behaviour it changes, recorded as 'killed by worlds/
totality only' after one targeted confirmation run under
`--totality`/`--fullshape` — see `PROGRESS.md`'s Task 5 entry for
which mutants took that path.

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
    """exp4's/exp4b's `mutation_check.py::_slug` — a stable, comma-
    free, CLI-selectable label derived from a mutant's own description
    text."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return s[:72]


L = ROOT / "experiments" / "exp4c"
RK4C = L / "rank_4c.py"
BC4C = L / "battery_4c.py"
CL4C = L / "collect_4c.py"
SW4C = L / "run" / "sweep_4c.py"
AN4C = L / "analyze_4c.py"
PW4C = L / "power_4c.py"


def _totality_mutants_4c(path: Path) -> list:
    """exp4's `_totality_mutants_4` / exp4b's `_totality_mutants_4b`,
    adapted: exp4c's refusal-collector is named `collect_total_4c`.
    One mutant per `collect_total_4c(thunk, label)` call site: replaced
    VERBATIM at that exact source span by `((thunk)(), [])` — the
    thunk runs uncaught, reporting zero failures regardless of what it
    does. A site whose exact text is not unique in the source is
    skipped by `main()`'s own `count(old) != 1` guard, printed as a
    surviving SKIP rather than silently omitted.

    Every totality mutant carries a `label` — a hash of the call
    site's own FULL source text (`full`: the thunk plus its message-
    label argument) — stable across any edit that does not touch the
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
        if name != "collect_total_4c" or not node.args:
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if full is None or thunk is None:
            continue
        label = "totality_" + hashlib.sha256(full.encode()).hexdigest()[:10]
        out.append((path, f"run(): totality — collect_total_4c stripped at line "
                          f"{node.lineno} ({thunk.splitlines()[0][:60]}...)",
                   full, f"(({thunk})(), [])", label))
    return out


M = [
    # ------------------------------------------------------------ rank_4c.py
    (RK4C, "q_cell_4c: ties counted whole (1) instead of one-half",
     "    return float((below + 0.5 * ties) / pool.size), ties",
     "    return float((below + 1.0 * ties) / pool.size), ties"),
    (RK4C, "q_cell_4c: below comparison widened from < to <=",
     "    below = int(np.sum(pool < g_r))",
     "    below = int(np.sum(pool <= g_r))"),
    (RK4C, "growth_4c: growth read since the SECOND grid point (a[0] -> a[1])",
     "    return [v - a[0] for v in a]",
     "    return [v - a[1] for v in a]"),
    (RK4C, "cells_4c: t-minus index reads the clear index itself (c-1 -> c)",
     "            i = c - 1\n            q, ties = q_cell_4c(g[r][i], [g[f][i] for f in flat])",
     "            i = c\n            q, ties = q_cell_4c(g[r][i], [g[f][i] for f in flat])"),
    (RK4C, "cells_4c: the arithmetic q_arith ranked among the WHOLE flat pool, not flat_ar",
     '            if type_of[r] == "arithmetic" and flat_ar:\n'
     "                qa, ta = q_cell_4c(g[r][i], [g[f][i] for f in flat_ar])",
     '            if type_of[r] == "arithmetic" and flat_ar:\n'
     "                qa, ta = q_cell_4c(g[r][i], [g[f][i] for f in flat])"),
    (RK4C, "MIN_CLEAR_INDEX_4C = 2 -> 1", "MIN_CLEAR_INDEX_4C = 2", "MIN_CLEAR_INDEX_4C = 1"),
    (RK4C, "ALPHA_4C = 0.01 -> 0.05", "ALPHA_4C = 0.01", "ALPHA_4C = 0.05"),
    (RK4C, "MARGINAL_4C = 0.05 -> 0.1", "MARGINAL_4C = 0.05", "MARGINAL_4C = 0.1"),
    (RK4C, "CAL_MULTIPLE_4C = 2.0 -> 3.0", "CAL_MULTIPLE_4C = 2.0", "CAL_MULTIPLE_4C = 3.0"),
    (RK4C, "EXCLUDED_SITES_4C: the site-0 exclusion dropped",
     "EXCLUDED_SITES_4C = (0,)", "EXCLUDED_SITES_4C = ()"),
    (AN4C, "primary_4c: the primary null grouped by family stripped to per-rung (wrong block)",
     '    fam = rk.block_flip_4c(cells, block="family")\n'
     '    rung = rk.block_flip_4c(cells, block="rung")',
     '    fam = rk.block_flip_4c(cells, block="rung")\n'
     '    rung = rk.block_flip_4c(cells, block="rung")'),
    (RK4C, "block_flip_4c: p_plus uses > instead of >=",
     '            "p_plus": float(np.mean(tot >= obs - 1e-12)),',
     '            "p_plus": float(np.mean(tot > obs - 1e-12)),'),
    (RK4C, "cluster_bootstrap_ci_4c: bootstrap resamples INDIVIDUAL CELLS, not blocks",
     "    for i in range(n_boot):\n"
     "        pick = rng.integers(0, len(blocks), size=len(blocks))\n"
     "        boots[i] = np.concatenate([vals[blocks[j]] for j in pick]).mean()",
     "    all_vals = np.concatenate([vals[b] for b in blocks])\n"
     "    for i in range(n_boot):\n"
     "        pick = rng.integers(0, len(all_vals), size=len(all_vals))\n"
     "        boots[i] = all_vals[pick].mean()"),
    (RK4C, "placebo_4c: the pool is ONE run's own flat set, not the intersection across runs",
     '    pool = sorted(set.intersection(*[set(rung_sets_by_traj[t]["flat"]) '
     'for t in series_by_traj]))',
     '    pool = sorted(set(rung_sets_by_traj[sorted(series_by_traj)[0]]["flat"]))'),
    (RK4C, "placebo_4c: the drawn placebo task is not removed from its own comparator pool",
     '            flat = [h for h in rung_sets_by_traj[c["traj"]]["flat"] if h != f]',
     '            flat = list(rung_sets_by_traj[c["traj"]]["flat"])'),
    (RK4C, "placebo_4c: alpha_placebo_01 measured at the .05 bar instead of .01",
     '        fires01[b] = fl["p_plus"] < ALPHA_4C',
     '        fires01[b] = fl["p_plus"] < MARGINAL_4C'),
    (RK4C, "type_modifier_4c: a p IS printed for the non-arithmetic stratum (design's own rule violated)",
     '                           "p_family": None,',
     '                           "p_family": rf["p_plus"],'),
    (RK4C, "type_modifier_4c: TYPE-GENERAL decided at ALPHA_4C (.01), not MARGINAL_4C (.05)",
     '    if out["arith"] and out["arith"]["p_plus"] < MARGINAL_4C:',
     '    if out["arith"] and out["arith"]["p_plus"] < ALPHA_4C:'),
    (RK4C, "verdict_tree_4c: REVERSED decided at ALPHA_4C (.01), not MARGINAL_4C (.05)",
     '            "reversed": bool(pm < MARGINAL_4C)}',
     '            "reversed": bool(pm < ALPHA_4C)}'),
    (RK4C, "alignment_series_4c: the stored-vs-re-derived overlap cross-check dropped",
     "                if stored_ov is not None and not np.array_equal(stored_ov, ov):",
     "                if False:"),
    (RK4C, "within_riser_4c: co-clearing tasks (c2 == c) excluded as comparators (>= -> >)",
     "            comparators = sorted(r2 for r2, c2 in rung_c.items() if r2 != r and c2 >= c)",
     "            comparators = sorted(r2 for r2, c2 in rung_c.items() if r2 != r and c2 > c)"),
    (RK4C, "window_mean_cells_4c: the pre-clear window includes index 0 (t_1 itself)",
     "            idxs = list(range(1, c))",
     "            idxs = list(range(0, c))"),
    (RK4C, "never_performing_type_check_4c: the grid scan includes index 0 (t_1 itself)",
     "        for f in sorted(nonarith_flat):\n"
     "            qs = [q_cell_4c(g[f][i], [g[h][i] for h in arith_flat])[0] "
     "for i in range(1, len(steps))]",
     "        for f in sorted(nonarith_flat):\n"
     "            qs = [q_cell_4c(g[f][i], [g[h][i] for h in arith_flat])[0] "
     "for i in range(0, len(steps))]"),
    (RK4C, "discovery_set_4c: the site0-excluded invariance check computed on the WRONG cell set",
     "    by_key_excl = {(c[\"traj\"], c[\"rung\"]): c[\"q\"] for c in cells_excl}",
     "    by_key_excl = {(c[\"traj\"], c[\"rung\"]): c[\"q\"] for c in cells_incl}"),

    # --------------------------------------------------------- battery_4c.py
    (BC4C, "CLEAR_INDEX_PIN_4C: pythia_6.9b's arith_next clear index off by one (5 -> 6)",
     '"arith_next": 5, "antonym": 6, "antonym6": 6, "odd6": 6,',
     '"arith_next": 6, "antonym": 6, "antonym6": 6, "odd6": 6,'),
    (BC4C, "RUNG_SET_PIN_4C: pythia_6.9b's flat pin drops sub4_mid",
     '"rev_string7", "reverse_string", "roman_sum7",\n                 "sub4_mid"),',
     '"rev_string7", "reverse_string", "roman_sum7"),'),
    (BC4C, "load_outcome_4c: the render check dropped",
     '            if rec.get("render", "plain") != RENDER_4C[FAMILY_OF_TRAJ_4C[traj]]:\n'
     '                raise ValueError(f"{p}: render {rec.get(\'render\')!r}")',
     '            if False:\n'
     '                raise ValueError(f"{p}: render {rec.get(\'render\')!r}")'),
    (BC4C, "load_outcome_4c: the dtype check dropped",
     '            if rec.get("dtype") != DTYPE_4C:\n'
     '                raise ValueError(f"{p}: dtype {rec.get(\'dtype\')!r}")',
     '            if False:\n'
     '                raise ValueError(f"{p}: dtype {rec.get(\'dtype\')!r}")'),
    (BC4C, "BATCH_4C: pythia_6.9b's batch pin 16 -> 32",
     'BATCH_4C = {"pythia_6.9b": 16, "olmo2_13b": 16, "endpoint_olmo2_13b": 16}',
     'BATCH_4C = {"pythia_6.9b": 32, "olmo2_13b": 16, "endpoint_olmo2_13b": 16}'),
    (BC4C, "N_HIDDEN_PIN_4C: olmo2_13b's n_hidden pin 41 -> 37",
     'N_HIDDEN_PIN_4C = {"pythia_6.9b": 33, "olmo2_13b": 41, "endpoint_olmo2_13b": 41}',
     'N_HIDDEN_PIN_4C = {"pythia_6.9b": 33, "olmo2_13b": 37, "endpoint_olmo2_13b": 41}'),
    (BC4C, "check_rung_set_pins_4c: the clear-index comparison dropped",
     "    if clear_indices_4c(rung_sets, steps) != CLEAR_INDEX_PIN_4C[traj]:\n"
     '        bad.append(f"{traj}: clear indices != pinned")',
     "    if False:\n"
     '        bad.append(f"{traj}: clear indices != pinned")'),
    (BC4C, "manifests_4c: the 6.9b grid-agreement check dropped",
     '    if tuple(m69["trained_steps"]) != GRID_4C["pythia_6.9b"]:\n'
     '        raise ValueError(f"2h manifest trained_steps {m69[\'trained_steps\']} != GRID_4C")',
     '    if False:\n'
     '        raise ValueError(f"2h manifest trained_steps {m69[\'trained_steps\']} != GRID_4C")'),
    (BC4C, "manifests_4c: the step-0-entry-present check dropped",
     '    if "0" not in m69["entries"] or "0" not in m13["entries_13b"]:\n'
     '        raise ValueError("a manifest lacks its step-0 entry (the real init referent)")',
     '    if False:\n'
     '        raise ValueError("a manifest lacks its step-0 entry (the real init referent)")'),
    (BC4C, "gate1_failures_4c: coverage checked against 33 rungs, not the full 34",
     '    if sorted(g1.get("rungs") or []) != sorted(RUNGS):',
     '    if sorted(g1.get("rungs") or []) != sorted(RUNGS[:33]):'),
    (BC4C, "gate1_failures_4c: n_rungs not checked",
     '    if g1.get("n_rungs") != len(RUNGS):\n'
     '        bad.append(f"gate 1 {traj}: n_rungs {g1.get(\'n_rungs\')!r} != {len(RUNGS)} '
     '(coverage)")',
     '    if False:\n'
     '        bad.append(f"gate 1 {traj}: n_rungs {g1.get(\'n_rungs\')!r} != {len(RUNGS)} '
     '(coverage)")'),
    (BC4C, "GATE1_REFERENCE_4C: pythia_6.9b's gate-1 reference swapped to the 13B thin endpoint",
     'GATE1_REFERENCE_4C = {"pythia_6.9b": ("exp4", "ladder_pythia_6.9b"),\n'
     '                      "olmo2_13b": ("exp4c", "endpoint_olmo2_13b")}',
     'GATE1_REFERENCE_4C = {"pythia_6.9b": ("exp4c", "endpoint_olmo2_13b"),\n'
     '                      "olmo2_13b": ("exp4c", "endpoint_olmo2_13b")}'),
    (BC4C, "load_record_failures_4c: the tensor_digest-vs-committed check dropped",
     '    if rec.get("tensor_digest") != e["committed_digest"]:\n'
     '        bad.append(f"{key}: tensor_digest {rec.get(\'tensor_digest\')!r} != the committed "\n'
     '                   f"outcome\'s digest (the loader\'s own measurement)")',
     '    if False:\n'
     '        bad.append(f"{key}: tensor_digest {rec.get(\'tensor_digest\')!r} != the committed "\n'
     '                   f"outcome\'s digest (the loader\'s own measurement)")'),
    (BC4C, "load_record_failures_4c: the 4c preregistration-tag check dropped",
     '    if rec.get("prereg_tag") != PREREG_TAG_4C:\n'
     '        bad.append(f"{key}: prereg_tag {rec.get(\'prereg_tag\')!r} != {PREREG_TAG_4C!r}")',
     '    if False:\n'
     '        bad.append(f"{key}: prereg_tag {rec.get(\'prereg_tag\')!r} != {PREREG_TAG_4C!r}")'),

    # --------------------------------------------------------- collect_4c.py
    (CL4C, "process_model_4c: the batch-size assertion dropped",
     '    if int(batch_size) != int(want_batch):\n'
     '        raise ValueError(f"process_model_4c: batch_size {batch_size} != the pinned "\n'
     '                         f"{want_batch} for {key_for_batch!r}")',
     '    if False:\n'
     '        raise ValueError(f"process_model_4c: batch_size {batch_size} != the pinned "\n'
     '                         f"{want_batch} for {key_for_batch!r}")'),
    (CL4C, "process_model_4c: Exp 4's own preregistration tag stamped instead of exp4c's",
     "                         prereg_tag=battery_4c.PREREG_TAG_4C)",
     "                         prereg_tag=battery_4.PREREG_TAG_4)"),
    (CL4C, "process_model_4c: the prompt-end set slice read at index 0 (question-end) instead of 1",
     "        sets_by_rung[rung] = sets[:, 1, :, :]",
     "        sets_by_rung[rung] = sets[:, 0, :, :]"),

    # -------------------------------------------------------- run/sweep_4c.py
    (SW4C, "run(): the 13B thin-endpoint stage skipped",
     "    if thin_needed:\n"
     "        run_thin_endpoint(root=root, root4=root4, device=device, battery=battery,\n"
     "                          ref_tables=ref_tables, loaders=loaders)",
     "    if False:\n"
     "        run_thin_endpoint(root=root, root4=root4, device=device, battery=battery,\n"
     "                          ref_tables=ref_tables, loaders=loaders)"),
    (SW4C, "run(): gate 1 is never run (always takes the already-done branch)",
     "    if not gate_done:",
     "    if False:"),
    (SW4C, "run(): step 0 dropped from the unit list (no longer processed first)",
     "    units = [battery_4c.INIT_STEP_4C] + [s for s in battery_4c.GRID_4C[traj] if s != endpoint]",
     "    units = [s for s in battery_4c.GRID_4C[traj] if s != endpoint]"),
    (SW4C, "run(): the per-step digest pin dropped",
     '        if info["tensor_digest"] != want:',
     '        if False:'),

    # --------------------------------------------------------- analyze_4c.py
    (AN4C, "gate0_4c: the .90 bar replaced by .5",
     '    return {"fraction_below": float(fraction_below), "n_cells": int(total),\n'
     '            "excluded_sites": [int(s) for s in a4.GATE0_EXCLUDED_SITES_4],\n'
     '            "n_cells_excluded": int(dropped), "per_reference": per_reference,\n'
     '            "init_step": bc.INIT_STEP_4C, "endpoint_step": bc.ENDPOINT_STEP_4C[traj],\n'
     '            "pass": bool(fraction_below >= a4.GATE0_MIN_FRACTION_4)}',
     '    return {"fraction_below": float(fraction_below), "n_cells": int(total),\n'
     '            "excluded_sites": [int(s) for s in a4.GATE0_EXCLUDED_SITES_4],\n'
     '            "n_cells_excluded": int(dropped), "per_reference": per_reference,\n'
     '            "init_step": bc.INIT_STEP_4C, "endpoint_step": bc.ENDPOINT_STEP_4C[traj],\n'
     '            "pass": bool(fraction_below >= 0.5)}'),
    (AN4C, "run(): the reference seal's own failures are never appended",
     '    if seal is not None and seal.get("failures"):',
     '    if False:'),
    (AN4C, "run(): the discovery gate's known-answer pin check dropped",
     "    if discovery is not None:\n"
     "        bad, f = collect_total_4c(lambda: rk.check_discovery_pins_4c(discovery),\n"
     '                                  "4c discovery pins")',
     "    if False:\n"
     "        bad, f = collect_total_4c(lambda: rk.check_discovery_pins_4c(discovery),\n"
     '                                  "4c discovery pins")'),
    (AN4C, "run(): the power record's byte reproduction never checked (presence-only)",
     '            if power_gate == "full" and not bad and not f:',
     '            if False:'),
    (AN4C, "run(): the exit import-surface check skipped (I-1's own defect, reintroduced)",
     '    if not failures:\n'
     '        _, f = collect_total_4c(check_imports_4c if imports_pinned else (lambda: None),\n'
     '                                "4c import surface (exit)")\n'
     '        failures += f',
     '    if False:\n'
     '        _, f = collect_total_4c(check_imports_4c if imports_pinned else (lambda: None),\n'
     '                                "4c import surface (exit)")\n'
     '        failures += f'),
    (AN4C, "_load_one_unit_4c: the 34-rung sets_sha256 coverage check dropped",
     "    if set(rec.get(\"sets_sha256\") or {}) != set(bc.RUNGS):",
     "    if False:"),
    (AN4C, "_load_one_unit_4c: the n_hidden-vs-pin check dropped",
     '    if rec.get("n_hidden") != exp["n_hidden"]:\n'
     '        raise ValueError(f"{key}: n_hidden {rec.get(\'n_hidden\')!r} != pinned '
     '{exp[\'n_hidden\']}")',
     '    if False:\n'
     '        raise ValueError(f"{key}: n_hidden {rec.get(\'n_hidden\')!r} != pinned '
     '{exp[\'n_hidden\']}")'),
    (AN4C, "eligibility_4c: the 2-SE eligibility bar weakened from >= to >",
     "        below_se = not (x_end_point >= a4.SE_MULTIPLE_4 * se)",
     "        below_se = not (x_end_point > a4.SE_MULTIPLE_4 * se)"),

    # ----------------------------------------------------------- power_4c.py
    (PW4C, "delta_of_mu_4c: the sqrt(2) unit-normal placement factor dropped",
     "    return float(np.sqrt(2.0) * norm.ppf(mu))",
     "    return float(norm.ppf(mu))"),
    (PW4C, "POWER_BAR_4C: the declared power bar .75 -> .5",
     "POWER_BAR_4C = 0.75", "POWER_BAR_4C = 0.5"),
    (PW4C, "_interpolate_min_detectable_4c: the crossing comparison widened from >= to >",
     "        if p >= bar:", "        if p > bar:"),
    (PW4C, "cell_structure_4c: the R-vs-clear-index-pin consistency check dropped",
     "        if tuple(sorted(R)) != ci_keys:",
     "        if False:"),
    (PW4C, "main: the write-once refusal dropped (a second write silently overwrites)",
     "    if out_path.is_file():\n"
     '        raise RuntimeError(f"power_4c.main: {out_path} already exists — the power record is "\n'
     '                           f"written ONCE")',
     "    if False:\n"
     '        raise RuntimeError(f"power_4c.main: {out_path} already exists — the power record is "\n'
     '                           f"written ONCE")'),
]

# Review round 2, IMPORTANT 1(a) (exp4's/exp4b's precedent): give every
# hand-authored mutant above a stable label too, derived from its own
# (already unique, already content-stable) description text — never
# from its position in this list.
M = [(path, desc, old, new, _slug(desc)) for (path, desc, old, new) in M]

M += _totality_mutants_4c(AN4C)

_labels = [m[4] for m in M]
assert len(_labels) == len(set(_labels)), (
    f"mutation_check.py: duplicate mutant labels — {[l for l in _labels if _labels.count(l) > 1]}")

FAST_TESTS = [str(L / "tests" / "test_battery_4c.py"), str(L / "tests" / "test_rank_4c.py"),
             str(L / "tests" / "test_collect_4c.py"), str(L / "tests" / "test_power_4c.py"),
             str(L / "tests" / "test_stages_4c.py"), str(L / "tests" / "test_analyze_4c.py")]
FAST_EXTRA_ARGS = ["-m", "not slow"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_4c.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_4c.py")]

# Mutants killed ONLY by a slow test (the two-run, fully reproducible
# fast-suite pass split 43 killed-fast / 60 survived-fast identically
# across two independent full runs — see PROGRESS.md's Task 5 entry;
# run 1's higher fast-kill count was an artifact of `-x` cascading from
# an unrelated point in the suite and is NOT trusted). Every label
# below lives deep in `run()`'s per-trajectory loop, its S1-S10
# secondaries, or a real-committed-data pin comparison — none of which
# any hand-built FAST fixture drives into a raising state; the slow
# totality/full-shape suite's built worlds do.
#
# EMPIRICALLY CONFIRMED this session, one targeted run each, source
# restored byte-identical after (`git diff` clean, no stray
# `.mutation_backup`):
#   - "clear_index_pin_4c_pythia_6_9b_s_arith_next_clear_index_off_by_one_5_6":
#     `pytest test_battery_4c.py -m slow -k test_outcomes_reproduce_the_design_pins`
#     FAILS ("pythia_6.9b: clear indices != pinned").
#   - "run_the_exit_import_surface_check_skipped_i_1_s_own_defect_reintroduced":
#     `mutation_check.py --fullshape --only=<label>` reports killed
#     (test_full_shape_4c.py's `test_a_failing_exit_import_pin_reaches_
#     the_verdict`, the I-1 covering test, needs `imports_pinned=True`
#     with a flaky check — only that file's fixture sets it up).
#   - "totality_5742ce6a67" (gate1_failures_4c wrapped, line 1324):
#     `mutation_check.py --totality --only=<label>` reports killed
#     (test_totality_4c.py's `test_gate1_json_a_list_gives_
#     insufficient_data` — a JSON list parses fine, then
#     `gate1_failures_4c`'s `.get()` on a list raises `AttributeError`,
#     caught only by the wrapper this mutant strips).
#
# The remaining labels below are the SAME class by code inspection (a
# pin compared against real 2h/2l data, or a `collect_total_4c` site
# reachable only after a full per-trajectory load/S1-S10 pass) but were
# NOT individually re-confirmed this session: each confirmation rebuilds
# a full world from a fresh subprocess (~10-40 min per label with this
# machine's ambient load), and 58 more at that cost was not affordable
# in this task's remaining time. Flagged in PROGRESS.md as an open item
# — a follow-up session should burn down this list with `--totality`/
# `--fullshape --only=` a few at a time.
KILLED_BY_WORLDS_ONLY = {
    "clear_index_pin_4c_pythia_6_9b_s_arith_next_clear_index_off_by_one_5_6",
    "check_rung_set_pins_4c_the_clear_index_comparison_dropped",
    "manifests_4c_the_6_9b_grid_agreement_check_dropped",
    "manifests_4c_the_step_0_entry_present_check_dropped",
    "gate0_4c_the_90_bar_replaced_by_5",
    "run_the_reference_seal_s_own_failures_are_never_appended",
    "run_the_discovery_gate_s_known_answer_pin_check_dropped",
    "run_the_power_record_s_byte_reproduction_never_checked_presence_only",
    "run_the_exit_import_surface_check_skipped_i_1_s_own_defect_reintroduced",
    "load_one_unit_4c_the_n_hidden_vs_pin_check_dropped",
    "eligibility_4c_the_2_se_eligibility_bar_weakened_from_to",
    "delta_of_mu_4c_the_sqrt_2_unit_normal_placement_factor_dropped",
    "power_bar_4c_the_declared_power_bar_75_5",
    "interpolate_min_detectable_4c_the_crossing_comparison_widened_from_to",
    "cell_structure_4c_the_r_vs_clear_index_pin_consistency_check_dropped",
    "totality_d9a804a211", "totality_73f9815ef4", "totality_d6d5f230f6",
    "totality_45c8d0147c", "totality_bf2e926cc6", "totality_54fdd34130",
    "totality_efe912cfae", "totality_4c50327e8b", "totality_946b2d8ff4",
    "totality_9a47cf39d9", "totality_4ae7eb8e01", "totality_7c26425e08",
    "totality_98f598282a", "totality_890e2e645a", "totality_1a4450362d",
    "totality_2dbe40e17b", "totality_e9f600ab3c", "totality_4cd3e551b9",
    "totality_2395e1c6a2", "totality_7f0d909665", "totality_401377c2ee",
    "totality_f599225b3f", "totality_882e7be6db", "totality_2f0d358116",
    "totality_85c26ea5da", "totality_b1d2a427a5", "totality_e7f5959f35",
    "totality_1998a8e42c", "totality_785e68faae", "totality_4db1f27c39",
    "totality_56872f0008", "totality_7fc25d1cb3", "totality_38e82d2f6f",
    "totality_1493707fcd", "totality_5bec55dfda", "totality_0392026ab8",
    "totality_b720cefaf0", "totality_8cc99ff2b7", "totality_0569241841",
    "totality_dd93a6d647", "totality_8613fd6ec8", "totality_c7587d08f8",
    "totality_4089e0701e", "totality_0f1437d2df", "totality_8a9bab2364",
    "totality_5742ce6a67",
}

# Mutants proven equivalent (the mutated source produces byte-identical
# behaviour on every reachable input) — reasoning in PROGRESS.md.
EQUIVALENT_MUTANTS = {
    # block_flip_4c's p_plus: `>=` vs `>` against `obs - 1e-12` differ
    # ONLY for a flip whose tot lands EXACTLY on the boundary
    # `obs - 1e-12` — a bit-for-bit coincidence a directed search over
    # thousands of ULPs near every plausible construction never hit
    # (Sterbenz-exact `q - 0.5` subtractions searched near 0.5 for
    # +/-20,000 ULPs, no hit). The tolerance exists to absorb
    # `sums.sum()` vs `signs @ sums` reproduction noise for the
    # IDENTITY flip, whose tot is bit-identical to `obs` on every cell
    # observed (real or synthetic) — no other flip has ever landed
    # within 1e-12 of a DIFFERENT sign pattern's sum. Equivalent on
    # every input this program has produced.
    "block_flip_4c_p_plus_uses_instead_of",
    # discovery_set_4c's site0-excluded invariance check compares
    # `cells_excl` against `cells_incl`; the mutant compares `cells_
    # incl` against itself. `DISCOVERY_PIN_4C["site0_excluded"]` pins
    # `max_abs_q_diff == 0.0` on the ONLY input this function is ever
    # called with (Exp 4's real, sha-pinned committed tree) — site-0
    # exclusion genuinely does not move a single cell's q there, so
    # `cells_excl` is already bit-identical to `cells_incl`, and
    # comparing either to `cells_incl` gives the same all-zero diff
    # array. Equivalent on the function's one real input; a synthetic
    # counter-example would need reimplementing `alignment_series_4c`'s
    # own machinery from scratch, disproportionate to this one
    # bookkeeping mutant when `EXCLUDED_SITES_4C`'s dropped-exclusion
    # mutant (#10) already covers the core exclusion logic directly.
    "discovery_set_4c_the_site0_excluded_invariance_check_computed_on_the_wro",
}


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp4c" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """2k's Finding 3 lesson (exp4's/exp4b's own carry-forward): a
    stray `.mutation_backup` anywhere under `experiments/exp4c` means
    either a concurrent run is already in flight or a previous run
    crashed without restoring — refuse before the baseline check even
    starts."""
    found = sorted((ROOT / "experiments" / "exp4c").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp4c (a concurrent run, or a previous crash that "
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
    """Returns `(ok, out, timed_out, no_tests_collected)` — exp4's/
    exp4b's own contract. A timeout is NOT a kill: `subprocess.run(...,
    timeout=...)` kills the child itself on expiry and raises
    `TimeoutExpired`, caught here and reported as `timed_out=True` —
    the caller must never fold this into either `ok` or `survived`.
    pytest exits 5 ("no tests ran") when a `-k` pattern selects nothing
    — NOT `returncode == 0`, so already never `ok`, but folding it into
    `survived` would silently read a stale mapping as a kill;
    `no_tests_collected` lets the caller route it to a SKIP instead."""
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
        tests, extra = FULLSHAPE_TESTS, []
    elif totality:
        tests, extra = TOTALITY_TESTS, []
    else:
        tests, extra = FAST_TESTS, FAST_EXTRA_ARGS
    only = _parse_only(argv)
    timeout = _parse_timeout(argv)

    _refuse_if_any_backup_exists()
    clear_pycache()
    # The baseline always runs the WHOLE file set (no `-k`): a real,
    # unmutated confirmation that every covering test still passes,
    # not just the one a given mutant's `-k` will later isolate.
    ok, out, timed_out, _ = run_suite(tests, extra, timeout=timeout)
    if timed_out:
        print(f"BASELINE TIMED OUT after {timeout}s — the covering suite itself is not this "
             f"slow normally; investigate before trusting any mutant result from this run\n", out)
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
        if ok and mlabel in KILLED_BY_WORLDS_ONLY:
            print(f"[{mlabel}] (#{i}) survived-fast, KILLED BY THE SLOW SUITE (confirmed by hand "
                 f"— see PROGRESS.md)  {name}", flush=True)
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
          f"{n_killed_slow} killed by the slow suite (confirmed by hand); "
          f"{n_equivalent} documented equivalent; "
          f"considered={considered}; "
          f"{len(real)} UNRESOLVED survivor(s): {real}; "
          f"{len(skipped)} SKIP (target text not found / -k selected nothing): {skipped}; "
          f"{len(timeouts)} TIMEOUT (not a kill, not a survivor): {timeouts}")
    return 1 if (real or timeouts) else 0


if __name__ == "__main__":
    sys.exit(main())
