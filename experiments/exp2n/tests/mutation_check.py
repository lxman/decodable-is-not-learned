# experiments/exp2n/tests/mutation_check.py
"""Mutation-test exp2n's OWN modules — battery_2n (the Comma v0.1-1T
ONE-repo grid, the loader family and its BOS-render + eos-stop pins,
the rung-set rule, the endpoint composite sha, the record stamps and
the dtype override, the gate-1 checkers, the pins/prereg binding),
run/endpoint_2n (both predictor seals, the three whichs, the rung set
from stage1_final), run/sweep_2n (gate 1, the endpoint seal, the twin,
the grid), and analyze_2n (the two predictor loaders through their
seals, the Comma trees, the tree/disclosures, the import-surface scan,
S3/S4/S5/S8/S8c/S9, the annotation C, and every `collect_total` call
site in `run()`/`load_predictors_2n`, AST-generated via 2i's own
`_totality_mutants`, imported verbatim rather than re-implemented).
Everything upstream of 2n (2m/2l/2k/2j/2i/2g/2h/2d/2c/exp3/exp3c/exp3d)
is frozen instrument, pinned by `FROZEN_SHA256_2N` /
`FROZEN_IMPORT_SHA256_2G` / `IMPORTED_SHA256_2J` / `IMPORTED_SHA256_2K`
/ `IMPORTED_SHA256_2L` / `IMPORTED_SHA256_2M`, and is not re-targeted
here.

2m's/2l's/2k's/2j's precedent: run each mutant against the FAST modules
only (`test_battery_2n.py`, `test_stages_2n.py`, `test_analyze_2n.py`,
`test_power_2n.py` with the real-tree/slow cases deselected — they take
minutes together and observe nothing a fast mutant changes). A mutant
that survives the fast modules is either closed with a new fast test
(preferred) or, when only a world/totality shape can observe the
behaviour it changes, recorded as 'killed by worlds/totality only'
after one targeted confirmation run under `--totality` or `--fullshape`
— see PROGRESS.md's Task 5 entry for which mutants took that path and
for any documented-equivalent mutant (a proof in the ledger, not merely
an assertion — 2j's `matched_k` clip precedent).

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

L = ROOT / "experiments/exp2n"
BK = L / "battery_2n.py"
EP = L / "run" / "endpoint_2n.py"
SW = L / "run" / "sweep_2n.py"
AN = L / "analyze_2n.py"

M = [
    # -------------------------------------------------------- battery_2n.py
    (BK, "GRID_COMMA missing 220000",
     '''GRID_COMMA = (10000, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000,
              200000, 220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000, 380000,
              400000, 420000, 440000, 460000)''',
     '''GRID_COMMA = (10000, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000,
              200000, 240000, 260000, 280000, 300000, 320000, 340000, 360000, 380000,
              400000, 420000, 440000, 460000)'''),
    (BK, "EVERY40K_SUBSET_2N with 460000 dropped (subset check must not hide it)",
     '''EVERY40K_SUBSET_2N = (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000,
                      400000, 440000, 460000)''',
     '''EVERY40K_SUBSET_2N = (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000,
                      400000, 440000)'''),
    (BK, "trained_steps_comma returns GRID_COMMA + (TWIN,) (the twin leaks into an outcome)",
     '''def trained_steps_comma() -> tuple:
    return tuple(GRID_COMMA)''',
     '''def trained_steps_comma() -> tuple:
    return tuple(GRID_COMMA) + (TWIN,)'''),
    (BK, "build_manifest_comma: duplicate refusal `step != ENDPOINT_STEP_2N and same` -> `False and ...`",
     '        if step != ENDPOINT_STEP_2N and same:',
     '        if False and same:'),
    (BK, "build_manifest_comma: the endpoint-revision pin check removed",
     '''    if endpoint_entry["revision"] != REV_ENDPOINT_2N:
        raise ValueError(f"{REPO_COMMA}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_ENDPOINT_2N!r}")''',
     '''    if False:
        raise ValueError(f"{REPO_COMMA}: endpoint revision {endpoint_entry['revision']!r} is not "
                         f"the pinned {REV_ENDPOINT_2N!r}")'''),
    (BK, "build_manifest_comma: main duplicate refusal removed (main's own check dropped from the loop)",
     '    for name, rev in (("stage2_final", REV_STAGE2_FINAL_2N), ("main", REV_MAIN_2N)):',
     '    for name, rev in (("stage2_final", REV_STAGE2_FINAL_2N),):'),
    (BK, "build_manifest_comma: the stage2_final duplicate refusal removed (dropped from the loop)",
     '    for name, rev in (("stage2_final", REV_STAGE2_FINAL_2N), ("main", REV_MAIN_2N)):',
     '    for name, rev in (("main", REV_MAIN_2N),):'),
    (BK, "build_manifest_comma: the twin's config_commit -> 'main'",
     '            "seed": TWIN_SEED, "config_commit": endpoint_entry["commit"]}',
     '            "seed": TWIN_SEED, "config_commit": "main"}'),
    (BK, "load_manifest_comma: the frozen-grid check removed",
     '''    if obj.get("grid_comma") != list(GRID_COMMA) or obj.get("every40k_subset") != list(EVERY40K_SUBSET_2N) \\
            or not isinstance(obj.get("twin"), dict) or obj["twin"].get("kind") != "from_config":
        raise ValueError(f"{path}: manifest is not the frozen Comma grid")''',
     '''    if False:
        raise ValueError(f"{path}: manifest is not the frozen Comma grid")'''),
    (BK, "entry_comma: the twin branch reads entries_comma['twin'] instead of the twin entry",
     '''    if step == TWIN:
        e = manifest.get("twin")''',
     '''    if step == TWIN:
        e = manifest.get("entries_comma", {}).get("twin")'''),
    (BK, "_STAGE1_RE_2N: \\d{6} -> \\d+ (documented-equivalent candidate, prove or kill)",
     '_STAGE1_RE_2N = re.compile(r"^stage1-step(\\d{6})-tokens(\\d+)B$")',
     '_STAGE1_RE_2N = re.compile(r"^stage1-step(\\d+)-tokens(\\d+)B$")'),
    (BK, "rung_set_from_counts_2n: r in R_CAP_2K -> r in STRATA_RUNGS",
     '    r_primary = tuple(r for r in r_comma if r in R_CAP_2K)',
     '    r_primary = tuple(r for r in r_comma if r in STRATA_RUNGS)'),
    (BK, "rung_set_from_counts_2n: R_ELEVEN_EXTRA computed without `not in R_CAP_2K`",
     '    r_eleven_extra = tuple(r for r in r_comma if r in STRATA_RUNGS and r not in R_CAP_2K)',
     '    r_eleven_extra = tuple(r for r in r_comma if r in STRATA_RUNGS)'),
    (BK, "rung_set_from_counts_2n: primary_is_the_nine -> True",
     '            "primary_is_the_nine": tuple(r_primary) == tuple(sorted(R_CAP_2K)),',
     '            "primary_is_the_nine": True,'),
    (BK, "rung_set_from_counts_2n: the returned dict's R_COMMA key renamed",
     '    return {"R_COMMA": list(r_comma), "R_PRIMARY": list(r_primary),',
     '    return {"R_3B": list(r_comma), "R_PRIMARY": list(r_primary),'),
    (BK, "endpoint_files: missing-file raise removed",
     '''    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(str(p))
        out[str(p.relative_to(root))] = bg.sha256_file(p)''',
     '''    for p in paths:
        if False:
            raise FileNotFoundError(str(p))
        out[str(p.relative_to(root))] = bg.sha256_file(p)'''),
    (BK, "endpoint_files: only two whichs (main's 34 records leave the composite)",
     '''    paths = [rung_set_path(root), power_path(root)]
    for which in ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            paths.append(endpoint_record_path(root, which, r))''',
     '''    paths = [rung_set_path(root), power_path(root)]
    for which in ("stage1_final", "stage2_final"):
        for r in bt.RUNGS:
            paths.append(endpoint_record_path(root, which, r))'''),
    (BK, "composite_sha: unsorted",
     '    lines = "\\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))',
     '    lines = "\\n".join(f"{rel} {sha}" for rel, sha in files.items())'),
    (BK, "item_record_2n: seal_tag ENDPOINT_SEAL_TAG_2N -> PREDICTOR_TAGS_2N",
     '                         seal={"tag": ENDPOINT_SEAL_TAG_2N, "sha256": PREDICTOR_SHA_2N},',
     '                         seal={"tag": PREDICTOR_TAGS_2N, "sha256": PREDICTOR_SHA_2N},'),
    (BK, "item_record_2n: endpoint_sha256 key dropped from the record",
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''    _ = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec'''),
    (BK, "item_record_2n: the dtype override removed",
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec'''),
    (BK, "item_record_2n: the render override removed",
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec'''),
    (BK, "item_record_2n: the eos_stop_id override removed",
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''    rec["endpoint_sha256"] = endpoint_sha
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    return rec'''),
    (BK, "endpoint_item_record_2n: the dtype override removed",
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec'''),
    (BK, "endpoint_item_record_2n: the render override removed",
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec'''),
    (BK, "endpoint_item_record_2n: the eos_stop_id override removed",
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    rec["eos_stop_id"] = EOS_STOP_ID_2N
    return rec''',
     '''                         ckpt=ckpt, seal=seal, t_s=t_s)
    rec["dtype"] = DTYPE_2N
    rec["render"] = RENDER_2N
    return rec'''),
    (BK, "checkpoint_record_2n: generation_eos_token_id key dropped",
     '''            "digest": ckpt["weight_sha256"], "download_seconds": round(seconds, 1),
            "config_eos_token_id": info.get("config_eos_token_id"),
            "generation_eos_token_id": info.get("generation_eos_token_id")}''',
     '''            "digest": ckpt["weight_sha256"], "download_seconds": round(seconds, 1),
            "config_eos_token_id": info.get("config_eos_token_id")}'''),
    (BK, "twin_checkpoint_record_2n: commit None -> ''",
     '            "revision": TWIN, "commit": None, "kind": "from_config", "seed": int(info["seed"]),',
     '            "revision": TWIN, "commit": "", "kind": "from_config", "seed": int(info["seed"]),'),
    (BK, "gate1_failures_comma: nc.get(r) != N_ITEMS -> <",
     '        if nc.get(r) != N_ITEMS:',
     '        if nc.get(r) is not None and nc.get(r) < N_ITEMS:'),
    (BK, "gate1_failures_comma: bd.get(r) != 0 removed",
     '        if bd.get(r) != 0:',
     '        if False:'),
    (BK, "gate1_failures_comma: digest check removed",
     '    if not dg_s or not dg_e or dg_s != dg_e:',
     '    if False:'),
    (BK, "gate1_failures_comma: prereg_tag check removed",
     '    if rec.get("prereg_tag") != PREREG_TAG_2N:',
     '    if False:'),
    (BK, "gate1_failures_comma: gate 1 does not measure digest_endpoint/commit_endpoint over the 34 records",
     '''    for field, att, label in (("weight_sha256", dg_e, "tensor digest"),
                              ("commit", ce, "commit")):''',
     '''    for field, att, label in ():'''),
    (BK, "gate1_rederive_comma: attested-vs-re-derived bit_diffs check removed",
     '        if bd_att.get(r) != bit_diff:',
     '        if False:'),
    (BK, "gate1_rederive_comma: coverage len(s_bits) != N_ITEMS -> <",
     '''        if not isinstance(s_bits, list) or not isinstance(e_bits, list) or \\
                len(s_bits) != N_ITEMS or len(e_bits) != N_ITEMS:''',
     '''        if not isinstance(s_bits, list) or not isinstance(e_bits, list) or \\
                len(s_bits) < N_ITEMS or len(e_bits) != N_ITEMS:'''),
    (BK, "gate1_rederive_comma: the re-derivation does not measure digest_sweep/commit_sweep over the 34 sweep records",
     '''    for field, att, label in (("weight_sha256", g.get("digest_sweep"), "tensor digest"),
                              ("commit", g.get("commit_sweep"), "commit")):''',
     '''    for field, att, label in ():'''),
    (BK, "predictor_sha_2n: the '2n|' prefix dropped (2m's composite of the same two seals)",
     '    return hashlib.sha256(f"2n|{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()',
     '    return hashlib.sha256(f"{seal_2k_sha}|{seal_2i_sha}".encode()).hexdigest()'),
    (BK, "require_prereg_2n: want != got -> ==",
     '        if want != got:',
     '        if want == got:'),
    (BK, "check_frozen_2n: drift check removed",
     '''    for p, want in FROZEN_SHA256_2N.items():
        got = bg.sha256_file(p)
        if got != want:''',
     '''    for p, want in FROZEN_SHA256_2N.items():
        got = bg.sha256_file(p)
        if False:'''),
    (BK, "clean_dir_comma: config.to_json_file line removed (2i stop #1)",
     '''    config.to_json_file(str(d / "config.json"))
    return d''',
     '''    return d'''),
    (BK, "check_tokenizer_2n: the plain-render special check removed",
     '''    if not plain or plain[0] in specials:
        raise RuntimeError(f"the plain render of 'Q:' begins with {plain[:1]} — a special id; the stack "
                           f"must add nothing on its own (dial n pins the prefix explicitly)")''',
     '''    if False:
        raise RuntimeError(f"the plain render of 'Q:' begins with {plain[:1]} — a special id; the stack "
                           f"must add nothing on its own (dial n pins the prefix explicitly)")'''),
    (BK, "check_tokenizer_2n: the BOS-render [BOS, plain[0]] check removed",
     '''    if bos[:2] != [BOS_TOKEN_ID_2N, plain[0]] or (len(bos) > 2 and bos[1] == BOS_TOKEN_ID_2N):
        raise RuntimeError(f"the BOS render of 'Q:' begins {bos[:3]}, not [{BOS_TOKEN_ID_2N}, {plain[0]}] — "
                           f"exactly one BOS, first (dial n)")''',
     '''    if False:
        raise RuntimeError(f"the BOS render of 'Q:' begins {bos[:3]}, not [{BOS_TOKEN_ID_2N}, {plain[0]}] — "
                           f"exactly one BOS, first (dial n)")'''),
    (BK, "check_tokenizer_2n: the len(tok) check removed",
     '''    n = len(tok_like)
    if n != VOCAB_LEN_2N:
        raise RuntimeError(f"len(tokenizer) is {n}, not {VOCAB_LEN_2N}")''',
     '''    n = len(tok_like)
    if False:
        raise RuntimeError(f"len(tokenizer) is {n}, not {VOCAB_LEN_2N}")'''),
    (BK, "check_tokenizer_2n: the bos_token_id/unk_token_id loop entries removed",
     '''    for name, want in (("pad_token_id", PAD_TOKEN_ID_2N), ("eos_token_id", EOS_TOKEN_ID_2N),
                       ("bos_token_id", BOS_TOKEN_ID_2N), ("unk_token_id", UNK_TOKEN_ID_2N)):''',
     '''    for name, want in (("pad_token_id", PAD_TOKEN_ID_2N), ("eos_token_id", EOS_TOKEN_ID_2N)):'''),
    (BK, "load_tokenizer_comma: padding_side 'left' -> 'right'",
     '    tok.padding_side = "left"',
     '    tok.padding_side = "right"'),
    (BK, "render_2n: BOS_TOKEN_2N + p -> p (the prefix dropped)",
     '    return [BOS_TOKEN_2N + p for p in prompts]',
     '    return [p for p in prompts]'),
    (BK, "BosRunner.generate: passes prompts unrendered",
     '        return self.inner.generate(render_2n(prompts), max_new_tokens)',
     '        return self.inner.generate(prompts, max_new_tokens)'),
    (BK, "set_eos_stop_2n: the assignment removed",
     '''    model.generation_config.eos_token_id = EOS_STOP_ID_2N
    facts = eos_facts_2n(model)''',
     '''    facts = eos_facts_2n(model)'''),
    (BK, "set_eos_stop_2n: the read-back != -> ==",
     '    if facts["generation_eos_token_id"] != EOS_STOP_ID_2N:',
     '    if facts["generation_eos_token_id"] == EOS_STOP_ID_2N:'),
    # -------------------------------------------------------- run/endpoint_2n.py
    (EP, "real_loaders: runner returns the bare HFRunner (no BosRunner)",
     '    return {"thin": thin, "runner": lambda tok, model: bn.BosRunner(HFRunner(tok, model, batch_size))}',
     '    return {"thin": thin, "runner": lambda tok, model: HFRunner(tok, model, batch_size)}'),
    (EP, "require_predictor_seals_2n: the 2k-seal literal check removed",
     '''    if seal_2k.get("sha256") != bn.SEAL_2K_SHA256:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bn.SEAL_2K_SHA256!r}")''',
     '''    if False:
        raise RuntimeError(f"refusing: 2k's seal sha {seal_2k.get('sha256')!r} is not the "
                           f"literal {bn.SEAL_2K_SHA256!r}")'''),
    (EP, "require_predictor_seals_2n: the 2i-seal literal check removed",
     '''    if seal_2i.get("sha256") != bn.SEAL_2I_SHA256:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bn.SEAL_2I_SHA256!r}")''',
     '''    if False:
        raise RuntimeError(f"refusing: 2i's seal sha {seal_2i.get('sha256')!r} is not the "
                           f"literal {bn.SEAL_2I_SHA256!r}")'''),
    (EP, "require_predictor_seals_2n: the composite re-derivation check removed",
     '''    if psha != bn.PREDICTOR_SHA_2N:
        raise RuntimeError("refusing: PREDICTOR_SHA_2N does not re-derive from the two seals")''',
     '''    if False:
        raise RuntimeError("refusing: PREDICTOR_SHA_2N does not re-derive from the two seals")'''),
    (EP, "run: rung_set_from_counts_2n fed main's counts instead of stage1_final's",
     '''                if which == "stage1_final":
                    stage1_final[rung] = rec''',
     '''                if which == "main":
                    stage1_final[rung] = rec'''),
    (EP, "run: seal_tag stamped ENDPOINT_SEAL_TAG_2N instead of PREDICTOR_TAGS_2N",
     '    seal_ref = {"tag": bn.PREDICTOR_TAGS_2N, "sha256": seals["predictor_sha"]}',
     '    seal_ref = {"tag": bn.ENDPOINT_SEAL_TAG_2N, "sha256": seals["predictor_sha"]}'),
    (EP, "run: the stage2_final load dropped from the loop (the rung set is still written)",
     '''    stage1_final = {}
    for which in bn.ENDPOINT_WHICH_2N:''',
     '''    stage1_final = {}
    for which in ("stage1_final", "main"):'''),
    # -------------------------------------------------------- run/sweep_2n.py
    (SW, "real_loaders: runner returns the bare HFRunner (no BosRunner)",
     '''    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer,
            "runner": lambda tok, model: bn.BosRunner(HFRunner(tok, model, batch_size)), "free": free}''',
     '''    return {"checkpoint": checkpoint, "twin": twin, "tokenizer": tokenizer,
            "runner": lambda tok, model: HFRunner(tok, model, batch_size), "free": free}'''),
    (SW, "run_gate1: the HALTED marker is no longer written on a gate-1 fire",
     '''    if bad:
        bn.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        bn.halt_marker_path(out_root).write_text("\\n".join(bad) + "\\n")
        raise RuntimeError(f"gate 1 comma_7b FAILED — halted: {bad[:3]}")''',
     '''    if bad:
        bn.halt_marker_path(out_root).parent.mkdir(parents=True, exist_ok=True)
        raise RuntimeError(f"gate 1 comma_7b FAILED — halted: {bad[:3]}")'''),
    (SW, "run_gate1: bit_diffs comparison inverted (a != b -> a == b)",
     '            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a != b))',
     '            bit_diffs[r] = int(sum(1 for a, b in zip(rec["bits"], ref["bits"]) if a == b))'),
    (SW, "records_complete_comma: checkpoint-record requirement removed",
     '''    if not all(bn.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return bn.checkpoint_record_path(out_root, step).exists()''',
     '''    if not all(bn.record_path(out_root, step, r).exists() for r in bt.RUNGS):
        return False
    return True'''),
    (SW, "run_step: free called with entry['commit'] instead of entry['revision']",
     '''        loaders["free"](entry["revision"], cache_root)
    print(f"[2n sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)''',
     '''        loaders["free"](entry["commit"], cache_root)
    print(f"[2n sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)'''),
    (SW, "run: the twin dropped from rest",
     '    rest = (bn.TWIN,) + tuple(s for s in bn.GRID_COMMA if s != bn.ENDPOINT_STEP_2N)',
     '    rest = tuple(s for s in bn.GRID_COMMA if s != bn.ENDPOINT_STEP_2N)'),
    (SW, "run_twin: the checkpoint record written BEFORE the rung loop",
     '''        for rung in bt.RUNGS:
            p = bn.record_path(out_root, bn.TWIN, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bn.item_record_2n(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=bn.TWIN,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2n sweep] twin/{rung}: {rec['correct']}/{rec['n']}", flush=True)
        _write(bn.checkpoint_record_path(out_root, bn.TWIN), bn.twin_checkpoint_record_2n(info=info))''',
     '''        _write(bn.checkpoint_record_path(out_root, bn.TWIN), bn.twin_checkpoint_record_2n(info=info))
        for rung in bt.RUNGS:
            p = bn.record_path(out_root, bn.TWIN, rung)
            if p.exists():
                continue
            ev = evaluate_items(runner, battery[rung], verify_fn)
            rec = bn.item_record_2n(rung=rung, cap=battery[rung], ev=ev, ckpt=ckpt, step=bn.TWIN,
                                    endpoint_sha=endpoint_sha, t_s=0.0)
            _write(p, rec)
            print(f"[2n sweep] twin/{rung}: {rec['correct']}/{rec['n']}", flush=True)'''),
    (SW, "run: require_endpoint_seal_2n removed from run",
     '''    require_predictor_seals_2n(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2n(out_root, blobs_bound=blobs_bound)
    manifest = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)''',
     '''    require_predictor_seals_2n(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    manifest = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)'''),
    (SW, "run: endpoint_sha computed BEFORE the endpoint seal binds (reorder) — "
         "documented-equivalent candidate, prove or kill",
     '''    prereg = bn.require_prereg_2n(tag_exists=tag_exists, blob_sha=blob_sha)
    bn.check_frozen_2n()
    require_predictor_seals_2n(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2n(out_root, blobs_bound=blobs_bound)
    manifest = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    if bn.halt_marker_path(out_root).exists():
        raise RuntimeError(f"comma_7b: the sweep is halted ({bn.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bn.TWIN,) + tuple(s for s in bn.GRID_COMMA if s != bn.ENDPOINT_STEP_2N)
    pending = [s for s in rest if not records_complete_comma(out_root, s)]
    gate_done = bn.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2n sweep] prereg tag {prereg['tag']!r}; dtype {bn.DTYPE_2N}; gate 1 "
              f"{'done' if gate_done else 'pending'}; would run "
              f"{len(pending) + (0 if gate_done else 1)} step(s): "
              f"{('gate1, ' if not gate_done else '') + str(pending)}", flush=True)
        return
    if loaders is None:
        _assert_provenance()
        loaders = real_loaders()
    battery = bg.load_battery()
    verify_fn = a2d.load_verify()
    endpoint_sha = bn.endpoint_sha256(out_root)''',
     '''    prereg = bn.require_prereg_2n(tag_exists=tag_exists, blob_sha=blob_sha)
    bn.check_frozen_2n()
    endpoint_sha = bn.endpoint_sha256(out_root)
    require_predictor_seals_2n(tag_exists=tag_exists, blobs_bound=blobs_bound, root_2i=root_2i,
                               root_2k=root_2k)
    require_endpoint_seal_2n(out_root, blobs_bound=blobs_bound)
    manifest = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    if bn.halt_marker_path(out_root).exists():
        raise RuntimeError(f"comma_7b: the sweep is halted ({bn.halt_marker_path(out_root)}); "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
    rest = (bn.TWIN,) + tuple(s for s in bn.GRID_COMMA if s != bn.ENDPOINT_STEP_2N)
    pending = [s for s in rest if not records_complete_comma(out_root, s)]
    gate_done = bn.gate1_path(out_root).is_file()
    if dry_run:
        print(f"[2n sweep] prereg tag {prereg['tag']!r}; dtype {bn.DTYPE_2N}; gate 1 "
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
        bad = bn.gate1_failures_comma(json.loads(g1.read_text()), _load_stage1_final(out_root))
        if bad:
            raise RuntimeError(f"gate 1 comma_7b record on disk fails re-derivation: {bad[:3]}")
        if not records_complete_comma(out_root, bn.ENDPOINT_STEP_2N):''',
     '''    else:
        if not records_complete_comma(out_root, bn.ENDPOINT_STEP_2N):'''),
    (SW, "run_twin: the tokenizer commit -> bn.REV_MAIN_2N",
     '        tok = loaders["tokenizer"](entry["repo"], entry["config_commit"])',
     '        tok = loaders["tokenizer"](entry["repo"], bn.REV_MAIN_2N)'),
    # -------------------------------------------------------------- analyze_2n.py
    (AN, "verdict_tree_2n: PYTHIA-ONLY and OLMO-ONLY swapped",
     '''    if a and not b:
        verdict = "PYTHIA-ONLY"
    elif b and not a:
        verdict = "OLMO-ONLY"''',
     '''    if a and not b:
        verdict = "OLMO-ONLY"
    elif b and not a:
        verdict = "PYTHIA-ONLY"'''),
    (AN, "verdict_2n: THIN threshold < 3 -> < 2",
     '    if len(r_primary) < 3:',
     '    if len(r_primary) < 2:'),
    (AN, "verdict_2n: the UNDERPOWERED disclosure condition inverted",
     '        if not res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":',
     '        if res["fires"] and status == "DECLARED UNDERPOWERED IN ADVANCE":'),
    (AN, "verdict_2n: annotation not carried into the return",
     '    return {"verdict": tree["verdict"], "reason": reason, "disclosures": disclosures, "annotation": annotation}',
     '    return {"verdict": tree["verdict"], "reason": reason, "disclosures": disclosures, "annotation": None}'),
    (AN, "_licensed_2n: disclosures dropped",
     '''    licensed = LICENSED_2N[tree["verdict"]]
    if tree.get("disclosures"):''',
     '''    licensed = LICENSED_2N[tree["verdict"]]
    if False:'''),
    (AN, "_licensed_2n: the annotation modifier dropped",
     '''    if tree.get("annotation"):
        licensed = "; ".join([licensed, C_MODIFIERS_2N[_c_modifier_key_2n(tree["annotation"]["C"])]])
    return licensed''',
     '''    return licensed'''),
    (AN, "_c_modifier_key_2n: covers/excludes swapped",
     '''    if r in ("B-LEADS", "NO-LEAD"):
        return f"{r}-{'covers' if c.get('covers_3b_increment') else 'excludes'}"''',
     '''    if r in ("B-LEADS", "NO-LEAD"):
        return f"{r}-{'excludes' if c.get('covers_3b_increment') else 'covers'}"'''),
    (AN, "load_power_2n: n_trained_steps check removed",
     '''        if sub.get("n_trained_steps") != bn.n_trained_comma():
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bn.n_trained_comma()}")''',
     '''        if False:
            raise ValueError(f"{p}: test {test!r} n_trained_steps {sub.get('n_trained_steps')!r} "
                             f"!= {bn.n_trained_comma()}")'''),
    (AN, "load_power_2n: block_sd_A presence check removed",
     '''    bsd = rec.get("block_sd_A")
    if not isinstance(bsd, dict) or any(k not in bsd for k in BLOCK_SD_FIELDS_2N):
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — {BLOCK_SD_FIELDS_2N}")''',
     '''    bsd = rec.get("block_sd_A")
    if False:
        raise ValueError(f"{p}: block_sd_A missing or incomplete (dial h) — {BLOCK_SD_FIELDS_2N}")'''),
    (AN, "load_power_2n: predictor_sha256 check removed",
     '''    if rec.get("predictor_sha256") != predictor_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")''',
     '''    if False:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"composite predictor sha {predictor_sha!r}")'''),
    (AN, "load_power_2n: rungs != -> subset (a superset of R_PRIMARY silently accepted)",
     '        if not isinstance(sub.get("rungs"), list) or set(sub["rungs"]) != set(r_primary):',
     '        if not isinstance(sub.get("rungs"), list) or not set(r_primary).issubset(set(sub["rungs"])):'),
    (AN, "load_power_2n: delta_sd requirement removed",
     '''    dsd = rec.get("delta_sd")
    if not isinstance(dsd, dict) or any(k not in dsd for k in DELTA_SD_FIELDS_2N):
        raise ValueError(f"{p}: delta_sd missing or incomplete (dial h) — {DELTA_SD_FIELDS_2N}")''',
     '''    dsd = rec.get("delta_sd")
    if False:
        raise ValueError(f"{p}: delta_sd missing or incomplete (dial h) — {DELTA_SD_FIELDS_2N}")'''),
    (AN, "load_power_2n: formula pin removed",
     '''    if dsd.get("formula") != DELTA_FORMULA_LITERAL_2N:
        raise ValueError(f"{p}: delta_sd formula {dsd.get('formula')!r} is not the literal "
                         f"{DELTA_FORMULA_LITERAL_2N!r}")''',
     '''    if False:
        raise ValueError(f"{p}: delta_sd formula {dsd.get('formula')!r} is not the literal "
                         f"{DELTA_FORMULA_LITERAL_2N!r}")'''),
    (AN, "check_power_claims_2n: B re-derived on 2m's composite strata, not the base (dial b)",
     '''    for test, x in (("A", x_a256), ("B", x_b)):
        dropped_by_test[test] = set(an2i._degenerate_rungs(x, strata, r_primary))''',
     '''    for test, x, s in (("A", x_a256, strata),
                       ("B", x_b, an2i._composite_strata_median(strata, x_a256, r_primary))):
        dropped_by_test[test] = set(an2i._degenerate_rungs(x, s, r_primary))'''),
    (AN, "check_power_claims_2n: n_pos_lower_bound check removed",
     '        if "n_pos_lower_bound" in prim:',
     '        if False:'),
    (AN, "check_power_claims_2n: k_by_rung measurement removed",
     '''        if got_k != want_k:
            bad.append(f"2n power claims delta_sd: k_by_rung {got_k!r} != re-derived {want_k!r}")''',
     '''        if False:
            bad.append(f"2n power claims delta_sd: k_by_rung {got_k!r} != re-derived {want_k!r}")'''),
    (AN, "check_power_claims_2n: delta_sd rungs measurement removed",
     '''        if sorted(dsd.get("rungs") or []) != sorted(keep_both):
            bad.append(f"2n power claims delta_sd: rungs {sorted(dsd.get('rungs') or [])} != "
                       f"{sorted(keep_both)} (R_PRIMARY minus the union of both predictors' degenerate rungs)")''',
     '''        if False:
            bad.append(f"2n power claims delta_sd: rungs {sorted(dsd.get('rungs') or [])} != "
                       f"{sorted(keep_both)} (R_PRIMARY minus the union of both predictors' degenerate rungs)")'''),
    (AN, "_record_common_failures_2n: predictor_sha check removed",
     '''    if rec.get("predictor_sha") != bn.PREDICTOR_SHA_2N:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bn.PREDICTOR_SHA_2N}")''',
     '''    if False:
        bad.append(f"{label}: predictor_sha {rec.get('predictor_sha')} is not "
                   f"{bn.PREDICTOR_SHA_2N}")'''),
    (AN, "_record_common_failures_2n: size expected bn.SIZE_OUT -> bi.SIZE_OUT",
     '    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),',
     '    for k, v in (("size", bi.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),'),
    (AN, "_record_common_failures_2n: the dtype pin dropped from the tuple",
     '''    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bn.DTYPE_2N),
                 ("render", bn.RENDER_2N), ("eos_stop_id", bn.EOS_STOP_ID_2N)):''',
     '''    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag),
                 ("render", bn.RENDER_2N), ("eos_stop_id", bn.EOS_STOP_ID_2N)):'''),
    (AN, "_record_common_failures_2n: the render pin dropped from the tuple",
     '''    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bn.DTYPE_2N),
                 ("render", bn.RENDER_2N), ("eos_stop_id", bn.EOS_STOP_ID_2N)):''',
     '''    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bn.DTYPE_2N),
                 ("eos_stop_id", bn.EOS_STOP_ID_2N)):'''),
    (AN, "_record_common_failures_2n: the eos_stop_id pin dropped from the tuple",
     '''    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bn.DTYPE_2N),
                 ("render", bn.RENDER_2N), ("eos_stop_id", bn.EOS_STOP_ID_2N)):''',
     '''    for k, v in (("size", bn.SIZE_OUT), ("family", bn.FAMILY), ("n", bt.N_ITEMS),
                 ("seal_tag", seal_tag), ("dtype", bn.DTYPE_2N),
                 ("render", bn.RENDER_2N)):'''),
    (AN, "step_record_failures_2n: endpoint_sha256 check removed",
     '''    if rec.get("endpoint_sha256") != endpoint_sha:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")''',
     '''    if False:
        bad.append(f"{label}: endpoint_sha256 {rec.get('endpoint_sha256')!r} is not the composite "
                   f"re-derived from the committed endpoint files {endpoint_sha!r}")'''),
    (AN, "step_record_failures_2n: the twin's kind check removed",
     '''        if rec.get("kind") != "from_config":
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")''',
     '''        if False:
            bad.append(f"{label}: kind = {rec.get('kind')!r}, expected 'from_config'")'''),
    (AN, "step_record_failures_2n: commit check removed",
     '''    elif rec.get("commit") != entry["commit"]:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")''',
     '''    elif False:
        bad.append(f"{label}: commit {rec.get('commit')} is not the manifest's {entry['commit']}")'''),
    (AN, "checkpoint_record_failures_2n: generation_eos_token_id check removed",
     '''    if crec.get("generation_eos_token_id") != bn.EOS_STOP_ID_2N:
        bad.append(f"comma_7b/step{int(step)}: checkpoint record generation_eos_token_id "
                   f"{crec.get('generation_eos_token_id')!r} is not the pinned stop id "
                   f"{bn.EOS_STOP_ID_2N} — the loader did not apply set_eos_stop_2n")''',
     '''    if False:
        bad.append(f"comma_7b/step{int(step)}: checkpoint record generation_eos_token_id "
                   f"{crec.get('generation_eos_token_id')!r} is not the pinned stop id "
                   f"{bn.EOS_STOP_ID_2N} — the loader did not apply set_eos_stop_2n")'''),
    (AN, "twin_checkpoint_record_failures_2n: seed check removed",
     '    if crec.get("seed") != bn.TWIN_SEED:',
     '    if False:'),
    (AN, "twin_checkpoint_record_failures_2n: generation_eos_token_id check removed",
     '''    if crec.get("generation_eos_token_id") != bn.EOS_STOP_ID_2N:
        bad.append(f"comma_7b/twin: checkpoint record generation_eos_token_id "
                   f"{crec.get('generation_eos_token_id')!r} is not the pinned stop id "
                   f"{bn.EOS_STOP_ID_2N} — the loader did not apply set_eos_stop_2n")''',
     '''    if False:
        bad.append(f"comma_7b/twin: checkpoint record generation_eos_token_id "
                   f"{crec.get('generation_eos_token_id')!r} is not the pinned stop id "
                   f"{bn.EOS_STOP_ID_2N} — the loader did not apply set_eos_stop_2n")'''),
    (AN, "load_sweep_comma: steps default without the TWIN",
     '    steps = tuple(steps) if steps is not None else bn.GRID_COMMA + (bn.TWIN,)',
     '    steps = tuple(steps) if steps is not None else bn.GRID_COMMA'),
    (AN, "load_sweep_comma: LFS sha check removed",
     '''            for name, want in entry.get("lfs_sha256", {}).items():
                if crec.get("sha256", {}).get(name) != want:''',
     '''            for name, want in entry.get("lfs_sha256", {}).items():
                if False:'''),
    (AN, "load_sweep_comma: the twin routed through the generic checkpoint check",
     '''        if step == bn.TWIN:
            cbad = twin_checkpoint_record_failures_2n(crec, entry=entry, step_records=out[step])''',
     '''        if step == bn.TWIN:
            cbad = checkpoint_record_failures_2n(crec, step=0, entry=entry, step_records=out[step])'''),
    (AN, "outcomes_comma: steps default -> GRID_COMMA + (TWIN,) (the twin leaks into an outcome)",
     '    steps = tuple(steps) if steps is not None else bn.trained_steps_comma()',
     '    steps = tuple(steps) if steps is not None else bn.GRID_COMMA + (bn.TWIN,)'),
    (AN, "outcomes_comma: the off-grid steps refusal removed",
     '''    if any(s not in bn.GRID_COMMA for s in steps):
        raise ValueError(f"outcomes_comma: steps {steps} are not all on the frozen grid")''',
     '''    if False:
        raise ValueError(f"outcomes_comma: steps {steps} are not all on the frozen grid")'''),
    (AN, "ceiling_fraction_comma: v == n_steps -> v >= 1",
     '        n_c = int(sum(1 for v in y if v == n_steps))',
     '        n_c = int(sum(1 for v in y if v >= 1))'),
    (AN, "_load_rung_set_2n: subset-of-nine check removed",
     '''    if not set(rec["R_PRIMARY"]).issubset(set(bn.R_CAP_2K)):
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")''',
     '''    if False:
        raise ValueError(f"{p}: R_PRIMARY is not a subset of 2k's nine")'''),
    (AN, "_load_rung_set_2n: partition check removed",
     '''    if set(rec["R_PRIMARY"]) | set(rec["R_ELEVEN_EXTRA"]) | set(rec["R_EXTRA"]) != set(rec["R_COMMA"]):
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_COMMA")''',
     '''    if False:
        raise ValueError(f"{p}: R_PRIMARY/R_ELEVEN_EXTRA/R_EXTRA do not partition R_COMMA")'''),
    (AN, "_check_rung_set_derivation_2n: per-key comparison -> set equality (order-blind)",
     '''        want, got = list(rung_set.get(key, [])), list(red[key])
        if got != want:''',
     '''        want, got = list(rung_set.get(key, [])), list(red[key])
        if set(got) != set(want):'''),
    (AN, "_check_rung_set_endpoint_shas_2n: per-file comparison removed",
     '''    for rel in sorted(set(want) & set(got)):
        if got[rel] != want[rel]:''',
     '''    for rel in sorted(set(want) & set(got)):
        if False:'''),
    (AN, "_check_rung_set_endpoint_shas_2n: coverage check removed",
     '''    if missing:
        bad.append(f"rung set comma_7b: endpoint_file_sha256 attests nothing for {missing}")''',
     '''    if False:
        bad.append(f"rung set comma_7b: endpoint_file_sha256 attests nothing for {missing}")'''),
    (AN, "_endpoint_seal_paths_2n: only two whichs bound by the seal",
     '''def _endpoint_seal_paths_2n(root) -> list:
    paths = [bn.rung_set_path(root), bn.power_path(root)]
    for which in bn.ENDPOINT_WHICH_2N:''',
     '''def _endpoint_seal_paths_2n(root) -> list:
    paths = [bn.rung_set_path(root), bn.power_path(root)]
    for which in ("stage1_final", "stage2_final"):'''),
    (AN, "load_predictors_2n: the 2k-seal literal check removed",
     '''    if isinstance(seal_2k, dict) and seal_2k.get("sha256") != bn.SEAL_2K_SHA256:
        failures.append(f"2n predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")''',
     '''    if False:
        failures.append(f"2n predictor 2k seal sha {seal_2k.get('sha256')!r} is not the literal")'''),
    (AN, "load_predictors_2n: the 2i-seal literal check removed",
     '''    if isinstance(seal_2i, dict) and seal_2i.get("sha256") != bn.SEAL_2I_SHA256:
        failures.append(f"2n predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")''',
     '''    if False:
        failures.append(f"2n predictor 2i seal sha {seal_2i.get('sha256')!r} is not the literal")'''),
    (AN, "load_predictors_2n: the seal_failures_2k call removed",
     '        if seal_2k is not None and all(len(cells_2k.get(s, {})) == len(bn.R_CAP_2K) for s in bk.SIZES_2K):',
     '        if False and all(len(cells_2k.get(s, {})) == len(bn.R_CAP_2K) for s in bk.SIZES_2K):'),
    (AN, "load_predictors_2n: the _check_predictor_counts_2i call removed",
     '    if seal_2i is not None and records_2i is not None and x_b is not None:',
     '    if False:'),
    (AN, "load_predictors_2n: R_CAP == nine check removed",
     '''    if rs2i is not None and tuple(sorted(rs2i["R_CAP"])) != tuple(sorted(bn.R_CAP_2K)):
        failures.append(f"2n predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")''',
     '''    if False:
        failures.append(f"2n predictor 2i rung set: R_CAP {sorted(rs2i['R_CAP'])} != 2k's nine")'''),
    (AN, "load_predictors_2n: x_B bits do not reproduce raise removed",
     '''            if fn.counts_from_bits(bits[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")''',
     '''            if False:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")'''),
    (AN, "load_predictors_2n: the halt-marker scan removed",
     '''    for m in bk.halt_markers(root_2k):
        failures.append(f"2n predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")''',
     '''    for m in []:
        failures.append(f"2n predictor 2k tier HALTED marker present: {m.parent.name}/{m.name}")'''),
    (AN, "run()/_core: Test B on 2m's composite strata (drops dial b's unconditioned form)",
     '            B = _run_test(x_b, bi.SIZE_PRED, out, strata, r_primary, n_perm=n_perm, n_boot=n_boot)',
     '            B = _run_test(x_b, bi.SIZE_PRED, out, an2i._composite_strata_median(strata, x256, r_primary),\n'
     '                          r_primary, n_perm=n_perm, n_boot=n_boot)'),
    (AN, "run()/_core: Test A predictor -> counts[64] instead of counts[K_TOTAL]",
     '            x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL] for r in r_primary}',
     '            x256 = {r: cells_2k["1b"][r]["counts"][64] for r in r_primary}'),
    (AN, "check_imports_2n: 'tests' in rp.parts swallows everything -> True",
     '        if not s.startswith(_EXPERIMENTS_ROOT_2N + "/") or "tests" in rp.parts:',
     '        if not s.startswith(_EXPERIMENTS_ROOT_2N + "/") or True:'),
    (AN, "s3_paired_difference_2n: the difference sign flipped (b - a -> a - b)",
     '            diffs.append(b - a)',
     '            diffs.append(a - b)'),
    (AN, "s3_paired_difference_2n: the bootstrap unpaired (A and B on DIFFERENT index draws)",
     '        a, b = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})',
     '        a, _b0 = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})\n'
     '        _a0, b = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})'),
    (AN, "s4_matched_2n: increment sign flipped",
     '            "increment": (None if t_b is None or t_a["T"] is None else t_b - t_a["T"])}',
     '            "increment": (None if t_b is None or t_a["T"] is None else t_a["T"] - t_b)}'),
    (AN, "thinned_x_b_2n: row[:k] -> row[-k:] (the LAST block)",
     '        x_thin[r] = [int(sum(row[:k])) for row in bits_b[r]]',
     '        x_thin[r] = [int(sum(row[-k:])) for row in bits_b[r]]'),
    (AN, "thinned_x_b_2n: row[:k] -> row[:64] (no thinning)",
     '        x_thin[r] = [int(sum(row[:k])) for row in bits_b[r]]',
     '        x_thin[r] = [int(sum(row[:64])) for row in bits_b[r]]'),
    (AN, "paired_contrast_2n: the resampling groups drawn on DIFFERENT index draws",
     '    for _ in range(n_boot if rungs else 0):\n'
     '        c = _contrast(_t({r: rng.integers(0, n, size=n).tolist() for r in rungs}))',
     '    for _ in range(n_boot if rungs else 0):\n'
     '        ts_a = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})\n'
     '        ts_b = _t({r: rng.integers(0, n, size=n).tolist() for r in rungs})\n'
     '        c = _contrast({**{k: v for k, v in ts_a.items() if k in group_a},\n'
     '                       **{k: v for k, v in ts_b.items() if k in group_b}})'),
    (AN, "paired_contrast_2n: _contrast a - b -> b - a",
     '        return float(np.mean(a) - np.mean(b))',
     '        return float(np.mean(b) - np.mean(a))'),
    (AN, "annotation_c_2n: ci[0] > 0 -> >= 0",
     '    elif ci[0] > 0:',
     '    elif ci[0] >= 0:'),
    (AN, "annotation_c_2n: ci[1] < 0 -> <= 0",
     '    elif ci[1] < 0:',
     '    elif ci[1] <= 0:'),
    (AN, "annotation_c_2n: the B-LEADS/A-LEADS branches swapped",
     '''    elif ci[0] > 0:
        reading = "B-LEADS"
    elif ci[1] < 0:
        reading = "A-LEADS"''',
     '''    elif ci[0] > 0:
        reading = "A-LEADS"
    elif ci[1] < 0:
        reading = "B-LEADS"'''),
    (AN, "annotation_c_2n: covers -> not covers",
     '    covers = (ci is not None) and (ci[0] <= increment_3b <= ci[1])',
     '    covers = (ci is not None) and not (ci[0] <= increment_3b <= ci[1])'),
    (AN, "read_increment_3b_2n: returning the literal instead of the file's value",
     '    return float(inc)',
     '    return float(INCREMENT_3B_2N)'),
    (AN, "s5_answer_prior_2n: non_gating True -> False",
     '            "non_gating": True, "no_alpha_claim": True, "note": NO_ALPHA_NOTE_2N.format(name="S5"),',
     '            "non_gating": False, "no_alpha_claim": True, "note": NO_ALPHA_NOTE_2N.format(name="S5"),'),
    (AN, "s8_outcome_order_2n: descriptive True -> False",
     '                     "descriptive": True, "no_alpha_claim": True,\n'
     '                     "note": NO_ALPHA_NOTE_2N.format(name="S8")}',
     '                     "descriptive": False, "no_alpha_claim": True,\n'
     '                     "note": NO_ALPHA_NOTE_2N.format(name="S8")}'),
    (AN, "s8_outcome_order_2n: every rung of the committed outcome, not R_PRIMARY ∩ it",
     '        rungs_k = [r for r in r_primary if r in out_k]',
     '        rungs_k = [r for r in out_k]'),
    (AN, "collapses_comma: threshold >= -> >",
     '            if n >= threshold:',
     '            if n > threshold:'),
    (AN, "run(): the post-secondaries import re-check does not refuse",
     '''            if f:
                failures += f
                referents["failures"] = list(failures)
                t2 = verdict_2n(failures, None, None, None, ())''',
     '''            if False:
                failures += f
                referents["failures"] = list(failures)
                t2 = verdict_2n(failures, None, None, None, ())'''),
    (AN, "run(): the annotation C failure misrouted away from `failures`",
     '''        if fC:
            failures += fC''',
     '''        sec_failures_c = []
        if fC:
            sec_failures_c += fC'''),
    (AN, "sensitivities: every40k_subset computed over bn.GRID_COMMA, not EVERY40K_SUBSET_2N",
     '                sub = outcomes_comma(sweep, rungs=tuple(bt.RUNGS), steps=bn.EVERY40K_SUBSET_2N)',
     '                sub = outcomes_comma(sweep, rungs=tuple(bt.RUNGS), steps=bn.GRID_COMMA)'),
    (AN, "sensitivities: every40k_subset 'control' True -> False",
     '                                            "control": True,',
     '                                            "control": False,'),
    (AN, "s8c_corpus_contrast_2n: groups swapped",
     '    pc = paired_contrast_2n({k: rows[k] for k in pile}, {k: rows[k] for k in dclm}, out, strata, rungs,',
     '    pc = paired_contrast_2n({k: rows[k] for k in dclm}, {k: rows[k] for k in pile}, out, strata, rungs,'),
    (AN, "s8c_corpus_contrast_2n: the smollm3_3b row dropped from dclm",
     '    dclm = ["olmo2_7b", "olmo2_13b", "smollm3_3b"]',
     '    dclm = ["olmo2_7b", "olmo2_13b"]'),
    (AN, "load_committed_outcomes_2n: the smollm3_3b key dropped",
     '''    return {"pythia_2.8b": py["2.8b"], "pythia_6.9b": py["6.9b"], "olmo2_7b": out7b, "olmo2_13b": out13b,
            "smollm3_3b": out3b}''',
     '''    return {"pythia_2.8b": py["2.8b"], "pythia_6.9b": py["6.9b"], "olmo2_7b": out7b, "olmo2_13b": out13b}'''),
    (AN, "s9_sign_ledger_2n: OPTION_RUNGS_2N -> the nine",
     '    for r in OPTION_RUNGS_2N:',
     '    for r in bn.R_CAP_2K:'),
    # ---- freeze F-1: the reading-narrower-than-R_PRIMARY disclosure (2l/2m's lineage)
    (AN, "F-1: _partial_eligible_2n never speaks (the pre-freeze behaviour)",
     '    if len(elig) < 3 or len(elig) >= len(prim):\n        return None',
     '    if True:\n        return None'),
    (AN, "F-1: verdict_2n does not consult _partial_eligible_2n",
     '''        else:
            d2 = _partial_eligible_2n(
                test, res, r_primary,
                rungs_simulated=(power or {}).get(test, {}).get("rungs_simulated"))   # freeze F-1 / R-1
            if d2:
                disclosures.append(d2)''',
     '''        else:
            d2 = None
            if d2:
                disclosures.append(d2)'''),
    (AN, "F-1: the partial disclosure names the rungs READ, not the rungs missed",
     '    missing = [r for r in prim if r not in elig]',
     '    missing = [r for r in prim if r in elig]'),
    (AN, "R-1 (2m's lineage): the SAME/WIDER decision inverted, so the wrong scope clause prints",
     '    same = bool(sim) and sim == sorted(set(elig))',
     '    same = not (bool(sim) and sim == sorted(set(elig)))'),
    # ---- freeze F-2 lineage: a which assembled from two loads
    (AN, "F-2: which_coherence_failures_2n never speaks",
     '''    for field, label in (("weight_sha256", "tensor digest"), ("commit", "commit"),
                         ("config_source", "config source")):''',
     '''    for field, label in ():'''),
    (AN, "F-2: load_endpoint_which_2n does not apply the coherence check",
     '''    coh = which_coherence_failures_2n(which, out)   # freeze F-2
    if coh:
        raise ValueError("; ".join(coh))''',
     '''    coh = []
    if coh:
        raise ValueError("; ".join(coh))'''),
]

# One mutant per collect_total(...) call site in analyze_2n.py's run() AND
# load_predictors_2n, generated from the real, current source at import
# time rather than hand-picked (2j's Finding 4 lesson, applied at build
# time by 2k/2l/2m/2n alike — this file has several functions with
# collect_total sites, not one, and _totality_mutants walks the whole
# file).
M += _totality_mutants(AN)

# Task 5 ruling: fast modules only by default (test_battery_2n.py,
# test_stages_2n.py, test_analyze_2n.py, test_power_2n.py with the
# real-tree/slow cases deselected — they take minutes and observe
# nothing a fast mutant changes). A `--totality` flag switches the
# covering suite to TOTALITY_TESTS (test_totality_2n.py alone) so a
# totality-only kill is reproducible from the committed harness, not a
# scratch script; `--fullshape` switches to test_full_shape_2n.py for
# the handful of shapes only a synthetic-Comma-tree world can observe
# (the endpoint-composite/gate-1/power-record byte-level corruptions).
FAST_TESTS = [str(L / "tests" / "test_battery_2n.py"), str(L / "tests" / "test_stages_2n.py"),
             str(L / "tests" / "test_analyze_2n.py"), str(L / "tests" / "test_power_2n.py")]

# M-6 (2m's final review, carried forward): these are SUBSTRING matches
# against the pytest node id (`-k`), not exact test-name matches — any
# future fast test whose name happens to contain one of these substrings
# silently drops out of the mutation fast pass.
FAST_EXTRA_ARGS = ["-m", "not slow", "-k",
                  "not test_run_on_empty_tree and not test_s4 and not test_s5 and not real_trees "
                  "and not real_tree and not test_read_increment and not test_s9_sign"]
TOTALITY_TESTS = [str(L / "tests" / "test_totality_2n.py")]
FULLSHAPE_TESTS = [str(L / "tests" / "test_full_shape_2n.py")]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2n" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def _refuse_if_any_backup_exists() -> None:
    """2k's Finding 3 lesson, applied from commit one: a stray
    `.mutation_backup` anywhere under `experiments/exp2n` means either a
    concurrent run is already in flight or a previous run crashed
    without restoring — either way, starting a NEW run on top of it
    corrupts the restore. Refuse before the baseline check even
    starts."""
    found = sorted((ROOT / "experiments" / "exp2n").rglob("*.mutation_backup"))
    if found:
        raise RuntimeError(f"refusing: {len(found)} .mutation_backup file(s) already present "
                           f"under experiments/exp2n (a concurrent run, or a previous crash that "
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
