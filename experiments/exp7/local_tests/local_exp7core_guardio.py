# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest, tempfile
from pathlib import Path
from exp7core.contract import digest
from exp7core.guardio import Pins, run_stage
SCRATCH = Path(tempfile.gettempdir())

class IOTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'input.txt').write_bytes(b'frozen')
        self.pins = Pins(self.root, {'input.txt': digest(b'frozen')})

    def test_invalid_root_is_also_a_terminal(self):
        r = run_stage(None, 'analyze', pins=self.pins, body=lambda: {})
        self.assertEqual(r['state'], 'INSUFFICIENT_DATA')
        self.assertIn('TypeError', r['failures'][0])
