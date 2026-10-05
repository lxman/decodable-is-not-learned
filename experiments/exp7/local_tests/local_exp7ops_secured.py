# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import Refusal, digest, once, snapshot
from exp7ops.operator import Approval
from exp7ops.secured import write_secured, reverify_secured

def approval(stage='outcome'):
    return Approval(digest(b'contract'), 'b' * 64, stage, 42, 7, 'exp7-outcome', 100, 25, 'c' * 64)

class OperationsTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_independent_verifier_rederives_remote_inventory_and_git_bytes(self):
        evidence = self.root / 'independent-tree'
        evidence.mkdir()
        once(evidence / 'data', b'raw, failed units, host records and logs')
        files = snapshot(evidence)
        observed = {'exit_code': 2, 'controller_live': False, 'group_live': False, 'kind': 'error'}

        class Reader:
            remote = 'd' * 40
            data = (evidence / 'data').read_bytes()

            def remote_master(self):
                return self.remote

            def committed_file(self, head, name):
                return self.data

            def terminal_observation(self):
                return observed

            def required_inventory(self, terminal):
                return dict(files)

            def check_verifier_source(self):
                return 'c' * 64
        reader = Reader()
        paths = {'data': 'experiments/exp7/operations/evidence/data'}
        output = self.root / 'independent-receipt.json'
        write_secured(approval=approval(), reader=reader, root=evidence, files=files, evidence_commit='d' * 40, observed_terminal=observed, publication_paths=paths, output=output)
        data = output.read_bytes()
        self.assertEqual(reverify_secured(data, approval=approval(), reader=reader, root=evidence, publication_paths=paths), digest(data))
        reader.remote = 'e' * 40
        with self.assertRaises(Refusal):
            reverify_secured(data, approval=approval(), reader=reader, root=evidence, publication_paths=paths)
        reader.remote = 'd' * 40
        reader.data = b'corrupt committed blob'
        with self.assertRaises(Refusal):
            reverify_secured(data, approval=approval(), reader=reader, root=evidence, publication_paths=paths)
