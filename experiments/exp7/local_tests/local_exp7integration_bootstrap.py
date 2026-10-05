# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from contextlib import contextmanager, redirect_stdout
from fractions import Fraction
from exp7ops.evidence import canonical, digest, strict
from testing_paths import WORK

@contextmanager
def replace(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)

class IntegrationReviewRegressions(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_INTR1_calibration_cli_preserves_fraction_result_with_exit_zero(self):
        from exp7integration import bootstrap
        from exp7stats.calibration import rate_summary
        from exp7stats.common import dumps, decode
        result = {'state': 'NO-DETECTED-CALIBRATION-DEFECT', 'rate': rate_summary(0, 2, Fraction(1, 200))}
        site = self.root / 'site'
        site.write_bytes(canonical({'synthetic_only': True}))
        checks = []
        entry = bootstrap.ENTRIES['calibration_7.py']
        out = io.StringIO()
        bootstrap.ENTRIES['calibration_7.py'] = lambda *a: result
        try:
            with replace(bootstrap, 'load_bound', lambda *a: NS(check_sources=lambda: checks.append('exit'))), redirect_stdout(out):
                code = bootstrap.main('calibration_7.py', [], site, digest(site.read_bytes()))
        finally:
            bootstrap.ENTRIES['calibration_7.py'] = entry
        self.assertEqual(code, 0)
        self.assertEqual(checks, ['exit'])
        self.assertEqual(out.getvalue().encode(), dumps(result))
        restored = decode(strict(out.getvalue()))
        self.assertIsInstance(restored['rate']['null_rate'], Fraction)
        self.assertEqual(restored['rate']['null_rate'], Fraction(1, 200))
        self.assertEqual(restored['rate']['binomial_excess_p'], result['rate']['binomial_excess_p'])
