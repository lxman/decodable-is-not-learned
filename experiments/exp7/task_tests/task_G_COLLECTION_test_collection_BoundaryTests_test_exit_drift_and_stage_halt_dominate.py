# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.provenance import terminal
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_exit_drift_and_stage_halt_dominate(self):

        def body():
            with self.f.campaign() as c:
                (self.repo / 'source.txt').write_bytes(b'changed after entry')
            return {'would_be': 'success'}
        result = terminal(self.f.root, 'fake', body)
        self.assertEqual(result['state'], 'INSUFFICIENT_DATA')
        self.assertTrue((self.f.root / 'HALTED.json').exists())
        calls = []
        self.assertEqual(terminal(self.f.root, 'again', lambda: calls.append(1))['state'], 'INSUFFICIENT_DATA')
        self.assertEqual(calls, [])
