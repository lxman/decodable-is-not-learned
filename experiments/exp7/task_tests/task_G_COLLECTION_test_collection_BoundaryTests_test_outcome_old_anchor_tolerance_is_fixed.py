# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7core.collectors import persist_receipt, collect_outcome_anchors
from collection_fixtures import fixture, FakeSession
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_outcome_old_anchor_tolerance_is_fixed(self):
        with self.f.campaign() as c:
            s = FakeSession(c, 'outcome-40000')
            persist_receipt(c, s.load, s.receipt)
            original = s.greedy

            def bad(prompts, cap):
                got = original(prompts, cap)
                got[:16] = ['2'] * 16
                return got
            s.greedy = bad
            with self.assertRaisesRegex(Refusal, 'Mac anchor tolerance'):
                collect_outcome_anchors(c, s, s.load, 40000)
