# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.cold import cold_suite, COLD_TASKS

class WorldProtocolTests(unittest.TestCase):

    def test_cold_suite_task_selection_no_real_read_sweep(self):
        with tempfile.TemporaryDirectory() as directory:
            tasks = []

            def run(task):
                tasks.append(task)
                return {'tests': 1, 'failures': 0, 'errors': 0, 'returncode': 0}
            cold_suite(run, Path(directory) / 'cold', synthetic=False)
            self.assertEqual(tuple(tasks), COLD_TASKS)
