# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal, canonical
from exp7integration.provider import BoundProvider
from local_exp7integration_provider_collection_fixture import ROOT

class O8PortTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'test-work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_provider_selects_metadata_exact_delete_and_sanitizes_all_failures(self):

        class HTTP:

            def __init__(self):
                self.calls = []
                self.response = (200, canonical({'success': True, 'instances': [{'id': 7, 'machine_id': 8, 'label': 'approved', 'actual_status': 'running', 'instance_api_key': 'SECRET-SENTINEL'}]}))

            def request(self, method, path):
                self.calls.append((method, path))
                if isinstance(self.response, Exception):
                    raise self.response
                return self.response
        http = HTTP()
        provider = BoundProvider(instance=7, http=http)
        self.assertNotIn('SECRET-SENTINEL', repr(provider.instances()))
        with self.assertRaises(Refusal):
            provider.delete(8)
        self.assertEqual(len(http.calls), 1)
        for response in ((500, b'SECRET-SENTINEL'), (200, b'SECRET-SENTINEL'), (200, canonical({'success': False, 'instances': []})), (200, canonical({'success': True, 'instances': [], 'error': 'SECRET-SENTINEL'})), RuntimeError('SECRET-SENTINEL')):
            http.response = response
            with self.assertRaises(ValueError) as got:
                provider.instances()
            self.assertNotIn('SECRET-SENTINEL', str(got.exception))
            self.assertTrue(got.exception.__suppress_context__)
        http.response = (200, canonical({'success': True, 'instance_api_key': 'SECRET-SENTINEL'}))
        self.assertEqual(provider.delete(7), {'success': True})
        self.assertEqual(http.calls[-1], ('DELETE', '/instances/7/'))
        self.assertFalse(hasattr(provider, 'create'))
