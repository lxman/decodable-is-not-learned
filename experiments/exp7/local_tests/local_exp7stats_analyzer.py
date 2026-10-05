# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import tempfile
import unittest
from exp7stats.common import Shape
from exp7stats.analyzer import run
from local_exp7stats_analyzer_stats_fixtures import FakeCampaign, WORK

class AnalysisTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.campaign = FakeCampaign(self.tmp.name)
        self.shape = Shape(n=24, grid=(1, 2, 3), permutations=200, bootstraps=3)

    def test_production_cannot_accept_miniature_coverage(self):
        result = run(self.campaign)
        self.assertEqual(result['state'], 'INSUFFICIENT_DATA')
        self.assertIn('coverage', ' '.join(result['failures']))
