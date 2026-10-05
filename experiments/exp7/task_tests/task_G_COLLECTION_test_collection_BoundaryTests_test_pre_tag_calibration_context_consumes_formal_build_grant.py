# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import canonical, digest
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_pre_tag_calibration_context_consumes_formal_build_grant(self):
        d = self.f.data
        d['prereg'] = {}
        g = {'schema': 'exp7.build-grant.v2', 'owner': 'Michael Jordan', 'scope': 'calibration', 'evidence_path': 'owner.txt', 'evidence_sha256': d['repo_pins']['owner.txt'], 'quote': 'authorized fake scope', 'source_manifest_sha256': d['source_manifest_sha256'], 'code_manifest_sha256': d['code_manifest_sha256']}
        raw = canonical(g)
        (self.repo / 'grants/calibration.json').write_bytes(raw)
        d['repo_pins']['grants/calibration.json'] = digest(raw)
        d['grants']['calibration'] = {'path': 'grants/calibration.json', 'canonical_sha256': digest(raw), 'commit': '1' * 40}
        path = self.f.root / 'statistics/calibration'
        path.mkdir(parents=True)
        (path / 'CLAIM.json').write_bytes(canonical({'stage': 'calibration', 'production': True}))
        c = self.f.campaign()
        with c.entryexit('calibration') as bound:
            self.assertEqual(bound['code_manifest_sha256'], d['code_manifest_sha256'])
            self.assertTrue((self.f.root / 'claims/calibration.CLAIM').exists())
        with self.assertRaises(FileExistsError):
            with c.entryexit('calibration'):
                pass
