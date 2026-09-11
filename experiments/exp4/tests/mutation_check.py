# experiments/exp4/tests/mutation_check.py
"""Mutation-test exp4's OWN modules -- metric_4 (the k-NN alignment
metric, CKA, depth pairing, the planted calibration fixture),
battery_4 (the model tables, the load dispatcher's record contract,
the rung-set/t_clear rule, the gate-1 byte checkers, the pins/prereg
binding), collect_4 (the collector's padding-masked pooling, the set
tables, the overlap machinery, the write-then-reread integrity check),
run/reference_4 (the reference stage's digest pins and halt gate),
run/sweep_4 (gate 1, the reference-seal/eligibility/power/first-unit
requirements, the per-step digest pin), and analyze_4 (the excess/phi/
primary/eligibility/gate-0/gate-1/tree/run() verdict path -- every
`collect_total_4` call site in `run()`, AST-generated via a LOCAL
`_totality_mutants_4`, not 2i's `_totality_mutants`: exp4's own
refusal-collecting function is named `collect_total_4`, not
`collect_total`, so 2i's name-matched AST walk finds nothing here --
`_totality_mutants_4` is the same walk with the name check changed).
Everything imported from `experiments/exp2*`/`experiments/exp3*` is
FROZEN instrument and is not re-targeted here.

2n's/2i's precedent: run each mutant against the FAST modules only
(`test_metric_4.py`, `test_battery_4.py`, `test_collect_4.py`,
`test_stages_4.py`, `test_analyze_4.py -m "not slow"`, `test_power_4.
py`) -- together they take a few seconds to a few minutes and observe
nothing a `--totality`/`--fullshape` mutant changes. A mutant that
survives the fast modules is either closed with a new fast test
(preferred) or, when only totality/full-shape can observe the
behaviour it changes, recorded as 'killed by worlds/totality only'
after one targeted confirmation run under `--totality`/`--fullshape`
-- see PROGRESS.md's Task 5 entry for which mutants took that path.

Mutates sources IN PLACE (with an exclusive `.mutation_backup`) and
restores them in `finally` -- run alone, detached, never under a
foreground timeout, never concurrently with another mutation run."""
from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

L = ROOT / "experiments" / "exp4"
MT = L / "metric_4.py"
BK = L / "battery_4.py"
CL = L / "collect_4.py"
RF = L / "run" / "reference_4.py"
SW = L / "run" / "sweep_4.py"
AN = L / "analyze_4.py"
PW = L / "power_4.py"


def _totality_mutants_4(path: Path) -> list:
    """2i's `_totality_mutants`, adapted: exp4's refusal-collector is
    named `collect_total_4`, not `collect_total`, so the AST name
    check is changed to match it. One mutant per `collect_total_4(
    thunk, label)` call site: replaced VERBATIM at that exact source
    span by `(thunk(), [])` -- the thunk runs uncaught, reporting zero
    failures regardless of what it does. A site whose exact text is
    not unique in the source is skipped by main()'s own `count(old) !=
    1` guard, printed as a surviving SKIP rather than silently
    omitted."""
    src = path.read_text()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total_4" or not node.args:
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if full is None or thunk is None:
            continue
        out.append((path, f"run(): totality -- collect_total_4 stripped at line "
                          f"{node.lineno} ({thunk.splitlines()[0][:60]}...)",
                   full, f"(({thunk})(), [])"))
    return out


