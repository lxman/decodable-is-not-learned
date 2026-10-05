# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7core.collectors import backend_of, require_result
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_empty_backends_never_select_live(self):
        with self.f.campaign() as c:
            for empty in (None, {}, [], False, 0, ''):
                with self.subTest(value=empty), self.assertRaises(Refusal):
                    backend_of(c, empty, 'predictor-collection')
            for got in ({'700100': ['x'] * 64}, {700100: ['x'] * 63}, {700100: [None] * 64}, {}):
                with self.assertRaises(Refusal):
                    require_result(got, (700100,), 64)
