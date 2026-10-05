# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

class Launch(unittest.TestCase):

    def test_contract(self):
        from exp7integration.launch import SiteBoundProcess
        from exp7ops.operator import stage_argv
        from exp7ops.evidence import digest, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / 'site'
            site.write_bytes(b'fake administratively bound site')
            calls = []
            deployment = NS(data={'python': '/python'}, repo=Path('/repo'), site_sha256=digest(site.read_bytes()), site_path=site, check_sources=lambda: None)
            process = SiteBoundProcess(NS(spawn=lambda argv, **kw: calls.append(argv) or 7), deployment, 'power', '/contract')
            argv = stage_argv('/python', '/repo', 'power', '/contract')
            self.assertEqual(process.spawn(argv), 7)
            self.assertIn('--site-sha256', calls[0])
            with self.assertRaises(Refusal):
                process.spawn(argv + ['--B', '3'])
            site.write_bytes(b'drift')
            with self.assertRaises(Refusal):
                process.spawn(argv)
            self.assertEqual(len(calls), 1)
