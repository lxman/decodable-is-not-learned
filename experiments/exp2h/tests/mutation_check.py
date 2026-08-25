# experiments/exp2h/tests/mutation_check.py
"""Mutation-test exp2h's OWN modules — battery_2h, analyze_2h,
run/sweep_2h (the code new to this experiment; the frozen exp2g
modules it imports/mirrors have their own mutation battery in
`experiments/exp2g/tests/mutation_check.py` and are not re-targeted
here). Categories: rung set, grid, manifest uniqueness/final-dup
handling, sampler-count parse (battery_2h); tree boundaries, gate-1
comparisons, plus the Task-2-re-review NAMED mutant — stripping the
`collect()` wrapping at run()'s load_sweep_69 call site (analyze_2h);
runner order/seal/halt (run/sweep_2h). Mutates sources IN PLACE and
restores them — run alone, detached (nohup), never under a foreground
timeout."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "experiments/exp2h"
B, A, S = (H / "battery_2h.py", H / "analyze_2h.py", H / "run/sweep_2h.py")

M = [
    # ---------------------------------------------------- battery_2h.py
    (B, "rung set: R_69 check inert",
     "    if set(got) != set(R_69):",
     "    if False:"),
    (B, "manifest: grid/excluded check inert",
     '    if obj.get("grid") != list(GRID_69) or obj.get("excluded", {}) != {}:',
     "    if False:"),
    (B, "manifest: duplicate candidates allowed",
     "        if step != FINAL_STEP_69 and same:",
     "        if False:"),
    (B, "sampler_counts: verify_fn ignored (counts every draw)",
     'counts[row["item"]] = sum(1 for d in row["draws"][str(spec["seed"])]\n'
     '                                      if verify_fn(d, ans, cap["answer_type"]))',
     'counts[row["item"]] = sum(1 for d in row["draws"][str(spec["seed"])]\n'
     '                                      if True)'),
    (B, "sampler_counts: probe-size guard inert",
     "    if size not in bt.PROBE_SIZES:",
     "    if False:"),
    (B, "m4 pin re-assertion inert",
     '        if rec["correct"] != FINAL_COUNT_PIN_69[r]:',
     "        if False:"),
    (B, "manifest: final-point commit not checked",
     '    if main_entry is None or main_entry["commit"] != _pythia_sha_69():',
     "    if main_entry is None:"),
    (B, "check_frozen_2h: sha comparison inert",
     "        if got != want:",
     "        if False:"),
    # ---------------------------------------------------- analyze_2h.py
    (A, "tree: effect bar dropped",
     "    if p < ALPHA and T >= T_BAR:",
     "    if p < ALPHA:"),
    (A, "gate 1: counts not compared",
     "        elif counts[r] != bh.FINAL_COUNT_PIN_69[r]:",
     "        elif False:"),
    (A, "gate 1: digests not compared",
     "    if not da or not db or da != db:",
     "    if False:"),
    (A, "gate 1: continuation diffs ignored",
     "        if cd.get(r) != 0:",
     "        if False:"),
    (A, "gate 1: prereg_tag not compared",
     '    if rec.get("prereg_tag") != bh.PREREG_TAG_2H:',
     "    if False:"),
    (A, "require_prereg_2h: tag check inert",
     "    if not tag_exists(bh.PREREG_TAG_2H):",
     "    if False:"),
    (A, "load_sweep_69: missing record tolerated",
     '            if not p.is_file():\n'
     '                raise FileNotFoundError(f"sweep record missing: {p}")',
     '            if not p.is_file():\n'
     '                continue'),
    (A, "primary_2h: no-eligible-rung check inert",
     '    if not cells:\n        raise ValueError("primary_2h: no eligible rung")',
     '    if False:\n        raise ValueError("primary_2h: no eligible rung")'),
    (A, "outcomes_69: step0 counted",
     "        hits = [s for s in steps if bits[s][i]]",
     "        hits = [s for s in sweep if bits[s][i]]"),
    (A, "run(): collect() stripped at the load_sweep_69 call site (Task 2 re-review)",
     '    sweep, f = collect_total(lambda: load_sweep_69(root, battery, verify_fn, manifest=manifest,\n'
     '                                                   seal_sha=seal_sha) if _sweep_ready else\n'
     '                             (_ for _ in ()).throw(ValueError("manifest, battery, verify "\n'
     '                                                              "criterion or predictor missing")),\n'
     '                             f"sweep {bh.SIZE}")\n'
     '    failures += f\n',
     '    sweep = (lambda: load_sweep_69(root, battery, verify_fn, manifest=manifest,\n'
     '                                   seal_sha=seal_sha) if _sweep_ready else\n'
     '             (_ for _ in ()).throw(ValueError("manifest, battery, verify "\n'
     '                                              "criterion or predictor missing")))()\n'
     '    f = []\n'
     '    failures += f\n'),
    # ------------------------- the freeze's F-1 closure (totality)
    (A, "collect_total: exception surface narrowed back to 2g's four names",
     "    except (ValueError, KeyError, RuntimeError, TypeError, AttributeError,\n"
     "            OSError) as e:",
     "    except (ValueError, KeyError, RuntimeError) as e:"),
    (A, "run(): gate-1 re-derivation no longer behind a refusal",
     '            gbad, f = collect_total(lambda: gate1_failures_69(gate1),\n'
     '                                    f"gate 1 {bh.SIZE} re-derivation")\n'
     '            failures += f + (gbad or [])',
     '            failures += gate1_failures_69(gate1)'),
    (A, "run(): halt-marker read no longer behind a refusal",
     '        halted, f = collect_total(\n'
     '            lambda: bh.halt_marker_path_2h(root).read_text().strip()[:200],\n'
     '            f"gate 1 {bh.SIZE} halt marker")\n'
     '        failures += f\n'
     '        if not f:\n'
     '            failures.append(f"gate 1 {bh.SIZE}: the runner halted ({halted})")',
     '        failures.append(f"gate 1 {bh.SIZE}: the runner halted "\n'
     '                        f"({bh.halt_marker_path_2h(root).read_text().strip()[:200]})")'),
    (A, "run(): the primary no longer behind a refusal",
     '        core, f = collect_total(lambda: _primary_core(sweep, floors, strata, n_perm=n_perm,\n'
     '                                                      n_boot=n_boot), f"primary {bh.SIZE}")\n'
     '        failures += f',
     '        core = _primary_core(sweep, floors, strata, n_perm=n_perm, n_boot=n_boot)\n'
     '        failures += []'),
    (A, "run(): gate-1 referent dict guard dropped",
     '(gate1 if isinstance(gate1, dict) else {}).items()',
     "(gate1 or {}).items()"),
    (A, "run(): referent-manifest check skipped",
     "    if referents_sha is not None:",
     "    if False:"),
    (A, "run(): power-record check skipped",
     "    if power_sha is not None:",
     "    if False:"),
    (A, "run(): halt marker not consulted",
     "    if bh.halt_marker_path_2h(root).exists():",
     "    if False:"),
    (A, "gate 1: continuation-comparison COVERAGE not required (F-2)",
     "        if nc.get(r) != bt.N_ITEMS:",
     "        if False:"),
    (A, "require_prereg_2h: instrument drift from the tag ignored (F-3)",
     "    if drift:",
     "    if False:"),
    # ------------------------------------------------------ run/sweep_2h.py
    (S, "runner: prereg tag not required",
     "    prereg = ah.require_prereg_2h(tag_exists=tag_exists, blob_sha=blob_sha)",
     '    prereg = {"tag": bh.PREREG_TAG_2H}'),
    (S, "runner: halt marker not written",
     '        bh.halt_marker_path_2h(out_root).write_text("\\n".join(failures) + "\\n")',
     "        pass"),
    (S, "runner: gate 1 record/halt skipped on failure",
     '    if failures:\n        _write(bh.gate1_path_2h(out_root), rec)\n'
     '        bh.halt_marker_path_2h(out_root).parent.mkdir(parents=True, exist_ok=True)',
     '    if False:\n        _write(bh.gate1_path_2h(out_root), rec)\n'
     '        bh.halt_marker_path_2h(out_root).parent.mkdir(parents=True, exist_ok=True)'),
    (S, "runner: gate 1 always passes",
     "    failures = ah.gate1_failures_69(rec)",
     "    failures = []"),
    (S, "runner: skip-if-exists disabled",
     "    if records_complete_69(out_root, step):\n        return",
     "    if False:\n        return"),
    (S, "runner: halted-tree resume not refused",
     "    if bh.halt_marker_path_2h(out_root).exists():",
     "    if False:"),
    (S, "runner: on-disk gate1 record not re-derived",
     '        bad = ah.gate1_failures_69(json.loads(g1.read_text()))\n        if bad:',
     "        bad = []\n        if bad:"),
    (S, "runner: incomplete final-step records not caught",
     "        if not records_complete_69(out_root, bh.FINAL_STEP_69):",
     "        if False:"),
]

TESTS = [str(H / "tests")]
DESELECT = ["--deselect", "experiments/exp2h/tests/test_full_shape_2h.py"]


def clear_pycache():
    for d in ROOT.rglob("__pycache__"):
        if "exp2h" in str(d):
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
            print(f"[{i:2d}] SKIP  {name}: target text not found exactly once in {path.name}")
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
