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

    def test_preoutcome_refuses_even_unconsumed_outcome_grant(self):
        self.f.stage_grant('outcome-preflight')
        with self.assertRaisesRegex(Refusal, 'outcome grant'):
            self.f.campaign().require_preoutcome()
