import guard  # FIRST: direct imports require guarded launcher
import unittest,random
from fractions import Fraction as F
from exp7core.simulations import prompt_probabilities,expected_x,simulate_table,rankz,rank_outcome,attainable_target,binomial_excess,binomial_interval

class MiniatureSimulationTests(unittest.TestCase):

    def test_valid_tables_and_impossible_no_clipping(self):
        s = prompt_probabilities(F(1, 5), F(1, 10), F(9, 10), 0)
        self.assertEqual(s['rows'], ((F(18, 100), F(2, 100), F(4, 5)), (F(9, 100), F(1, 100), F(9, 10))))
        self.assertEqual(prompt_probabilities(F(1), F(1), F(99, 100), F(1, 5))['status'], 'UNSUPPORTED')
        t = simulate_table(s, 4, random.Random(9))
        self.assertLessEqual(t.m0, 4)
        self.assertLessEqual(t.m1, 4)

    def test_support_attenuation(self):
        self.assertEqual(expected_x(0, 1, F(1, 5), 64), 0)
        self.assertEqual(expected_x(1, 1, F(1, 5), 64), F(1, 5))
        self.assertEqual(expected_x(F(1, 2), F(1, 2), F(1, 5), 1), F(1, 20))

    def test_rank_generator_ties_and_exact_positive_count(self):
        self.assertEqual(rankz((1, 1, 1)), (0.0, 0.0, 0.0))
        y = rank_outcome(tuple(range(30)), n_positive=20, max_count=3, rho=0.2, rng=random.Random(17))
        self.assertEqual(sum((v > 0 for v in y)), 20)
        self.assertEqual(set(y), {0, 1, 2, 3})

    def test_constant_predictor_target_is_unsupported(self):
        r = attainable_target((0,) * 30, (0,) * 30, target=0.15, n_positive=20, max_count=3, rng_factory=lambda b: random.Random(8 + b), n_cal=2, iterations=3)
        self.assertEqual(r['status'], 'UNSUPPORTED')
        self.assertEqual(r['shape_ceiling_mean_D'], 0)

    def test_exact_binomial_tail_and_interval(self):
        self.assertEqual(binomial_excess(3, 4, F(1, 2)), F(5, 16))
        self.assertEqual(binomial_excess(0, 4, F(1, 2)), 1)
        lo, hi = binomial_interval(0, 4)
        self.assertEqual(lo, 0)
        self.assertAlmostEqual(hi, 1 - 0.025 ** 0.25, places=10)
        lo, hi = binomial_interval(4, 4)
        self.assertEqual(hi, 1)
        self.assertAlmostEqual(lo, 0.025 ** 0.25, places=10)
