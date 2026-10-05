import guard  # FIRST: direct imports require guarded launcher
import random,unittest
from fractions import Fraction as F
from itertools import combinations
from exp7core.scoring import Table,Score
from exp7core.strata import availability_buckets
from exp7core.inference import Cell,somers,eligibility,aggregate_D,hypergeom_weights,randomized_table,selectivity_test,permutation_test,selectivity_fires,forecast_fires,primary

def brute(x, y, strata):
    num = den = 0
    for i, j in combinations(range(len(x)), 2):
        if strata[i] == strata[j] and y[i] != y[j]:
            den += 1
            num += ((x[i] > x[j]) - (x[i] < x[j])) * ((y[i] > y[j]) - (y[i] < y[j]))
    return (num, den)

def cell(f, *, reverse=False, constant=False, positive=20):
    scores = tuple((Score(Table(j, 20 - j, 20 - j, j, 20), Table(j, 20 - j, 20 - j, j, 20)) for j in range(20, -1, -1)))
    if constant:
        scores = (Score(Table(10, 10, 10, 10, 20), Table(10, 10, 10, 10, 20)),) * 21
    y = tuple((21 - i if i < positive else 0 for i in range(21)))
    if reverse:
        y = y[::-1]
    return Cell(f, tuple(range(21)), scores, y, ('s',) * 21)

class InferenceTests(unittest.TestCase):

    def test_fenwick_matches_independent_bruteforce(self):
        rng = random.Random(88)
        for _ in range(200):
            n = rng.randrange(1, 35)
            x = [F(rng.randrange(-4, 5), rng.randrange(1, 5)) for _ in range(n)]
            y = [rng.randrange(5) for _ in range(n)]
            strata = [rng.randrange(4) for _ in range(n)]
            num, den = brute(x, y, strata)
            r = somers(x, y, strata)
            self.assertEqual((r['numerator'], r['denominator']), (num, den))
            self.assertEqual(r['D'], F(num, den) if den else None)

    def test_outcome_untied_denominator_predictor_ties_zero(self):
        r = somers((0, 0, 1), (0, 1, 2), (0, 0, 0))
        self.assertEqual(r['denominator'], 3)
        self.assertEqual(r['D'], F(2, 3))
        self.assertEqual(somers((0, 0, 0), (0, 1, 2), (0, 0, 0))['D'], 0)

    def test_pool_counts_before_family_mean(self):
        r = somers((0, 1, 0, 1, 2), (0, 1, 2, 1, 0), (0, 0, 1, 1, 1))
        self.assertEqual(r['D'], F(-1, 2))

    def test_eligibility_no_sign_or_constant_selection(self):
        cells = (cell('a'), cell('b', reverse=True), cell('c', constant=True), cell('d', positive=19))
        keep, report = eligibility(cells)
        self.assertEqual(keep, ('a', 'b', 'c'))
        self.assertEqual(report['c']['D'], 0)
        self.assertLess(report['b']['D'], 0)
        self.assertEqual(aggregate_D(cells, keep), 0)
        thin = primary(cells[:2], namespace='mini', B=3)
        self.assertEqual(thin['state'], 'UNDETERMINED')
        self.assertIsNone(thin['selectivity'])

    def test_fixed_margin_null_exact_expectation(self):
        for m0, m1, K in ((2, 3, 4), (20, 10, 27), (1, 1, 1), (4, 8, 0)):
            lo, ws = hypergeom_weights(m0, m1, K)
            expect = sum((F(w, sum(ws)) * (F(a, m0) - F(K - a, m1)) for a, w in zip(range(lo, lo + len(ws)), ws)))
            self.assertEqual(expect, 0)
        rng = random.Random(9)
        t = Table(18, 2, 9, 1, 64)
        for _ in range(30):
            r = randomized_table(t, rng)
            self.assertEqual((r.m0, r.m1, r.n00 + r.n10), (20, 10, 27))

    def test_null_randomization_eligibility_invariant(self):
        rng = random.Random(5)
        c = cell('a')
        scores = tuple((Score(randomized_table(s.canonical, rng), randomized_table(s.sham, rng)) for s in c.scores))
        b0, _ = availability_buckets(c.strata, tuple((s.u for s in c.scores)))
        b1, _ = availability_buckets(c.strata, tuple((s.u for s in scores)))
        original = Cell(c.family, c.ids, c.scores, c.y, b0)
        randomized = Cell(c.family, c.ids, scores, c.y, b1)
        self.assertEqual(b0, b1)
        self.assertEqual(eligibility((original,))[0], eligibility((randomized,))[0])

    def test_finite_p_and_strict_boundaries(self):
        self.assertTrue(selectivity_fires({'mean_x': F(1, 20), 'p': F(49, 10001)}))
        self.assertFalse(selectivity_fires({'mean_x': F(1, 20), 'p': F(1, 200)}))
        self.assertTrue(forecast_fires({'T': F(1, 10), 'p': F(49, 10001)}))
        self.assertTrue(forecast_fires({'T': F(1, 10), 'p': F(50, 10001)}))
        self.assertFalse(forecast_fires({'T': F(1, 10), 'p': F(51, 10001)}))
        c = cell('constant', constant=True)
        r = permutation_test((c,), ('constant',), namespace='mini', B=7)
        self.assertEqual(r['p'], 1)
        self.assertEqual(r['T'], 0)

    def test_randomization_deterministic_miniature(self):
        cs = tuple((cell(f) for f in ('a', 'b', 'c')))
        r = primary(cs, namespace='fixture-repeat', B=7)
        self.assertEqual(r, primary(cs, namespace='fixture-repeat', B=7))
        self.assertEqual(r['order']['T'], 1)
        self.assertFalse(r['forecast'])
