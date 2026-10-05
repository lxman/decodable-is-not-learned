# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
import tempfile
import unittest
from exp7ops.evidence import canonical, digest
from exp7integration.deployment import FixedStageDeployment, STAGE_MAP
from exp7integration.calibration_copy import copy_accepted_calibration
from local_exp7integration_calibration_copy_collection_fixture import ROOT, put

class DeploymentTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'test-work')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.repo.mkdir()
        self.root = self.repo / 'experiments/exp7/campaign'
        self.root.mkdir(parents=True)
        pins = {}
        for package in ('exp7core', 'exp7stats', 'exp7ops', 'exp7integration', 'run'):
            name = f'experiments/exp7/{package}/__init__.py'
            pins[name] = put(self.repo, name, b'# independently pinned fake source\n')
        self.grant = {'scope': 'fixture', 'evidence': 'explicit test double'}
        self.calls, self.events = ([], [])
        self.config = {'schema': 'exp7.fixed-deployment.v1', 'repo': str(self.repo), 'root': str(self.root), 'source_pins': pins, 'outcome_host': 'fakehost', 'python': '/fixed/python', 'stages': {}}
        for name in STAGE_MAP:
            raw = canonical({'schema': 'exp7.stage-contract.v1', 'stage': name, 'grant_sha256': digest(canonical(self.grant)), 'instance': None, 'machine': None, 'label': None, 'credit_before': 0, 'cap': 0, 'verifier_code_sha256': digest(b'verifier')})
            path = self.repo / f'{name}.json'
            path.write_bytes(raw)
            self.config['stages'][name] = {'trust_path': 'independent-trust.json', 'trust_sha256': digest(b'trust'), 'contract_path': str(path), 'contract_sha256': digest(raw), 'output': str(Path(self.tmp.name) / 'supervisors' / name), 'adapter_authority_path': str(self.repo.parent / 'not-read-authority.json'), 'adapter_authority_sha256': digest(b'authority')}
        self.config['digest_baseline'] = {'trust_path': 'baseline-trust.json', 'trust_sha256': digest(b'baseline authority')}
        self.path = self.repo / 'deployment.json'

        def collection(root, repo, **kwargs):
            self.calls.append(kwargs)
            return {'state': 'COMPLETE', 'value': {'fixture': True}}

        def campaign(*args, **kwargs):
            self.events.append('Campaign constructor')
            trust = SimpleNamespace(prereg_projection=lambda: self.events.append('prereg/projection'), grant=lambda scope: self.events.append(scope) or deepcopy(self.grant))
            return SimpleNamespace(root=self.root, repo=self.repo, trust=trust)
        self.collection, self.campaign = (collection, campaign)
        self.persist()

    def persist(self):
        self.path.write_bytes(canonical(self.config))
        self.deployment = FixedStageDeployment(self.path, digest(self.path.read_bytes()), collection=self.collection, campaign_factory=self.campaign)

    def test_copy_accepted_calibration_exact_bytes_and_existing_path_refusal(self):
        source = self.repo / 'pretag-accepted'
        source.mkdir()
        files = {'CLAIM.json': canonical({'stage': 'calibration'}), 'REPORT.md': b'FAKE archived acceptance fixture\n', 'calibration.json': canonical({'production': True, 'fixture': 'saved-binding-only', 'state': 'NO-DETECTED-CALIBRATION-DEFECT'})}
        files['COMPLETE.json'] = canonical({'files': {n: digest(files[n]) for n in ('calibration.json', 'REPORT.md')}})
        pins = {n: digest(v) for n, v in files.items()}
        for name, value in files.items():
            (source / name).write_bytes(value)
        self.assertEqual(copy_accepted_calibration(source, self.root, accepted_files=pins), pins)
        for name, value in files.items():
            self.assertEqual((self.root / 'statistics/calibration' / name).read_bytes(), value)
        with self.assertRaises(FileExistsError):
            copy_accepted_calibration(source, self.root, accepted_files=pins)
