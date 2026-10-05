# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal
from exp7ops.watcher import validate_snapshot

class OperationsTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_unknown_snapshot_and_missing_final_inventory_fail(self):
        for value in ({}, {'units': [], 'terminal': None}, {'units': {'unknown': 'a' * 64}, 'terminal': None}):
            with self.assertRaises(Refusal):
                validate_snapshot(value, ('unit',))
