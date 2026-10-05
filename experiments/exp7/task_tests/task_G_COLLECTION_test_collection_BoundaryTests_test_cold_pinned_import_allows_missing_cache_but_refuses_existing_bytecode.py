# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import sys
import tempfile
import importlib
import unittest
from exp7core.contract import Refusal, digest
from exp7core.provenance import Trace
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_cold_pinned_import_allows_missing_cache_but_refuses_existing_bytecode(self):
        source = self.repo / 'cold_collection_fixture.py'
        source.write_text('answer = 42\n')
        trace = Trace(self.repo, self.f.root, {source.name: digest(source.read_bytes())})
        sys.path.insert(0, str(self.repo))
        self.addCleanup(lambda: sys.path.remove(str(self.repo)))
        self.addCleanup(lambda: sys.modules.pop('cold_collection_fixture', None))
        trace.start()
        try:
            module = importlib.import_module('cold_collection_fixture')
            self.assertEqual(module.answer, 42)
            self.assertIn(str(source), trace.executed)
            path = self.repo / 'existing.pyc'
            path.write_bytes(b'not trusted')
            with self.assertRaisesRegex(Refusal, 'bytecode refused'):
                path.read_bytes()
        finally:
            trace.stop()
