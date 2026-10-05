# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.mutation import run_mutants
from exp7ops.evidence import snapshot

class MutationTests(unittest.TestCase):

    def test_one_harmless_fixture_mutant_restores_all_bytes_and_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'original'
            source.mkdir()
            (source / 'fixture.py').write_text('def value():\n    return 1\n')
            original = snapshot(source)
            seen = []

            def evaluate(copy, task):
                ns = {}
                exec(compile((copy / 'fixture.py').read_bytes(), str(copy / 'fixture.py'), 'exec'), ns)
                value = ns['value']()
                seen.append(value)
                failed = int(value != 1)
                return {'tests': 1, 'failures': failed, 'errors': 0, 'returncode': failed}
            mutant = {'id': 'harmless', 'file': 'fixture.py', 'old': 'return 1', 'new': 'return 2', 'task': 'fixture'}
            result = run_mutants(source, root / 'run', [mutant], evaluate)
            self.assertEqual(seen, [1, 2, 1])
            self.assertEqual(result[0]['status'], 'KILLED')
            self.assertEqual(snapshot(source), original)
            self.assertEqual(snapshot(root / 'run/copy'), original)
            self.assertEqual(len(list((root / 'run/logs').glob('*.json'))), 5)
