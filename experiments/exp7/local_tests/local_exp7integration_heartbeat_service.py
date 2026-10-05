# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
from copy import deepcopy
import builtins
import tempfile
import unittest
from types import FunctionType, SimpleNamespace
from exp7ops.evidence import Refusal, digest, strict, canonical, once, state
from exp7ops.heartbeat import HeartbeatWriter, HeartbeatSession
from exp7integration.heartbeat_service import (
    OSHeartbeatService, NativeHeartbeatOS, OSHeartbeatHandle, run_bound_heartbeat,
)
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


class SyntheticNativeOS:
    """Execute installed identity bytecode with local fake OS/ps leaves only.

    The real import guard stays installed; no subprocess module is imported or
    placed in sys.modules. Only this function's builtins resolve its fake port.
    """

    def __init__(self, case, response):
        self.case, self.response = case, response
        self.calls, self.waits = [], []
        self.on_wait = None
        method = NativeHeartbeatOS.identity

        def import_port(name, *args, **kwargs):
            if name == 'subprocess':
                return SimpleNamespace(run=self.run)
            return builtins.__import__(name, *args, **kwargs)

        namespace = dict(method.__globals__,
                         os=SimpleNamespace(uname=lambda: SimpleNamespace(sysname='Darwin')),
                         __builtins__=dict(vars(builtins), __import__=import_port))
        self.observe = FunctionType(method.__code__, namespace)

    def run(self, argv, **kwargs):
        self.case.assertEqual(argv, ['/bin/ps', '-p', '1001', '-o', 'lstart=',
                                    '-o', 'ppid=', '-o', 'pgid=', '-o', 'command='])
        self.case.assertEqual(kwargs, dict(capture_output=True, text=True, timeout=10,
                                         env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}))
        self.calls.append((argv, kwargs))
        if isinstance(self.response, Exception):
            raise self.response
        code, stdout = self.response
        return SimpleNamespace(returncode=code, stdout=stdout)

    def identity(self, pid):
        return self.observe(None, pid)

    def heartbeat_age(self, stamp):
        return 0

    def wait(self, seconds):
        self.waits.append(seconds)
        self.case.assertEqual(seconds, 60)
        self.case.assertEqual(len(self.waits), 1, 'worker must finish after one fake interval')
        self.on_wait()


