# experiments/exp2l/tests/mutation_check.py
"""Mutation-test exp2l's OWN modules — battery_2l (the 13B inventory +
manifest, the loader family, the rung-set rule, the endpoint composite
sha, the record stamps, the gate-1 checkers, the pins/prereg binding),
run/endpoint_2l (both predictor seals, the rung set from stage1_final),
run/sweep_2l (gate 1, the endpoint seal, the grid + real step 0), and
analyze_2l (the two predictor loaders through their seals, the 13B
trees, the tree/disclosures, the import-surface scan, S4/S5, and every
`collect_total` call site in `run()`/`load_predictors_2l`, AST-generated
via 2i's own `_totality_mutants`, imported verbatim rather than
re-implemented). Everything upstream of 2l (2k/2i/2j/2g/2h/2d/2c/exp3/
exp3c/exp3d) is frozen instrument, pinned by `FROZEN_SHA256_2L` /
`FROZEN_IMPORT_SHA256_2G` / `IMPORTED_SHA256_2J` / `IMPORTED_SHA256_2K`,
and is not re-targeted here.

2k's/2j's precedent: run each mutant against the FAST modules only
(`test_battery_2l.py`, `test_stages_2l.py`, `test_analyze_2l.py` with
the three real-tree cases deselected — `test_run_on_empty_tree_is_
insufficient_never_raises`, `test_s4_matched_2l_uses_2k_rule_and_2j_
blocks`, `test_s5_answer_prior_2l_is_2j_functional_on_2i_rows` — they
take ≈ 95 s together and observe nothing a fast mutant changes). A
mutant that survives the fast modules is either closed with a new fast
test (preferred) or, when only a world/totality shape can observe the
behaviour it changes, recorded as 'killed by worlds/totality only'
after one targeted confirmation run under `--totality` or `--fullshape`
— see PROGRESS.md's Task 5 entry for which mutants took that path and
for any documented-equivalent mutant (a proof in the ledger, not
merely an assertion — 2j's `matched_k` clip precedent).

Mutates sources IN PLACE (with an exclusive `.mutation_backup`) and
restores them in `finally` — run alone, detached (nohup), never under
a foreground timeout, never concurrently with another mutation run
(both `--totality` and `--fullshape` mutate the SAME files by path)."""
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

L = ROOT / "experiments/exp2l"
BK = L / "battery_2l.py"
EP = L / "run" / "endpoint_2l.py"
SW = L / "run" / "sweep_2l.py"
AN = L / "analyze_2l.py"

