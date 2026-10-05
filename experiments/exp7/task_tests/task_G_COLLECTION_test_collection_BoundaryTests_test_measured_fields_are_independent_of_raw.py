# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import copy
import tempfile
import unittest
from exp7core.contract import Refusal, digest
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

    def test_measured_fields_are_independent_of_raw(self):
        with self.f.campaign() as c:
            s = FakeSession(c, 'sample-pythia_1b')
            receipt = copy.deepcopy(s.receipt)
            receipt['model']['tensor_digest'] = digest(b'wrong')
            with self.assertRaises(Refusal):
                persist_receipt(c, s.load, receipt)
            receipt = copy.deepcopy(s.receipt)
            receipt['host']['device'] = 'wrong'
            with self.assertRaises(Refusal):
                persist_receipt(c, s.load, receipt)
            receipt = copy.deepcopy(s.receipt)
            receipt['probe']['nonfinite'] = 1
            with self.assertRaises(Refusal):
                persist_receipt(c, s.load, receipt)
            receipt = copy.deepcopy(s.receipt)
            receipt['pass'] = True
            with self.assertRaises(Refusal):
                persist_receipt(c, s.load, receipt)
