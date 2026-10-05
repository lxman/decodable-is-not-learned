from pathlib import Path
from copy import deepcopy
import tempfile
import unittest
from exp7ops.evidence import Refusal, canonical, digest, strict
from exp7ops.heartbeat import HeartbeatWriter, HeartbeatSession
from exp7integration.heartbeat_service import OSHeartbeatService
from exp7integration.provider import BoundProvider
from exp7integration.security import TerminalObserver
from collection_fixture import ROOT


class FakeChild:
    def __init__(self):
        self.pid, self.code, self.joined = 1002, None, False
    def poll(self):
        return self.code
    def wait(self, timeout):
        if self.code is None:
            raise TimeoutError("fake still running")
        self.joined = True
        return self.code


class FakeOS:
    def __init__(self, config, *, ready=True, finish=True):
        self.config, self.t, self.due = config, 0., 0.
        self.parent = {"pid": 1001, "start_ticks": "fixture-start", "group": 1001}
        self.calls, self.pulses = [], []
        self.writer, self.child = None, FakeChild()
        self.pulse_enabled, self.finish_enabled = ready, finish
    def identity(self, pid):
        return deepcopy(self.parent)
    def clock(self):
        return self.t
    def heartbeat_age(self, stamp):
        return self.t-float(stamp)
    def spawn(self, argv, *, cwd, log):
        self.calls.append((argv, cwd))
        if self.pulse_enabled:
            self.writer = HeartbeatWriter.from_config(self.config, now=lambda: str(self.t))
            self.writer.start()
            self.pulse()
            self.due = 60.
        return self.child
    def pulse(self):
        if not self.finish_enabled and strict(self.config.with_name("heartbeat-mailbox.json").read_bytes())["exit_code"] is not None:
            return
        self.pulses.append(self.t)
        if not self.writer.tick():
            self.child.code = 0
    def wait(self, seconds):
        target = self.t+seconds
        while self.writer is not None and self.child.code is None and self.due <= target:
            self.t = self.due
            self.pulse()
            self.due += 60
        self.t = target


