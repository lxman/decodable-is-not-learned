# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from contextlib import contextmanager

class patch:

    @staticmethod
    @contextmanager
    def object(target, name, value):
        before = getattr(target, name)
        setattr(target, name, value)
        try:
            yield
        finally:
            setattr(target, name, before)

class CalibrationCLI(unittest.TestCase):

    def test_contract(self):
        from exp7stats import calibration_cli as cli, calibration
        calls = []

        class Context:

            def __init__(self, *a, **k):
                calls.append('context')

            def _manifest(self):
                calls.append('manifest')
                return 'bound'

            def _check(self, value):
                self_value = value
                calls.append('check:' + self_value)
        with patch.object(cli, 'close_cli_stdin', lambda stream: calls.append('fake-close-helper')), patch.object(cli, 'CalibrationContext', Context), patch.object(calibration, 'run', lambda ctx: calls.append('dispatch') or {'state': 'NO-DETECTED-CALIBRATION-DEFECT'}):
            result = cli.main(['--root', '/fake', '--repo', '/fake', '--candidate-commit', 'a' * 40, '--manifest', 'manifest.json', '--manifest-sha256', 'b' * 64])
        self.assertEqual(result, 0)
        self.assertEqual(calls, ['fake-close-helper', 'context', 'manifest', 'check:bound', 'dispatch'])
