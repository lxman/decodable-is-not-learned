# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal, canonical, digest
from exp7integration.security import TerminalObserver
from local_exp7integration_security_collection_fixture import ROOT

class O8PortTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'test-work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_independent_terminal_requires_absent_bound_parent_and_group(self):

        class Observation:
            observed = {'pid': 10, 'start': 'old'}
            members = [10]

            def identity(self, pid):
                return self.observed

            def group_members(self, group):
                return self.members
        observer = Observation()
        heartbeat_identity_sha256 = digest(b'bound heartbeat')
        path = self.root / 'status.json'
        path.write_bytes(canonical({'pid': 10, 'heartbeat_identity_sha256': heartbeat_identity_sha256, 'exit_code': 0, 'stage': 'complete'}))
        observe = TerminalObserver(identity={'pid': 10, 'start': 'old'}, group=10, status_path=path, heartbeat_identity_sha256=heartbeat_identity_sha256, observer=observer)
        self.assertIsNone(observe())
        observer.observed = {'pid': 10, 'start': 'new'}
        self.assertIsNone(observe())
        observer.members = []
        self.assertEqual(observe()['controller_live'], False)
        path.write_bytes(canonical({'pid': 10, 'heartbeat_identity_sha256': digest(b'forged'), 'exit_code': 0, 'stage': 'complete'}))
        with self.assertRaises(Refusal):
            observe()
