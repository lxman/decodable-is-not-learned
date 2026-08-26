# experiments/exp2i/tests/mutation_check.py
"""Mutation-test exp2i's OWN modules — battery_2i, analyze_2i,
power_2i, run/sample_2i, run/endpoint_2i, run/seal_2i, run/sweep_2i
(the code new to this experiment; the frozen exp2h/exp2g/exp2d/exp2c/
exp3/exp3c modules it imports/mirrors have their own mutation
batteries and are not re-targeted here). Categories per Task 4's
ruling 6: grid/revision, candidate/signature refusal, tokenizer
asserts, rung-set bar, composite-strata bucket, firing rule
boundaries, world table, gate-1 coverage, a representative slice of
totality (`collect_total` stripped at a call site — not literally
every one of run()'s ~27 sites; the ones covered are the ones a
dedicated `test_totality_2i.py` world already exercises as a failure,
so a stripped wrapper is guaranteed reachable and killable — disclosed
scope reduction, not the full site count), seal/prereg refusals,
runner order/halt/free, sampling row format, power write-once,
fires_2i shared. Mutates sources IN PLACE and restores them — run
alone, detached (nohup), never under a foreground timeout."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
I = ROOT / "experiments/exp2i"
BI = I / "battery_2i.py"
AN = I / "analyze_2i.py"
PW = I / "power_2i.py"
SM = I / "run/sample_2i.py"
EP = I / "run/endpoint_2i.py"
SL = I / "run/seal_2i.py"
SW = I / "run/sweep_2i.py"

M = [
    # -------------------------------------------------------- battery_2i.py
    (BI, "revision_of_7b: off-grid step check inert",
     "    if step_i not in GRID_7B:",
     "    if False:"),
    (BI, "build_manifest: duplicate-signature refusal inert",
     "        if step != ENDPOINT_STEP_7B and same:",
     "        if False:"),
    (BI, "check_tokenizer: padding_side check inert",
     '    if side != "left":',
     "    if False:"),
    (BI, "check_tokenizer: pad_token_id check inert",
     "    if pad_id != PAD_TOKEN_ID:",
     "    if False:"),
    (BI, "check_tokenizer: BOS-prefix check inert",
     "    if first_id in specials:",
     "    if False:"),
    (BI, "rung_set_from_counts: significance bar inert (accepts every rung)",
     '    r_olmo = tuple(r for r in sorted(counts) if per_rung[r]["significant"])',
     "    r_olmo = tuple(r for r in sorted(counts))"),
    (BI, "check_frozen_2i: sha comparison inert",
     "        got = bg.sha256_file(path)\n        if got != want:",
     "        got = bg.sha256_file(path)\n        if False:"),
    (BI, "check_pythia_predictor_files: sha comparison inert",
     "        got = bg.sha256_file(p)\n        if got != want:",
     "        got = bg.sha256_file(p)\n        if False:"),
    (BI, "sampler_counts_olmo: seed key read as int (KeyError on the real "
         "str-keyed row format)",
     'row["draws"][str(SAMPLING_SEED)]',
     'row["draws"][SAMPLING_SEED]'),
    # -------------------------------------------------------- analyze_2i.py
    (AN, "require_prereg_2i: tag-existence check inert",
     "    if not tag_exists(bi.PREREG_TAG):",
     "    if False:"),
    (AN, "require_prereg_2i: instrument-drift check inert",
     "    if drift:\n        raise RuntimeError(f\"refusing: the instrument has drifted from \"\n"
     "                           f\"{bi.PREREG_TAG!r} — {'; '.join(drift)}\")",
     "    if False:\n        raise RuntimeError(f\"refusing: the instrument has drifted from \"\n"
     "                           f\"{bi.PREREG_TAG!r} — {'; '.join(drift)}\")"),
    (AN, "require_seal_2i: tag-existence check inert (always 'exists')",
     "    if not exists:\n        return {\"tag\": tag, \"n_paths\": len(paths),\n"
     "                \"failures\": [f\"the tag {tag!r} does not exist\"]}",
     "    if False:\n        return {\"tag\": tag, \"n_paths\": len(paths),\n"
     "                \"failures\": [f\"the tag {tag!r} does not exist\"]}"),
    (AN, "require_seal_2i: blob-drift check inert",
     "    if drift:\n        return {\"tag\": tag, \"n_paths\": len(paths),\n"
     "                \"failures\": [f\"{tag!r} does not bind {sorted(drift)}\"]}",
     "    if False:\n        return {\"tag\": tag, \"n_paths\": len(paths),\n"
     "                \"failures\": [f\"{tag!r} does not bind {sorted(drift)}\"]}"),
    (AN, "gate1_failures_7b: bit-diff check inert",
     "        if bd.get(r) != 0:",
     "        if False:"),
    (AN, "gate1_failures_7b: continuation-diff check inert",
     "        if cd.get(r) != 0:",
     "        if False:"),
    (AN, "gate1_failures_7b: coverage (continuations_compared) check inert (F-2)",
     "        if nc.get(r) != bt.N_ITEMS:",
     "        if False:"),
    (AN, "gate1_failures_7b: commit-equality check inert",
     "    if not cs or not ce or cs != ce:",
     "    if False:"),
    (AN, "gate1_failures_7b: digest-equality check inert",
     "    if not dg_s or not dg_e or dg_s != dg_e:",
     "    if False:"),
    (AN, "gate1_failures_7b: prereg_tag check inert",
     '    if rec.get("prereg_tag") != bi.PREREG_TAG:',
     "    if False:"),
    (AN, "fires_2i: p-value boundary loosened (<= instead of <)",
     "    return bool(p < ALPHA and T >= T_BAR)",
     "    return bool(p <= ALPHA and T >= T_BAR)"),
    (AN, "fires_2i: T-effect boundary tightened (> instead of >=)",
     "    return bool(p < ALPHA and T >= T_BAR)",
     "    return bool(p < ALPHA and T > T_BAR)"),
    (AN, "verdict_tree_2i: SHARED/LINEAGE swapped",
     '        verdict = "SHARED"',
     '        verdict = "LINEAGE"'),
    (AN, "_composite_strata: zero-cut boundary widened (>= 0, always true)",
     "int(c > 0)",
     "int(c >= 0)"),
    (AN, "_degenerate_rungs: single-value-per-stratum drop rule inert",
     "        if all(len(vals) < 2 for vals in by_stratum.values()):",
     "        if False:"),
    (AN, "run(): totality — predictor seal content no longer behind a refusal",
     '    predictor_rec, f = collect_total(lambda: _load_predictor_seal_content(root),\n'
     '                                     "predictor seal content")\n'
     '    failures += f',
     '    predictor_rec = (lambda: _load_predictor_seal_content(root))()\n'
     '    f = []\n'
     '    failures += f'),
    (AN, "run(): totality — rung set no longer behind a refusal",
     '    rung_set, f = collect_total(lambda: _load_rung_set(root), "rung set")\n'
     '    failures += f',
     '    rung_set = (lambda: _load_rung_set(root))()\n'
     '    f = []\n'
     '    failures += f'),
    (AN, "run(): totality — power record no longer behind a refusal",
     '    power, f = collect_total(lambda: _load_power(root), "power record")\n'
     '    failures += f',
     '    power = (lambda: _load_power(root))()\n'
     '    f = []\n'
     '    failures += f'),
    (AN, "run(): totality — gate1.json parse no longer behind a refusal",
     '        gate1, f = collect_total(lambda: json.loads(g1p.read_text()),\n'
     '                                 "gate 1 olmo7b record")\n'
     '        failures += f',
     '        gate1 = (lambda: json.loads(g1p.read_text()))()\n'
     '        f = []\n'
     '        failures += f'),
    (AN, "run(): totality — stage1_final endpoint load no longer behind a refusal",
     '    stage1_final, f = collect_total(\n'
     '        lambda: load_endpoint_which(root, "stage1_final", battery, verify_fn,\n'
     '                                    entry=entry_stage1,\n'
     '                                    predictor_sha=predictor_rec["sha256"])\n'
     '        if _stage1_ready else\n'
     '        (_ for _ in ()).throw(ValueError("battery, verify criterion, predictor "\n'
     '                                         "seal or manifest entry missing")),\n'
     '        "endpoint stage1_final")\n'
     '    failures += f',
     '    stage1_final = (\n'
     '        lambda: load_endpoint_which(root, "stage1_final", battery, verify_fn,\n'
     '                                    entry=entry_stage1,\n'
     '                                    predictor_sha=predictor_rec["sha256"])\n'
     '        if _stage1_ready else\n'
     '        (_ for _ in ()).throw(ValueError("battery, verify criterion, predictor "\n'
     '                                         "seal or manifest entry missing")))()\n'
     '    f = []\n'
     '    failures += f'),
    (AN, "run(): totality — sweep load no longer behind a refusal",
     '    sweep, f = collect_total(\n'
     '        lambda: load_sweep_7b(root, battery, verify_fn, manifest=manifest,\n'
     '                              predictor_sha=predictor_rec["sha256"]) if _sweep_ready\n'
     '        else (_ for _ in ()).throw(ValueError("manifest, battery, verify criterion "\n'
     '                                              "or predictor seal missing")),\n'
     '        "sweep olmo7b")\n'
     '    failures += f',
     '    sweep = (\n'
     '        lambda: load_sweep_7b(root, battery, verify_fn, manifest=manifest,\n'
     '                              predictor_sha=predictor_rec["sha256"]) if _sweep_ready\n'
     '        else (_ for _ in ()).throw(ValueError("manifest, battery, verify criterion "\n'
     '                                              "or predictor seal missing")))()\n'
     '    f = []\n'
     '    failures += f'),
    # ------------------------------------------------------------ power_2i.py
    (PW, "main(): write-once guard inert (silently overwrites)",
     "    if out_path.exists():",
     "    if False:"),
    (PW, "_one: fires_2i re-derived locally instead of shared",
     '    fires = an.fires_2i({"stratified": strat})',
     '    fires = bool(strat["p"] <= an.ALPHA and strat["T"] > an.T_BAR)'),
    (PW, "_one_test_power: declared_status bar tightened (> instead of >=)",
     '    rec["declared_status"] = ("POWERED" if declare_p >= BAR',
     '    rec["declared_status"] = ("POWERED" if declare_p > BAR'),
    (PW, "_one_test_power: thin threshold off by one",
     '          "thin": len(rungs) < 3, "targets": {}}',
     '          "thin": len(rungs) < 2, "targets": {}}'),
    # ------------------------------------------------------ run/sample_2i.py
    (SM, "run_sampling_rung: rung skip-if-exists disabled",
     "    if out.exists() and dpath.exists():",
     "    if False:"),
    (SM, "run_sampling_rung: verify_fn ignored in the tally (counts every draw)",
     '                  if verify_fn(d, answers[row["item"]], cap["answer_type"]))',
     "                  if True)"),
    (SM, "run(): already-sealed refusal inert",
     "    if seal_path.exists():",
     "    if False:"),
    # ---------------------------------------------------- run/endpoint_2i.py
    (EP, "item_record_2i: exactly-one-of-step/which check inert",
     "    if (step is None) == (which is None):",
     "    if False:"),
    (EP, "_require_predictor_seal: missing-file check inert",
     "    if not seal_path.is_file():",
     "    if False:"),
    (EP, "_require_predictor_seal: blob-drift check inert",
     "    drift = blobs_bound(bi.PREDICTOR_SEAL_TAG, rel_paths, repo_root=rr)\n    if drift:",
     "    drift = blobs_bound(bi.PREDICTOR_SEAL_TAG, rel_paths, repo_root=rr)\n    if False:"),
    (EP, "run(): per-which full-skip check inert (reloads an already-complete which)",
     "        if not which_pending:",
     "        if False:"),
    # -------------------------------------------------------- run/seal_2i.py
    (SL, "seal_predictor: already-sealed guard inert",
     "    if out_path.exists():",
     "    if False:"),
    (SL, "seal_predictor: missing draws+record pair check inert",
     "    if missing:",
     "    if False:"),
    # ------------------------------------------------------- run/sweep_2i.py
    (SW, "run(): prereg refusal replaced by a stub tag (no real check)",
     "    prereg = require_prereg_2i(tag_exists=tag_exists, blob_sha=blob_sha)",
     '    prereg = {"tag": bi.PREREG_TAG}'),
    (SW, "run(): frozen-imports check not called",
     "    bi.check_frozen_2i()",
     "    pass"),
    (SW, "run(): predictor-seal check not called",
     "    _require_predictor_seal(out_root, blobs_bound=blobs_bound, repo_root=repo_root)",
     "    pass"),
    (SW, "run(): endpoint-seal check not called",
     "    _require_endpoint_seal(out_root, blobs_bound=blobs_bound, repo_root=repo_root)",
     "    pass"),
    (SW, "run(): halted-tree resume not refused",
     "    if bi.halt_marker_path(out_root).exists():",
     "    if False:"),
    (SW, "run(): dry-run no longer short-circuits (would build a real loader)",
     "    if dry_run:",
     "    if False:"),
    (SW, "run(): on-disk gate1 record not re-derived on resume",
     "        bad = gate1_failures_7b(json.loads(g1.read_text()), stage1_final)",
     "        bad = []"),
    (SW, "run(): incomplete-final-step-records check inert on resume",
     "        if not records_complete_7b(out_root, bi.ENDPOINT_STEP_7B):",
     "        if False:"),
    (SW, "run_gate1: failure check inert (never halts, no matter the diff)",
     "    bad = gate1_failures_7b(gate_rec, stage1_final)\n    if bad:",
     "    bad = gate1_failures_7b(gate_rec, stage1_final)\n    if False:"),
    (SW, "run_gate1: HALTED marker not written on failure",
     '        bi.halt_marker_path(out_root).write_text("\\n".join(bad) + "\\n")',
     "        pass"),
    (SW, "run_gate1: free_checkpoint not called (cache survives the gate)",
     '    finally:\n        _release(model)\n        loaders["free"](entry["revision"], cache_root)\n'
     '\n    digest_endpoint = stage1_final[rungs[0]].get("weight_sha256")',
     '    finally:\n        _release(model)\n'
     '\n    digest_endpoint = stage1_final[rungs[0]].get("weight_sha256")'),
    (SW, "run_step: free_checkpoint not called (cache survives the step)",
     '    finally:\n        _release(model)\n        loaders["free"](entry["revision"], cache_root)\n'
     '    print(f"[2i sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)',
     '    finally:\n        _release(model)\n'
     '    print(f"[2i sweep] step{step} done in {time.time() - t0:.0f} s", flush=True)'),
    (SW, "run_step: skip-if-exists disabled (re-runs an already-complete step)",
     "    if records_complete_7b(out_root, step):\n        return",
     "    if False:\n        return"),
    (SW, "run_twin: skip-if-exists disabled (re-runs the twin)",
     "    if records_complete_7b(out_root, bi.TWIN):\n        return",
     "    if False:\n        return"),
    (SW, "_require_endpoint_seal: rung_set/power existence check inert",
     "    if not bi.rung_set_path(root).is_file() or not bi.power_path(root).is_file():",
     "    if False:"),
    (SW, "_require_endpoint_seal: blob-drift check inert",
     "    drift = blobs_bound(bi.ENDPOINT_SEAL_TAG, rel_paths, repo_root=rr)\n    if drift:",
     "    drift = blobs_bound(bi.ENDPOINT_SEAL_TAG, rel_paths, repo_root=rr)\n    if False:"),
]

TESTS = [str(I / "tests")]
DESELECT = ["--deselect", "experiments/exp2i/tests/test_full_shape_2i.py"]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2i" in str(d):
            shutil.rmtree(d, ignore_errors=True)


def run_suite():
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        *TESTS, *DESELECT], cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode == 0, r.stdout[-600:]


def main(argv=None) -> int:
    clear_pycache()
    ok, out = run_suite()
    if not ok:
        print("BASELINE FAILS — fix the suite first\n", out)
        return 2
    survivors = []
    for i, (path, name, old, new) in enumerate(M, 1):
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
            ok, out = run_suite()
        finally:
            shutil.copy2(backup, path)
            backup.unlink()
            clear_pycache()
        print(f"[{i:2d}] {'killed' if not ok else 'SURVIVED'}  {name}", flush=True)
        if ok:
            survivors.append((i, name, "survived"))
    print(f"\n{len(M) - len(survivors)}/{len(M)} killed; survivors: {survivors}")
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
