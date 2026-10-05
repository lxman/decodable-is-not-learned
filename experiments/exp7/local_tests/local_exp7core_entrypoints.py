# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
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

class Entrypoints(unittest.TestCase):

    def test_contract(self):
        from exp7core import entrypoints
        from exp7core.contract import Refusal
        calls = []

        class Campaign:

            def __init__(self, *a, **k):
                pass

            def __enter__(self):
                calls.append('enter')
                return self

            def __exit__(self, *a):
                calls.append('exit')
        with tempfile.TemporaryDirectory() as tmp, patch.object(entrypoints, 'Campaign', Campaign):
            value = entrypoints.run_collection(Path(tmp), Path(tmp), trust_path='fake', trust_sha256='a' * 64, stage='unknown')
            self.assertEqual(value['state'], 'INSUFFICIENT_DATA')
            self.assertEqual(calls, ['enter', 'exit'])
            self.assertTrue((Path(tmp) / 'HALTED.json').exists())
