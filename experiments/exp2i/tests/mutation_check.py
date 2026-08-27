# experiments/exp2i/tests/mutation_check.py
"""Mutation-test exp2i's OWN modules — battery_2i, analyze_2i,
power_2i, run/sample_2i, run/endpoint_2i, run/seal_2i, run/sweep_2i
(the code new to this experiment; the frozen exp2h/exp2g/exp2d/exp2c/
exp3/exp3c modules it imports/mirrors have their own mutation
batteries and are not re-targeted here). Categories per Task 4's
ruling 6: grid/revision, candidate/signature refusal, tokenizer
asserts, rung-set bar, composite-strata bucket, firing-rule boundaries
(p/T, plus the `named_inside_2i` sign branch — distinct from the
world-table swap below, corrected wording per review round 1 finding
3), world table (`verdict_tree_2i`'s SHARED/LINEAGE swap), gate-1
coverage, TOTALITY AT EVERY `collect_total` CALL SITE in `run()`
(review round 1 finding 4 — generated programmatically, below, one
mutant per site via AST source-segment extraction; NOT a hand-picked
subset), seal/prereg refusals, runner order/halt/free, sampling row
format, power write-once, `fires_2i` shared. Mutates sources IN PLACE
and restores them — run alone, detached (nohup), never under a
foreground timeout."""
import ast
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


