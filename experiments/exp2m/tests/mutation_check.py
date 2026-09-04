# experiments/exp2m/tests/mutation_check.py
"""Mutation-test exp2m's OWN modules — battery_2m (the SmolLM3 grid +
two-repo manifest, the loader family and its tokenizer pins, the
rung-set rule, the endpoint composite sha, the record stamps and the
dtype override, the gate-1 checkers, the pins/prereg binding),
run/endpoint_2m (both predictor seals, the three whichs, the rung set
from stage1_final), run/sweep_2m (gate 1, the endpoint seal, the twin,
the grid), and analyze_2m (the two predictor loaders through their
seals, the SmolLM3 trees, the tree/disclosures, the import-surface
scan, S3/S4/S5/S8, and every `collect_total` call site in `run()`/
`load_predictors_2m`, AST-generated via 2i's own `_totality_mutants`,
imported verbatim rather than re-implemented). Everything upstream of
2m (2l/2k/2j/2i/2g/2h/2d/2c/exp3/exp3c/exp3d) is frozen instrument,
pinned by `FROZEN_SHA256_2M` / `FROZEN_IMPORT_SHA256_2G` /
`IMPORTED_SHA256_2J` / `IMPORTED_SHA256_2K` / `IMPORTED_SHA256_2L`, and
is not re-targeted here.

2l's/2k's/2j's precedent: run each mutant against the FAST modules only
(`test_battery_2m.py`, `test_stages_2m.py`, `test_analyze_2m.py` with
the real-tree cases deselected — they take minutes together and observe
nothing a fast mutant changes). A mutant that survives the fast modules
is either closed with a new fast test (preferred) or, when only a
world/totality shape can observe the behaviour it changes, recorded as
'killed by worlds/totality only' after one targeted confirmation run
under `--totality` or `--fullshape` — see PROGRESS.md's Task 5 entry
for which mutants took that path and for any documented-equivalent
mutant (a proof in the ledger, not merely an assertion — 2j's
`matched_k` clip precedent).

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

L = ROOT / "experiments/exp2m"
BK = L / "battery_2m.py"
EP = L / "run" / "endpoint_2m.py"
SW = L / "run" / "sweep_2m.py"
AN = L / "analyze_2m.py"

M = [
    # -------------------------------------------------------- battery_2m.py
    (BK, "GRID_3B missing 3200000",
     '''GRID_3B = (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000, 400000,
           600000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000, 2200000,
           2400000, 2600000, 2800000, 3000000, 3200000, 3400000, 3440000)''',
     '''GRID_3B = (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000, 400000,
           600000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000, 2200000,
           2400000, 2600000, 2800000, 3000000, 3400000, 3440000)'''),
    (BK, "LOG_HEAD_SUBSET_2M with 120000 added (no longer 2i's log-head shape)",
     '''LOG_HEAD_SUBSET_2M = (40000, 80000, 160000, 320000, 400000, 600000, 800000, 1000000, 1200000,
                      1400000, 1600000, 1800000, 2000000, 2200000, 2400000, 2600000, 2800000,
                      3000000, 3200000, 3400000, 3440000)''',
     '''LOG_HEAD_SUBSET_2M = (40000, 80000, 120000, 160000, 320000, 400000, 600000, 800000, 1000000,
                      1200000, 1400000, 1600000, 1800000, 2000000, 2200000, 2400000, 2600000,
                      2800000, 3000000, 3200000, 3400000, 3440000)'''),
    (BK, "trained_steps_3b returns GRID_3B + (TWIN,) (the twin leaks into an outcome)",
     '''def trained_steps_3b() -> tuple:
    return tuple(GRID_3B)''',
     '''def trained_steps_3b() -> tuple:
    return tuple(GRID_3B) + (TWIN,)'''),
    (BK, "build_manifest_3b: duplicate refusal `step != ENDPOINT_STEP_2M and same` -> `False and ...`",
     '        if step != ENDPOINT_STEP_2M and same:',
     '        if False and same:'),
    (BK, "build_manifest_3b: the endpoint-revision pin check removed",
     '''    if endpoint_entry["revision"] != REV_ENDPOINT_2M:
        raise ValueError(f"{REPO_CKPT}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_ENDPOINT_2M!r}")''',
     '''    if False:
        raise ValueError(f"{REPO_CKPT}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_ENDPOINT_2M!r}")'''),
    (BK, "build_manifest_3b: the stage-3 duplicate refusal removed",
     '''    same3 = dups_of(REV_STAGE3_FINAL_2M)
    if same3:''',
     '''    same3 = dups_of(REV_STAGE3_FINAL_2M)
    if False:'''),
    (BK, "build_manifest_3b: the twin's config_commit -> 'main'",
     '            "seed": TWIN_SEED, "config_commit": endpoint_entry["commit"]}',
     '            "seed": TWIN_SEED, "config_commit": "main"}'),
    (BK, "load_manifest_3b: the frozen-grid check removed",
     '''    if obj.get("grid_3b") != list(GRID_3B) or obj.get("log_head_subset") != list(LOG_HEAD_SUBSET_2M) \\
            or not isinstance(obj.get("twin"), dict) or obj["twin"].get("kind") != "from_config":
        raise ValueError(f"{path}: manifest is not the frozen SmolLM3 grid")''',
     '''    if False:
        raise ValueError(f"{path}: manifest is not the frozen SmolLM3 grid")'''),
    (BK, "entry_3b: the twin branch reads entries_3b['twin'] instead of the twin entry",
     '''    if step == TWIN:
        e = manifest.get("twin")''',
     '''    if step == TWIN:
        e = manifest.get("entries_3b", {}).get("twin")'''),
    (BK, "rung_set_from_counts_2m: r in R_CAP_2K -> r in STRATA_RUNGS",
     '    r_primary = tuple(r for r in r_3b if r in R_CAP_2K)',
     '    r_primary = tuple(r for r in r_3b if r in STRATA_RUNGS)'),
    (BK, "rung_set_from_counts_2m: R_ELEVEN_EXTRA computed without `not in R_CAP_2K`",
     '    r_eleven_extra = tuple(r for r in r_3b if r in STRATA_RUNGS and r not in R_CAP_2K)',
     '    r_eleven_extra = tuple(r for r in r_3b if r in STRATA_RUNGS)'),
    (BK, "rung_set_from_counts_2m: primary_is_the_nine -> True",
     '            "primary_is_the_nine": tuple(r_primary) == tuple(sorted(R_CAP_2K)),',
     '            "primary_is_the_nine": True,'),
    (BK, "endpoint_files: missing-file raise removed",
     '''    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(str(p))
        out[str(p.relative_to(root))] = bg.sha256_file(p)''',
     '''    for p in paths:
        if False:
            raise FileNotFoundError(str(p))
        out[str(p.relative_to(root))] = bg.sha256_file(p)'''),
    (BK, "endpoint_files: only two whichs (the base's 34 records leave the composite)",
     '''    paths = [rung_set_path(root), power_path(root)]
    for which in ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            paths.append(endpoint_record_path(root, which, r))''',
     '''    paths = [rung_set_path(root), power_path(root)]
    for which in ("stage1_final", "stage3_final"):
        for r in bt.RUNGS:
            paths.append(endpoint_record_path(root, which, r))'''),
    (BK, "composite_sha: unsorted",
     '    lines = "\\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))',
     '    lines = "\\n".join(f"{rel} {sha}" for rel, sha in files.items())'),
    (BK, "item_record_2m: seal_tag ENDPOINT_SEAL_TAG_2M -> PREDICTOR_TAGS_2M",
     '                         seal={"tag": ENDPOINT_SEAL_TAG_2M, "sha256": PREDICTOR_SHA_2M},',
     '                         seal={"tag": PREDICTOR_TAGS_2M, "sha256": PREDICTOR_SHA_2M},'),
    (BK, "item_record_2m: endpoint_sha256 key dropped from the record",
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2M
    return rec''',
     '''    _ = endpoint_sha
    rec["dtype"] = DTYPE_2M
    return rec'''),
    (BK, "item_record_2m: the dtype override removed",
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2M
    return rec''',
     '''    rec["endpoint_sha256"] = endpoint_sha
    return rec'''),
    (BK, "endpoint_item_record_2m: the dtype override removed",
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2M
    return rec''',
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    return rec'''),
    (BK, "checkpoint_record_2m: size SIZE_OUT -> bi.SIZE_OUT",
     '    return {"family": FAMILY, "size": SIZE_OUT, "step": int(step), "repo": info.get("repo"),',
     '    return {"family": FAMILY, "size": bi.SIZE_OUT, "step": int(step), "repo": info.get("repo"),'),
    (BK, "twin_checkpoint_record_2m: commit None -> ''",
     '            "revision": TWIN, "commit": None, "kind": "from_config", "seed": int(info["seed"]),',
     '            "revision": TWIN, "commit": "", "kind": "from_config", "seed": int(info["seed"]),'),
    (BK, "gate1_failures_3b: nc.get(r) != N_ITEMS -> <",
     '        if nc.get(r) != N_ITEMS:',
     '        if nc.get(r) is not None and nc.get(r) < N_ITEMS:'),
    (BK, "gate1_failures_3b: bd.get(r) != 0 removed",
     '        if bd.get(r) != 0:',
     '        if False:'),
    (BK, "gate1_failures_3b: digest check removed",
     '    if not dg_s or not dg_e or dg_s != dg_e:',
     '    if False:'),
    (BK, "gate1_failures_3b: prereg_tag check removed",
     '    if rec.get("prereg_tag") != PREREG_TAG_2M:',
     '    if False:'),
    (BK, "gate1_rederive_3b: attested-vs-re-derived bit_diffs check removed",
     '        if bd_att.get(r) != bit_diff:',
     '        if False:'),
    (BK, "gate1_rederive_3b: coverage len(s_bits) != N_ITEMS -> <",
     '                len(s_bits) != N_ITEMS or len(e_bits) != N_ITEMS:',
     '                len(s_bits) < N_ITEMS or len(e_bits) != N_ITEMS:'),
    (BK, "predictor_sha_2m: the '2m|' prefix dropped (2l's composite of the same two seals)",
     '    return hashlib.sha256(f"2m|{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()',
     '    return hashlib.sha256(f"{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()'),
    (BK, "require_prereg_2m: want != got -> ==",
     '        if want != got:',
     '        if want == got:'),
    (BK, "check_frozen_2m: drift check removed",
     '        if got != want:',
     '        if False:'),
    (BK, "clean_dir_3b: config.to_json_file line removed (2i stop #1)",
     '''    config.to_json_file(str(d / "config.json"))
    return d''',
     '''    return d'''),
    (BK, "check_tokenizer_2m: the pad-id check removed",
     '    if pad_id != PAD_TOKEN_ID_2M:',
     '    if False:'),
    (BK, "check_tokenizer_2m: the eos-id check removed",
     '    if eos_id != EOS_TOKEN_ID_2M:',
     '    if False:'),
    (BK, "check_tokenizer_2m: the prepended-special (BOS) check removed",
     '    if first_id in specials:',
     '    if False:'),
    (BK, "load_tokenizer_3b: padding_side 'left' -> 'right'",
     '    tok.padding_side = "left"',
     '    tok.padding_side = "right"'),
    # -------------------------------------------------------- run/endpoint_2m.py
    (EP, "require_predictor_seals_2m: the 2i-seal literal check removed",
     '''    if seal_2i.get("sha256") != bm.SEAL_2I_SHA256:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bm.SEAL_2I_SHA256!r}")''',
     '''    if False:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bm.SEAL_2I_SHA256!r}")'''),
    (EP, "require_predictor_seals_2m: the 2k-seal literal check removed",
     '''    if seal_2k.get("sha256") != bm.SEAL_2K_SHA256:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bm.SEAL_2K_SHA256!r}")''',
     '''    if False:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bm.SEAL_2K_SHA256!r}")'''),
    (EP, "require_predictor_seals_2m: the composite re-derivation check removed",
     '''    if psha != bm.PREDICTOR_SHA_2M:
        raise RuntimeError("refusing: PREDICTOR_SHA_2M does not re-derive from the two seals")''',
     '''    if False:
        raise RuntimeError("refusing: PREDICTOR_SHA_2M does not re-derive from the two seals")'''),
    (EP, "run: rung_set_from_counts_2m fed the base's counts instead of stage1_final's",
     '''                if which == "stage1_final":
                    stage1_final[rung] = rec''',
     '''                if which == "base":
                    stage1_final[rung] = rec'''),
    (EP, "run: seal_tag stamped ENDPOINT_SEAL_TAG_2M instead of PREDICTOR_TAGS_2M",
     '    seal_ref = {"tag": bm.PREDICTOR_TAGS_2M, "sha256": seals["predictor_sha"]}',
     '    seal_ref = {"tag": bm.ENDPOINT_SEAL_TAG_2M, "sha256": seals["predictor_sha"]}'),
    (EP, "run: the endpoint loop skips the base (the rung set is still written)",
     '''    stage1_final = {}
    for which in bm.ENDPOINT_WHICH_2M:''',
     '''    stage1_final = {}
    for which in ("stage1_final", "stage3_final"):'''),
    # -------------------------------------------------------- run/sweep_2m.py
    (SW, "run_gate1: the HALTED marker is no longer written on a gate-1 fire",
     '''    if bad:
        bm.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        bm.halt_marker_path(out_root).write_text("\\n".join(bad) + "\\n")
        raise RuntimeError(f"gate 1 smollm3_3b FAILED — halted: {bad[:3]}")''',
     '''    if bad:
        bm.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        raise RuntimeError(f"gate 1 smollm3_3b FAILED — halted: {bad[:3]}")'''),
    (SW, "run_gate1: bit_diffs comparison inverted (a != b -> a == b)",
     '            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a != b))',
     '            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a == b))'),
    (SW, "records_complete_3b: checkpoint-record requirement removed",
     '''    if not all(bm.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return bm.checkpoint_record_path(out_root, step).exists()''',
     '''    if not all(bm.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return True'''),
    (SW, "run_step: free called with entry['commit'] instead of entry['revision']",
     '''    finally:
        _release(model)
        loaders["free"](entry["revision"], cache_root)
    print(f"[2m sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)''',
     '''    finally:
        _release(model)
        loaders["free"](entry["commit"], cache_root)
    print(f"[2m sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)'''),
    (SW, "run: the twin dropped from rest",
     '    rest = (bm.TWIN,) + tuple(s for s in bm.GRID_3B if s != bm.ENDPOINT_STEP_2M)',
     '    rest = tuple(s for s in bm.GRID_3B if s != bm.ENDPOINT_STEP_2M)'),
    (SW, "run_twin: the checkpoint record written BEFORE the rung loop",
     '''        for rung in bt.RUNGS:
            p = bm.record_path(out_root, bm.TWIN, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bm.item_record_2m(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=bm.TWIN,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2m sweep] twin/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bm.checkpoint_record_path(out_root, bm.TWIN), bm.twin_checkpoint_record_2m(info=info))''',
     '''        _write(bm.checkpoint_record_path(out_root, bm.TWIN), bm.twin_checkpoint_record_2m(info=info))
        for rung in bt.RUNGS:
            p = bm.record_path(out_root, bm.TWIN, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bm.item_record_2m(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=bm.TWIN,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2m sweep] twin/{rung}: {rec['correct']}/{rec['n']}", flush=True)'''),
    (SW, "run: require_endpoint_seal_2m removed from run",
     '''    require_predictor_seals_2m(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2m(out_root, blobs_bound=blobs_bound)
    manifest = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)''',
     '''    require_predictor_seals_2m(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    manifest = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)'''),
    (SW, "run: endpoint_sha computed BEFORE the endpoint seal binds (reorder) — "
         "documented-equivalent candidate, prove or kill",
     '''    prereg = bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha)
    bm.check_frozen_2m()
    require_predictor_seals_2m(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2m(out_root, blobs_bound=blobs_bound)
    manifest = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    if bm.halt_marker_path(out_root).exists():
        raise RuntimeError(f"smollm3_3b: the sweep is halted ({bm.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bm.TWIN,) + tuple(s for s in bm.GRID_3B if s != bm.ENDPOINT_STEP_2M)
    pending = [s for s in rest if not records_complete_3b(out_root, s)]
    gate_done = bm.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2m sweep] prereg tag {prereg['tag']!r}; dtype {bm.DTYPE_2M}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    endpoint_sha = bm.endpoint_sha256(out_root)''',
     '''    prereg = bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha)
    bm.check_frozen_2m()
    endpoint_sha = bm.endpoint_sha256(out_root)
    require_predictor_seals_2m(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2m(out_root, blobs_bound=blobs_bound)
    manifest = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    if bm.halt_marker_path(out_root).exists():
        raise RuntimeError(f"smollm3_3b: the sweep is halted ({bm.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bm.TWIN,) + tuple(s for s in bm.GRID_3B if s != bm.ENDPOINT_STEP_2M)
    pending = [s for s in rest if not records_complete_3b(out_root, s)]
    gate_done = bm.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2m sweep] prereg tag {prereg['tag']!r}; dtype {bm.DTYPE_2M}; gate 1 "
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
        bad = bm.gate1_failures_3b(json.loads(g1.read_text()), _load_stage1_final(out_root))
        if bad:
            raise RuntimeError(f"gate 1 smollm3_3b record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_3b(out_root, bm.ENDPOINT_STEP_2M):''',
     '''    else:
        if not records_complete_3b(out_root, bm.ENDPOINT_STEP_2M):'''),
    (SW, "run_twin: the tokenizer commit -> bm.REV_BASE_2M",
     '        tok = loaders["tokenizer"](entry["repo"], entry["config_commit"])',
     '        tok = loaders["tokenizer"](entry["repo"], bm.REV_BASE_2M)'),
    # -------------------------------------------------------------- analyze_2m.py
    (AN, "verdict_tree_2m: PYTHIA-ONLY and OLMO-ONLY swapped",
     '''    if a and not b:
        verdict = "PYTHIA-ONLY"
    elif b and not a:
        verdict = "OLMO-ONLY"''',
     '''    if a and not b:
        verdict = "OLMO-ONLY"
    elif b and not a:
        verdict = "PYTHIA-ONLY"'''),
    (AN, "verdict_2m: THIN threshold < 3 -> < 2",
     '    if len(r_primary) < 3:',
     '    if len(r_primary) < 2:'),
    (AN, "verdict_2m: the UNDERPOWERED disclosure condition inverted",
     '        if not res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":',
     '        if res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":'),
    (AN, "_licensed_2m: disclosures dropped",
     '''    licensed = LICENSED_2M[tree["verdict"]]
    if tree.get("disclosures"):''',
     '''    licensed = LICENSED_2M[tree["verdict"]]
    if False:'''),
    (AN, "load_power_2m: n_trained_steps check removed",
     '''        if sub.get("n_trained_steps") != bm.n_trained_3b():
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bm.n_trained_3b()}")''',
     '''        if False:
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bm.n_trained_3b()}")'''),
    (AN, "load_power_2m: block_sd_A presence check removed",
     '''    bsd = rec.get("block_sd_A")
    if not isinstance(bsd, dict) or any(k not in bsd for k in BLOCK_SD_FIELDS_2M):
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — {BLOCK_SD_FIELDS_2M}")''',
     '''    bsd = rec.get("block_sd_A")
    if False:
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — {BLOCK_SD_FIELDS_2M}")'''),
    (AN, "load_power_2m: predictor_sha256 check removed",
     '''    if rec.get("predictor_sha256") != predictor_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")''',
     '''    if False:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")'''),
    (AN, "load_power_2m: rungs != -> subset (a superset of R_PRIMARY silently accepted)",
     '        if not isinstance(sub.get("rungs"), list) or set(sub["rungs"]) != set(r_primary):',
     '        if not isinstance(sub.get("rungs"), list) or not set(r_primary).issubset(set(sub["rungs"])):'),
    (AN, "check_power_claims_2m: B re-derived on 2l's composite strata, not the base (dial b)",
     '''    for test, x in (("A", x_a256), ("B", x_b)):
        prim = (power or {}).get(test)
        if not isinstance(prim, dict):
            bad.append(f"2m power claims {test}: no block")
            continue
        missing = [k for k in POWER_CLAIM_FIELDS_2M if k not in prim]
        if missing:
            bad.append(f"2m power claims {test}: the record does not attest {missing}")
        dropped = list(an2i._degenerate_rungs(x, strata, r_primary))''',
     '''    for test, x, s in (("A", x_a256, strata),
                       ("B", x_b, an2i._composite_strata_median(strata, x_a256, r_primary))):
        prim = (power or {}).get(test)
        if not isinstance(prim, dict):
            bad.append(f"2m power claims {test}: no block")
            continue
        missing = [k for k in POWER_CLAIM_FIELDS_2M if k not in prim]
        if missing:
            bad.append(f"2m power claims {test}: the record does not attest {missing}")
        dropped = list(an2i._degenerate_rungs(x, s, r_primary))'''),
    (AN, "check_power_claims_2m: n_pos_lower_bound check removed",
     '        if "n_pos_lower_bound" in prim:',
     '        if False:'),
    (AN, "_record_common_failures_2m: predictor_sha check removed",
     '''    if rec.get("predictor_sha") != bm.PREDICTOR_SHA_2M:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bm.PREDICTOR_SHA_2M}")''',
     '''    if False:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bm.PREDICTOR_SHA_2M}")'''),
    (AN, "_record_common_failures_2m: size expected bm.SIZE_OUT -> bi.SIZE_OUT",
     '    for k, v in (("size", bm.SIZE_OUT), ("family", bm.FAMILY), ("n", bt.N_ITEMS),',
     '    for k, v in (("size", bi.SIZE_OUT), ("family", bm.FAMILY), ("n", bt.N_ITEMS),'),
    (AN, "_record_common_failures_2m: the dtype pin dropped from the tuple",
     '                 ("seal_tag", seal_tag), ("dtype", bm.DTYPE_2M)):',
     '                 ("seal_tag", seal_tag)):'),
    (AN, "step_record_failures_2m: endpoint_sha256 check removed",
     '''    if rec.get("endpoint_sha256") != endpoint_sha:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")''',
     '''    if False:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")'''),
    (AN, "step_record_failures_2m: the twin's kind check removed",
     '''        if rec.get("kind") != "from_config":
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")''',
     '''        if False:
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")'''),
    (AN, "step_record_failures_2m: commit check removed",
     '''    elif rec.get("commit") != entry["commit"]:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")''',
     '''    elif False:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")'''),
    (AN, "load_sweep_3b: steps default without the TWIN",
     '    steps = tuple(steps) if steps is not None else bm.GRID_3B + (bm.TWIN,)',
     '    steps = tuple(steps) if steps is not None else bm.GRID_3B'),
    (AN, "load_sweep_3b: LFS sha check removed",
     '''            for name, want in entry.get("lfs_sha256", {}).items():
                if crec.get("sha256", {}).get(name) != want:''',
     '''            for name, want in entry.get("lfs_sha256", {}).items():
                if False:'''),
    (AN, "load_sweep_3b: the twin routed through the generic checkpoint check",
     '''        if step == bm.TWIN:
            cbad = twin_checkpoint_record_failures_2m(crec, entry=entry, step_records=out[step])''',
     '''        if step == bm.TWIN:
            cbad = checkpoint_record_failures_2m(crec, step=0, entry=entry, step_records=out[step])'''),
    (AN, "twin_checkpoint_record_failures_2m: seed check removed",
     '    if crec.get("seed") != bm.TWIN_SEED:',
     '    if False:'),
    (AN, "outcomes_3b: steps default -> GRID_3B + (TWIN,) (the twin leaks into an outcome)",
     '    steps = tuple(steps) if steps is not None else bm.trained_steps_3b()',
     '    steps = tuple(steps) if steps is not None else bm.GRID_3B + (bm.TWIN,)'),
    (AN, "outcomes_3b: the off-grid steps refusal removed",
     '''    if any(s not in bm.GRID_3B for s in steps):
        raise ValueError(f"outcomes_3b: steps {steps} are not all on the frozen grid")''',
     '''    if False:
        raise ValueError(f"outcomes_3b: steps {steps} are not all on the frozen grid")'''),
    (AN, "ceiling_fraction_3b: v == n_steps -> v >= 1",
     '        n_c = int(sum(1 for v in y if v == n_steps))',
     '        n_c = int(sum(1 for v in y if v >= 1))'),
    (AN, "_load_rung_set_2m: subset-of-nine check removed",
     '''    if not set(rec["R_PRIMARY"]).issubset(set(bm.R_CAP_2K)):
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")''',
     '''    if False:
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")'''),
    (AN, "_load_rung_set_2m: partition check removed",
     '''    if set(rec["R_PRIMARY"]) | set(rec["R_ELEVEN_EXTRA"]) | set(rec["R_EXTRA"]) != set(rec["R_3B"]):
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_3B")''',
     '''    if False:
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_3B")'''),
    (AN, "_check_rung_set_derivation_2m: per-key comparison -> set equality (order-blind)",
     '''        want, got = list(rung_set.get(key, [])), list(red[key])
        if got != want:''',
     '''        want, got = list(rung_set.get(key, [])), list(red[key])
        if set(got) != set(want):'''),
    (AN, "_check_rung_set_endpoint_shas_2m: per-file comparison removed",
     '''    for rel in sorted(set(want) & set(got)):
        if got[rel] != want[rel]:''',
     '''    for rel in sorted(set(want) & set(got)):
        if False:'''),
    (AN, "_check_rung_set_endpoint_shas_2m: coverage check removed",
     '''    if missing:
        bad.append(f"rung set smollm3_3b: endpoint_file_sha256 attests nothing for {missing}")''',
     '''    if False:
        bad.append(f"rung set smollm3_3b: endpoint_file_sha256 attests nothing for {missing}")'''),
    (AN, "_endpoint_seal_paths_2m: only two whichs bound by the seal",
     '''def _endpoint_seal_paths_2m(root) -> list:
    paths = [bm.rung_set_path(root), bm.power_path(root)]
    for which in bm.ENDPOINT_WHICH_2M:''',
     '''def _endpoint_seal_paths_2m(root) -> list:
    paths = [bm.rung_set_path(root), bm.power_path(root)]
    for which in ("stage1_final", "stage3_final"):'''),
    (AN, "load_predictors_2m: the 2k-seal literal check removed",
     '''    if isinstance(seal_2k, dict) and seal_2k.get("sha256") != bm.SEAL_2K_SHA256:
        failures.append(f"2m predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")''',
     '''    if False:
        failures.append(f"2m predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")'''),
    (AN, "load_predictors_2m: the 2i-seal literal check removed",
     '''    if isinstance(seal_2i, dict) and seal_2i.get("sha256") != bm.SEAL_2I_SHA256:
        failures.append(f"2m predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")''',
     '''    if False:
        failures.append(f"2m predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")'''),
    (AN, "load_predictors_2m: the seal_failures_2k call removed",
     '        if seal_2k is not None and all(len(cells_2k.get(s, {})) == len(bm.R_CAP_2K) for s in bk.SIZES_2K):',
     '        if False and all(len(cells_2k.get(s, {})) == len(bm.R_CAP_2K) for s in bk.SIZES_2K):'),
    (AN, "load_predictors_2m: the _check_predictor_counts_2i call removed",
     '    if seal_2i is not None and records_2i is not None and x_b is not None:',
     '    if False:'),
    (AN, "load_predictors_2m: R_CAP == nine check removed",
     '''    if rs2i is not None and tuple(sorted(rs2i["R_CAP"])) != tuple(sorted(bm.R_CAP_2K)):
        failures.append(f"2m predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")''',
     '''    if False:
        failures.append(f"2m predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")'''),
    (AN, "load_predictors_2m: x_B bits do not reproduce raise removed",
     '''            if fn.counts_from_bits(bits[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")''',
     '''            if False:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")'''),
    (AN, "load_predictors_2m: the halt-marker scan removed",
     '''    for m in bk.halt_markers(root_2k):
        failures.append(f"2m predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")''',
     '''    for m in []:
        failures.append(f"2m predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")'''),
    (AN, "run()/_core: Test B on 2l's composite strata (drops dial b's unconditioned form)",
     '            B = _run_test(x_b, bi.SIZE_PRED, out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)',
     '            B = _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata_median(strata, x256, r_primary),\n'
     '                          r_primary, n_perm=n_perm, n_boot=n_boot)'),
    (AN, "run()/_core: Test A predictor -> counts[64] instead of counts[K_TOTAL]",
     '            x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL] for r in r_primary}',
     '            x256 = {r: cells_2k["1b"][r]["counts"][64] for r in r_primary}'),
    (AN, "check_imports_2m: 'tests' in rp.parts swallows everything -> True",
     '        if not s.startswith(_EXPERIMENTS_ROOT_2M + "/") or "tests" in rp.parts:',
     '        if not s.startswith(_EXPERIMENTS_ROOT_2M + "/") or True:'),
    (AN, "s3_paired_difference_2m: the difference sign flipped (b - a -> a - b)",
     '            diffs.append(b - a)',
     '            diffs.append(a - b)'),
    (AN, "s3_paired_difference_2m: the bootstrap unpaired (A and B on DIFFERENT index draws)",
     '        a, b = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})',
     '        a, _b0 = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})\n'
     '        _a0, b = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})'),
    (AN, "s4_matched_2m: increment sign flipped",
     '            "increment": (None if t_b is None or t_a["T"] is None else t_b - t_a["T"])}',
     '            "increment": (None if t_b is None or t_a["T"] is None else t_a["T"] - t_b)}'),
    (AN, "s5_answer_prior_2m: non_gating True -> False",
     '            "non_gating": True,',
     '            "non_gating": False,'),
    (AN, "s8_outcome_order_2m: descriptive True -> False",
     '                     "descriptive": True}',
     '                     "descriptive": False}'),
    (AN, "s8_outcome_order_2m: every rung of the committed outcome, not R_PRIMARY ∩ it",
     '        rungs_k = [r for r in r_primary if r in out_k]',
     '        rungs_k = [r for r in out_k]'),
    (AN, "collapses_3b: threshold >= -> >",
     '            if n >= threshold:',
     '            if n > threshold:'),
    (AN, "run(): the post-secondaries import re-check does not refuse",
     '''        if f:
            failures += f
            referents["failures"] = list(failures)
            t2 = verdict_2m(failures, None, None, None, ())''',
     '''        if False:
            failures += f
            referents["failures"] = list(failures)
            t2 = verdict_2m(failures, None, None, None, ())'''),
    (AN, "sensitivities: log_head_subset computed over bm.GRID_3B, not LOG_HEAD_SUBSET_2M",
     '            sub = outcomes_3b(sweep, rungs=tuple(bt.RUNGS), steps=bm.LOG_HEAD_SUBSET_2M)',
     '            sub = outcomes_3b(sweep, rungs=tuple(bt.RUNGS), steps=bm.GRID_3B)'),
]

# One mutant per collect_total(...) call site in analyze_2m.py's run() AND
# load_predictors_2m, generated from the real, current source at import
# time rather than hand-picked (2j's Finding 4 lesson, applied at build
# time by 2k, 2l and 2m alike — this file has several functions with
# collect_total sites, not one, and _totality_mutants walks the whole
# file).
M += _totality_mutants(AN)

# Task 5 ruling: fast modules only by default (test_battery_2m.py,
# test_stages_2m.py, test_analyze_2m.py with the real-tree cases
# deselected — they take minutes and observe nothing a fast mutant
# changes). A `--totality` flag switches the covering suite to
# TOTALITY_TESTS (test_totality_2m.py alone) so a totality-only kill is
# reproducible from the committed harness, not a scratch script;
# `--fullshape` switches to test_full_shape_2m.py for the handful of
# shapes only a synthetic-SmolLM3-tree world can observe (the
# endpoint-composite/gate-1/power-record byte-level corruptions).
FAST_TESTS = [str(L / "tests" / "test_battery_2m.py"), str(L / "tests" / "test_stages_2m.py"),
             str(L / "tests" / "test_analyze_2m.py")]
FAST_EXTRA_ARGS = ["-m", "not slow", "-k",
                  "not test_run_on_empty_tree and not test_s4 and not test_s5 and not real_trees "
                  "and not real_tree"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_2m.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_2m.py")]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2m" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """2k's Finding 3 lesson, applied from commit one: a stray
    `.mutation_backup` anywhere under `experiments/exp2m` means either a
    concurrent run is already in flight or a previous run crashed
    without restoring — either way, starting a NEW run on top of it
    corrupts the restore. Refuse before the baseline check even
    starts."""
    found = sorted((ROOT / "experiments" / "exp2m").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp2m (a concurrent run, or a previous crash that "
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
