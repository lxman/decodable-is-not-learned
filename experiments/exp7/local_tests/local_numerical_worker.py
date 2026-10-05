import unittest
from pathlib import Path
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

class NumericalWorker(unittest.TestCase):

    def test_contract(self):
        import numerical_worker as worker
        import sys
        calls = []
        with patch.object(sys, 'argv', ['worker', '--fixture', '/fake/export', '--fixture-sha256', 'a' * 64, '--output', '/fake/report']), patch.object(worker, 'analysis_worker', lambda *a: calls.append(a)):
            worker.main()
        self.assertEqual(calls, [(Path('/fake/export'), 'a' * 64, Path('/fake/report'))])
