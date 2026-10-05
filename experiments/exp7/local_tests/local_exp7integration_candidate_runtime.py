# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import canonical, digest, strict, Refusal
from exp7integration.candidate_runtime import propose_runtime, accept_reviewed_runtime
from testing_paths import WORK

class RuntimePreparationTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ('stdlib', 'numpy'):
            (self.root / name).mkdir()
        source = self.root / 'stdlib/fake.py'
        source.write_bytes(b'# fabricated runtime bytes\n')
        self.selection = {'schema': 'exp7.runtime-selection.v1', 'roots': {k: str(self.root / k) for k in ('stdlib', 'numpy')}, 'files': {str(source): 'stdlib'}, 'frozen': [], 'generated': {}}
        self.path = self.root / 'selection.json'
        self.path.write_bytes(canonical(self.selection))
        self.proposal = self.root / 'proposal.json'
        self.sha = propose_runtime(self.path, digest(self.path.read_bytes()), self.proposal, generated_witnesses={})

    def test_measured_proposal_is_not_a_candidate_runtime_or_review(self):
        value = strict(self.proposal.read_bytes())
        self.assertIs(value['authority'], False)
        with self.assertRaises(Refusal):
            accept_reviewed_runtime(self.proposal, self.sha, self.proposal, self.sha, self.root / 'runtime.json')
        self.assertFalse((self.root / 'runtime.json').exists())
