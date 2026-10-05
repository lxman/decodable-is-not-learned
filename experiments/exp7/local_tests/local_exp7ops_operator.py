# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal

class OperationsTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_live_or_unknown_group_blocks_release(self):
        for live in (True, None, 0):
            value = {'exit_code': 0, 'controller_live': False, 'group_live': live, 'kind': 'complete'}
            from exp7ops.operator import terminal
            with self.assertRaises(Refusal):
                terminal(value)
