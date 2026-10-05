# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import ARMS
from exp7core.collection_schema import execution_order
from exp7core.collectors import persist_receipt, sample_family
from exp7core.records import strict_json
from collection_fixtures import fixture, FakeSession
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_full_render_schedule_controls_contact_not_storage(self):
        with self.f.campaign() as c:
            s = FakeSession(c, 'sample-pythia_1b')
            persist_receipt(c, s.load, s.receipt)
            values = sample_family(c, 'pythia_1b', 'unscrambling', s)
            expected = [p.prompts[ARMS.index(a)] for p, a in execution_order(c.battery(), 'unscrambling')]
            self.assertEqual(s.calls, expected)
            self.assertEqual(len(s.calls), 2000)
            self.assertEqual([strict_json(r)['index'] for r in values['q0'].splitlines()], list(range(500)))
