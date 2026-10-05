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

class ProducerExportWorker(unittest.TestCase):

    def test_contract(self):
        import producer_export_worker as worker
        import sys
        from exp7ops.evidence import canonical, digest, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'setup'
            source.write_bytes(canonical({'schema': 'exp7.full-synthetic-setup.v1', 'extra': True}))
            with patch.object(sys, 'argv', ['worker', '--spec', str(source), '--spec-sha256', digest(source.read_bytes()), '--output', str(root / 'export')]), patch.object(worker, 'ProducerWorldFixture', lambda *a, **k: self.fail('invalid setup constructed producer')):
                with self.assertRaisesRegex(Refusal, 'fixed synthetic setup schema'):
                    worker.main()
            self.assertFalse((root / 'export').exists())
