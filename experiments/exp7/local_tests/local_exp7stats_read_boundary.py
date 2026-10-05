# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import os
import stat
from types import SimpleNamespace
import unittest
from exp7core.contract import Refusal
from exp7stats.common import digest
from exp7stats.read_boundary import snapshot_bytes

class FakeCalls:

    def __init__(self, data=b'PINNED\n', *, wrong_identity=False, replace_after_read=False):
        self.data, self.closed, self.position = (data, [], 0)
        self.wrong_identity, self.replace_after_read = (wrong_identity, replace_after_read)
        self.opened = []

    def record(self, inode=7):
        return SimpleNamespace(st_dev=1, st_ino=inode, st_mode=stat.S_IFREG | 256, st_size=7, st_mtime_ns=1, st_ctime_ns=1)

    def open(self, path, flags):
        self.opened.append((path, flags))
        return 41

    def stat(self, path):
        return self.record()

    def fstat(self, fd):
        return self.record(99 if self.wrong_identity or (self.replace_after_read and self.position) else 7)

    def read(self, fd, size):
        data = self.data if self.position == 0 else b''
        self.position += 1
        return data

    def close(self, fd):
        self.closed.append(fd)

class ReadBoundaryTests(unittest.TestCase):

    def test_SR1_R_platform_snapshot_checks_actual_fd_identity_bytes_and_replacement(self):
        for kind in ('good', 'wrong_identity', 'replacement', 'wrong_bytes'):
            calls = FakeCalls(data=b'UNBOUND' if kind == 'wrong_bytes' else b'PINNED\n', wrong_identity=kind == 'wrong_identity', replace_after_read=kind == 'replacement')
            if kind == 'good':
                self.assertEqual(snapshot_bytes(calls, '/pinned/input', digest(b'PINNED\n')), b'PINNED\n')
            else:
                with self.assertRaises(Refusal):
                    snapshot_bytes(calls, '/pinned/input', digest(b'PINNED\n'))
            self.assertEqual(calls.closed, [41])
            self.assertTrue(calls.opened[0][1] & os.O_NOFOLLOW)