def _totality_mutants(path: Path) -> list:
    """One mutant per `collect_total(thunk, label)` call site in
    `path`'s source (review finding 4 — every site, not a hand-picked
    subset). Found via the AST rather than a regex, so multi-line
    lambda/ternary/generator-throw thunks are captured exactly as
    written: any `Call` node whose function is named `collect_total`
    (bare name or `mod.collect_total`) is replaced, VERBATIM at that
    exact source span, by `(thunk(), [])` — a plain tuple that still
    unpacks correctly wherever the call site reads `NAME, f =
    collect_total(...)`, but calls the thunk directly, uncaught, and
    reports zero failures regardless of what the thunk does. A site
    whose thunk is not a lambda/bare-callable (none in this file) or
    whose exact text is not unique in the source is skipped by main()'s
    own `count(old) != 1` guard, printed as a surviving SKIP rather
    than silently omitted."""
    src = path.read_text()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.id if isinstance(func, ast.Name) else
                func.attr if isinstance(func, ast.Attribute) else None)
        if name != "collect_total" or not node.args:
            continue
        full = ast.get_source_segment(src, node)
        thunk = ast.get_source_segment(src, node.args[0])
        if full is None or thunk is None:
            continue
        out.append((path, f"run(): totality — collect_total stripped at line "
                          f"{node.lineno} ({thunk.splitlines()[0][:60]}...)",
                   full, f"(({thunk})(), [])"))
    return out


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
    (BI, "clean_dir: pinned config.json write stripped (campaign stop #1's "
         "weights-only clean dir)",
     '    config.to_json_file(str(d / "config.json"))\n    return d',
     '    return d'),
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
    (AN, "named_inside_2i: sign branch flipped (T > 0 instead of T < 0)",
     "    if T < 0:",
     "    if T > 0:"),
    # ---------------------------------------- whole-branch review fix wave
    (AN, "run(): gate-1 re-derivation ignored (failures dropped on the floor)",
     "    failures += f + (g2bad or [])",
     "    failures += f"),
    (AN, "gate1_rederive_7b: continuation diff not re-derived (always 0)",
     "        cont_diff = sum(1 for a, b in zip(s_conts, e_conts) if a != b)",
     "        cont_diff = 0"),
    # freeze R-1: the mutant the fix-wave re-review specified and the
    # harness substituted away — continuation diffs computed from the
    # BIT arrays. Every other gate-1 test flips a bit and its
    # continuation together, so only a continuation-ONLY mismatch (bits
    # held equal) separates this from the real implementation.
    (AN, "gate1_rederive_7b: continuation diff computed from the BITS, not "
         "the continuations",
     "        cont_diff = sum(1 for a, b in zip(s_conts, e_conts) if a != b)",
     "        cont_diff = sum(1 for a, b in zip(s_bits, e_bits) if a != b)"),
    # freeze R-2: an undefined test's T back to NaN (a bare `NaN` token
    # in verdict.json), and the writer's strictness guarantee removed.
    (AN, "_undefined_result_2i: T back to NaN instead of None (bare NaN in "
         "verdict.json)",
     '    empty = {"T": None, "p": 1.0, "n_perm": 0, "n_ge": 0}',
     '    empty = {"T": float("nan"), "p": 1.0, "n_perm": 0, "n_ge": 0}'),
    (AN, "run(): the written verdict is no longer sanitized to strict JSON",
     "        outp.write_text(json.dumps(_json_safe(v), indent=1, default=_jsonable,\n"
     "                                   allow_nan=False))",
     "        outp.write_text(json.dumps(v, indent=1, default=_jsonable))"),
    (AN, "run(): rung-set re-derivation skipped (failures dropped on the floor)",
     "    failures += f + (rbad2 or [])",
     "    failures += f"),
    (AN, "_run_test: an all-degenerate test raises instead of returning "
         "fires=False (Ruling 18 short-circuit disabled)",
     "        if not keep:\n            reason = (",
     "        if False:\n            reason = ("),
    (AN, "verdict_tree_2i: the undefined disclosure dropped from reason",
     "    parts.extend(disclosures)",
     "    pass"),
    # ------------------------------------------- freeze F-1 (the class defect)
    (AN, "predictor_record_failures_2i: the pinned-field loop inert (any "
         "checkpoint/protocol accepted)",
     "    for k in PREDICTOR_RECORD_PINS_2I:\n        if rec.get(k) != want[k]:",
     "    for k in PREDICTOR_RECORD_PINS_2I:\n        if False:"),
    (AN, "predictor_record_failures_2i: the 1B commit check inert",
     '    want_commit = entry_1b.get("commit")\n    if rec.get("commit") != want_commit:',
     '    want_commit = entry_1b.get("commit")\n    if False:'),
    (AN, "predictor_record_failures_2i: items_sha256 check inert",
     '    # the answer column the draws were actually verified against.\n'
     '    if rec.get("items_sha256") != cap["items_sha256"]:',
     '    # the answer column the draws were actually verified against.\n'
     "    if False:"),
    (AN, "predictor_record_failures_2i: the answer-column alignment check inert",
     "        n = sum(1 for a, b in zip(answers, want_answers) if a != b)\n        if n:",
     "        n = sum(1 for a, b in zip(answers, want_answers) if a != b)\n        if False:"),
    (AN, "predictor_record_failures_2i: the tally coverage check inert (F-2 "
         "lesson on the predictor stage)",
     '    elif tallies[key].get("n_draws") != bt.N_ITEMS * bi.DRAWS_PER_ITEM:',
     "    elif False:"),
    (AN, "_check_predictor_seal_sampling: the seal-vs-records revision "
         "cross-check inert",
     '        if rec.get("revision") != s.get("revision"):',
     "        if False:"),
    (AN, "_check_predictor_seal_sampling: the seal-vs-frozen-constants loop inert",
     '        if s.get(k) != want:',
     "        if False:"),
    (AN, "_check_predictor_counts_2i: attested full_string not compared with "
         "the re-derived count",
     "            if att != sum(counts):",
     "            if False:"),
    (AN, "_check_predictor_counts_2i: the seal's per-item counts not compared",
     "            if list(got) != list(counts):",
     "            if False:"),
    (AN, "run(): the predictor-record failures dropped on the floor",
     "        failures += f + (sbad or [])",
     "        failures += f"),
    (AN, "run(): the predictor-counts failures dropped on the floor",
     "        failures += f + (cbad or [])",
     "        failures += f"),
    # ------------------------------------------------------- freeze F-2
    (AN, "collect_total: the compressed-stream widening removed (a truncated "
         "draws .gz raises EOFError out of the frozen verdict)",
     "    except (EOFError, zlib.error) as e:\n"
     "        return None, [f\"{label}: {type(e).__name__}: {e}\"]",
     "    except RuntimeError as e:\n"
     "        raise"),
    (AN, "_check_predictor_counts_2i: a non-dict `counts` silently skips the "
         "whole cross-check again",
     "    if not isinstance(seal_counts, dict):",
     "    if False:"),
    (AN, "_check_predictor_counts_2i: a `counts` dict missing a rung skipped",
     "    missing = sorted(r for r in x_b if r not in seal_counts)\n    if missing:",
     "    missing = sorted(r for r in x_b if r not in seal_counts)\n    if False:"),
    (AN, "_check_rung_set_vs_endpoint: a non-dict `per_rung` silently skips "
         "every rung again",
     "    if not isinstance(per_rung, dict):",
     "    if False:"),
    (AN, "_check_rung_set_vs_endpoint: a `per_rung` missing rungs not reported",
     "    absent = sorted(r for r in bt.RUNGS if r not in per_rung)\n    if absent:",
     "    absent = sorted(r for r in bt.RUNGS if r not in per_rung)\n    if False:"),
    (AN, "_predictor_seal_paths: the seal's own file list no longer unioned "
         "in (attack item 24)",
     '    if isinstance(seal, dict) and isinstance(seal.get("files"), dict):',
     "    if False:"),
    (AN, "_load_power: R_CAP equality relaxed back to issubset (a table over "
         "a strict subset of the rungs accepted)",
     "        if r_cap is not None and set(rungs) != r_cap:",
     "        if r_cap is not None and not set(rungs).issubset(r_cap):"),
    (AN, "_git_sha: no longer total (raises out of run() when git is absent)",
     "    try:\n        return subprocess.run([\"git\", \"rev-parse\", \"HEAD\"], cwd=bg.REPO,\n"
     "                              capture_output=True, text=True).stdout.strip()\n"
     "    except OSError:\n        return \"\"",
     "    return subprocess.run([\"git\", \"rev-parse\", \"HEAD\"], cwd=bg.REPO,\n"
     "                          capture_output=True, text=True).stdout.strip()"),
    # -------------------------------------------- freeze: attack item 10
    (AN, "run(): the rung set re-derived from `main`'s counts, not "
         "stage1_final's (design section 3.3: main is descriptive only)",
     "            lambda: _check_rung_set_derivation(rung_set, stage1_final, floors),",
     "            lambda: _check_rung_set_derivation(rung_set, main_rec, floors),"),
    (SL, "seal_predictor: the predictor-record provenance refusal inert",
     "    if bad:\n        raise RuntimeError(f\"refusing to seal: {len(bad)} predictor-record \"",
     "    if False:\n        raise RuntimeError(f\"refusing to seal: {len(bad)} predictor-record \""),
    # totality: EVERY collect_total(...) call site in analyze_2i.py's
    # run(), generated programmatically below (review finding 4) —
    # appended to M after this literal, not hand-picked here.
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
     '          "thin": len(keep) < 3, "targets": {}}',
     '          "thin": len(keep) < 2, "targets": {}}'),
    (PW, "_one_test_power: degeneracy drop skipped (simulates over every "
         "rung, degenerate or not)",
     "    keep = tuple(r for r in rungs if r not in dropped)",
     "    keep = tuple(rungs)"),
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
    # freeze R-3: the resume window — a step whose 34 rung records exist
    # but whose checkpoint record does not is NOT complete.
    (SW, "records_complete_7b: checkpoint record no longer required (R-3 "
         "resume deadlock restored)",
     "    return bi.checkpoint_record_path(out_root, step).exists()",
     "    return True"),
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

# Review finding 4: one mutant per collect_total(...) call site in
# analyze_2i.run() — not the six hand-picked ones from the first
# round. `_totality_mutants` walks the real, current source at import
# time, so this count tracks the file rather than a number typed here.
M += _totality_mutants(AN)

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
