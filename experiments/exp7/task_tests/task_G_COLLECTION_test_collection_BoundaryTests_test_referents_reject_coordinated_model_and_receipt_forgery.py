# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
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

    def test_referents_reject_coordinated_model_and_receipt_forgery(self):
        self.f.data['models']['olmo2_1b']['tensor_digest'] = digest(b'forged')
        with self.f.campaign() as c:
            s = FakeSession(c, 'sample-olmo2_1b')
            with self.assertRaisesRegex(Refusal, 'independent old tensor'):
                persist_receipt(c, s.load, s.receipt)