M = [
    # -------------------------------------------------------- battery_2l.py
    (BK, "GRID_13B missing 576000",
     '''GRID_13B = (1000, 2000, 4000, 8000, 16000, 32000,
            64000, 128000, 192000, 256000, 320000, 384000, 448000, 512000, 576000,
            596057)''',
     '''GRID_13B = (1000, 2000, 4000, 8000, 16000, 32000,
            64000, 128000, 192000, 256000, 320000, 384000, 448000, 512000,
            596057)'''),
    (BK, "trained_steps_13b returns GRID_13B + (STEP0,) (step 0 leaks into an outcome)",
     '''def trained_steps_13b() -> tuple:
    return tuple(GRID_13B)''',
     '''def trained_steps_13b() -> tuple:
    return tuple(GRID_13B) + (STEP0,)'''),
    (BK, "build_manifest_13b: duplicate refusal `step != ENDPOINT_STEP_13B and same` -> `False and ...`",
     '        if step != ENDPOINT_STEP_13B and same:',
     '        if False and same:'),
    (BK, "build_manifest_13b: the endpoint-revision pin check removed",
     '''    if endpoint_entry["revision"] != REV_13B_ENDPOINT:
        raise ValueError(f"{REPO_13B}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_13B_ENDPOINT!r}")''',
     '''    if False:
        raise ValueError(f"{REPO_13B}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_13B_ENDPOINT!r}")'''),
    (BK, "build_manifest_13b: the step-0 pin check removed",
     '''    if entries[str(STEP0)]["revision"] != REV_13B_STEP0:
        raise ValueError(f"{REPO_13B}: step-0 revision {entries[str(STEP0)]['revision']!r} is "
                         f"not the pinned {REV_13B_STEP0!r}")''',
     '''    if False:
        raise ValueError(f"{REPO_13B}: step-0 revision {entries[str(STEP0)]['revision']!r} is "
                         f"not the pinned {REV_13B_STEP0!r}")'''),
    (BK, "load_manifest_13b: the frozen-grid check removed",
     '''    if obj.get("grid_13b") != list(GRID_13B) or obj.get("step0") != STEP0:
        raise ValueError(f"{path}: manifest is not the frozen 13B grid")''',
     '''    if False:
        raise ValueError(f"{path}: manifest is not the frozen 13B grid")'''),
    (BK, "rung_set_from_counts_2l: r in R_CAP_2K -> r in STRATA_RUNGS (doc slip (a)'s exact failure)",
     '    r_primary = tuple(r for r in r_13b if r in R_CAP_2K)',
     '    r_primary = tuple(r for r in r_13b if r in STRATA_RUNGS)'),
    (BK, "rung_set_from_counts_2l: R_ELEVEN_EXTRA computed without `not in R_CAP_2K`",
     '    r_eleven_extra = tuple(r for r in r_13b if r in STRATA_RUNGS and r not in R_CAP_2K)',
     '    r_eleven_extra = tuple(r for r in r_13b if r in STRATA_RUNGS)'),
    (BK, "rung_set_from_counts_2l: primary_is_the_nine -> True",
     '            "primary_is_the_nine": tuple(r_primary) == tuple(sorted(R_CAP_2K)),',
     '            "primary_is_the_nine": True,'),
    (BK, "endpoint_files: missing-file raise removed",
     '''    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(str(p))''',
     '''    for p in paths:
        if False:
            raise FileNotFoundError(str(p))'''),
    (BK, "composite_sha: unsorted",
     '    lines = "\\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))',
     '    lines = "\\n".join(f"{rel} {sha}" for rel, sha in files.items())'),
    (BK, "item_record_2l: seal_tag ENDPOINT_SEAL_TAG_2L -> PREDICTOR_TAGS_2L",
     '                         seal={"tag": ENDPOINT_SEAL_TAG_2L, "sha256": PREDICTOR_SHA_2L},',
     '                         seal={"tag": PREDICTOR_TAGS_2L, "sha256": PREDICTOR_SHA_2L},'),
    (BK, "item_record_2l: endpoint_sha256 key dropped from the record",
     '''    rec["endpoint_sha256"] = endpoint_sha
    return rec''',
     '''    _ = endpoint_sha
    return rec'''),
    (BK, "checkpoint_record_2l: size SIZE_OUT -> bi.SIZE_OUT",
     '    return {"family": FAMILY, "size": SIZE_OUT, "step": int(step),',
     '    return {"family": FAMILY, "size": bi.SIZE_OUT, "step": int(step),'),
    (BK, "gate1_failures_13b: nc.get(r) != N_ITEMS -> <",
     '        if nc.get(r) != N_ITEMS:',
     '        if nc.get(r) is not None and nc.get(r) < N_ITEMS:'),
    (BK, "gate1_failures_13b: bd.get(r) != 0 removed",
     '        if bd.get(r) != 0:',
     '        if False:'),
    (BK, "gate1_failures_13b: digest check removed",
     '    if not dg_s or not dg_e or dg_s != dg_e:',
     '    if False:'),
    (BK, "gate1_failures_13b: prereg_tag check removed",
     '    if rec.get("prereg_tag") != PREREG_TAG_2L:',
     '    if False:'),
    (BK, "gate1_rederive_13b: attested-vs-re-derived bit_diffs check removed",
     '        if bd_att.get(r) != bit_diff:',
     '        if False:'),
    (BK, "gate1_rederive_13b: coverage len(s_bits) != N_ITEMS -> <",
     '                len(s_bits) != N_ITEMS or len(e_bits) != N_ITEMS:',
     '                len(s_bits) < N_ITEMS or len(e_bits) != N_ITEMS:'),
    (BK, "predictor_sha_2l: separator | -> '' (a different composite)",
     '    return hashlib.sha256(f"{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()',
     '    return hashlib.sha256(f"{seal_2k_sha}{seal_2i_sha}".encode()).hexdigest()'),
    (BK, "require_prereg_2l: want != got -> ==",
     '        if want != got:',
     '        if want == got:'),
    (BK, "check_frozen_2l: drift check removed",
     '        if got != want:',
     '        if False:'),
    (BK, "clean_dir_13b: config.to_json_file line removed (2i stop #1)",
     '''    config.to_json_file(str(d / "config.json"))
    return d''',
     '''    return d'''),
    # -------------------------------------------------------- run/endpoint_2l.py
    (EP, "require_predictor_seals_2l: the 2i-seal literal check removed",
     '''    if seal_2i.get("sha256") != bl.SEAL_2I_SHA256:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bl.SEAL_2I_SHA256!r}")''',
     '''    if False:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bl.SEAL_2I_SHA256!r}")'''),
    (EP, "require_predictor_seals_2l: the 2k-seal literal check removed",
     '''    if seal_2k.get("sha256") != bl.SEAL_2K_SHA256:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bl.SEAL_2K_SHA256!r}")''',
     '''    if False:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bl.SEAL_2K_SHA256!r}")'''),
    (EP, "require_predictor_seals_2l: the composite re-derivation check removed",
     '''    if psha != bl.PREDICTOR_SHA_2L:
        raise RuntimeError("refusing: PREDICTOR_SHA_2L does not re-derive from the two seals")''',
     '''    if False:
        raise RuntimeError("refusing: PREDICTOR_SHA_2L does not re-derive from the two seals")'''),
    (EP, "run: rung_set_from_counts_2l fed main's counts instead of stage1_final's",
     '''                if which == "stage1_final":
                    stage1_final[rung] = rec''',
     '''                if which == "main":
                    stage1_final[rung] = rec'''),
    (EP, "run: seal_tag stamped ENDPOINT_SEAL_TAG_2L instead of PREDICTOR_TAGS_2L",
     '    seal_ref = {"tag": bl.PREDICTOR_TAGS_2L, "sha256": seals["predictor_sha"]}',
     '    seal_ref = {"tag": bl.ENDPOINT_SEAL_TAG_2L, "sha256": seals["predictor_sha"]}'),
    # -------------------------------------------------------- run/sweep_2l.py
    (SW, "run_gate1: the HALTED marker is no longer written on a gate-1 fire",
     '''    if bad:
        bl.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        bl.halt_marker_path(out_root).write_text("\\n".join(bad) + "\\n")
        raise RuntimeError(f"gate 1 olmo13b FAILED — halted: {bad[:3]}")''',
     '''    if bad:
        bl.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        raise RuntimeError(f"gate 1 olmo13b FAILED — halted: {bad[:3]}")'''),
    (SW, "run_gate1: bit_diffs comparison inverted (a != b -> a == b)",
     '            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a != b))',
     '            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a == b))'),
    (SW, "records_complete_13b: checkpoint-record requirement removed",
     '''    if not all(bl.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return bl.checkpoint_record_path(out_root, step).exists()''',
     '''    if not all(bl.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return True'''),
    (SW, "run_step: free called with entry['commit'] instead of entry['revision']",
     '''    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)
    print(f"[2l sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)''',
     '''    finally:
        _release(model)
        loaders["free"](entry["commit"], cache_root)
    print(f"[2l sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)'''),
    (SW, "run: step 0 dropped from rest",
     '    rest = (bl.STEP0,) + tuple(s for s in bl.GRID_13B if s != bl.ENDPOINT_STEP_13B)',
     '    rest = tuple(s for s in bl.GRID_13B if s != bl.ENDPOINT_STEP_13B)'),
    (SW, "run: require_endpoint_seal_2l removed from run",
     '''    require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2l(out_root, blobs_bound=blobs_bound)
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)''',
     '''    require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)'''),
    (SW, "run: endpoint_sha computed BEFORE the endpoint seal binds (reorder) — "
         "documented-equivalent candidate, prove or kill",
     '''    prereg = bl.require_prereg_2l(tag_exists=tag_exists, blob_sha=blob_sha)
    bl.check_frozen_2l()
    require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2l(out_root, blobs_bound=blobs_bound)
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    if bl.halt_marker_path(out_root).exists():
        raise RuntimeError(f"olmo13b: the sweep is halted ({bl.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bl.STEP0,) + tuple(s for s in bl.GRID_13B if s != bl.ENDPOINT_STEP_13B)
    pending = [s for s in rest if not records_complete_13b(out_root, s)]
    gate_done = bl.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2l sweep] prereg tag {prereg['tag']!r}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    endpoint_sha = bl.endpoint_sha256(out_root)''',
     '''    prereg = bl.require_prereg_2l(tag_exists=tag_exists, blob_sha=blob_sha)
    bl.check_frozen_2l()
    endpoint_sha = bl.endpoint_sha256(out_root)
    require_predictor_seals_2l(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2l(out_root, blobs_bound=blobs_bound)
    manifest = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    if bl.halt_marker_path(out_root).exists():
        raise RuntimeError(f"olmo13b: the sweep is halted ({bl.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bl.STEP0,) + tuple(s for s in bl.GRID_13B if s != bl.ENDPOINT_STEP_13B)
    pending = [s for s in rest if not records_complete_13b(out_root, s)]
    gate_done = bl.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2l sweep] prereg tag {prereg['tag']!r}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()'''),
    (SW, "run: the resume gate-1 re-check removed",
     '''    else:
        bad = bl.gate1_failures_13b(json.loads(g1.read_text()), _load_stage1_final(out_root))
        if bad:
            raise RuntimeError(f"gate 1 olmo13b record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_13b(out_root, bl.ENDPOINT_STEP_13B):''',
     '''    else:
        if not records_complete_13b(out_root, bl.ENDPOINT_STEP_13B):'''),
    # -------------------------------------------------------------- analyze_2l.py
    (AN, "verdict_2l: THIN threshold < 3 -> < 2",
     '    if len(r_primary) < 3:',
     '    if len(r_primary) < 2:'),
    (AN, "verdict_2l: the UNDERPOWERED disclosure condition not res['fires'] -> res['fires']",
     '        if not res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":',
     '        if res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":'),
    (AN, "_licensed_2l: disclosures dropped",
     '    if tree.get("disclosures"):',
     '    if False:'),
    (AN, "load_power_2l: n_trained_steps check removed",
     '''        if sub.get("n_trained_steps") != bl.n_trained_13b():
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bl.n_trained_13b()}")''',
     '''        if False:
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bl.n_trained_13b()}")'''),
    (AN, "load_power_2l: block_sd_A presence check removed",
     '''    bsd = rec.get("block_sd_A")
    if not isinstance(bsd, dict) or any(k not in bsd for k in BLOCK_SD_FIELDS_2L):
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — "
                         f"{BLOCK_SD_FIELDS_2L}")''',
     '''    bsd = rec.get("block_sd_A")
    if False:
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — "
                         f"{BLOCK_SD_FIELDS_2L}")'''),
    (AN, "load_power_2l: predictor_sha256 check removed",
     '''    if rec.get("predictor_sha256") != predictor_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")''',
     '''    if False:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")'''),
    (AN, "load_power_2l: rungs != -> subset (a superset of R_PRIMARY silently accepted)",
     '        if not isinstance(sub.get("rungs"), list) or set(sub["rungs"]) != set(r_primary):',
     '        if not isinstance(sub.get("rungs"), list) or not set(r_primary).issubset(set(sub["rungs"])):'),
    (AN, "check_power_claims_2l: B's strata -> base strata",
     '    for test, x, s in (("A", x_a256, strata), ("B", x_b, strata_b)):',
     '    for test, x, s in (("A", x_a256, strata), ("B", x_b, strata)):'),
    (AN, "check_power_claims_2l: n_pos_lower_bound check removed",
     '        if "n_pos_lower_bound" in prim:',
     '        if False:'),
    (AN, "_record_common_failures_2l: predictor_sha check removed",
     '''    if rec.get("predictor_sha") != bl.PREDICTOR_SHA_2L:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bl.PREDICTOR_SHA_2L}")''',
     '''    if False:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bl.PREDICTOR_SHA_2L}")'''),
    (AN, "_record_common_failures_2l: size expected bl.SIZE_OUT -> bi.SIZE_OUT",
     '    for k, v in (("size", bl.SIZE_OUT), ("family", bl.FAMILY), ("n", bt.N_ITEMS),',
     '    for k, v in (("size", bi.SIZE_OUT), ("family", bl.FAMILY), ("n", bt.N_ITEMS),'),
    (AN, "step_record_failures_2l: endpoint_sha256 check removed",
     '''    if rec.get("endpoint_sha256") != endpoint_sha:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")''',
     '''    if False:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")'''),
    (AN, "step_record_failures_2l: commit check removed",
     '''    if rec.get("commit") != entry["commit"]:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")''',
     '''    if False:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")'''),
    (AN, "load_sweep_13b: steps default without STEP0",
     '    steps = tuple(steps) if steps is not None else bl.GRID_13B + (bl.STEP0,)',
     '    steps = tuple(steps) if steps is not None else bl.GRID_13B'),
    (AN, "load_sweep_13b: LFS sha check removed",
     '''        for name, want in entry.get("lfs_sha256", {}).items():
            if crec.get("sha256", {}).get(name) != want:
                raise ValueError(f"olmo13b/step{step}: downloaded {name} sha "
                                 f"{crec.get('sha256', {}).get(name)} != manifest {want}")''',
     '''        for name, want in entry.get("lfs_sha256", {}).items():
            if False:
                raise ValueError(f"olmo13b/step{step}: downloaded {name} sha "
                                 f"{crec.get('sha256', {}).get(name)} != manifest {want}")'''),
    (AN, "outcomes_13b: steps -> GRID_13B + (STEP0,) (step 0 leaks into an outcome)",
     '''def outcomes_13b(sweep: dict, *, rungs=None) -> dict:
    """`analyze_2i.outcomes_7b`'s body over `trained_steps_13b()` (16
    points). Step 0 is never in an outcome: `steps` excludes it even
    though `sweep` carries it."""
    steps = bl.trained_steps_13b()''',
     '''def outcomes_13b(sweep: dict, *, rungs=None) -> dict:
    """`analyze_2i.outcomes_7b`'s body over `trained_steps_13b()` (16
    points). Step 0 is never in an outcome: `steps` excludes it even
    though `sweep` carries it."""
    steps = bl.GRID_13B + (bl.STEP0,)'''),
    (AN, "_load_rung_set_2l: subset-of-nine check removed",
     '''    if not set(rec["R_PRIMARY"]).issubset(set(bl.R_CAP_2K)):
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")''',
     '''    if False:
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")'''),
    (AN, "_load_rung_set_2l: partition check removed",
     '''    if set(rec["R_PRIMARY"]) | set(rec["R_ELEVEN_EXTRA"]) | set(rec["R_EXTRA"]) != set(rec["R_13B"]):
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_13B")''',
     '''    if False:
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_13B")'''),
    (AN, "_check_rung_set_derivation_2l: per-key comparison -> set equality (order-blind)",
     '        if got != want:',
     '        if set(got) != set(want):'),
    (AN, "load_predictors_2l: the 2k-seal literal check removed",
     '''    if isinstance(seal_2k, dict) and seal_2k.get("sha256") != bl.SEAL_2K_SHA256:
        failures.append(f"2l predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")''',
     '''    if False:
        failures.append(f"2l predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")'''),
    (AN, "load_predictors_2l: the 2i-seal literal check removed",
     '''    if isinstance(seal_2i, dict) and seal_2i.get("sha256") != bl.SEAL_2I_SHA256:
        failures.append(f"2l predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")''',
     '''    if False:
        failures.append(f"2l predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")'''),
    (AN, "load_predictors_2l: the seal_failures_2k call removed",
     '''        if seal_2k is not None and all(len(cells_2k.get(s, {})) == len(bl.R_CAP_2K) for s in bk.SIZES_2K):''',
     '''        if False and all(len(cells_2k.get(s, {})) == len(bl.R_CAP_2K) for s in bk.SIZES_2K):'''),
    (AN, "load_predictors_2l: the _check_predictor_counts_2i call removed",
     '    if seal_2i is not None and records_2i is not None and x_b is not None:',
     '    if False:'),
    (AN, "load_predictors_2l: R_CAP == nine check removed",
     '''    if rs2i is not None and tuple(sorted(rs2i["R_CAP"])) != tuple(sorted(bl.R_CAP_2K)):
        failures.append(f"2l predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")''',
     '''    if False:
        failures.append(f"2l predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")'''),
    (AN, "load_predictors_2l: x_B bits do not reproduce raise removed",
     '''            if fn.counts_from_bits(bits[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")''',
     '''            if False:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")'''),
    (AN, "run()/_core: Test B strata -> base strata (drops the median-bucket conditioning)",
     '            B = _run_test(x_b, bi.SIZE_PRED, out, strata_b, r_primary, n_perm=n_perm, n_boot=n_boot)',
     '            B = _run_test(x_b, bi.SIZE_PRED, out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)'),
    (AN, "run()/_core: Test A predictor -> counts[64] instead of counts[K_TOTAL]",
     '            x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL] for r in r_primary}',
     '            x256 = {r: cells_2k["1b"][r]["counts"][64] for r in r_primary}'),
    (AN, "load_predictors_2l: the halt-marker scan removed",
     '''    for m in bk.halt_markers(root_2k):
        failures.append(f"2l predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")''',
     '''    for m in []:
        failures.append(f"2l predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")'''),
    (AN, "check_imports_2l: 'tests' in rp.parts swallows everything -> True",
     '        if not s.startswith(_EXPERIMENTS_ROOT_2L + "/") or "tests" in rp.parts:',
     '        if not s.startswith(_EXPERIMENTS_ROOT_2L + "/") or True:'),
    (AN, "s4_matched_2l: increment sign flipped",
     '''    return {"per_rung": per, "thinned_B": {"T": t_b}, "T_A256": t_a["T"],
            "increment": (None if t_b is None or t_a["T"] is None else t_b - t_a["T"])}''',
     '''    return {"per_rung": per, "thinned_B": {"T": t_b}, "T_A256": t_a["T"],
            "increment": (None if t_b is None or t_a["T"] is None else t_a["T"] - t_b)}'''),
    (AN, "s5_answer_prior_2l: non_gating True -> False",
     '            "non_gating": True,',
     '            "non_gating": False,'),
    (AN, "collapses_13b: threshold >= -> >",
     '            if n >= threshold:',
     '            if n > threshold:'),
    # ------------------------------------------------- freeze closures
    (AN, "F-2: checkpoint_record_failures_2l revision/commit check removed",
     '''    for k in ("revision", "commit"):
        if crec.get(k) != entry.get(k):''',
     '''    for k in ():
        if crec.get(k) != entry.get(k):'''),
    (AN, "F-2: checkpoint_record_failures_2l candidate-file coverage check removed",
     '        uncovered = sorted(set(entry.get("files", [])) - set(shas))',
     '        uncovered = sorted(set(entry.get("lfs_sha256", {})) - set(shas))'),
    (AN, "F-2: checkpoint_record_failures_2l digest coherence check removed",
     '    off = sorted(r for r, rec in step_records.items() if rec.get("weight_sha256") != dg)',
     '    off = []'),
    (AN, "F-2: load_sweep_13b does not raise on the checkpoint-record failures",
     '''        cbad = checkpoint_record_failures_2l(crec, step=step, entry=entry, step_records=out[step])
        if cbad:''',
     '''        cbad = checkpoint_record_failures_2l(crec, step=step, entry=entry, step_records=out[step])
        if False:'''),
    (AN, "F-3: _check_rung_set_endpoint_shas_2l per-file comparison removed",
     '''    for rel in sorted(set(want) & set(got)):
        if got[rel] != want[rel]:''',
     '''    for rel in sorted(set(want) & set(got)):
        if False:'''),
    (AN, "F-3: _check_rung_set_endpoint_shas_2l coverage check removed",
     '''    if missing:
        bad.append(f"rung set olmo13b: endpoint_file_sha256 attests nothing for {missing}")''',
     '''    if False:
        bad.append(f"rung set olmo13b: endpoint_file_sha256 attests nothing for {missing}")'''),
    (AN, "F-4: _thin_eligible_2l never fires (len(elig) >= 3 -> >= 0)",
     '    if len(elig) >= 3:',
     '    if len(elig) >= 0:'),
    (AN, "F-1: the post-secondaries import re-check does not refuse",
     '''        if f:
            failures += f
            referents["failures"] = list(failures)
            t2 = verdict_2l(failures, None, None, None, ())''',
     '''        if False:
            failures += f
            referents["failures"] = list(failures)
            t2 = verdict_2l(failures, None, None, None, ())'''),
]

