"""Pinned pure-package bootstrap; guard precedes project/test/third-party imports."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import guard
from pathlib import Path
import argparse
import importlib
import json
import tempfile
import os
import unittest
from task_registry import TASKS, BUILD_TASKS, TEST_OWNERS

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--task", choices=tuple(TASKS)+("all",))
    selection.add_argument("--build-task", choices=tuple(BUILD_TASKS))
    parser.add_argument("--red", action="store_true", help="test-first: current primary must be absent; prerequisites/support must exist")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.red and (not args.build_task or not BUILD_TASKS[args.build_task].get("primary")):
        parser.error("--red requires one module implementation task")
    missing_primary = BUILD_TASKS[args.build_task]["primary"] if args.red else None
    if missing_primary and (BASE/missing_primary).exists():
        parser.error("red phase requires current primary absent")
    if args.receipt.exists():
        raise ValueError("write-once test receipt")
    from testing_paths import WORK as scratch
    tempfile.tempdir = str(scratch)
    os.environ["TMPDIR"] = str(scratch)
    sys.path.insert(0, str(BASE/"tests"))
    sys.path.insert(0, str(BASE/"task_tests"))
    sys.path.insert(0, str(BASE/"statistics_tests"))
    sys.path.insert(0, str(BASE/"local_tests"))
    suite = unittest.TestSuite()
    selected = tuple(BUILD_TASKS[args.build_task]["tests"]) if args.build_task else tuple(TASKS) if args.task == "all" else (args.task,)
    completed_owners = set()
    def check_owner(owner):
        if owner in completed_owners:
            return
        for dependency in BUILD_TASKS[owner]["depends"]:
            check_owner(dependency)
        if owner not in completed_owners:
            for name in BUILD_TASKS[owner]["sources"]:
                if name == missing_primary:
                    continue
                if not (BASE/name).is_file():
                    raise ValueError("missing prerequisite source: "+name)
            completed_owners.add(owner)
    for task in selected:
        check_owner(TEST_OWNERS[task])
        for name in TASKS[task]:
            # Fixed registry name only; unittest retains import failures as
            # failing tests/receipts, including genuine test-first module absence.
            suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    forbidden = sorted(n for n in sys.modules if guard.forbidden(n))
    receipt = {"task": args.task or args.build_task, "red": args.red, "selected_tasks": list(selected), "prerequisite_owners": sorted(completed_owners),
               "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "skipped": len(result.skipped), "forbidden_loaded": forbidden, "refused_attempts": guard.attempts,
               "model_contacts": 0, "production_calibrations": 0, "production_power_runs": 0,
               "production_analyzer_runs": 0, "actual_operational_process_spawns": 0,
                "loaded_package_files": sorted({Path(m.__file__).resolve().relative_to(BASE).as_posix()
                    for m in tuple(sys.modules.values()) if getattr(m, "__file__", None)
                    and Path(m.__file__).resolve().is_relative_to(BASE)}),
                "loaded_project_modules": sorted(n for n in sys.modules if n.startswith(("exp7core", "exp7stats", "exp7ops", "exp7integration")))}
    with args.receipt.open("x") as f:
        json.dump(receipt, f, indent=2)
        f.write("\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if result.wasSuccessful() and not forbidden else 1


if __name__ == "__main__":
    raise SystemExit(main())
