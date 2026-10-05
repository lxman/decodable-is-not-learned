# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.scans import ReadImportScan
from exp7ops.evidence import digest, Refusal

class ScanTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / '__init__.py'
        self.source.write_text('value = 7\n')
        self.pins = {'__init__.py': digest(self.source.read_bytes())}

    def test_dynamic_unpinned_read_and_exit_mutation_refuse(self):
        unknown = self.root / 'dynamic.json'
        unknown.write_text('{}')
        with self.assertRaises(Refusal):
            with ReadImportScan({self.root: self.pins}):
                unknown.read_bytes()
        with self.assertRaises(Refusal):
            with ReadImportScan({self.root: self.pins}):
                self.source.write_text('value = 9\n')