# One mutant per collect_total(...) call site in analyze_2l.py's run() AND
# load_predictors_2l, generated from the real, current source at import
# time rather than hand-picked (2j's Finding 4 lesson, applied at build
# time by 2k and 2l alike — this file has several functions with
# collect_total sites, not one, and _totality_mutants walks the whole
# file).
M += _totality_mutants(AN)

# Task 5 ruling: fast modules only by default (test_battery_2l.py,
# test_stages_2l.py, test_analyze_2l.py with the three real-tree cases
# deselected — they take ≈ 95 s and observe nothing a fast mutant
# changes). A `--totality` flag switches the covering suite to
# TOTALITY_TESTS (test_totality_2l.py alone, ≈ 3 min) so a
# totality-only kill is reproducible from the committed harness, not a
# scratch script; `--fullshape` switches to test_full_shape_2l.py
# (≈ 7 min) for the handful of shapes only a synthetic-13B-tree world
# can observe (the endpoint-composite/gate-1/power-record byte-level
# corruptions).
FAST_TESTS = [str(L / "tests" / "test_battery_2l.py"), str(L / "tests" / "test_stages_2l.py"),
             str(L / "tests" / "test_analyze_2l.py")]
FAST_EXTRA_ARGS = ["-m", "not slow", "-k",
                  "not test_run_on_empty_tree and not test_s4 and not test_s5"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_2l.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_2l.py")]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2l" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """2k's Finding 3 lesson, applied from commit one: a stray
    `.mutation_backup` anywhere under `experiments/exp2l` means either a
    concurrent run is already in flight or a previous run crashed
    without restoring — either way, starting a NEW run on top of it
    corrupts the restore. Refuse before the baseline check even
    starts."""
    found = sorted((ROOT / "experiments" / "exp2l").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp2l (a concurrent run, or a previous crash that "
                           f"never restored) — resolve by hand before starting a new run: {found}")


def _acquire_backup(path):
    """Exclusive-create `path`'s `.mutation_backup` (`open(..., 'xb')`):
    a second, concurrent `mutation_check.py` targeting the SAME path
    refuses immediately instead of racing this run's own restore-then-
    delete cycle."""
    backup = path.with_suffix(path.suffix + ".mutation_backup")
    try:
        with open(backup, "xb") as f:
            f.write(path.read_bytes())
    except FileExistsError:
        raise RuntimeError(f"refusing: {backup} already exists — a concurrent mutation_check.py "
                           f"run may be in flight against {path.name} (or a previous run crashed "
                           f"without restoring); resolve it by hand before retrying")
    return backup


def run_suite(tests, extra_args=None):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    args = list(extra_args or [])
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        *tests, *args], cwd=ROOT, env=env, capture_output=True, text=True)
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
    fullshape = "--fullshape" in argv
    if fullshape:
        tests, extra = FULLSHAPE_TESTS, []
    elif totality:
        tests, extra = TOTALITY_TESTS, []
    else:
        tests, extra = FAST_TESTS, FAST_EXTRA_ARGS
    only = _parse_only(argv)

    _refuse_if_any_backup_exists()
    clear_pycache()
    ok, out = run_suite(tests, extra)
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    label = "fullshape" if fullshape else ("totality" if totality else "fast")
    print(f"baseline OK ({label} pass, "
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
        backup = _acquire_backup(path)
        try:
            path.write_text(src.replace(old, new))
            clear_pycache()
            ok, out = run_suite(tests, extra)
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        print(f"[{i:2d}] {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((i, name, "survived"))
    skipped = [s for s in survivors if s[2] == "target-not-found"]
    real = [s for s in survivors if s[2] == "survived"]
    print(f"\n{considered - len(survivors)}/{considered} killed; "
          f"{len(real)} survivor(s): {real}; "
          f"{len(skipped)} SKIP (target text not found, stale mutant): {skipped}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