class O8PortTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/"test-work")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def service(self, **kwargs):
        config = self.root/"heartbeat-config.json"
        os_port = FakeOS(config, **kwargs)
        source = self.root/"heartbeat_source.py"; source.write_bytes(b"# fake independently pinned source\n")
        service = OSHeartbeatService(config_path=config, python="/fixed/python", bootstrap="/fixed/heartbeat_7.py",
                                     fixed_stage="power", source_root=self.root, source_pins={source.name: digest(source.read_bytes())},
                                     os_port=os_port, site_sha256=digest(b"fake independent site"))
        session = HeartbeatSession(self.root, pid=1001, stage="power", now=lambda: str(os_port.t), service=service)
        return service, session, os_port

    def test_independent_pulses_fixed_spawn_parent_start_identity_and_terminal_join(self):
        service, session, os_port = self.service()
        session.start()
        self.assertEqual(os_port.calls[0][0], ["/fixed/python", "-I", "-B", "/fixed/heartbeat_7.py", "--site-sha256", digest(b"fake independent site"), "power"])
        bound = strict((self.root/"heartbeat-parent.json").read_bytes())
        self.assertEqual(bound["parent"]["start_ticks"], "fixture-start")
        os_port.wait(901)  # no foreground callback/timer while fake work blocks
        self.assertLessEqual(max(b-a for a, b in zip(os_port.pulses, os_port.pulses[1:])), 60)
        session({"phase": "power", "completed": 1, "total": 1})
        session.finish(exit_code=0, stage="complete")
        self.assertTrue(os_port.child.joined)
        final = strict((self.root/"status.json").read_bytes())
        self.assertEqual((final["stage"], final["exit_code"], final["sequence"]), ("complete", 0, 2))
        self.assertEqual(os_port.child.poll(), 0)

    def test_reused_parent_pid_refused(self):
        _, session, os_port = self.service()
        session.start()
        os_port.parent["start_ticks"] = "reused-pid"
        with self.assertRaisesRegex(Refusal, "reused"):
            session.check()

    def test_dead_heartbeat_refused(self):
        _, session, os_port = self.service()
        session.start()
        os_port.child.code = 1
        with self.assertRaisesRegex(Refusal, "not live"):
            session.check()

    def test_live_but_stalled_worker_refuses_stale_pulse(self):
        _, session, os_port = self.service()
        session.start()
        os_port.t = 901  # advance clock without scheduling any worker tick
        with self.assertRaisesRegex(Refusal, "stale"):
            session.check()

    def test_readiness_is_finitely_bounded(self):
        _, session, os_port = self.service(ready=False)
        with self.assertRaisesRegex(ValueError, "readiness timeout"):
            session.start()
        self.assertGreaterEqual(os_port.t, 75)
        self.assertLess(os_port.t, 76)
        self.assertFalse((self.root/"status.json").exists())

    def test_final_ack_is_finitely_bounded_and_does_not_forge_status(self):
        _, session, os_port = self.service(finish=False)
        session.start()
        with self.assertRaisesRegex(ValueError, "acknowledgement timeout"):
            session.finish(exit_code=1, stage="error")
        self.assertIsNone(strict((self.root/"status.json").read_bytes())["exit_code"])

    def test_service_rejects_free_config_path_and_source_drift_before_spawn(self):
        service, session, os_port = self.service()
        with self.assertRaises(Refusal):
            service.start(self.root/"other-config.json")
        (self.root/"heartbeat_source.py").write_bytes(b"changed")
        with self.assertRaises(Refusal):
            session.start()
        self.assertEqual(os_port.calls, [])

    def test_provider_selects_metadata_exact_delete_and_sanitizes_all_failures(self):
        class HTTP:
            def __init__(self):
                self.calls = []
                self.response = (200, canonical({"success": True, "instances": [{"id": 7, "machine_id": 8,
                    "label": "approved", "actual_status": "running", "instance_api_key": "SECRET-SENTINEL"}]}))
            def request(self, method, path):
                self.calls.append((method, path))
                if isinstance(self.response, Exception):
                    raise self.response
                return self.response
        http = HTTP()
        provider = BoundProvider(instance=7, http=http)
        self.assertNotIn("SECRET-SENTINEL", repr(provider.instances()))
        with self.assertRaises(Refusal):
            provider.delete(8)
        self.assertEqual(len(http.calls), 1)
        for response in ((500, b"SECRET-SENTINEL"), (200, b"SECRET-SENTINEL"),
                         (200, canonical({"success": False, "instances": []})),
                         (200, canonical({"success": True, "instances": [], "error": "SECRET-SENTINEL"})),
                         RuntimeError("SECRET-SENTINEL")):
            http.response = response
            with self.assertRaises(ValueError) as got:
                provider.instances()
            self.assertNotIn("SECRET-SENTINEL", str(got.exception))
            self.assertTrue(got.exception.__suppress_context__)
        http.response = (200, canonical({"success": True, "instance_api_key": "SECRET-SENTINEL"}))
        self.assertEqual(provider.delete(7), {"success": True})
        self.assertEqual(http.calls[-1], ("DELETE", "/instances/7/"))
        self.assertFalse(hasattr(provider, "create"))

    def test_independent_terminal_requires_absent_bound_parent_and_group(self):
        class Observation:
            observed = {"pid": 10, "start": "old"}
            members = [10]
            def identity(self, pid):
                return self.observed
            def group_members(self, group):
                return self.members
        observer = Observation()
        heartbeat_identity_sha256 = digest(b"bound heartbeat")
        path = self.root/"status.json"
        path.write_bytes(canonical({"pid": 10, "heartbeat_identity_sha256": heartbeat_identity_sha256, "exit_code": 0, "stage": "complete"}))
        observe = TerminalObserver(identity={"pid": 10, "start": "old"}, group=10, status_path=path,
                                   heartbeat_identity_sha256=heartbeat_identity_sha256, observer=observer)
        self.assertIsNone(observe())
        observer.observed = {"pid": 10, "start": "new"}
        self.assertIsNone(observe())  # same group still occupied: conservative refusal
        observer.members = []
        self.assertEqual(observe()["controller_live"], False)
        path.write_bytes(canonical({"pid": 10, "heartbeat_identity_sha256": digest(b"forged"), "exit_code": 0, "stage": "complete"}))
        with self.assertRaises(Refusal):
            observe()