M = [
    # ------------------------------------------------------------ metric_4.py
    (MT, "K_4 = 10 -> 9", "K_4 = 10", "K_4 = 9"),
    (MT, "knn_sets: self not excluded (fill_diagonal dropped)",
     "    np.fill_diagonal(sims, -np.inf)",
     "    pass"),
    (MT, "knn_sets: ties broken by descending index, not ascending",
     '''    order = np.argsort(-sims, axis=1, kind="stable")[:, :k]
    order.sort(axis=1)''',
     '''    n = sims.shape[0]
    rev_sims = sims[:, ::-1]
    order_rev = np.argsort(-rev_sims, axis=1, kind="stable")[:, :k]
    order = (n - 1) - order_rev
    order.sort(axis=1)'''),
    (MT, "overlap_counts: union instead of intersection",
     "        out[i] = len(set(A[i].tolist()) & set(B[i].tolist()))",
     "        out[i] = len(set(A[i].tolist()) | set(B[i].tolist()))"),
    (MT, "chance_4: denominator off by one (n instead of n-1)",
     "    return k / (n - 1)",
     "    return k / n"),
    (MT, "depth_pairs: ties broken to the LARGER q (rounding up), not the smaller",
     "        best = min(sites_q, key=lambda q: (abs(h / dm - q / dq), q))",
     "        best = min(sites_q, key=lambda q: (abs(h / dm - q / dq), -q))"),
    (MT, "_hsic_unbiased: t1 uses K + L instead of K * L",
     "    t1 = float(np.sum(K * L))",
     "    t1 = float(np.sum(K + L))"),
    (MT, "planted_pair: base normalised by d_latent instead of sqrt(d_latent)",
     "    base = s * (Z @ A) / np.sqrt(d_latent)",
     "    base = s * (Z @ A) / d_latent"),
    (MT, "sites_4: sorted() dropped (returns an unordered set)",
     "    return sorted({l for l, _ in probe_2f.site_family(int(n_hidden))})",
     "    return {l for l, _ in probe_2f.site_family(int(n_hidden))}"),
    (MT, "_unit_rows: the non-finite/zero-row guard disabled",
     '    if not np.all(np.isfinite(X)) or np.any(norms == 0):',
     "    if False:"),

    # ----------------------------------------------------------- battery_4.py
    (BK, "RENDER_4: comma is 'plain' instead of 'bos'",
     'RENDER_4 = {"pythia": "plain", "olmo2": "plain", "smollm3": "plain", "comma": "bos"}',
     'RENDER_4 = {"pythia": "plain", "olmo2": "plain", "smollm3": "plain", "comma": "plain"}'),
    (BK, "BATCH_4: the 6e9 threshold's batch sizes inverted",
     "BATCH_4 = {k: (16 if v >= 6e9 else 32) for k, v in PARAMS_4.items()}",
     "BATCH_4 = {k: (32 if v >= 6e9 else 16) for k, v in PARAMS_4.items()}"),
    (BK, "load_record_failures_4: the committed_digest pin skipped",
     '''    if rec.get("committed_digest") != expected_committed_digest:
        bad.append(f"{key}: committed_digest {rec.get('committed_digest')!r} != "
                   f"{expected_committed_digest!r}")''',
     '''    if False:
        bad.append(f"{key}: committed_digest {rec.get('committed_digest')!r} != "
                   f"{expected_committed_digest!r}")'''),
    (BK, "load_record_failures_4: the render pin (RENDER_4) unchecked on the record",
     '''    if rec.get("render") != expected_render:
        bad.append(f"{key}: render {rec.get('render')!r} != {expected_render!r}")''',
     '''    if False:
        bad.append(f"{key}: render {rec.get('render')!r} != {expected_render!r}")'''),
    (BK, "load_record_failures_4: the family pin skipped",
     '''    if rec.get("family") != expected_family:
        bad.append(f"{key}: family {rec.get('family')!r} != {expected_family!r}")''',
     '''    if False:
        bad.append(f"{key}: family {rec.get('family')!r} != {expected_family!r}")'''),
    (BK, "load_record_failures_4: the batch_size pin skipped",
     '''    if rec.get("batch_size") != expected_batch:
        bad.append(f"{key}: batch_size {rec.get('batch_size')!r} != {expected_batch!r}")''',
     '''    if False:
        bad.append(f"{key}: batch_size {rec.get('batch_size')!r} != {expected_batch!r}")'''),
    (BK, "load_record_failures_4: the refs pin skipped",
     '''    if tuple(rec.get("refs") or ()) != tuple(expected_refs):
        bad.append(f"{key}: refs {rec.get('refs')!r} != {list(expected_refs)!r}")''',
     '''    if False:
        bad.append(f"{key}: refs {rec.get('refs')!r} != {list(expected_refs)!r}")'''),
    (BK, "load_record_failures_4: the prereg_tag pin skipped",
     '''    if rec.get("prereg_tag") != PREREG_TAG_4:
        bad.append(f"{key}: prereg_tag {rec.get('prereg_tag')!r} != {PREREG_TAG_4!r}")''',
     '''    if False:
        bad.append(f"{key}: prereg_tag {rec.get('prereg_tag')!r} != {PREREG_TAG_4!r}")'''),
    (BK, "gate1_rederive_4: sets_equal compares 33 rungs, not 34",
     '''    sets_equal = {}
    for r in RUNGS:
        a = (ref_dir / "sets" / f"{r}.npz").read_bytes()
        b = (sweep_d / "sets" / f"{r}.npz").read_bytes()
        sets_equal[r] = (a == b)''',
     '''    sets_equal = {}
    for r in RUNGS[:33]:
        a = (ref_dir / "sets" / f"{r}.npz").read_bytes()
        b = (sweep_d / "sets" / f"{r}.npz").read_bytes()
        sets_equal[r] = (a == b)'''),
    (BK, "check_rung_set_pins_4: the R-set comparison against RUNG_SET_PIN_4 skipped",
     '''    got_r = tuple(sorted(rung_sets["R"]))
    want_r = tuple(sorted(RUNG_SET_PIN_4[traj]))
    if got_r != want_r:''',
     '''    got_r = tuple(sorted(rung_sets["R"]))
    want_r = tuple(sorted(RUNG_SET_PIN_4[traj]))
    if False:'''),
    (BK, "t_clear_4: takes the LAST significant step instead of the first (break removed)",
     '''            if st.binomial_bar(rec["correct"], rec["n"], floors[rung])["significant"]:
                first = step
                break''',
     '''            if st.binomial_bar(rec["correct"], rec["n"], floors[rung])["significant"]:
                first = step'''),
    (BK, "clears_and_stays_4: any() instead of all() (a transient rung reads as clears-and-stays)",
     "            if all(flags[i:]):",
     "            if any(flags[i:]):"),
    (BK, "rung_sets_4: a rung with a t_clear reads as flat (elif inverted)",
     "        elif tc[rung] is None:",
     "        elif tc[rung] is not None:"),
    (BK, "require_prereg_4: the tag_exists check skipped",
     "    if not tag_exists(PREREG_TAG_4):",
     "    if False:"),
    (BK, "require_prereg_4: the blob-binding equality check skipped",
     '''        want, got = blob_sha(PREREG_TAG_4, rel), bg.sha256_file(p)
        if want != got:''',
     '''        want, got = blob_sha(PREREG_TAG_4, rel), bg.sha256_file(p)
        if False:'''),
    (BK, "unit_complete_4: the sets_sha256 34-rung coverage check skipped",
     "    if set(sets_sha) != set(RUNGS):\n        return False",
     "    if False:\n        return False"),
    (BK, "gate1_failures_4: the activation_sha_equal per-rung check skipped",
     '''        if ae.get(r) is not True:
            bad.append(f"gate 1 {traj}/{r}: activation_sha_equal is not True")''',
     '''        if False:
            bad.append(f"gate 1 {traj}/{r}: activation_sha_equal is not True")'''),
    (BK, "gate1_failures_4: the digest_equal check skipped",
     '''    if g1.get("digest_equal") is not True:
        bad.append(f"gate 1 {traj}: digest_equal is not True")''',
     '''    if False:
        bad.append(f"gate 1 {traj}: digest_equal is not True")'''),
    (BK, "_N_HIDDEN_TRAJ_4: smollm3_3b's n_hidden off by one (37 -> 36)",
     '_N_HIDDEN_TRAJ_4 = {"pythia_2.8b": 33, "olmo2_7b": 33, "smollm3_3b": 37, "comma_7b": 33}',
     '_N_HIDDEN_TRAJ_4 = {"pythia_2.8b": 33, "olmo2_7b": 33, "smollm3_3b": 36, "comma_7b": 33}'),

    # ----------------------------------------------------------- collect_4.py
    (CL, "collect_rung_4: the pooled mean averages over PADDED tokens too (mask dropped)",
     "                pooled = (hs_b * mask_b[:, None]).sum(axis=1) / valid  # [n_sites, d]",
     "                pooled = hs_b.sum(axis=1) / valid  # [n_sites, d]"),
    (CL, "align_scalars_4: knn_prompt_end means over sites instead of items (wrong axis)",
     '        entry["knn_prompt_end"] = (ov_pe.astype(np.float64) / k).mean(axis=1).tolist()',
     '        entry["knn_prompt_end"] = (ov_pe.astype(np.float64) / k).mean(axis=0).tolist()'),
    (CL, "overlap_table_4: the pairing-length check skipped",
     '''    if len(pairing) != n_sites:
        raise ValueError(f"overlap_table_4: pairing length {len(pairing)} != n_sites {n_sites}")''',
     '''    if False:
        raise ValueError(f"overlap_table_4: pairing length {len(pairing)} != n_sites {n_sites}")'''),
    (CL, "non_pythia_refs_4: returns the Pythia reference instead of excluding it",
     '    return tuple(r for r in battery_4.REFERENCES_4 if battery_4.FAMILY_OF_KEY_4[r] != "pythia")',
     '    return tuple(r for r in battery_4.REFERENCES_4 if battery_4.FAMILY_OF_KEY_4[r] == "pythia")'),
    # #34: PROVEN EQUIVALENT, not a real survivor -- battery_4.py
    # populates FAMILY_OF_KEY_4 from the SAME source dict under BOTH
    # conventions (`FAMILY_OF_KEY_4.update(_FAMILY_OF_TRAJ_4)` keys it
    # by the raw traj name; `FAMILY_OF_KEY_4[f"endpoint_{_traj}"] =
    # _FAMILY_OF_TRAJ_4[_traj]` copies the identical value under the
    # endpoint key), so `FAMILY_OF_KEY_4[traj] ==
    # FAMILY_OF_KEY_4[f"endpoint_{traj}"]` for every real trajectory by
    # construction -- verified directly for all four (task-5-report.md
    # / PROGRESS.md carry the printed proof). No black-box test on the
    # real module can distinguish this mutant; confirmed SURVIVED via
    # `--only=34` after every other Task 5 survivor was independently
    # re-verified killed.
    (CL, "family_of_traj_4: looks up the raw traj name instead of its endpoint key",
     '    return battery_4.FAMILY_OF_KEY_4[f"endpoint_{traj}"]',
     '    return battery_4.FAMILY_OF_KEY_4[traj]'),
    (CL, "write_load_4: the sets re-read integrity check disabled",
     '''            if not np.array_equal(z["sets"], arrays["sets"]):
                raise ValueError(f"write_load_4: {sp} sets re-read mismatch")''',
     '''            if False:
                raise ValueError(f"write_load_4: {sp} sets re-read mismatch")'''),
    (CL, "write_load_4: the endpoint's activation sha is not recorded before deletion",
     '''            activation_sha[rung] = bg.sha256_file(acp)
            if not keep_activations:
                acp.unlink()''',
     '''            if not keep_activations:
                acp.unlink()
                activation_sha[rung] = None
            else:
                activation_sha[rung] = bg.sha256_file(acp)'''),
    (CL, "set_tables_4: site and position axes swapped",
     "            out[s, p] = metric_4.knn_sets(X[:, s, p, :].astype(np.float32), k=k)",
     "            out[s, p] = metric_4.knn_sets(X[:, p, s, :].astype(np.float32), k=k)"),

    # ------------------------------------------------------- run/reference_4.py
    (RF, "reference_4 run(): the any-HALTED-marker guard disabled",
     '''    if _any_halted(root):
        raise RuntimeError(f"refusing: a HALTED marker exists under {Path(root) / 'results'}")''',
     '''    if False:
        raise RuntimeError(f"refusing: a HALTED marker exists under {Path(root) / 'results'}")'''),
    (RF, "reference_4 run(): the endpoint digest pin skipped",
     '''        want = battery_4.committed_step_digest_4(traj, battery_4.ENDPOINT_STEP_4[traj])
        if info["tensor_digest"] != want:''',
     '''        want = battery_4.committed_step_digest_4(traj, battery_4.ENDPOINT_STEP_4[traj])
        if False:'''),
    (RF, "reference_4 run(): the first-unit digest pin skipped",
     '''        want = battery_4.committed_step_digest_4(traj, step)
        if info["tensor_digest"] != want:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
            _halt_reference(root, f"{traj} step{step}: digest {info['tensor_digest']} != "''',
     '''        want = battery_4.committed_step_digest_4(traj, step)
        if False:
            loaders["release"](model)
            loaders["free_step"](traj, step, cache_root=cache_root)
            _halt_reference(root, f"{traj} step{step}: digest {info['tensor_digest']} != "'''),
    (RF, "reference_4 run(): the init digest pin skipped",
     '''        want = battery_4.committed_init_digest_4(traj)
        if info["tensor_digest"] != want:''',
     '''        want = battery_4.committed_init_digest_4(traj)
        if False:'''),
    (RF, "reference_4 run(): eligibility is written even when `only` restricts the run",
     "    if eligibility_fn is not None and only is None:",
     "    if eligibility_fn is not None:"),

    # ----------------------------------------------------------- run/sweep_4.py
    (SW, "sweep_4 run(): the reference-seal requirement removed",
     "    require_reference_seal_4(root, tag_exists=tag_exists, blobs_bound=blobs_bound)\n"
     "    if not battery_4.eligibility_path(root).is_file():",
     "    if not battery_4.eligibility_path(root).is_file():"),
    (SW, "sweep_4 run(): the eligibility-record-present requirement removed",
     '''    if not battery_4.eligibility_path(root).is_file():
        raise RuntimeError(f"refusing: {battery_4.eligibility_path(root)} is not present")''',
     '''    if False:
        raise RuntimeError(f"refusing: {battery_4.eligibility_path(root)} is not present")'''),
    (SW, "sweep_4 run(): the power-record-present requirement removed",
     '''    if not battery_4.power_path(root).is_file():
        raise RuntimeError(f"refusing: {battery_4.power_path(root)} is not present")''',
     '''    if False:
        raise RuntimeError(f"refusing: {battery_4.power_path(root)} is not present")'''),
    (SW, "sweep_4 run(): the HALTED-for-this-trajectory guard removed",
     '''    if battery_4.halt_marker_path(root, traj).exists():
        raise RuntimeError(f"refusing: {traj} sweep is halted "''',
     '''    if False:
        raise RuntimeError(f"refusing: {traj} sweep is halted "'''),
    (SW, "sweep_4 run(): the first unit is not required complete before the rest run",
     '''    if not battery_4.unit_complete_4(root, (traj, first_step)):
        raise RuntimeError(f"refusing: {traj} step{first_step} (the reference stage's first "''',
     '''    if False:
        raise RuntimeError(f"refusing: {traj} step{first_step} (the reference stage's first "'''),
    (SW, "sweep_4 run_gate1(): the endpoint digest pin skipped",
     '    if got != want or got != ref_rec.get("tensor_digest"):',
     "    if False:"),
    (SW, "sweep_4 run(): the per-step digest pin skipped",
     '''        want = battery_4.committed_step_digest_4(traj, step)
        if info["tensor_digest"] != want:''',
     '''        want = battery_4.committed_step_digest_4(traj, step)
        if False:'''),

    # ------------------------------------------------------------- analyze_4.py
    (AN, "T_BAR_4 = 0.25 -> 0.2", "T_BAR_4 = 0.25", "T_BAR_4 = 0.2"),
    (AN, "ALPHA_4 = 0.01 -> 0.05", "ALPHA_4 = 0.01", "ALPHA_4 = 0.05"),
    (AN, "MIN_CELLS_4 = 3 -> 1", "MIN_CELLS_4 = 3", "MIN_CELLS_4 = 1"),
    (AN, "MIN_RUNGS_4 = 3 -> 1", "MIN_RUNGS_4 = 3", "MIN_RUNGS_4 = 1"),
    (AN, "SE_MULTIPLE_4 = 2.0 -> 1.0 (eligibility at 1x SE, not 2x)",
     "SE_MULTIPLE_4 = 2.0", "SE_MULTIPLE_4 = 1.0"),
    (AN, "MIN_CLEAR_INDEX_4 = 2 -> 1", "MIN_CLEAR_INDEX_4 = 2", "MIN_CLEAR_INDEX_4 = 1"),
    (AN, "GATE0_MIN_FRACTION_4 = 0.90 -> 0.5", "GATE0_MIN_FRACTION_4 = 0.90", "GATE0_MIN_FRACTION_4 = 0.5"),
    (AN, "cells_4: trend computed over R instead of flat",
     '        trend = trend_4(series["a"], rs["flat"], series["steps"])',
     '        trend = trend_4(series["a"], rs["R"], series["steps"])'),
    (AN, "phi_4: reads x[t_clear_index] instead of x[t_clear_index - 1]",
     "    return float(x[t_clear_index - 1] / x[-1])",
     "    return float(x[t_clear_index] / x[-1])"),
    (AN, "primary_4: sign flips applied per cell, not per rung",
     '''    S, method = _flip_signs(len(rungs), seed=seed)
    per_rung_sum = np.zeros(len(rungs)); np.add.at(per_rung_sum, rid, phi)
    T_flip = (S @ per_rung_sum) / len(cells)''',
     '''    S, method = _flip_signs(len(cells), seed=seed)
    T_flip = (S @ phi) / len(cells)'''),
    (AN, "primary_4: the bootstrap resamples individual cells, not whole rungs",
     '''    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(rungs), size=len(rungs))
        vals = np.concatenate([phi[rid == j] for j in pick])
        boots.append(vals.mean())''',
     '''    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(phi), size=len(phi))
        boots.append(phi[pick].mean())'''),
    (AN, "verdict_tree_4: PARTIAL and UNDETERMINED swapped",
     '''    if p < ALPHA_4 and 0 < T < T_BAR_4:
        return {"verdict": "PARTIAL", "reason": f"T {T:.4f} in (0, {T_BAR_4}), p+ {p:.4g} < {ALPHA_4} — real, below the bar"}
    if p >= ALPHA_4 and ci[1] < T_BAR_4:
        return {"verdict": "FOLLOWS", "reason": f"p+ {p:.4g} ≥ {ALPHA_4} and CI95 upper {ci[1]:.4f} < {T_BAR_4}"}
    return {"verdict": "UNDETERMINED", "reason": f"T {T:.4f}, p+ {p:.4g}, p− {primary['p_minus']:.4g}, CI95 {ci}"}''',
     '''    if p < ALPHA_4 and 0 < T < T_BAR_4:
        return {"verdict": "UNDETERMINED", "reason": f"T {T:.4f} in (0, {T_BAR_4}), p+ {p:.4g} < {ALPHA_4} — real, below the bar"}
    if p >= ALPHA_4 and ci[1] < T_BAR_4:
        return {"verdict": "FOLLOWS", "reason": f"p+ {p:.4g} ≥ {ALPHA_4} and CI95 upper {ci[1]:.4f} < {T_BAR_4}"}
    return {"verdict": "PARTIAL", "reason": f"T {T:.4f}, p+ {p:.4g}, p− {primary['p_minus']:.4g}, CI95 {ci}"}'''),
    (AN, "verdict_tree_4: the LEADS condition uses OR instead of AND",
     "    if p < ALPHA_4 and T >= T_BAR_4:",
     "    if p < ALPHA_4 or T >= T_BAR_4:"),
    (AN, "verdict_tree_4: NO-CONVERGENCE requires both bars low (and instead of or)",
     "    if n_eligible_cells < MIN_CELLS_4 or n_eligible_rungs < MIN_RUNGS_4:",
     "    if n_eligible_cells < MIN_CELLS_4 and n_eligible_rungs < MIN_RUNGS_4:"),
    (AN, "_flip_signs: sign values are (1, -2) instead of (+-1)",
     "    return (1 - 2 * bits).astype(np.int8), \"exact\"",
     "    return (1 - 3 * bits).astype(np.int8), \"exact\""),
    (AN, "per_item_alignment_4: the stored overlap is not cross-checked against the re-derivation",
     '''            stored_ov = (stored.get(ref) or {}).get(rung)
            if stored_ov is not None and not np.array_equal(stored_ov, ov):''',
     '''            stored_ov = (stored.get(ref) or {}).get(rung)
            if False:'''),
    (AN, "gate0_4/_gate0_site_means_4: averaged over references instead of kept per reference",
     '''        per_ref = {}
        for ref, pairing in pairing_by_ref.items():
            sq = ref_tables[ref][rung]
            ov = collect_4.overlap_table_4(sm, sq, pairing)      # [n_sites, 500] uint8
            per_ref[ref] = (ov.astype(np.float64) / metric_4.K_4).mean(axis=1)   # -> [n_sites]
        out[rung] = per_ref''',
     '''        per_ref = []
        for ref, pairing in pairing_by_ref.items():
            sq = ref_tables[ref][rung]
            ov = collect_4.overlap_table_4(sm, sq, pairing)      # [n_sites, 500] uint8
            per_ref.append(ov.astype(np.float64) / metric_4.K_4)
        stacked = np.stack(per_ref, axis=0)
        out[rung] = stacked.mean(axis=(0, 2))'''),
    (AN, "run(): gate 1's attested_sha_equal agreement not required",
     '''                if (not all(g1_der["sets_equal"].values())
                    or not all(g1_der["activation_sha_equal"].values())
                    or not all(g1_der["attested_sha_equal"].values())
                    or not g1_der["digest_equal"]):''',
     '''                if (not all(g1_der["sets_equal"].values())
                    or not all(g1_der["activation_sha_equal"].values())
                    or not g1_der["digest_equal"]):'''),
    (AN, "s2_known_answer_gates_4: 2d's AUC tolerance weakened from 1e-12 to 1e-1",
     '    if abs(auc_2d - 0.5454545454545454) >= 1e-12:',
     '    if abs(auc_2d - 0.5454545454545454) >= 1e-1:'),
    (AN, "s2_known_answer_gates_4: 2e's AUC tolerance weakened from 1e-12 to 1e-1",
     '    if abs(auc_2e - 0.6126482213438735) >= 1e-12:',
     '    if abs(auc_2e - 0.6126482213438735) >= 1e-1:'),
    (AN, "cells_4: the eligible flag is not checked, only presence",
     '''            e = elig.get(rung)
            if not e or not e.get("eligible"):
                continue''',
     '''            e = elig.get(rung)
            if not e:
                continue'''),
    (AN, "_compare_eligibility_4: the numeric tolerance weakened from 1e-12 to 1e-1",
     "        elif abs(float(a) - float(b)) > 1e-12:",
     "        elif abs(float(a) - float(b)) > 1e-1:"),
    (AN, "s1_order_4: concordant/discordant counts swapped",
     '''                if (dx > 0) == (dy > 0):
                    c += 1
                else:
                    d += 1''',
     '''                if (dx > 0) == (dy > 0):
                    d += 1
                else:
                    c += 1'''),
    (AN, "_eligibility_summary_4: counts every R rung, not only the eligible ones",
     '        n_eligible = sum(1 for e in r.values() if e.get("eligible"))',
     '        n_eligible = sum(1 for e in r.values())'),
    (AN, "gate0_4: the pass bar compares with > instead of >=",
     '           "pass": bool(fraction_below >= GATE0_MIN_FRACTION_4)}',
     '           "pass": bool(fraction_below > GATE0_MIN_FRACTION_4)}'),

    # -------------------------------------------------------------- power_4.py
    (PW, "_solve_m: phi* = 0 uses c_r + 1 instead of the disclosed c_r + 3",
     "        return float(c_r) + 3.0",
     "        return float(c_r) + 1.0"),
    (PW, "compute(): eligibility re-derived with the wrong SE multiple (1x instead of SE_MULTIPLE_4)",
     "                    ok = x_end_sim >= an.SE_MULTIPLE_4 * info[\"se_r\"]",
     "                    ok = x_end_sim >= 1.0 * info[\"se_r\"]"),
    (PW, "compute(): the declaration bar reads .5 instead of .75",
     '        declaration = "POWERED" if arms[decl_key]["P_LEADS"] >= 0.75 else "UNDERPOWERED IN ADVANCE"',
     '        declaration = "POWERED" if arms[decl_key]["P_LEADS"] >= 0.5 else "UNDERPOWERED IN ADVANCE"'),
    (PW, "main(): the ONCE guard (power record exists) removed",
     '''    if out_path.exists():
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")''',
     '''    if False:
        raise RuntimeError(f"{out_path} exists — the power record is written ONCE")'''),
]

