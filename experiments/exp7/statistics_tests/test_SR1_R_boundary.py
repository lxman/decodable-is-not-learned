"""Bounded cold-input controls; platform observations/syscalls are fabricated."""
import builtins
import errno
import functools
import io
import os
import stat
from types import SimpleNamespace
import unittest
from exp7core.contract import Refusal
from exp7stats.common import digest
from exp7stats.read_boundary import inherited_descriptors, snapshot_bytes, os_backed_readable, close_cli_stdin
from read_fixture import FakeColdPort
import test_integration_boundaries as ib


class FakeCalls:
    def __init__(self, data=b'PINNED\n', *, wrong_identity=False, replace_after_read=False):
        self.data, self.closed, self.position = data, [], 0
        self.wrong_identity, self.replace_after_read = wrong_identity, replace_after_read
        self.opened = []

    def record(self, inode=7):
        return SimpleNamespace(st_dev=1, st_ino=inode, st_mode=stat.S_IFREG | 0o400,
                               st_size=7, st_mtime_ns=1, st_ctime_ns=1)

    def open(self, path, flags):
        self.opened.append((path, flags))
        return 41

    def stat(self, path):
        return self.record()

    def fstat(self, fd):
        return self.record(99 if self.wrong_identity or self.replace_after_read and self.position else 7)

    def read(self, fd, size):
        data = self.data if self.position == 0 else b''
        self.position += 1
        return data

    def close(self, fd):
        self.closed.append(fd)


