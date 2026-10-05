"""Exact inherited-input regressions; fabricated files, no live process census."""
import os
import unittest
from exp7core.contract import Refusal
import test_integration_boundaries as ib
from read_fixture import FakeColdPort


class InheritedInputRegressions(unittest.TestCase):
    def candidate(self):
        helper = ib.IntegrationBoundaryTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        ctx, _ = helper.candidate()
        hidden = ctx.repo.parent/'unbound-input.txt'
        hidden.write_bytes(b'FABRICATED-UNBOUND-INPUT\n')
        return ctx, hidden

    def test_SR1_R_preopened_FileIO_read_refuses_before_consumption(self):
        ctx, hidden = self.candidate()
        handle = hidden.open('rb', buffering=0)
        try:
            ctx.read_port = FakeColdPort(descriptors=(handle.fileno(),), streams=(handle,))
            with self.assertRaises(Refusal):
                with ctx.entryexit('calibration'):
                    self.assertEqual(handle.read(), b'FABRICATED-UNBOUND-INPUT\n')
        finally:
            handle.close()

    def test_SR1_R_preopened_os_read_refuses_before_consumption(self):
        ctx, hidden = self.candidate()
        fd = os.open(hidden, os.O_RDONLY)
        try:
            ctx.read_port = FakeColdPort(descriptors=(fd,))
            with self.assertRaises(Refusal):
                with ctx.entryexit('calibration'):
                    self.assertEqual(os.read(fd, 4096), b'FABRICATED-UNBOUND-INPUT\n')
        finally:
            os.close(fd)
