# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal, digest
from exp7core.provenance import Git
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_annotated_tag_identity_and_blob_are_actually_checked(self):

        class OfflineGit(Git):
            kind = b'tag\n'
            raw = b'correct'

            def call(self, *args):
                if args[0] == 'cat-file':
                    return self.kind
                if args[0] == 'show':
                    return self.raw
                return (('2' * 40 if args[1].startswith('refs/') else '1' * 40) + '\n').encode()
        g = OfflineGit(self.repo)
        args = ('exp7-preregistered', '2' * 40, '1' * 40, {'file': digest(b'correct')})
        g.tag(*args)
        g.kind = b'commit\n'
        with self.assertRaisesRegex(Refusal, 'annotated'):
            g.tag(*args)
        g.kind, g.raw = (b'tag\n', b'forged')
        with self.assertRaisesRegex(Refusal, 'blob differs'):
            g.tag(*args)
