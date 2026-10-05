# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
from pathlib import Path

class Inventory(unittest.TestCase):

    def test_contract(self):
        from exp7integration.inventory import enumerate_tree, verify_classification, ReadOnlyCampaign
        from exp7stats.common import dumps, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'receipt.json'
            path.write_bytes(dumps({'stage': 'predictor-preflight'}))
            verify_classification(root, {'path': path.name, 'phase': 'predictor'})
            self.assertEqual(set(enumerate_tree(root)[0]), {path.name})
            path.write_bytes(dumps({'stage': 'outcome-preflight'}))
            with self.assertRaises(Refusal):
                verify_classification(root, {'path': path.name, 'phase': 'predictor'})
            guard = ReadOnlyCampaign(root)
            guard.start()
            try:
                fleeting = root / 'probe'
                fleeting.write_bytes(b'x')
                fleeting.unlink()
                with self.assertRaises(Refusal):
                    guard.check()
            finally:
                guard.stop()
