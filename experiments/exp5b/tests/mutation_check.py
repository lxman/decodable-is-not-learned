# experiments/exp5b/tests/mutation_check.py
"""Mutation-test exp5b's OWN modules — `stats_5b.py` (the matched
placebo, the primary/tree, sigma-hat/calibration, the modifier, S8/S9),
`power_5b.py` (the noise model, the grid order, the deciding arm, the
write-once guard), `collect_5b.py` (the unit pipeline: the digest halt,
write order, the torn-unit rmtree, gate 1's attestation), `run/units_5b.
py` (the refusal chain, the host stack comparison, unit order), `battery_
5b.py` (the two bindings, the contracts, the pins) and `analyze_5b.py`
(the gates, `run()`'s verdict path — every `collect_total_5b` call site
in `run()`'s own body, AST-generated via a LOCAL `_totality_mutants_5b`,
Experiment 5's own `mutation_check.py` with the name check changed to
`collect_total_5b` and the walk restricted to the `run` FunctionDef —
`test_totality_5b.py`'s own `_site_templates_5b` is the same
restriction, kept independent here rather than imported so this file
has no test-module dependency). Everything imported from `experiments/
exp5*` outside `exp5b` is FROZEN instrument and is not re-targeted here.

Run each mutant against the FAST modules only (`test_battery_5b.py`,
`test_stats_5b.py`, `test_power_5b.py`, `test_collect_5b.py`, `test_
stages_5b.py`, `test_analyze_5b.py`, `test_verify_referents_5b.py`) —
together under four minutes. A mutant that survives the fast modules is
either closed with a new fast test (preferred) or, when only the slow
worlds can observe the behaviour it changes, recorded in `NON_FAST_
KILLS_5B` below and confirmed by `--worlds-only` (against `test_
totality_5b.py` first, `test_full_shape_5b.py` second). The two
reproducible records of which mutants took which path are the committed
`mutation_build.log` (`main()`'s own fast-pass run) and `mutation_
worlds.log` (`run_worlds_only`'s non-fast pass) — both regenerated from
the CURRENT source by re-running this file, never hand-edited.

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
    """exp4c's/Experiment 5's `mutation_check.py::_slug` — a stable,
    comma-free, CLI-selectable label derived from a mutant's own
    description text."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return s[:72]


L = ROOT / "experiments" / "exp5b"
ST5B = L / "stats_5b.py"
PW5B = L / "power_5b.py"
CL5B = L / "collect_5b.py"
UN5B = L / "run" / "units_5b.py"
BAT5B = L / "battery_5b.py"
AN5B = L / "analyze_5b.py"