# One mutant per collect_total_4(...) call site in analyze_4.py's run(),
# generated from the real, current source at import time.
M += _totality_mutants_4(AN)

FAST_TESTS = [str(L / "tests" / "test_metric_4.py"), str(L / "tests" / "test_battery_4.py"),
             str(L / "tests" / "test_collect_4.py"), str(L / "tests" / "test_stages_4.py"),
             str(L / "tests" / "test_analyze_4.py"), str(L / "tests" / "test_power_4.py")]
FAST_EXTRA_ARGS = ["-m", "not slow"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_4.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_4.py")]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp4" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """2k's Finding 3 lesson: a stray `.mutation_backup` anywhere under
    `experiments/exp4` means either a concurrent run is already in
    flight or a previous run crashed without restoring -- refuse
    before the baseline check even starts."""
    found = sorted((ROOT / "experiments" / "exp4").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp4 (a concurrent run, or a previous crash that "
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


def run_suite(tests, extra_args=None, timeout=None):
    """Returns `(ok, out, timed_out)`. A timeout is NOT a kill (the
    controller's ruling, review round 1): `subprocess.run(...,
    timeout=...)` kills the child itself on expiry (SIGKILL after the
    grace period) and raises `TimeoutExpired`, caught here and
    reported as `timed_out=True` with whatever partial stdout the
    child had produced — the caller must never fold this into either
    `ok` or `survived`."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    args = list(extra_args or [])
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                            *tests, *args], cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode == 0, r.stdout[-600:], False
    except subprocess.TimeoutExpired as e:
        partial = e.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode(errors="replace")
        return False, partial[-600:], True


def _parse_only(argv) -> set:
    for a in argv:
        if a.startswith("--only="):
            return {int(x) for x in a[len("--only="):].split(",") if x}
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 < len(argv):
            return {int(x) for x in argv[i + 1].split(",") if x}
    return None


def _parse_timeout(argv):
    """`--timeout=SECONDS` (review round 1, IMPORTANT 1): applied to
    EVERY `run_suite` call in this invocation, baseline included --
    used to bound a single pathological mutant (e.g. #38) without
    risking another multi-minute block of the whole harness. `None`
    (no bound) unless given."""
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
    ok, out, timed_out = run_suite(tests, extra, timeout=timeout)
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
    for i, (path, name, old, new) in enumerate(M, 1):
        if only is not None and i not in only:
            continue
        considered += 1
        src = path.read_text()
        if src.count(old) != 1:
            print(f"[{i:3d}] SKIP  {name}: target text not found exactly once in {path.name} "
                  f"(count={src.count(old)})")
            survivors.append((i, name, "target-not-found"))
            continue
        backup = _acquire_backup(path)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out, timed_out = run_suite(tests, extra, timeout=timeout)
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        if timed_out:
            print(f"[{i:3d}] TIMEOUT  {name}  (no verdict — not counted as killed or survived; "
                 f"a timeout is not a kill)", flush=True)
            timeouts.append((i, name, "timeout"))
            continue
        print(f"[{i:3d}] {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((i, name, "survived"))
    skipped = [s for s in survivors if s[2] == "target-not-found"]
    real = [s for s in survivors if s[2] == "survived"]
    killed = considered - len(survivors) - len(timeouts)
    print(f"\n{killed}/{considered} killed; "
          f"{len(real)} survivor(s): {real}; "
          f"{len(skipped)} SKIP (target text not found, stale mutant): {skipped}; "
          f"{len(timeouts)} TIMEOUT (not a kill, not a survivor): {timeouts}")
    return 1 if (survivors or timeouts) else 0


if __name__ == "__main__":
    sys.exit(main())
