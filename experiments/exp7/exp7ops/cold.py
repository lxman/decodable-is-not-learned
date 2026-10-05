"""Retired orchestration; use run_task_tests.py's registry or exp7integration.freeze.

The compatibility exports below refuse before effects; they do not dispatch a
cold battery or the separately authorized future full synthetic freeze.
"""
from .evidence import require

# Legacy compatibility data, not an executable registry.
COLD_TASKS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10",
              "operations", "scans", "mutation-mini", "world-protocol", "dispatch", "review-fixes")
INTEGRATION_TASKS = tuple(f"G{i}" for i in range(1, 11)) + ("full-worlds", "import-scan",
    "read-scan", "determinism", "mutation-full")

def cold_suite(run_task, output, *, synthetic, integrated_tasks=()):
    """Retired; use run_task_tests.py --task with the installed registry."""
    require(False, "exp7ops.cold.cold_suite is retired; use run_task_tests.py --task with the installed registry")

def deterministic_twice(process, *, python, worker, fixture, output):
    """Retired; use exp7integration.freeze.deterministic_twice with a fixture pin."""
    require(False, "exp7ops.cold.deterministic_twice is retired; use exp7integration.freeze.deterministic_twice")