class HeartbeatIdentityTests(unittest.TestCase):
    """Schema amendment only: real serializers/authenticators, fake OS ports."""
    field = "heartbeat_identity_sha256"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/"test-work")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def session(self, root=None):
        from heartbeat_fakes import FakeClock, FakeHeartbeatService
        clock = FakeClock()
        session = HeartbeatSession(root or self.root, pid=123, stage="power",
                                   now=lambda: clock.value, service=FakeHeartbeatService(clock))
        return session

    def altered(self, value, case):
        value = deepcopy(value)
        if case == "wrong":
            value[self.field] = digest(b"wrong synthetic heartbeat identity")
        else:
            legacy, mixed = case
            value[legacy] = value[self.field]
            if not mixed:
                del value[self.field]
        return value

    def test_identity_is_unchanged_canonical_root_pid_stage_and_config_refuses_old(self):
        session = self.session()
        expected = digest(canonical({"root": str(self.root), "pid": 123, "stage": "power"}))
        self.assertEqual(session.config[self.field], expected)
        self.assertEqual(set(session.config), {"root", "pid", "stage", self.field})
        for case in ("wrong", ("token", False), ("heartbeat_token", False),
                     ("token", True), ("heartbeat_token", True)):
            with self.subTest(case=case), self.assertRaises(Refusal):
                HeartbeatWriter(self.altered(session.config, case), now=lambda: 0)
        for key, value in (("pid", 124), ("stage", "verdict")):
            with self.subTest(key=key), self.assertRaisesRegex(Refusal, "identity"):
                HeartbeatWriter({**session.config, key: value}, now=lambda: 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_generated_records_and_supervisor_inventory_use_only_new_identity(self):
        from exp7integration.supervisor import check_supervisor
        session = self.session()
        session.start()
        session.update({"phase": "testing", "completed": 1, "total": 1})
        session.finish(exit_code=0, stage="complete")
        def check():
            check_supervisor(self.root, repo=self.root.with_name(self.root.name+"-repo"),
                             campaign=self.root.with_name(self.root.name+"-campaign"), stage="power")
        check()
        for name in ("heartbeat-config.json", "heartbeat-writer.CLAIM", "heartbeat-mailbox.json", "status.json"):
            path = self.root/name
            raw = path.read_bytes()
            value = strict(raw)
            self.assertEqual(value[self.field], session.config[self.field])
            self.assertFalse({"token", "heartbeat_token"} & set(value))
            cases = [("token", False), ("heartbeat_token", False), ("token", True), ("heartbeat_token", True)]
            if name in ("heartbeat-config.json", "heartbeat-writer.CLAIM"):
                cases.append("wrong")
            for case in cases:
                with self.subTest(name=name, case=case):
                    try:
                        path.write_bytes(canonical(self.altered(value, case)))
                        with self.assertRaises(Refusal):
                            check()
                    finally:
                        path.write_bytes(raw)
        check()

    def test_mailbox_refuses_legacy_mixed_and_wrong_identity_without_status_rewrite(self):
        for index, case in enumerate(("wrong", ("token", False), ("heartbeat_token", False),
                                      ("token", True), ("heartbeat_token", True))):
            with self.subTest(case=case):
                root = self.root/str(index); root.mkdir()
                session = self.session(root); session.start()
                path = root/"heartbeat-mailbox.json"; raw = path.read_bytes()
                status = (root/"status.json").read_bytes()
                try:
                    path.write_bytes(canonical(self.altered(strict(raw), case)))
                    with self.assertRaises(Refusal):
                        session.service.writer.tick()
                    self.assertEqual((root/"status.json").read_bytes(), status)
                finally:
                    path.write_bytes(raw)

    def test_session_service_and_terminal_observer_refuse_old_and_wrong_status(self):
        from types import SimpleNamespace
        from exp7integration.heartbeat_service import OSHeartbeatHandle
        session = self.session(); session.start()
        path = self.root/"status.json"; raw = path.read_bytes(); value = strict(raw)
        parent = {"pid": 123, "start": "synthetic-start"}
        fake_os = SimpleNamespace(identity=lambda pid: parent, heartbeat_age=lambda stamp: 0)
        handle = OSHeartbeatHandle(FakeChild(), session.config, parent, fake_os, timeout=75)
        observer = TerminalObserver(identity=parent, group=123, status_path=path,
            heartbeat_identity_sha256=session.config[self.field],
            observer=SimpleNamespace(identity=lambda pid: None, group_members=lambda group: []))
        self.assertEqual(handle.check()[self.field], session.config[self.field])
        session.handle = SimpleNamespace(check=lambda: None)
        value.update(exit_code=0, stage="complete")
        path.write_bytes(canonical(value)); self.assertEqual(observer()["kind"], "complete")
        for case in ("wrong", ("token", False), ("heartbeat_token", False),
                     ("token", True), ("heartbeat_token", True)):
            with self.subTest(case=case):
                try:
                    path.write_bytes(canonical(self.altered(value, case)))
                    for consume in (session.check, handle.check, observer):
                        with self.assertRaises(Refusal):
                            consume()
                finally:
                    path.write_bytes(raw)

    def test_os_service_refuses_old_or_wrong_config_before_fake_spawn(self):
        config_path = self.root/"heartbeat-config.json"
        source = self.root/"source.py"; source.write_bytes(b"# synthetic pinned source\n")
        fake_os = FakeOS(config_path)
        service = OSHeartbeatService(config_path=config_path, python="/fake/python", bootstrap="/fake/heartbeat_7.py",
            fixed_stage="power", source_root=self.root, source_pins={source.name: digest(source.read_bytes())},
            os_port=fake_os, site_sha256=digest(b"synthetic site binding"))
        config = self.session().config
        for case in ("wrong", ("token", False), ("heartbeat_token", False),
                     ("token", True), ("heartbeat_token", True)):
            with self.subTest(case=case):
                try:
                    config_path.write_bytes(canonical(self.altered(config, case)))
                    with self.assertRaises(Refusal):
                        service.start(config_path)
                    self.assertEqual(fake_os.calls, [])
                finally:
                    config_path.write_bytes(canonical(config))

    def test_bound_worker_keeps_parent_and_source_authentication_and_new_terminal(self):
        from types import SimpleNamespace
        from exp7integration.heartbeat_service import run_bound_heartbeat
        from exp7ops.evidence import once, state
        session = self.session()
        config_path = self.root/"heartbeat-config.json"
        once(config_path, session.config)
        state(self.root/"heartbeat-mailbox.json", session._mailbox(stage="power"))
        parent = {"pid": 123, "start": "synthetic-start"}
        once(self.root/"heartbeat-parent.json", {"config_sha256": digest(config_path.read_bytes()), "parent": parent})
        source = self.root/"source.py"; source.write_bytes(b"# synthetic source\n")
        pins = {source.name: digest(source.read_bytes())}
        waits = []
        def wait(seconds):
            waits.append(seconds)
            session.sequence += 1
            state(self.root/"heartbeat-mailbox.json", session._mailbox(stage="complete", exit_code=0))
        port = SimpleNamespace(identity=lambda pid: parent, wait=wait)
        original = config_path.read_bytes()
        config_path.write_bytes(canonical({**session.config, "stage": "verdict"}))
        with self.assertRaisesRegex(Refusal, "parent/config binding"):
            run_bound_heartbeat(config_path, source_root=self.root, source_pins=pins, os_port=port, now=lambda: 0)
        config_path.write_bytes(original)
        source.write_bytes(b"# changed\n")
        with self.assertRaises(Refusal):
            run_bound_heartbeat(config_path, source_root=self.root, source_pins=pins, os_port=port, now=lambda: 0)
        source.write_bytes(b"# synthetic source\n")
        result = run_bound_heartbeat(config_path, source_root=self.root, source_pins=pins, os_port=port, now=lambda: 0)
        self.assertEqual(result["state"], "COMPLETE"); self.assertEqual(waits, [60])
        status = strict((self.root/"status.json").read_bytes())
        self.assertEqual((status[self.field], status["exit_code"]), (session.config[self.field], 0))

    def test_remote_bootstrap_passes_new_binding_and_refuses_legacy_configuration(self):
        from types import SimpleNamespace
        from exp7integration import bootstrap, security, remote_evidence
        session = self.session(); session.start(); session.finish(exit_code=0, stage="complete")
        parent = {"pid": 123, "start": "synthetic-start"}
        plan = {"parent_identity": parent, "process_group": 123, "status_path": str(self.root/"status.json"),
                self.field: session.config[self.field]}
        deployment = SimpleNamespace(data={"remote": plan})
        old_observer, old_final = security.TerminalObserver, remote_evidence.final_evidence
        received = []
        def observe(**kwargs):
            received.append(kwargs)
            return old_observer(**kwargs, observer=SimpleNamespace(identity=lambda pid: None, group_members=lambda group: []))
        security.TerminalObserver = observe
        remote_evidence.final_evidence = lambda deployment, observer: observer()
        try:
            self.assertEqual(bootstrap.remote_entry(["final-evidence"], deployment)["kind"], "complete")
            self.assertEqual(received[0][self.field], session.config[self.field])
            for case in ("wrong", ("token", False), ("heartbeat_token", False),
                         ("token", True), ("heartbeat_token", True)):
                with self.subTest(case=case), self.assertRaises(Refusal):
                    deployment.data["remote"] = self.altered(plan, case)
                    bootstrap.remote_entry(["final-evidence"], deployment)
        finally:
            security.TerminalObserver, remote_evidence.final_evidence = old_observer, old_final
