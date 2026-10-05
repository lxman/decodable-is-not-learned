# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from fractions import Fraction as F
import unittest
from exp7core.contract import Refusal
from exp7stats.power import PowerSpec, verify_power_semantics

class SimulationContractTests(unittest.TestCase):

    def test_saved_power_arithmetic_rederived_without_simulations(self):
        from copy import deepcopy
        from local_exp7stats_power_validation_saved_fixtures import power_record
        spec = PowerSpec(n_sim=1, n_cal=1, n_validate=1, iterations=1, permutations=3, positive_counts=(20,), count_ranges=(3,), targets=(F(3, 20),))
        r, geometry = power_record(spec=spec, n=24, mode='constant')
        self.assertIsNotNone(verify_power_semantics(r, 'd' * 64, 'a' * 64, geometry=geometry, spec=spec))
        bad = deepcopy(r)
        key = next((k for k in bad['rows'] if k.endswith('/null')))
        bad['rows'][key]['fire_count'] = 1
        bad['rows'][key]['p_fires'] = F(1)
        with self.assertRaises(Refusal):
            verify_power_semantics(bad, 'd' * 64, 'a' * 64, geometry=geometry, spec=spec)
