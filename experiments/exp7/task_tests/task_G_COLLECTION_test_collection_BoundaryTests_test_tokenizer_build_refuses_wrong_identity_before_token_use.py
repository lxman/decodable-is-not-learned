# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal, canonical, digest
from exp7core.preflight import build_tokenizer_checks
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_tokenizer_build_refuses_wrong_identity_before_token_use(self):
        d = self.f.data
        assets = {k: v for k, v in d['assets'].items() if k != 'twin'}
        grant = {'schema': 'exp7.build-grant.v2', 'owner': 'Michael Jordan', 'scope': 'tokenizer-only-build-cap-validation', 'evidence_path': 'owner.txt', 'evidence_sha256': d['repo_pins']['owner.txt'], 'quote': 'authorized fake scope', 'battery_sha256': self.f.battery.bytes_sha256, 'assets_sha256': digest(canonical(assets))}
        raw = canonical(grant)
        (self.repo / 'tokenizer-grant.json').write_bytes(raw)
        from collection_fixtures import FakeGit
        calls = []

        def loader(asset):
            calls.append(asset)
            return (object(), {**asset, 'commit': '4' * 40})
        with self.assertRaisesRegex(Refusal, 'measured tokenizer asset'):
            build_tokenizer_checks(battery=self.f.battery, read=lambda p: (self.repo / p).read_bytes(), git=FakeGit(), grant_path='tokenizer-grant.json', grant_sha256=digest(raw), grant_commit='1' * 40, assets=assets, output_root=self.f.root, loader=loader)
        self.assertEqual(len(calls), 1)
        self.assertFalse((self.f.root / 'cap-validation/DONE.json').exists())
