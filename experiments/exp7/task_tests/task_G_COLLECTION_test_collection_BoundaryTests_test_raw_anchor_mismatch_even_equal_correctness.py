# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7core.collectors import persist_receipt, collect_anchors
from collection_fixtures import fixture, FakeSession
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_raw_anchor_mismatch_even_equal_correctness(self):
        with self.f.campaign() as c:
            s = FakeSession(c, 'sample-pythia_1b')
            persist_receipt(c, s.load, s.receipt)
            normal = s.sample

            def bad(prompt, **kw):
                values = normal(prompt, **kw)
                return {k: [' 1'] * len(v) for k, v in values.items()}
            s.sample = bad
            with self.assertRaisesRegex(Refusal, 'raw anchor equality'):
                collect_anchors(c, 'pythia_1b', s)
            self.assertFalse((c.root / 'units/anchors/pythia_1b/add_base8').exists())
