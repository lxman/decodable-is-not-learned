# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import once, state, canonical, digest

class ReviewFixTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_R6_worker_stops_on_bound_parent_loss_without_inventing_terminal(self):
        from exp7ops.heartbeat import heartbeat_worker
        config = {'root': str(self.root), 'pid': 123, 'stage': 'watch'}
        config['heartbeat_identity_sha256'] = digest(canonical(config))
        once(self.root / 'config.json', config)
        state(self.root / 'status.json', {'pid': 123, 'stage': 'watch', 'exit_code': None})
        before = (self.root / 'status.json').read_bytes()
        result = heartbeat_worker(self.root / 'config.json', now=lambda: 0, wait=lambda s: self.fail('wait after parent loss'), parent_alive=lambda p: False)
        self.assertEqual(result['state'], 'INSUFFICIENT_DATA')
        self.assertEqual((self.root / 'status.json').read_bytes(), before)
