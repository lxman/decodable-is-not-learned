# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
from contextlib import contextmanager
import tempfile
import unittest
from exp7core.contract import Refusal
from local_exp7integration_adapter_collection_fixture import StrictCollection, ROOT, put
WORK = ROOT / 'test-work'

class AdapterTests(unittest.TestCase):

    @contextmanager
    def fixture(self, **kwargs):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root = Path(tmp) / 'campaign'
            root.mkdir()
            yield StrictCollection(root, **kwargs)

    def test_calibration_must_use_standalone_context(self):
        with self.fixture() as f:
            put(f.root, 'statistics/calibration/CLAIM.json', {'stage': 'calibration'})
            with self.assertRaisesRegex(Refusal, 'standalone'):
                with f.adapter().entryexit('calibration'):
                    self.fail('collection calibration entered')
            self.assertEqual(f.events, [])