def _run_function_node(path: Path):
    src = path.read_text()
    tree = ast.parse(src, filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            return node, src
    raise RuntimeError(f"{path}: no top-level run() found")


def _totality_mutants_5b(path: Path) -> list:
    """One mutant per `collect_total_5b(thunk, label)` call site
    TEXTUALLY INSIDE `run()`'s own body (the same AST restriction
    `test_totality_5b.py::_site_templates_5b` uses — `secondaries_5b`,
    a separate top-level function `run()` merely calls, is excluded):
    replaced VERBATIM at that exact source span by `((thunk)(), [])` —
    the thunk runs uncaught, reporting zero failures regardless of what
    it does. A site whose exact text is not unique in the source is
    skipped by `main()`'s own `count(old) != 1` guard.

    Every totality mutant carries a `label` — a hash of the call site's
    own FULL source text — stable across any edit that does not touch
    the site itself, independent of its line number."""
    fn_node, src = _run_function_node(path)
    out = []
    for node in ast.walk(fn_node):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total_5b" or not node.args:
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if full is None or thunk is None:
            continue
        label = "totality_" + hashlib.sha256(full.encode()).hexdigest()[:10]
        out.append((path, f"run(): totality — collect_total_5b stripped at line "
                          f"{node.lineno} ({thunk.splitlines()[0][:60]}...)",
                   full, f"(({thunk})(), [])", label))
    return out


M = [
    # -------------------------------------------------------------- stats_5b.py
    (ST5B, "placebo_terms_5b: the weight / SQRT2_5B replaced by / 1.0",
     'terms.append(abs((a - float(b)) + sign * (small["f_B"] - n_j)) / b5b.SQRT2_5B)',
     'terms.append(abs((a - float(b)) + sign * (small["f_B"] - n_j)) / 1.0)'),
    (ST5B, "placebo_terms_5b: the abs( dropped",
     '            terms.append(abs((a - float(b)) + sign * (small["f_B"] - n_j)) / b5b.SQRT2_5B)',
     '            terms.append(((a - float(b)) + sign * (small["f_B"] - n_j)) / b5b.SQRT2_5B)'),
    (ST5B, "placebo_terms_5b: the b_plus side skipped",
     '    for side in ("b_minus", "b_plus"):', '    for side in ("b_minus",):'),
    (ST5B, "cell_5b: M = _mean(...) becomes M = sum(...)",
     "    M = _mean(placebo_terms_5b(cell5, small))", "    M = sum(placebo_terms_5b(cell5, small))"),
    (ST5B, "cell_5b: Q dropped from c_naive",
     '        "c_naive": ((R - 0.5 * (float(P) + Q)) / n) if (Q is not None and P is not None) else None,',
     '        "c_naive": ((R - float(P)) / n) if (Q is not None and P is not None) else None,'),
    (ST5B, "cell_5b: R read from abs(a - f_B) instead of cell5['R']",
     '    R, P = float(cell5["R"]), cell5["P"]',
     '    R, P = abs(float(cell5["a"]) - float(small["f_B"])), cell5["P"]'),
    (ST5B, "tree_5b: the bar T >= T_BAR_5B widened to T > T_BAR_5B",
     "T >= b5b.T_BAR_5B", "T > b5b.T_BAR_5B"),
    (ST5B, "tree_5b: the alpha comparison p < ALPHA_5B widened to p <= ALPHA_5B",
     "p < b5b.ALPHA_5B", "p <= b5b.ALPHA_5B"),
    (ST5B, "tree_5b: SIGN-ONLY/SIZE-ONLY swapped",
     '    cell = "SIZE-ONLY" if big else ("SIGN-ONLY" if sig else "INSIDE")',
     '    cell = "SIGN-ONLY" if big else ("SIZE-ONLY" if sig else "INSIDE")'),
    (ST5B, "calibration_read_5b: alpha < ALPHA_CAL_5B widened to <=",
     '            "cell": "CALIBRATED" if alpha < b5b.ALPHA_CAL_5B else "INFLATED",',
     '            "cell": "CALIBRATED" if alpha <= b5b.ALPHA_CAL_5B else "INFLATED",'),
    (ST5B, "calibration_read_5b: the OFF-GRID condition sigma_hat > top widened to >=",
     "    if sigma_hat > top:", "    if sigma_hat >= top:"),
    (ST5B, "calibration_read_5b: the bottom clamp dropped",
     "    x = max(float(sigma_hat), bottom)", "    x = float(sigma_hat)"),
    (ST5B, "cell_5b: np.std(reads4, ddof=1) becomes ddof=0",
     '        "small_sd": float(np.std(reads4, ddof=1)) if len(reads4) >= 2 else None,',
     '        "small_sd": float(np.std(reads4, ddof=0)) if len(reads4) >= 2 else None,'),
    (ST5B, "sigma_hat_5b: the RMS becomes a mean of SDs",
     '    return {"pooled": (math.sqrt(float(np.mean([c["small_sd"] ** 2 for c in live]))) if live else None),',
     '    return {"pooled": (float(np.mean([c["small_sd"] for c in live])) if live else None),'),
    (ST5B, "tree_5b: MIN_LIVE_CELLS_5B (20) read as a literal 19",
     "    if n < b5b.MIN_LIVE_CELLS_5B or k < b5b.MIN_NONZERO_BLOCKS_5B:",
     "    if n < 19 or k < b5b.MIN_NONZERO_BLOCKS_5B:"),
    (ST5B, "modifier_5b: R_gt_M selector replaced by an unconditional True",
     '    sel = [c for c in analysed_5b(cells) if c["R_gt_M"]]',
     "    sel = [c for c in analysed_5b(cells) if True]"),
    (ST5B, "s9_spike_5b: the exclusion inverted (keeps ONLY the spike pair)",
     '    r = _sub(cells, lambda c: not (c["small"] == small and c["large"] == large), n_sample=n_sample, seed=seed)',
     '    r = _sub(cells, lambda c: (c["small"] == small and c["large"] == large), n_sample=n_sample, seed=seed)'),
    (ST5B, "s8_one_member_5b: f_B read from the cell instead of the S11 row's final",
     '        small = {"f_B": int(row["final"]), "members": {b5.S11_STEP_5: int(row["s11"])}}',
     '        small = {"f_B": int(c["f_B"]), "members": {b5.S11_STEP_5: int(row["s11"])}}'),

    # -------------------------------------------------------------- power_5b.py
    (PW5B, "simulate_5b: f_read = pw._read(f_true, sigma_s, rng) replaced by f_true (f not noised)",
     "        f_read = pw._read(f_true, sigma_s, rng)", "        f_read = f_true"),
    (PW5B, "simulate_5b: the members' shared drift dropped",
     "        members = {step: pw._read(f_true + d_s, sigma_s, rng) for step in b5b.WINDOW_STEPS_5B}",
     "        members = {step: pw._read(f_true, sigma_s, rng) for step in b5b.WINDOW_STEPS_5B}"),
    (PW5B, "compute_5b: the sigma_s grid's order reversed",
     "    for sigma_s in b5b.SIGMA_GRID_5B:", "    for sigma_s in reversed(b5b.SIGMA_GRID_5B):"),
    (PW5B, "compute_5b: sigma_hat_axis read from the nominal grid instead of the simulated mean",
     '            "sigma_hat_axis": [g["sigma_hat_sim_mean"] for g in grid],',
     '            "sigma_hat_axis": list(b5b.SIGMA_GRID_5B),'),
    (PW5B, "compute_5b: the deciding arm read at grid index 0 instead of the belief index",
     '    deciding = grid[i_belief]["arms"]["plugin"]["P_fire_5b"]',
     '    deciding = grid[0]["arms"]["plugin"]["P_fire_5b"]'),
    (PW5B, "compute_5b: the declaration's >= widened to >",
     '            "declaration": "POWERED" if deciding >= POWER_BAR_5B else "DECLARED UNDERPOWERED IN ADVANCE",',
     '            "declaration": "POWERED" if deciding > POWER_BAR_5B else "DECLARED UNDERPOWERED IN ADVANCE",'),
    (PW5B, "main: the write-once refusal dropped (a second write silently overwrites)",
     '    if out.is_file():\n'
     '        raise RuntimeError(f"power_5b.main: {out} exists — the power record is written ONCE")',
     '    if False:\n'
     '        raise RuntimeError(f"power_5b.main: {out} exists — the power record is written ONCE")'),
    (PW5B, "main: require_exp5_closed_5b call removed",
     "    closed = b5b.require_exp5_closed_5b(tag_exists=tag_exists, blob_sha=blob_sha, verdict_sha=verdict_sha,\n"
     "                                        exp5_root=exp5_root)",
     '    closed = {"verdict_sha256": None}'),

    # ------------------------------------------------------------- collect_5b.py
    (CL5B, "run_unit_5b: the digest halt (SystemExit) removed",
     "            raise SystemExit(2)", "            pass"),
    (CL5B, "run_unit_5b: _unit_5b.json written BEFORE run_unit_5 (reread=None, moved above)",
     '    r = c5.run_unit_5(size, step, root=root, why=why, **kw)\n'
     "    reread = None\n"
     "    if int(step) in b5b.reread_steps_5b():\n"
     "        reread = reread_compare_5b(root, size, step, exp5_root=exp5_root)\n"
     '    write_unit5b_record_5b(root, size, step, why=why, host=kw["host"], git_sha=kw["git_sha"], reread=reread)',
     '    write_unit5b_record_5b(root, size, step, why=why, host=kw["host"], git_sha=kw["git_sha"], reread=None)\n'
     '    r = c5.run_unit_5(size, step, root=root, why=why, **kw)\n'
     "    reread = None\n"
     "    if int(step) in b5b.reread_steps_5b():\n"
     "        reread = reread_compare_5b(root, size, step, exp5_root=exp5_root)"),
    (CL5B, "reread_compare_5b: byte_identical ignoring per_doc",
     '            "byte_identical": bool(per_doc == 0 and repr(ls_here["loss"]) == repr(ls_there["loss"])\n'
     "                                   and sum(cont_diffs.values()) == 0 and sum(diffs.values()) == 0),",
     '            "byte_identical": bool(repr(ls_here["loss"]) == repr(ls_there["loss"])\n'
     "                                   and sum(cont_diffs.values()) == 0 and sum(diffs.values()) == 0),"),
    (CL5B, "reread_compare_5b: loss_within_tol <= narrowed to <",
     '"tolerance_failures": tol, "loss_within_tol": loss_delta <= b5b.LOSS_TOL_5B}',
     '"tolerance_failures": tol, "loss_within_tol": loss_delta < b5b.LOSS_TOL_5B}'),
    (CL5B, "run_unit_5b: the torn-5b-unit rmtree removed",
     "    d = b5b.unit_dir_5b(root, size, step)\n"
     "    if d.exists():\n"
     "        shutil.rmtree(d)",
     "    d = b5b.unit_dir_5b(root, size, step)"),
    (CL5B, "gate1_record_5b: pass forced True",
     '    rec = {"per_unit": per_unit, "pass": not failures, "failures": failures,',
     '    rec = {"per_unit": per_unit, "pass": True, "failures": failures,'),

    # --------------------------------------------------------- run/units_5b.py
    (UN5B, "run(): the power-record-present refusal dropped",
     '    if not present:\n'
     '        raise RuntimeError("refusing: results/power_5b.json is not present — power ONCE precedes the tag")',
     '    if False:\n'
     '        raise RuntimeError("refusing: results/power_5b.json is not present — power ONCE precedes the tag")'),
    (UN5B, "run(): the projection-ancestry refusal dropped",
     "    if not pc or not anc(pc, git_sha):\n"
     '        raise RuntimeError("refusing: the projection is not committed in this HEAD\'s history "\n'
     '                           "(design §7: the projection is sealed before any unit)")',
     "    if False:\n"
     '        raise RuntimeError("refusing: the projection is not committed in this HEAD\'s history "\n'
     '                           "(design §7: the projection is sealed before any unit)")'),
    (UN5B, "run(): the HALTED-marker refusal dropped",
     "    if b5b.halt_marker_path_5b(root, size).exists():\n"
     '        raise RuntimeError(f"refusing: {size} is halted ({b5b.halt_marker_path_5b(root, size)})")',
     "    if False:\n"
     '        raise RuntimeError(f"refusing: {size} is halted ({b5b.halt_marker_path_5b(root, size)})")'),
    (UN5B, "run(): the host stack/device comparison against the record on disk dropped",
     '        if host["stack"] != live["stack"] or host["device"] != live["device"]:\n'
     '            raise RuntimeError(f"refusing: the host record on disk ({host[\'stack\']}, {host[\'device\']}) "\n'
     '                               f"is not this process\'s ({live[\'stack\']}, {live[\'device\']})")',
     '        if False:\n'
     '            raise RuntimeError(f"refusing: the host record on disk ({host[\'stack\']}, {host[\'device\']}) "\n'
     '                               f"is not this process\'s ({live[\'stack\']}, {live[\'device\']})")'),
    (UN5B, "run(): the four units processed in reversed order",
     "    for i, step in enumerate(steps):", "    for i, step in enumerate(reversed(steps)):"),

    # ----------------------------------------------------------- battery_5b.py
    (BAT5B, "require_exp5_closed_5b: the verdict-sha check skipped",
     "    if verdict_sha is not False:", "    if False:"),
    (BAT5B, "unit5b_record_failures_5b: prereg_tag no longer checked",
     '    for k, v in (("size", size), ("step", int(step)), ("prereg_tag", PREREG_TAG_5B),\n'
     '                 ("exp5_closed_tag", EXP5_CLOSED_TAG_5B)):',
     '    for k, v in (("size", size), ("step", int(step)),\n'
     '                 ("exp5_closed_tag", EXP5_CLOSED_TAG_5B)):'),
    (BAT5B, "unit_complete_5b: the _unit_5b.json clause dropped",
     "    return b5.unit_complete_5(root, size, step) and unit5b_record_path_5b(root, size, step).is_file()",
     "    return b5.unit_complete_5(root, size, step)"),
    (BAT5B, "_strip_volatile: cells also stripped (exp5_verdict_equal_failures_5b blinded to it)",
     "def _strip_volatile(v: dict) -> dict:\n"
     "    out = dict(v)\n"
     '    out.pop("meta", None)\n'
     '    out.pop("pins_active", None)\n'
     "    return out",
     "def _strip_volatile(v: dict) -> dict:\n"
     "    out = dict(v)\n"
     '    out.pop("meta", None)\n'
     '    out.pop("pins_active", None)\n'
     '    out.pop("cells", None)\n'
     "    return out"),
    (BAT5B, "reread_steps_5b: returns only the final",
     "    return (b5.FINAL_STEP_5, WINDOW_STEPS_5B[0])", "    return (b5.FINAL_STEP_5,)"),
    (BAT5B, "expected_units_5b: the final dropped from the expected set",
     "    return {(s, st) for s in small_sides_5b() for st in unit_steps_5b()}",
     "    return {(s, st) for s in small_sides_5b() for st in WINDOW_STEPS_5B}"),

    # ----------------------------------------------------------- analyze_5b.py
    (AN5B, "_exp5: the gate-2 verdict equality check dropped (pin check alone)",
     "        bad = b5b.exp5_verdict_equal_failures_5b(v5, committed) + b5b.exp5_verdict_pin_failures_5b(v5)",
     "        bad = b5b.exp5_verdict_pin_failures_5b(v5)"),
    (AN5B, "load_side_5b: the extra-unit-on-disk check dropped",
     "    extra = sorted(on_disk - set(b5b.unit_steps_5b()))\n"
     "    if extra:\n"
     '        raise ValueError(f"gate 4 {size}: step{extra[0]} on disk but never requested (nothing else loaded)")',
     "    extra = sorted(on_disk - set(b5b.unit_steps_5b()))"),
    (AN5B, "load_side_5b: the torn-unit check dropped",
     "    torn = sorted(s for s in on_disk if not b5.unit_complete_5(root, size, s))\n"
     "    if torn:\n"
     '        raise ValueError(f"{size}: step{torn[0]} is on disk but is not a complete unit (torn)")',
     "    torn = sorted(s for s in on_disk if not b5.unit_complete_5(root, size, s))"),
    (AN5B, "load_side_5b: the _unit_5b.json requirement dropped",
     "        p = b5b.unit5b_record_path_5b(root, size, step)\n"
     "        if not p.is_file():\n"
     '            raise ValueError(f"{size}/step{step}: _unit_5b.json missing (a unit without 5b\'s attestation)")',
     "        p = b5b.unit5b_record_path_5b(root, size, step)"),
    (AN5B, "gate1_rederive_5b: the runner's attestation comparison dropped",
     '            att = side["rereads"].get(step) or {}\n'
     '            for k in ("digest_equal", "loss_within_tol", "tolerance_failures", "byte_identical"):\n'
     "                if att.get(k) != rr[k]:\n"
     '                    failures.append(f"gate 1 {key}: the runner\'s attested {k} {att.get(k)!r} != '
     're-derived {rr[k]!r}")',
     '            att = side["rereads"].get(step) or {}'),
    (AN5B, "power_failures_5b: the byte-for-byte comparison dropped",
     '        if json.dumps(recomputed, sort_keys=True) != json.dumps(rec, sort_keys=True):\n'
     '            bad.append("power record: the recomputed record differs byte-for-byte from the committed one")',
     "        if False:\n"
     '            bad.append("power record: the recomputed record differs byte-for-byte from the committed one")'),
    (AN5B, "projection_failures_5b: the per-unit ancestry loop dropped",
     "    for size, side in sides.items():\n"
     "        if side is None:\n"
     "            continue\n"
     '        for step, sha in (side.get("git_shas") or {}).items():\n'
     "            if not is_ancestor(projection_commit, sha):\n"
     '                bad.append(f"projection: {size}/step{step} was built at {sha}, not a descendant of the "\n'
     '                           f"projection commit ({projection_commit})")\n'
     "    return bad",
     "    return bad"),
    (AN5B, "run(): S1-S12 computed regardless of failures (the units gate dropped)",
     "    secondaries, secondary_failures = ({}, {})\n"
     "    if not failures:\n"
     "        secondaries, secondary_failures = secondaries_5b(\n"
     '            cells, cells5_all=(v5 or {}).get("cells", []), v5=v5 or {}, sides=sides, power_rec=power_rec,\n'
     "            sigma_hat=sigma_hat, calibration=calibration, gate1_rec=gate1_rec, floors=floors, "
     "exp5_root=exp5_root,\n"
     "            n_sample=n_sample, seed=b5.PERM_SEED_5)",
     "    secondaries, secondary_failures = secondaries_5b(\n"
     '        cells, cells5_all=(v5 or {}).get("cells", []), v5=v5 or {}, sides=sides, power_rec=power_rec,\n'
     "        sigma_hat=sigma_hat, calibration=calibration, gate1_rec=gate1_rec, floors=floors, exp5_root=exp5_root,\n"
     "        n_sample=n_sample, seed=b5.PERM_SEED_5)"),
]

# Every hand mutant above is a 4-tuple (path, name, old, new); every
# AST-generated totality mutant is already a 5-tuple with its own
# hash-derived label. Normalize the hand mutants to 5-tuples by
# deriving their label from the description text (`_slug`), THEN
# append the totality mutants — so hand-mutant labels are always
# `_slug(name)`, never a totality hash.
M = [(p, name, old, new, _slug(name)) for p, name, old, new in M]
M += _totality_mutants_5b(AN5B)

_labels = [m[4] for m in M]
assert len(_labels) == len(set(_labels)), (
    f"mutation_check.py: duplicate mutant labels — {[l for l in _labels if _labels.count(l) > 1]}")


FAST_TESTS = [str(L / "tests" / "test_battery_5b.py"), str(L / "tests" / "test_stats_5b.py"),
             str(L / "tests" / "test_power_5b.py"), str(L / "tests" / "test_collect_5b.py"),
             str(L / "tests" / "test_stages_5b.py"), str(L / "tests" / "test_analyze_5b.py"),
             str(L / "tests" / "test_verify_referents_5b.py")]
FAST_EXTRA_ARGS = ["-m", "not slow"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_5b.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_5b.py")]
WORLDS_TESTS = TOTALITY_TESTS + FULLSHAPE_TESTS

# Mutants killed ONLY by a slow (totality/full-shape) test — populated as
# fast-pass survivors are individually confirmed against the slow suites
# via `--worlds-only`; see PROGRESS.md's Task 6 entry for the transcript.
# Each value names the exact killing test.
NON_FAST_KILLS_5B = {
    # both individually re-confirmed (script transcript, PROGRESS.md Task 6): applying either
    # mutant alone and running test_totality_5b.py fails inside the corruption-shapes test —
    # #44 (the gate-2 equality check dropped) is caught by shape 15b's own message-substring
    # assertion ("differs from the committed" — the pin check alone reports a different
    # message even though it still refuses); #51 (secondaries computed regardless of
    # failures) is caught by every `_assert_insufficient` call's `secondaries == {}` check.
    "exp5_the_gate_2_verdict_equality_check_dropped_pin_check_alone":
        "test_totality_5b.py::test_every_runner_leavable_tree_shape_gives_insufficient_data",
    "run_s1_s12_computed_regardless_of_failures_the_units_gate_dropped":
        "test_totality_5b.py::test_every_runner_leavable_tree_shape_gives_insufficient_data",
    # The seven totality mutants the rebuilt fast suite does not catch (the sites with only a
    # SLOW behavioural test): each individually re-confirmed by applying it alone and running
    # test_totality_5b.py -k "not test_site_template_count_is_24" -m slow (script transcript,
    # PROGRESS.md Task 6 fix round 1).
    "totality_eb285f87a4":     # line 410, the halt marker — shape 1
        "test_totality_5b.py::test_every_runner_leavable_tree_shape_gives_insufficient_data",
    "totality_eed0ac97ed":     # line 529, st.cells_5b
        "test_totality_5b.py::test_the_five_post_units_sites_raise_without_the_wrapper",
    "totality_fadbfe1930":     # line 531, st.primary_5b
        "test_totality_5b.py::test_the_five_post_units_sites_raise_without_the_wrapper",
    "totality_f7b4069e79":     # line 533, st.sigma_hat_5b
        "test_totality_5b.py::test_the_five_post_units_sites_raise_without_the_wrapper",
    "totality_ab35a54246":     # line 534, st.calibration_read_5b
        "test_totality_5b.py::test_the_five_post_units_sites_raise_without_the_wrapper",
    "totality_4455ad799d":     # line 537, st.modifier_5b
        "test_totality_5b.py::test_the_five_post_units_sites_raise_without_the_wrapper",
    "totality_01f5677eb0":     # line 568, the verdict write
        "test_totality_5b.py::test_verdict_write_site_raises_without_the_wrapper",
}
# The remaining 17 totality mutants are killed by the FAST suite directly and so carry NO
# entry here — this table lists only what the fast suite does not catch, never a static list
# of "all totality labels". Nine are the sites the new fast tests target directly (frozen
# modules, both import-surface sites, manifest, slice, referents, battery, floors, verify).
# The other eight (prereg tag, exp5-closed, exp5, host record, units, gate 1, power record,
# projection) are caught COLLATERALLY by every one of those same nine new fast tests: `_
# isolated_kwargs` points `exp5_root` at an empty tmp directory and sets `tag_exists=lambda t:
# False`, so require_prereg_5b/require_exp5_closed_5b/Experiment 5's own analyzer/the host
# record/every unit load/gate 1/the power record/the projection check ALL genuinely fail for
# real in every one of those tests (not simulated) — stripping any ONE of their wrappers
# crashes the test with an uncaught exception, same mechanism as the sites those tests were
# built for. These eight ALSO have their original behavioural kill from the eighteen
# corruption shapes (slow); the fast collateral kill is confirmed in the rebuilt fast-pass
# run (PROGRESS.md Task 6 fix round 1), not assumed.
#
# Fix round 1 (Important 1): the 24 AST-generated totality mutants were previously routed
# through `test_site_template_count_is_24` alone — a STRUCTURAL check (it fires whenever ANY
# collect_total_5b call is stripped from run()'s AST, whether or not the site's underlying
# thunk is ever driven to raise) rather than a BEHAVIOURAL one. Every one of the 24 sites now
# has a dedicated behavioural test (nine fast, in test_analyze_5b.py: frozen modules, both
# import-surface sites, manifest, slice, referents, battery, floors, verify; six slow, in
# test_totality_5b.py's new test_the_five_post_units_sites_raise_without_the_wrapper — cells,
# primary, sigma hat, calibration, modifier — and test_verdict_write_site_raises_without_the_
# wrapper; the remaining nine were already covered by the eighteen corruption shapes: halt
# marker, prereg tag, exp5-closed, exp5, host record, units (all size-loop entries), gate 1,
# power record, projection). Each of the 24 individually re-confirmed against its OWN
# behavioural test (script transcripts, PROGRESS.md Task 6 fix round 1) BEFORE `run_worlds_
# only` was changed to rely on them; the count test remains as a supplementary, non-authoritative
# check inside test_totality_5b.py — `run_worlds_only` never credits it as a kill (see its
# `sequence` construction below). Nothing is pre-populated here for the totality labels: the
# fast pass (`main()`) now resolves most of them directly (a fast behavioural test failing IS
# "killed by the fast suite"), and whatever still survives fast is discovered fresh by `run_
# worlds_only`'s own totality-labelled sequence, never guessed in advance.

# Fix round 1 (Important 1): NON_FAST_KILLS_5B's neighbour table — a totality label lands
# here, never in NON_FAST_KILLS_5B, when NEITHER the fast suite nor the totality file's own
# behavioural tests (excluding the count test) catch it, so `run_worlds_only` falls back to
# `test_site_template_count_is_24` ONLY to disclose that the kill is structural (an AST
# call-site count), never behavioural. Populated only from an observed `--worlds-only` run,
# same discipline as NON_FAST_KILLS_5B. Expected to stay empty now that every one of the 24
# totality sites has a dedicated behavioural test; kept as the disclosure mechanism the ruling
# requires in case a future refactor reopens a gap.
STRUCTURAL_ONLY_5B = {}

# Mutants that survive BOTH the fast and slow suites, with a DOCUMENTED
# reason the mutation is behaviourally equivalent on every input this
# instrument's own tests can construct — never added without a proof in
# the comment beside the entry.
EQUIVALENT_MUTANTS = set()


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp5b" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """exp4c's/2k's/Experiment 5's Finding 3 lesson: a stray `.mutation_
    backup` anywhere under `experiments/exp5b` means either a concurrent
    run is already in flight or a previous run crashed without
    restoring — refuse before the baseline check even starts."""
    found = sorted((ROOT / "experiments" / "exp5b").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp5b (a concurrent run, or a previous crash that "
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
    reported as `timed_out=True` — the caller must never fold this into
    either `ok` or `survived`. pytest exits 5 ("no tests ran") when a
    `-k` pattern selects nothing — NOT `returncode == 0`, so already
    never `ok`, but folding it into `survived` would silently read a
    stale mapping as a kill; `no_tests_collected` lets the caller route
    it to a SKIP instead."""
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
    """The pytest node id of the first FAILED test in a `-x` run's FULL
    stdout (never the 600-char-truncated `run_suite` tail)."""
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


WORLD_ONLY_LABELS = sorted(NON_FAST_KILLS_5B)


def run_worlds_only(argv) -> int:
    """Executes every label in `WORLD_ONLY_LABELS` against `test_
    totality_5b.py`/`test_determinism_5b.py` first, `test_full_shape_
    5b.py` second if totality alone doesn't catch it (`-m slow` both
    times). Prints one line per label with the identified killing test
    (or OPEN if every route survives) and a final tally; writes nothing
    to `NON_FAST_KILLS_5B` itself — the caller reads this run's own
    stdout log and updates that table by hand, so the committed record
    is never wider than what was actually observed."""
    only = _parse_only(argv)
    labels = [lbl for lbl in WORLD_ONLY_LABELS if only is None or lbl in only]
    by_label = {m[4]: m for m in M}
    missing = [lbl for lbl in labels if lbl not in by_label]
    if missing:
        raise RuntimeError(f"run_worlds_only: label(s) not found in M: {missing}")

    _refuse_if_any_backup_exists()
    clear_pycache()

    killed_by, structural_only, open_survivors, errors = {}, {}, [], []
    for n, label in enumerate(labels, 1):
        path, name, old, new, mlabel = by_label[label]
        if label.startswith("totality_"):
            # Fix round 1 (Important 1): BEHAVIOURAL tests run first — the fast suite (nine of
            # the 24 sites now have a dedicated fast test: frozen modules, both import-surface
            # sites, manifest, slice, referents, battery, floors, verify), then the totality
            # file's own behavioural tests EXCLUDING the count test by name (the eighteen
            # corruption shapes cover nine more sites; the new `test_the_five_post_units_
            # sites_raise_without_the_wrapper` and `test_verdict_write_site_raises_without_the_
            # wrapper` cover the remaining six). `test_site_template_count_is_24` is never in
            # this sequence — it fires on ANY stripped site regardless of behaviour, so crediting
            # it here would launder a structural-only kill as behavioural.
            sequence = [("fast-behavioural", FAST_TESTS, []),
                       ("totality-behavioural", TOTALITY_TESTS,
                        ["-m", "slow", "-k", "not test_site_template_count_is_24"])]
        else:
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
                ok, out, timed_out, no_tests = _run_suite_full(tests, extra, timeout=2400)
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
        if found:
            continue
        if not label.startswith("totality_"):
            print(f"[{label}] ({n}/{len(labels)}) OPEN SURVIVOR — every route tried failed to "
                 f"kill it: {name}", flush=True)
            open_survivors.append(label)
            continue
        # supplementary-only, for disclosure: confirm the AST count still catches it, but
        # this is NEVER credited as a kill — a real behavioural gap would need a new test,
        # not a note here.
        backup = _acquire_backup(path)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out, timed_out, no_tests = _run_suite_full(
                TOTALITY_TESTS, ["-m", "slow", "-k", "test_site_template_count_is_24"], timeout=120)
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        if not timed_out and not no_tests and not ok:
            print(f"[{label}] ({n}/{len(labels)}) STRUCTURAL-ONLY (no behavioural test drives "
                 f"this site) — the AST count test alone catches it: {name}", flush=True)
            structural_only[label] = "test_site_template_count_is_24 (structural-only, not a behavioural kill)"
        else:
            print(f"[{label}] ({n}/{len(labels)}) OPEN SURVIVOR — every route, including the "
                 f"structural count, failed to kill it: {name}", flush=True)
            open_survivors.append(label)

    print(f"\n=== run_worlds_only tally === considered={len(labels)} killed={len(killed_by)} "
         f"structural_only={len(structural_only)} open_survivors={len(open_survivors)} "
         f"errors={len(errors)}")
    print(f"killed_by = {killed_by}")
    print(f"structural_only = {structural_only}")
    print(f"open_survivors = {open_survivors}")
    print(f"errors = {errors}")
    return 1 if (open_survivors or errors or structural_only) else 0


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
        if ok and mlabel in NON_FAST_KILLS_5B:
            print(f"[{mlabel}] (#{i}) survived-fast, killed by the slow suite — "
                 f"{NON_FAST_KILLS_5B[mlabel]} (individually re-confirmed, see PROGRESS.md)  "
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
