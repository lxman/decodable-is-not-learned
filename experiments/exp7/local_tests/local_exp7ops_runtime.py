# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal

class ReviewFixTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_R1_bound_child_handle_checks_exit_before_sid_or_termination(self):
        from exp7ops.runtime import SystemProcess
        port = SystemProcess()

        class ExitedChild:

            def poll(self):
                return 0

            def terminate(self):
                raise AssertionError('exited bound child must not be signaled')
        port.children[123] = ExitedChild()
        with self.assertRaises(ProcessLookupError):
            port.session_id(123)
        port.terminate(123)
        with self.assertRaises(Refusal):
            port.terminate(456)
