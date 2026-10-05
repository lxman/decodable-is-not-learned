# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import os
import tempfile
import unittest
from exp7core.contract import digest
from exp7core.provenance import Trace
from testing_paths import WORK

class ReadWriteTraceTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.root = self.repo / 'campaign'
        self.root.mkdir()
        self.pinned = self.repo / 'pinned.txt'
        self.pinned.write_bytes(b'pinned bytes')
        self.unknown = self.repo / 'unknown.txt'
        self.unknown.write_bytes(b'unpinned input')

    def trace(self):
        return Trace(self.repo, self.root, {'pinned.txt': digest(b'pinned bytes')})

    def readwrite(self, path, mode):
        if isinstance(mode, str):
            with path.open(mode) as handle:
                return handle.read()
        fd = os.open(path, mode)
        try:
            return os.read(fd, 100)
        finally:
            os.close(fd)

    def test_pinned_readwrite_read_is_traced_and_passes_unchanged(self):
        for mode in ('r+', 'r+b', os.O_RDWR, os.O_RDWR | os.O_APPEND, os.O_RDWR | os.O_CREAT):
            with self.subTest(mode=mode):
                trace = self.trace()
                trace.start()
                try:
                    value = self.readwrite(self.pinned, mode)
                    self.assertIn(value, ('pinned bytes', b'pinned bytes'))
                    self.assertIn(str(self.pinned), trace.reads)
                finally:
                    trace.stop()
