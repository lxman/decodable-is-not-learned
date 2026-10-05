# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_formal_grant_once_consumption(self):
        with self.f.campaign() as c:
            c.trust.grant('predictor-preflight', consume=True)
            with self.assertRaises(FileExistsError):
                c.trust.grant('predictor-preflight', consume=True)
