# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7core.collectors import persist_receipt
from collection_fixtures import fixture, FakeSession
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_torn_unit_refused_before_sampling(self):
        with self.f.campaign() as c:
            s = FakeSession(c, 'sample-pythia_1b')
            persist_receipt(c, s.load, s.receipt)
            n = 'units/predictor/pythia_1b/unscrambling/q0'
            p = c.root / n
            p.mkdir(parents=True)
            (p / 'raw.jsonl').write_bytes(b'partial\n')
            with self.assertRaises(Refusal):
                c.raw_unit(n)
            self.assertEqual(s.calls, [])
