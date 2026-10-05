# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7stats.common import dumps, digest
from exp7stats.calibration_context import CalibrationContext
from local_exp7stats_calibration_context_stats_fixtures import WORK
from local_exp7stats_calibration_context_runtime_fixture import allowance
from local_exp7stats_calibration_context_read_fixture import FakeColdPort

class MiniCandidateContext(CalibrationContext):

    def _source_inventory(self):
        return [self.repo / 'candidate.py', self.repo / 'helper.py']

class IntegrationBoundaryTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def candidate(self):
        repo, root = (self.root / 'repo', self.root / 'output')
        repo.mkdir()
        root.mkdir()
        content = {'candidate.py': b'# candidate\n', 'helper.py': b'# helper\n', 'design.md': b'# synthetic design\n', 'cases.json': b'{"schema":"synthetic-only"}\n'}
        content['runtime.json'] = dumps(allowance())
        files = {k: {'kind': 'source' if k.endswith('.py') else 'design' if k.endswith('.md') else 'synthetic_spec', 'sha256': digest(v)} for k, v in content.items()}
        files['runtime.json']['kind'] = 'runtime_spec'
        content['manifest.json'] = dumps({'schema': 'exp7.calibration-candidate.v1', 'files': files})
        for k, v in content.items():
            (repo / k).write_bytes(v)
        ctx = MiniCandidateContext(root, repo, candidate_commit='1' * 40, manifest_path='manifest.json', manifest_sha256=digest(content['manifest.json']), blob_reader=lambda repo, commit, path: content[path], tag_probe=lambda repo: False, read_port=FakeColdPort())
        return (ctx, content)

    def test_pre_tag_context_changed_source_and_unpinned_read_refuse(self):
        ctx, _ = self.candidate()
        (ctx.repo / 'hidden.txt').write_text('unbound')
        with self.assertRaisesRegex(Refusal, 'unpinned'):
            with ctx.entryexit('calibration'):
                (ctx.repo / 'hidden.txt').read_text()
        with self.assertRaisesRegex(Refusal, 'binding'):
            with ctx.entryexit('calibration'):
                (ctx.repo / 'helper.py').write_text('# changed\n')