class ReadBoundaryTests(unittest.TestCase):
    def candidate(self):
        helper = ib.IntegrationBoundaryTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        return helper.candidate()[0]

    def test_SR1_R_cold_cli_closes_kernel_stdin_even_when_stream_does_not(self):
        # No actual standard descriptor is touched by this test.
        calls = []
        stream = SimpleNamespace(fileno=lambda: 0, close=lambda: calls.append('stream'))
        close_cli_stdin(stream, close=lambda fd: calls.append(fd))
        self.assertEqual(calls, ['stream', 0])
        def already_closed(fd): raise OSError(errno.EBADF, 'stream owned fd')
        close_cli_stdin(stream, close=already_closed)
        def failed(fd): raise OSError(errno.EIO, 'cannot verify close')
        with self.assertRaises(Refusal): close_cli_stdin(stream, close=failed)

    def test_SR1_R_pinned_binary_text_buffer_aliases_and_iteration(self):
        ctx = self.candidate()
        with ctx.entryexit('calibration'):
            with open(ctx.repo/'helper.py', 'rb') as f:
                alias = f.read
                self.assertEqual(alias(), b'# helper\n')
                f.seek(0)
                self.assertEqual(list(f), [b'# helper\n'])
                with self.assertRaises(io.UnsupportedOperation):
                    f.fileno()
            with io.open(ctx.repo/'helper.py', 'r', encoding='utf8') as f:
                self.assertEqual(f.readline(), '# helper\n')
                f.seek(0)
                self.assertEqual(f.buffer.raw.read(), b'# helper\n')
            with open(ctx.repo/'helper.py', 'rb', buffering=0) as f:
                self.assertFalse(f.writable())
                with self.assertRaises(io.UnsupportedOperation):
                    f.write(b'BAD')

    def test_SR1_R_prefetched_binary_and_text_buffers_refuse_even_without_live_fd(self):
        for text in (False, True):
            ctx = self.candidate()
            path = ctx.repo.parent/'unbound-buffer.txt'
            path.write_text('PREFETCHED-UNBOUND\nsecond line\n')
            with open(path, 'r' if text else 'rb') as f:
                f.read(1)  # preload user-space buffer before entry, as fabricated input
                self.assertTrue(os_backed_readable(f))
                # Even a fake fd table with no readable fd cannot attest the
                # stale stream bytes. No real close/dup2/replacement is performed.
                ctx.read_port = FakeColdPort(streams=(f,))
                with self.assertRaisesRegex(Refusal, 'buffered streams'):
                    with ctx.entryexit('calibration'):
                        list(f)  # C iteration need not emit a c_call read event

    def test_SR1_R_prebound_read_and_partial_alias_refuse_at_entry(self):
        for partial in (False, True):
            ctx = self.candidate()
            path = ctx.repo.parent/'unbound-alias.txt'; path.write_bytes(b'UNBOUND')
            fd = os.open(path, os.O_RDONLY)
            try:
                alias = functools.partial(os.read, fd, 20) if partial else lambda: os.read(fd, 20)
                ctx.read_port = FakeColdPort(descriptors=(fd,))
                with self.assertRaisesRegex(Refusal, 'inherited readable descriptors'):
                    with ctx.entryexit('calibration'):
                        alias()
            finally:
                os.close(fd)

    def test_SR1_R_no_input_fd_exposure_or_bypass_open_alias(self):
        for kind in ('os_open', 'old_open', 'partial_old_open', 'FileIO', 'readwrite'):
            ctx = self.candidate()
            old = builtins.open
            with self.assertRaises(Refusal):
                with ctx.entryexit('calibration'):
                    path = ctx.repo/'helper.py'
                    if kind == 'os_open': os.open(path, os.O_RDONLY)
                    elif kind == 'old_open': old(path, 'rb')
                    elif kind == 'partial_old_open': functools.partial(old, path, 'rb')()
                    elif kind == 'FileIO': io.FileIO(path, 'rb')
                    else: open(path, 'r+b')

    def test_SR1_R_ordinary_write_only_outputs_and_wrapper_restoration(self):
        ctx = self.candidate()
        original, original_io = builtins.open, io.open
        output = ctx.root/'output.txt'
        with ctx.entryexit('calibration'):
            with open(output, 'w', encoding='utf8') as f:
                f.write('ORDINARY OUTPUT\n')
                self.assertFalse(f.readable())
        self.assertIs(builtins.open, original)
        self.assertIs(io.open, original_io)
        self.assertEqual(output.read_text(), 'ORDINARY OUTPUT\n')
        with self.assertRaisesRegex(ValueError, 'fixture terminal'):
            with ctx.entryexit('calibration'):
                raise ValueError('fixture terminal')
        self.assertIs(builtins.open, original)

    def test_SR1_R_platform_snapshot_checks_actual_fd_identity_bytes_and_replacement(self):
        for kind in ('good', 'wrong_identity', 'replacement', 'wrong_bytes'):
            calls = FakeCalls(data=b'UNBOUND' if kind == 'wrong_bytes' else b'PINNED\n',
                              wrong_identity=kind == 'wrong_identity', replace_after_read=kind == 'replacement')
            if kind == 'good':
                self.assertEqual(snapshot_bytes(calls, '/pinned/input', digest(b'PINNED\n')), b'PINNED\n')
            else:
                with self.assertRaises(Refusal):
                    snapshot_bytes(calls, '/pinned/input', digest(b'PINNED\n'))
            self.assertEqual(calls.closed, [41])
            self.assertTrue(calls.opened[0][1] & os.O_NOFOLLOW)

    def test_SR1_R_platform_census_readable_aliases_replaced_fds_and_outputs(self):
        class Census:
            def listdir(self, root):
                self.root = root
                return ['0','1','2','7','8','9']
            def flags(self, fd):
                if fd == 9: raise OSError(errno.EBADF, 'enumeration fd already closed')
                # 7 is an alias,8 a replaced numeric fd. Neither is trusted
                # through a claimed path/name or prior descriptor number.
                return os.O_WRONLY if fd in (1,2) else os.O_RDONLY if fd != 8 else os.O_RDWR
        for platform, root in (('darwin','/dev/fd'),('linux','/proc/self/fd')):
            calls = Census()
            self.assertEqual(inherited_descriptors(calls, platform), (0,7,8))
            self.assertEqual(calls.root, root)
        class Unobservable(Census):
            def flags(self, fd): raise OSError(errno.EACCES, 'unobservable')
        with self.assertRaises(Refusal): inherited_descriptors(Unobservable(), 'darwin')
        with self.assertRaises(Refusal): inherited_descriptors(Census(), 'unsupported')

    def test_SR1_R_memory_only_streams_are_not_inherited_file_buffers(self):
        self.assertFalse(os_backed_readable(io.BytesIO(b'literal fixture')))
        self.assertFalse(os_backed_readable(io.TextIOWrapper(io.BytesIO(b'literal fixture'))))

    def test_SR1_R_inherited_pinned_handle_is_reopened_not_auto_enrolled(self):
        ctx = self.candidate()
        with open(ctx.repo/'helper.py', 'rb') as f:
            ctx.read_port = FakeColdPort(descriptors=(f.fileno(),), streams=(f,))
            with self.assertRaisesRegex(Refusal, 'inherited readable'):
                with ctx.entryexit('calibration'):
                    f.read()
        ctx.read_port = FakeColdPort()
        with ctx.entryexit('calibration'):
            self.assertEqual((ctx.repo/'helper.py').read_bytes(), b'# helper\n')
