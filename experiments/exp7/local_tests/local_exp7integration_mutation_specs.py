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

class MutationSpecs(unittest.TestCase):

    def test_contract(self):
        from exp7integration import mutation_specs as module
        from exp7ops.evidence import digest, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'fixture.py'
            path.write_bytes(b'value = 1\n')
            spec = {'id': 'fake', 'file': 'fixture.py', 'task': 'FAKE', 'old': '1', 'new': '2'}
            with patch.object(module, 'MUTANTS', (spec,)):
                result = module.validate_targets(root, {'FAKE': []})
                self.assertEqual(result[0]['source_sha256'], digest(b'value = 1\n'))
                self.assertEqual(result[0]['mutant_sha256'], digest(b'value = 2\n'))
                self.assertEqual(path.read_bytes(), b'value = 1\n')
                with self.assertRaises(Refusal):
                    module.validate_targets(root, {})
                path.write_bytes(b'value = 11\n')
                with self.assertRaises(Refusal):
                    module.validate_targets(root, {'FAKE': []})
