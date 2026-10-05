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

class FreezeWorker(unittest.TestCase):

    def test_contract(self):
        import freeze_worker as worker
        import sys
        from exp7ops.evidence import canonical, digest, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'export'
            source.write_bytes(canonical({'fake_git': True, 'fake_model_outputs': True, 'miniature': True}))
            with patch.object(sys, 'argv', ['worker', '--task', 'worlds', '--fixture', str(source), '--fixture-sha256', digest(source.read_bytes()), '--output', str(root / 'result')]), patch.object(worker, 'open_export', lambda *a, **k: self.fail('miniature reached full-default worker')):
                with self.assertRaisesRegex(Refusal, 'full synthetic export only'):
                    worker.main()
            self.assertFalse((root / 'result').exists())
