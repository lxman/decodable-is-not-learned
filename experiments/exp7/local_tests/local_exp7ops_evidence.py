# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal, selected_instances

class ReviewFixTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_R3_failed_list_envelope_never_establishes_absence(self):
        for response in ({'success': False, 'error': 'secret synthetic failure', 'instances': []}, {'success': True, 'error': 'synthetic failure', 'instances': []}, {'success': 0, 'instances': []}, {'errors': ['failure'], 'instances': []}):
            with self.subTest(response=response), self.assertRaises(Refusal):
                selected_instances(response)
