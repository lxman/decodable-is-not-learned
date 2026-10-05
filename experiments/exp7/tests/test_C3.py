import guard  # FIRST: direct imports require guarded launcher
import unittest
from fractions import Fraction as F
from exp7core.strata import merge_levels,availability_buckets

class StrataTests(unittest.TestCase):

    def test_low_high_tail_and_nominal_isolation(self):
        nominal = ['A'] * 25 + ['B'] * 3
        ordinal = [0] * 4 + [1] * 7 + [2] * 11 + [3] * 3 + [0] * 3
        labels, report = merge_levels(nominal, ordinal)
        self.assertEqual([r['n'] for r in report], [11, 14, 3])
        self.assertEqual(labels[0], ('A', (0, 1)))
        self.assertEqual(labels[24], ('A', (2, 3)))
        self.assertEqual(sum((r['n'] for r in report)), 28)
        self.assertTrue(report[-1]['thin'])

    def test_median_tie_blocks_and_constant(self):
        s, report = availability_buckets(('a',) * 6, tuple(map(F, [0, 0, 0, 0, 1, 1])))
        self.assertEqual([v[1] for v in s], [0, 0, 0, 0, 1, 1])
        self.assertEqual(report[0]['sizes'], {0: 4, 1: 2})
        s, _ = availability_buckets(('a',) * 5, (F(0),) * 5, parts=3)
        self.assertEqual(len(set(s)), 1)

    def test_order_invariance_and_full_coverage(self):
        base = ('a', 'b', 'a', 'b', 'a', 'b')
        u = (F(0), F(1), F(1, 2), F(0), F(1), F(1, 2))
        s, _ = availability_buckets(base, u, parts=3)
        order = (5, 2, 0, 4, 1, 3)
        p, _ = availability_buckets(tuple((base[i] for i in order)), tuple((u[i] for i in order)), parts=3)
        self.assertEqual(p, tuple((s[i] for i in order)))
