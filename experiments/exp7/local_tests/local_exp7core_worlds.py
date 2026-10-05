# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from itertools import product
from exp7core.worlds import aggregate, LICENCES, licence

class WorldBootstrapTests(unittest.TestCase):

    def test_every_two_predictor_state_pair(self):
        for a, b in product(LICENCES, repeat=2):
            r = aggregate({'pythia_1b': {'state': a}, 'olmo2_1b': {'state': b}})
            self.assertEqual(r['states'], {'pythia_1b': a, 'olmo2_1b': b})
            self.assertIn('does not identify an internal algorithm', licence(a))
        self.assertEqual(aggregate({p: {'state': 'INPUT-SENSITIVE-FORECAST'} for p in ('pythia_1b', 'olmo2_1b')})['aggregate'], 'BOTH-PREDICTORS')
