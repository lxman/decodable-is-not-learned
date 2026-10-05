import guard  # FIRST: direct imports require guarded launcher
import unittest
from fractions import Fraction as F
from exp7core.resampling import bundle_indices,take_bundle,interval,paired_difference

class WorldBootstrapTests(unittest.TestCase):

    def test_bundle_resampling_preserves_every_component(self):
        bundles = tuple(((i, (i, i + 1, i + 2, i + 3), {'A': i, 'B': -i}) for i in range(7)))
        draws = list(bundle_indices({'a': 7, 'b': 5}, B=3, namespace='mini'))
        self.assertEqual(draws, list(bundle_indices({'b': 5, 'a': 7}, B=3, namespace='mini')))
        for d in draws:
            got = take_bundle(bundles, d['a'])
            self.assertEqual(got, tuple((bundles[i] for i in d['a'])))

    def test_undefined_bootstrap_counted_and_paired(self):
        r = interval([F(0), None, F(1)])
        self.assertEqual(r['undefined'], 1)
        self.assertEqual((r['low'], r['high']), (F(1, 40), F(39, 40)))
        r = paired_difference([F(1), None, F(3)], [F(0), F(8), None])
        self.assertEqual(r['defined'], 1)
        self.assertEqual(r['undefined'], 2)
