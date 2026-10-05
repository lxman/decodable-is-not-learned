# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_power_inventory_uses_actual_endpoint_and_receipt_paths(self):
        c = self.f.campaign()
        c.require_preoutcome()
        (self.f.root / 'units/endpoint').mkdir(parents=True)
        with self.assertRaisesRegex(Refusal, 'outcome contact precedes power'):
            c.require_preoutcome()
        (self.f.root / 'units/endpoint').rmdir()
        (self.f.root / 'receipts').mkdir()
        (self.f.root / 'receipts/thin.json').write_bytes(b'failed load evidence')
        with self.assertRaisesRegex(Refusal, 'outcome load receipt'):
            c.require_preoutcome()
