# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import sys
import tempfile
import types
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

    def test_trace_catches_unpinned_removed_alias_and_direct_read(self):
        source = self.repo / 'unpinned.py'
        source.write_text('value = 7\n')
        trace = Trace(self.repo, self.f.root, {'source.txt': self.f.data['repo_pins']['source.txt']})
        code = compile(source.read_bytes(), str(source), 'exec')
        trace.start()
        try:
            with self.assertRaises(Refusal):
                exec(code, {'__name__': 'throwaway_alias', '__file__': str(source)})
            with self.assertRaises(Refusal):
                source.read_bytes()
        finally:
            trace.stop()
        trace = Trace(self.repo, self.f.root, {'unpinned.py': digest(source.read_bytes())})
        trace.start()
        try:
            module = types.ModuleType('throwaway_alias')
            module.__file__ = str(source)
            sys.modules['throwaway_alias'] = module
            exec(code, module.__dict__)
            del sys.modules['throwaway_alias']
            self.assertIn(str(source), trace.executed)
        finally:
            trace.stop()
