from fractions import Fraction as F
import unittest
from exp7stats.bootstrap import Metric, run, difference


class BundleBootstrapTests(unittest.TestCase):
    def test_shared_indices_preserve_paired_means_and_undefined_counts(self):
        x = {"f": tuple(F(i) for i in range(7))}
        neg = {"f": tuple(-v for v in x["f"])}
        y = {"f": tuple(range(7))}
        strata = {"f": ("block",)*7}
        metrics = {"left": Metric(("f",), x, y, strata), "right": Metric(("f",), neg, y, strata),
                   "undefined": Metric(("f",), x, {"f": (0,)*7}, strata)}
        result, samples = run(metrics, {"f": 7}, B=5, namespace="paired-bootstrap-test")
        for a, b in zip(samples["left"]["mean"], samples["right"]["mean"]):
            self.assertEqual(a+b, 0)
        self.assertEqual(result["undefined"]["bootstrap"]["T"]["undefined"], 5)
        self.assertIsNone(result["undefined"]["bootstrap"]["T"]["low"])
        d = difference(result, samples, "left", "right")
        self.assertEqual(d["difference"], 2)
        self.assertEqual(d["bootstrap"]["low"], 2)
        self.assertEqual(d["bootstrap"]["high"], 2)
