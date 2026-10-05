# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
from copy import deepcopy
import tempfile
import unittest
from exp7ops.evidence import Refusal, digest, strict
from exp7ops.heartbeat import HeartbeatWriter, HeartbeatSession
from exp7integration.heartbeat_service import OSHeartbeatService
from local_exp7integration_heartbeat_service_collection_fixture import ROOT

class FakeChild:

    def __init__(self):
        self.pid, self.code, self.joined = (1002, None, False)

    def poll(self):
        return self.code

    def wait(self, timeout):
        if self.code is None:
            raise TimeoutError('fake still running')
        self.joined = True
        return self.code

class FakeOS:

    def __init__(self, config, *, ready=True, finish=True):
        self.config, self.t, self.due = (config, 0.0, 0.0)
        self.parent = {'pid': 1001, 'start_ticks': 'fixture-start', 'group': 1001}
        self.calls, self.pulses = ([], [])
        self.writer, self.child = (None, FakeChild())
        self.pulse_enabled, self.finish_enabled = (ready, finish)

    def identity(self, pid):
        return deepcopy(self.parent)

    def clock(self):
        return self.t

    def heartbeat_age(self, stamp):
        return self.t - float(stamp)

    def spawn(self, argv, *, cwd, log):
        self.calls.append((argv, cwd))
        if self.pulse_enabled:
            self.writer = HeartbeatWriter.from_config(self.config, now=lambda: str(self.t))
            self.writer.start()
            self.pulse()
            self.due = 60.0
        return self.child

    def pulse(self):
        if not self.finish_enabled and strict(self.config.with_name('heartbeat-mailbox.json').read_bytes())['exit_code'] is not None:
            return
        self.pulses.append(self.t)
        if not self.writer.tick():
            self.child.code = 0

    def wait(self, seconds):
        target = self.t + seconds
        while self.writer is not None and self.child.code is None and (self.due <= target):
            self.t = self.due
            self.pulse()
            self.due += 60
        self.t = target

class O8PortTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'test-work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def service(self, **kwargs):
        config = self.root / 'heartbeat-config.json'
        os_port = FakeOS(config, **kwargs)
        source = self.root / 'heartbeat_source.py'
        source.write_bytes(b'# fake independently pinned source\n')
        service = OSHeartbeatService(config_path=config, python='/fixed/python', bootstrap='/fixed/heartbeat_7.py', fixed_stage='power', source_root=self.root, source_pins={source.name: digest(source.read_bytes())}, os_port=os_port, site_sha256=digest(b'fake independent site'))
        session = HeartbeatSession(self.root, pid=1001, stage='power', now=lambda: str(os_port.t), service=service)
        return (service, session, os_port)

    def test_dead_heartbeat_refused(self):
        _, session, os_port = self.service()
        session.start()
        os_port.child.code = 1
        with self.assertRaisesRegex(Refusal, 'not live'):
            session.check()
