"""Cold battery orchestration; no automatic full-tree analyzer/read-sweep."""
from pathlib import Path
from .evidence import require, once, digest

COLD_TASKS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10",
              "operations", "scans", "mutation-mini", "world-protocol", "dispatch", "review-fixes")
INTEGRATION_TASKS = tuple(f"G{i}" for i in range(1, 11)) + ("full-worlds", "import-scan",
    "read-scan", "determinism", "mutation-full")

def cold_suite(run_task, output, *, synthetic, integrated_tasks=()):
    require(callable(run_task) and type(synthetic) is bool, "cold runner arguments")
    require(set(integrated_tasks) <= set(INTEGRATION_TASKS), "unknown integration task")
    require(synthetic or not set(integrated_tasks) & {"full-worlds", "import-scan", "read-scan", "determinism", "mutation-full"},
            "analysis-executing battery forbidden on real campaign tree")
    output = Path(output)
    output.mkdir()
    results = []
    for task in COLD_TASKS + tuple(integrated_tasks):
        # Integrated task names are checked by the guarded launcher's fixed table.
        result = run_task(task)
        require(type(result) is dict and result.get("tests", 0) > 0, "missing cold task receipt")
        once(output / (task + ".json"), result)
        results.append({"task": task, "result": result})
        require(result.get("returncode") == 0 and result.get("errors") == 0
                and result.get("failures") == 0 and result.get("skipped", 0) == 0, "cold task failed")
    once(output / "COMPLETE.json", {"tasks": results, "synthetic": synthetic,
         "read_sweep": "synthetic-only separately required" if synthetic else "SKIP: real-tree statistics prohibited"})
    return results

def deterministic_twice(process, *, python, worker, fixture, output):
    """A fake process adapter can test orchestration; freeze runs two real guarded workers."""
    output = Path(output)
    output.mkdir()
    reports = []
    for name in ("first", "second"):
        target = output / (name + ".json")
        argv = [str(python), "-I", "-B", str(worker), "--fixture", str(fixture), "--output", str(target)]
        process.run(argv, cwd=str(Path(worker).parent), shell=False, timeout=600)
        require(target.is_file(), "worker output missing")
        reports.append(target.read_bytes())
    require(reports[0] == reports[1], "two-process nondeterminism")
    receipt = {"sha256": digest(reports[0]), "invocations": 2, "byte_identical": True}
    once(output / "determinism.json", receipt)
    return receipt
