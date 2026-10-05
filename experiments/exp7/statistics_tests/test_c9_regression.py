import unittest
from exp7core.simulations import attainable_target


class FixedNoise:
    def __init__(self):
        self.values = iter((1.0, .8, .3))

    def gauss(self, *args):
        return next(self.values)

    def random(self):
        return .5


class FinalUndefinedRegression(unittest.TestCase):
    def test_final_fit_undefined_is_unsupported_not_retry(self):
        calls = []
        def factory(b):
            calls.append(b)
            return FixedNoise()
        result = attainable_target((-1, 0, 1), ("paired", "singleton", "paired"),
                                   target=.15, n_positive=1, max_count=1,
                                   rng_factory=factory, n_cal=1, iterations=1)
        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertIsNone(result["mean_D"])
        self.assertIn("uninformative", result["reason"])
        self.assertEqual(len(calls), 4)  # endpoints, one midpoint, final; no retry
