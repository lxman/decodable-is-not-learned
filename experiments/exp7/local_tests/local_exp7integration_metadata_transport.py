# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from exp7ops.evidence import canonical, digest
from exp7ops.wire import encode_payload, decode
from exp7integration.metadata_transport import ReceiptSSH
from local_exp7integration_metadata_transport_collection_fixtures import fixture, FakeSession
from local_exp7integration_metadata_transport_collection_fixture import ROOT

class O8CompositionTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'test-work')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)

    def metadata(self):
        f = fixture(self.repo)
        c = f.campaign()
        receipt = FakeSession(c, 'outcome-40000').receipt
        checks = []
        d = SimpleNamespace(data={'watch': {'remote_site_sha256': digest(b'remote launch site'), 'remote_package_root': '/workspace/repo/experiments/exp7'}}, check_sources=lambda: checks.append(True), _collection=lambda stage: f.campaign())

        class Process:
            response = {}
            calls = []

            def run(self, argv, **kwargs):
                self.calls.append(argv)
                return canonical(self.response).decode()
        p = Process()
        route = {'host': 'ssh1.vast.ai', 'port': 22, 'key': '/fake/key', 'known_hosts': '/fake/known_hosts'}
        transport = ReceiptSSH(p, route, self.repo, decode, d)
        return (f, receipt, d, p, transport)

    def test_real_load_metadata_lands_before_expected_unit_and_rejects_changed_receipt(self):
        f, receipt, d, p, transport = self.metadata()
        raw = canonical(receipt)
        name = 'receipts/outcome-40000.json'
        p.response = {'files': {name: digest(raw)}, 'payload': encode_payload({name: raw})}
        transport.sync_receipts()
        self.assertEqual((f.root / name).read_bytes(), raw)
        self.assertIn('metadata_7.py --site-sha256 ' + d.data['watch']['remote_site_sha256'], p.calls[0][-1])
        self.assertIn('/workspace/repo/experiments/exp7/run/metadata_7.py', p.calls[0][-1])
        self.assertNotIn('exp7_ops', p.calls[0][-1])
        with f.campaign() as c:
            expected = c.expected('units/outcome/40000')
            self.assertEqual(len(expected.addresses), 8000)
        transport.sync_receipts()
        bad = deepcopy(receipt)
        bad['host']['host_id'] = 'remote-self-claim'
        raw = canonical(bad)
        p.response = {'files': {name: digest(raw)}, 'payload': encode_payload({name: raw})}
        with self.assertRaises(ValueError):
            transport.sync_receipts()
        self.assertEqual((f.root / name).read_bytes(), canonical(receipt))
