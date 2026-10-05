# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal, canonical
from exp7core.records import strict_json
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_scopes_evidence_tag_and_projection(self):
        with self.f.campaign() as c:
            self.assertEqual(c.trust.grant('predictor-preflight')['scope'], 'predictor-preflight')
            with self.assertRaises(KeyError):
                c.trust.grant('rental-create')
        path = self.repo / 'grants/predictor-preflight.json'
        g = strict_json(path.read_bytes())
        g['scope'] = 'predictor-collection'
        path.write_bytes(canonical(g))
        with self.assertRaises(Refusal):
            with self.f.campaign():
                pass
