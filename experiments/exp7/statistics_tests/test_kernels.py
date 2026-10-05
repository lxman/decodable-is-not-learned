from fractions import Fraction as F
from itertools import permutations
import random
import unittest
import json
import time
import numpy as np
from exp7core.scoring import Table, Score
from exp7core.inference import Cell, somers as reference, mean
from exp7stats.kernels import (ExactLinear, SomersPlan, batch_somers, somers,
                              selectivity, forecast, decision, rng)


class KernelTests(unittest.TestCase):
    def test_exact_large_limb_dot_product_matches_fraction(self):
        weights = [F(1, v) for v in (53, 59, 61, 500, 499, 491, 487, 479, 467, 463, 457)]
        linear = ExactLinear(weights)
        values = np.random.Generator(np.random.PCG64DXSM(7)).integers(-10000, 10001, (100, len(weights)))
        values[0] = 0
        expected = []
        for row in values:
            value = sum((int(v)*w for v, w in zip(row, weights)), F(0))
            expected.append((value > 0)-(value < 0))
        self.assertEqual(linear.sign(values).tolist(), expected)

    def test_fast_counts_against_independent_fraction_core(self):
        gen = random.Random(711)
        for _ in range(120):
            n = gen.randrange(2, 35)
            x = tuple(F(gen.randrange(-5, 6), gen.randrange(1, 6)) for _ in range(n))
            s = tuple(gen.randrange(4) for _ in range(n))
            ys = np.asarray([[gen.randrange(5) for _ in range(n)] for _ in range(4)], dtype=np.int64)
            nums, dens = batch_somers(x, ys, s)
            for j, row in enumerate(ys):
                y = tuple(int(v) for v in row)
                want = reference(x, y, s)
                got = somers(x, y, s)
                self.assertEqual((got["numerator"], got["denominator"], got["D"]),
                                 (want["numerator"], want["denominator"], want["D"]))
                self.assertEqual((int(nums[j]), int(dens[j])), (want["numerator"], want["denominator"]))

    def test_all_permutations_small_histogram(self):
        plan = SomersPlan((F(0), F(0), F(1, 3), F(1)), (0, 1, 1, 2), (0, 0, 0, 0))
        perms = np.asarray(list(permutations(plan.codes)), dtype=np.int64)
        got = plan.numerators(perms)
        expected = [reference(tuple(int(v) for v in row), plan.y, plan.strata)["numerator"] for row in perms]
        self.assertEqual(got.tolist(), expected)

    def test_selectivity_exact_reference_same_numpy_draws(self):
        scores = (Score(Table(3, 1, 1, 2, 4), Table(1, 2, 0, 4, 4)),
                  Score(Table(0, 0, 2, 1, 4), Table(1, 3, 2, 2, 4)))
        cs = tuple(Cell(f, (0, 1), scores, (0, 1), (0, 0)) for f in ("a", "b", "c"))
        tables = [t for c in cs for score in c.scores for t in (score.canonical, score.sham) if t.supported]
        good = np.asarray([t.n00+t.n10 for t in tables])
        bad = np.asarray([t.m0+t.m1 for t in tables])-good
        row = np.asarray([t.m0 for t in tables])
        samples = rng("fraction-reference", "selectivity").hypergeometric(good, bad, row, size=(31, len(tables)))
        ge = 0
        for values in samples:
            delta = sum((F(int(a)-t.n00)*(F(1, t.m0)+F(1, t.m1))/12 for a, t in zip(values, tables)), F(0))
            ge += delta >= 0
        got = selectivity(cs, ("a", "b", "c"), B=31, namespace="fraction-reference", chunk=7)
        self.assertEqual(got["n_ge"], ge)
        self.assertEqual(got["p"], F(ge+1, 32))
        again = selectivity(cs, ("a", "b", "c"), B=31, namespace="fraction-reference", chunk=1)
        self.assertEqual(got, again)

    def test_early_decision_is_exact_and_does_not_fake_p(self):
        self.assertTrue(decision(50, 50, 10000)["nonreject"])
        self.assertFalse(decision(49, 50, 10000)["nonreject"])
        self.assertTrue(decision(0, 9951, 10000)["reject"])
        self.assertIsNone(decision(0, 9951, 10000)["p"])
        self.assertFalse(decision(0, 9950, 10000)["reject"])
        self.assertEqual(decision(49, 10000, 10000)["p"], F(50, 10001))

    def test_forecast_chunk_stability_constant_and_negative(self):
        ss = tuple(Score(Table(i, 5-i, 5-i, i, 5), Table(i, 5-i, 5-i, i, 5)) for i in range(6))
        cs = tuple(Cell(f, tuple(range(6)), ss, (5, 4, 3, 2, 1, 0), (0,)*6) for f in ("a", "b", "c"))
        a = forecast(cs, ("a", "b", "c"), B=17, namespace="chunks", chunk=1)
        b = forecast(cs, ("a", "b", "c"), B=17, namespace="chunks", chunk=7)
        self.assertEqual(a, b)
        self.assertEqual(a["T"], -1)
        self.assertEqual(a["p"], 1)

    def test_bounded_full_width_kernel_fixture_no_MC_test(self):
        # Only 32 integer numerator vectors, not an inferential test, null-rate
        # experiment, power cell, or timing claim about a full campaign.
        x = tuple(F(i-250, i % 63+1) for i in range(500))
        strata = tuple(i//50 for i in range(500))
        gen = np.random.Generator(np.random.PCG64DXSM(19))
        y = np.zeros((32, 500), dtype=np.int64)
        for b in range(32):
            positive = gen.permutation(500)[:125]
            y[b, positive] = 26-np.arange(125)*26//125
        t0 = time.perf_counter()
        num, den = batch_somers(x, y, strata)
        elapsed = time.perf_counter()-t0
        ref = reference(x, tuple(int(v) for v in y[0]), strata)
        self.assertEqual((int(num[0]), int(den[0])), (ref["numerator"], ref["denominator"]))
        weights = [(F(1, i%64+1)+F(1, (i*3)%64+1))/4000 for i in range(4000)]
        linear = ExactLinear(weights)
        changes = gen.integers(-64, 65, (32, 4000), dtype=np.int64)
        t0 = time.perf_counter()
        signs = linear.sign(changes)
        elapsed2 = time.perf_counter()-t0
        exact = sum((int(v)*w for v, w in zip(changes[0], weights)), F(0))
        self.assertEqual(int(signs[0]), (exact > 0)-(exact < 0))
        print("SYNTHETIC_KERNEL_FIXTURE " + json.dumps({"outcome_vectors": 32, "n": 500,
              "numerator_seconds": elapsed, "limb_vectors": 32, "limb_terms": 4000,
              "limb_seconds": elapsed2, "permutation_tests": 0, "power_estimates": 0}))
