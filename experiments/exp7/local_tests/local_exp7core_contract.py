# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from exp7core.contract import ARMS, FAMILIES, sampler_stream, seed

class ContractTests(unittest.TestCase):

    def test_stream_separation_and_budgets(self):
        streams = [sampler_stream(f, a, p, i, t) for f in FAMILIES for a in ARMS for i in range(500) for p, t in (('pythia_1b', False), ('olmo2_1b', False), ('pythia_1b', True))]
        self.assertEqual(len({s['stream_seed'] for s in streams}), 24000)
        self.assertEqual({s['draws_per_seed'] for s in streams if s['mode'] == 'trained'}, {64})
        self.assertEqual({s['draws_per_seed'] for s in streams if s['mode'] == 'untrained'}, {16})
        self.assertTrue(all((s['rung'].startswith('exp7/') for s in streams)))
        self.assertNotEqual(seed('selectivity', 'A'), seed('forecast', 'A'))