class NativeIdentityTests(unittest.TestCase):
    FIRST = 'Mon Oct  5 21:00:00 2026 900 1001 /fake/python operator.py --stage power\n'
    REPARENTED = 'Mon Oct  5 21:00:00 2026 1 1001 /fake/python operator.py --stage power\n'

    def fixture(self, root, port):
        config = {'root': str(root.resolve()), 'pid': 1001, 'stage': 'power'}
        config['heartbeat_identity_sha256'] = digest(canonical(config))
        path = root / 'heartbeat-config.json'
        once(path, config)
        parent = port.identity(1001)
        once(root / 'heartbeat-parent.json', {'config_sha256': digest(path.read_bytes()), 'parent': parent})
        mailbox = {'heartbeat_identity_sha256': config['heartbeat_identity_sha256'],
                   'pid': 1001, 'stage': 'power', 'sequence': 0, 'exit_code': None,
                   'detail': {'phase': 'starting'}, 'ended_utc': None}
        state(root / 'heartbeat-mailbox.json', mailbox)
        state(root / 'status.json', {**config, 'heartbeat_utc': 'fake-clock', 'sequence': 0, 'exit_code': None})
        source = root / 'source.py'
        source.write_bytes(b'# synthetic source pin\n')
        pins = {source.name: digest(source.read_bytes())}
        child = FakeChild()
        handle = OSHeartbeatHandle(child, config, parent, port, timeout=75)

        def terminal():
            state(root / 'heartbeat-mailbox.json', {**mailbox, 'stage': 'complete',
                  'sequence': 1, 'exit_code': 0, 'ended_utc': 'fake-clock'})
        port.on_wait = terminal
        return path, pins, handle

    def test_darwin_reparenting_preserves_handle_and_worker_identity(self):
        for label, observed in (('unchanged', self.FIRST), ('reparented', self.REPARENTED)):
            for route in ('handle', 'worker'):
                with self.subTest(observation=label, route=route), tempfile.TemporaryDirectory(dir=ROOT / 'test-work') as tmp:
                    root = Path(tmp)
                    port = SyntheticNativeOS(self, (0, self.FIRST))
                    path, pins, handle = self.fixture(root, port)
                    port.response = (0, observed)
                    if route == 'handle':
                        self.assertEqual(handle.check()['pid'], 1001)
                    else:
                        result = run_bound_heartbeat(path, source_root=root, source_pins=pins,
                                                     os_port=port, now=lambda: 'fake-clock')
                        self.assertEqual(result, {'state': 'COMPLETE', 'operator_terminal_acknowledged': True})
                        self.assertEqual(port.waits, [60])
                        self.assertEqual(strict((root / 'status.json').read_bytes())['exit_code'], 0)
                    self.assertFalse((root / 'heartbeat-parent-absent.json').exists())
                    self.assertFalse((root / 'heartbeat-error.json').exists())
                    self.assertEqual(len(port.calls), 2 if route == 'handle' else 3)

    def test_darwin_identity_changes_refuse_handle_and_worker(self):
        responses = {
            'reused': (0, self.REPARENTED.replace('21:00:00', '21:01:00')),
            'group': (0, self.REPARENTED.replace('1 1001 /fake', '1 2002 /fake')),
            'command': (0, self.REPARENTED.replace('operator.py', 'other.py')),
            'missing': (1, ''),
        }
        for label, response in responses.items():
            with self.subTest(observation=label), tempfile.TemporaryDirectory(dir=ROOT / 'test-work') as tmp:
                root = Path(tmp)
                port = SyntheticNativeOS(self, (0, self.FIRST))
                path, pins, handle = self.fixture(root, port)
                before = (root / 'status.json').read_bytes()
                port.response = response
                with self.assertRaisesRegex(Refusal, 'operator identity disappeared/reused'):
                    handle.check()
                with self.assertRaisesRegex(Refusal, 'heartbeat parent lost before terminal'):
                    run_bound_heartbeat(path, source_root=root, source_pins=pins,
                                        os_port=port, now=lambda: 'fake-clock')
                self.assertEqual(strict((root / 'heartbeat-parent-absent.json').read_bytes()),
                                 {'pid': 1001, 'child_exit': 'UNKNOWN'})
                self.assertEqual((root / 'status.json').read_bytes(), before)
                self.assertEqual(port.waits, [])

    def test_darwin_observation_errors_and_invalid_pids_refuse(self):
        for response, error, message in (
            ((2, ''), Refusal, 'parent identity observation unavailable'),
            ((0, ''), Refusal, 'parent identity observation unavailable'),
            ((1, self.FIRST), Refusal, 'parent identity observation unavailable'),
            (OSError('fake ps error'), OSError, 'fake ps error'),
            (TimeoutError('fake ps timeout'), TimeoutError, 'fake ps timeout'),
        ):
            with self.subTest(observation=str(response)), tempfile.TemporaryDirectory(dir=ROOT / 'test-work') as tmp:
                root = Path(tmp)
                port = SyntheticNativeOS(self, (0, self.FIRST))
                path, pins, handle = self.fixture(root, port)
                before = (root / 'status.json').read_bytes()
                port.response = response
                with self.assertRaisesRegex(error, message):
                    handle.check()
                with self.assertRaisesRegex(error, message):
                    run_bound_heartbeat(path, source_root=root, source_pins=pins,
                                        os_port=port, now=lambda: 'fake-clock')
                self.assertEqual((root / 'status.json').read_bytes(), before)
                self.assertFalse((root / 'heartbeat-parent-absent.json').exists())
                self.assertEqual(port.waits, [])
        port = SyntheticNativeOS(self, (0, self.FIRST))
        for pid in (True, 0, 1, -1, '1001', None):
            with self.subTest(pid=pid), self.assertRaisesRegex(Refusal, 'specific parent PID'):
                port.identity(pid)
        self.assertEqual(port.calls, [])

    def test_linux_identity_keeps_birth_boot_group_and_session(self):
        tail = ['S', '900', '1001', '1001'] + ['0'] * 15 + ['123456']
        files = {'/proc/1001/stat': '1001 (fake command) ' + ' '.join(tail),
                 '/proc/sys/kernel/random/boot_id': 'fake-boot\n'}
        reads = []

        def path(name):
            def read_text():
                reads.append(name)
                if name not in files:
                    raise FileNotFoundError(name)
                return files[name]
            return SimpleNamespace(read_text=read_text)

        method = NativeHeartbeatOS.identity
        namespace = dict(method.__globals__, Path=path,
                         os=SimpleNamespace(uname=lambda: SimpleNamespace(sysname='Linux')))
        observe = FunctionType(method.__code__, namespace)
        expected = {'pid': 1001, 'boot': 'fake-boot', 'start_ticks': '123456', 'group': 1001, 'session': 1001}
        self.assertEqual(observe(None, 1001), expected)
        files['/proc/1001/stat'] = files['/proc/1001/stat'].replace('S 900 ', 'S 1 ')
        self.assertEqual(observe(None, 1001), expected)
        files['/proc/1001/stat'] = files['/proc/1001/stat'].replace('123456', '123457')
        self.assertNotEqual(observe(None, 1001), expected)
        del files['/proc/1001/stat']
        self.assertIsNone(observe(None, 1001))
        self.assertEqual(set(reads), {'/proc/1001/stat', '/proc/sys/kernel/random/boot_id'})
