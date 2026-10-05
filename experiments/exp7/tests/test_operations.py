import guard
from pathlib import Path
import tempfile
import unittest
import json
from contextlib import nullcontext
from heartbeat_fakes import FakeClock, FakeHeartbeatService
from exp7ops.evidence import (Refusal, canonical, digest, once, strict, snapshot,
    selected_instances, selected_credit)
from exp7ops.operator import (Approval, detached_launch, stage_main, stage_argv,
    monitor_argv, land_unit, publish_git, cost_guard, release, recovery_inventory)
from exp7ops.runtime import remote_argv
from exp7ops.watcher import Watcher, heartbeat_loop, validate_snapshot
from exp7ops.secured import write_secured, reverify_secured
from exp7ops.wire import remote_main, decode

def approval(stage="outcome"):
    return Approval(digest(b"contract"), "b"*64, stage, 42, 7, "exp7-outcome", 100, 25, "c"*64)

def payload():
    raw, record = b'{"draw":"alpha"}\n', b'{"rows":1}\n'
    return {"raw.jsonl": raw, "record.json": record,
            "DONE.json": canonical({"raw.jsonl": digest(raw), "record.json": digest(record)})}

class FakeProcess:
    def __init__(self):
        self.calls, self.detached, self.fail_monitor = [], True, False

    def run(self, argv, **kw):
        if kw.get("shell") is not False:
            raise AssertionError("shell not false")
        self.calls.append(("run", argv, kw))
        if self.fail_monitor:
            raise RuntimeError("registration failed")
        return ""

    def spawn(self, argv, **kw):
        self.calls.append(("spawn", argv, kw))
        return 123

    def session_id(self, pid):
        return 123 if self.detached else 9

    def own_session_id(self):
        return 9

    def terminate(self, pid):
        self.calls.append(("terminate", pid))

class FakeProvider:
    def __init__(self):
        self.rows = {"instances": [{"id": 42, "machine_id": 7, "label": "exp7-outcome", "actual_status": "running", "instance_api_key": "NEVER-STORE"}]}
        self.deletes, self.reply, self.after, self.balance = [], {"success": True, "instance_api_key": "NEVER-STORE"}, {"instances": []}, {"credit": 99}

    def instances(self):
        return self.rows

    def delete(self, instance):
        self.deletes.append(instance)
        self.rows = self.after
        return self.reply

    def credit(self):
        return self.balance

class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def receipt(self, terminal=None):
        evidence = self.root / "evidence"
        evidence.mkdir()
        once(evidence / "all-raw-and-logs", b"complete fixture evidence")
        value = {"schema": "exp7.independently-secured.v1", "instance": 42, "machine": 7,
            "contract_sha256": approval().contract_sha256, "verifier_code_sha256": "c"*64,
            "files": snapshot(evidence), "evidence_commit": "d"*40,
            "terminal": terminal or {"exit_code": 0, "controller_live": False, "group_live": False, "kind": "complete"}}
        receipt = self.root / "secured.json"
        once(receipt, value)
        return evidence, receipt

    def release_args(self, provider, terminal=None):
        evidence, receipt = self.receipt(terminal)
        return dict(provider=provider, evidence_root=evidence, secured_receipt=receipt,
                    verify_secured=digest, out=self.root)

    def test_provider_malformed_never_means_absent(self):
        bad = ({}, None, [], {"instances": None}, {"instances": [None]},
               {"instances": [{"id": True}]}, {"instances": [{"id": 42, "machine_id": 7}]})
        for response in bad:
            with self.subTest(response=response), self.assertRaises(Refusal):
                selected_instances(response)
        self.assertEqual(selected_instances({"instances": []}), [])
        for response in ({}, {"credit": True}, {"credit": float("nan")}, {"credit": "1"}):
            with self.assertRaises(Refusal):
                selected_credit(response)

    def test_selected_provider_fields_only(self):
        row = selected_instances(FakeProvider().instances())[0]
        self.assertEqual(set(row), {"id", "machine_id", "label", "actual_status"})
        provider = FakeProvider()
        result = release(approval(), **self.release_args(provider))
        self.assertEqual(provider.deletes, [42])
        self.assertNotIn("NEVER-STORE", canonical(result).decode())

    def test_independent_receipt_is_required_before_delete(self):
        provider = FakeProvider()
        kwargs = self.release_args(provider)
        kwargs["verify_secured"] = lambda data: None
        with self.assertRaises(Refusal):
            release(approval(), **kwargs)
        self.assertEqual(provider.deletes, [])
        self.assertFalse((self.root / "release.CLAIM").exists())

    def test_live_or_unknown_group_blocks_release(self):
        for live in (True, None, 0):
            value = {"exit_code": 0, "controller_live": False, "group_live": live, "kind": "complete"}
            from exp7ops.operator import terminal
            with self.assertRaises(Refusal):
                terminal(value)

    def test_failed_scientific_terminal_can_release_secured_failure(self):
        provider = FakeProvider()
        kwargs = self.release_args(provider, {"exit_code": 2, "controller_live": False, "group_live": False, "kind": "error"})
        self.assertEqual(release(approval(), **kwargs)["instance"], 42)

    def test_wrong_machine_and_changed_evidence_refuse(self):
        provider = FakeProvider()
        kwargs = self.release_args(provider)
        provider.rows["instances"][0]["machine_id"] = 99
        with self.assertRaises(Refusal):
            release(approval(), **kwargs)
        self.assertEqual(provider.deletes, [])
        provider.rows["instances"][0]["machine_id"] = 7
        (kwargs["evidence_root"] / "all-raw-and-logs").write_bytes(b"changed")
        with self.assertRaises(Refusal):
            release(approval(), **kwargs)
        self.assertEqual(provider.deletes, [])

    def test_malformed_after_delete_keeps_claim_then_reconciles_once(self):
        provider = FakeProvider()
        provider.after = {}
        kwargs = self.release_args(provider)
        with self.assertRaises(Refusal):
            release(approval(), **kwargs)
        self.assertTrue((self.root / "release.CLAIM").exists())
        self.assertFalse((self.root / "release.json").exists())
        provider.rows = {"instances": []}
        release(approval(), **kwargs)
        self.assertEqual(provider.deletes, [42])
        before = snapshot(self.root)
        inventory = recovery_inventory(self.root)
        self.assertIn("release.CLAIM", inventory["claims"])
        self.assertEqual(snapshot(self.root), before)

    def test_cost_cap_and_malformed_credit_stop(self):
        self.assertEqual(cost_guard(approval(), {"credit": 99}, forecast_remaining=10, reserve=2)["projected"], 13)
        for balance, remaining in (({"credit": 70}, 0), ({}, 1), ({"credit": 101}, 1)):
            with self.assertRaises(Refusal):
                cost_guard(approval(), balance, forecast_remaining=remaining, reserve=2)

    def test_constant_cli_and_remote_injection_refusal(self):
        self.assertIn("outcome", stage_argv("/python", "/repo", "outcome", "/contract"))
        with self.assertRaises(Refusal):
            stage_argv("/python", "/repo", "outcome; touch /bad", "/contract")
        route = {"host": "ssh7.vast.ai", "port": 1234, "key": "/private/key", "known_hosts": "/private/hosts"}
        argv = remote_argv(route, "snapshot")
        self.assertNotIn("-c", argv)
        for bad in ("ssh7.vast.ai;bad", "-oProxyCommand=bad", "ssh7.vast.ai\ncommand"):
            with self.assertRaises(Refusal):
                remote_argv({**route, "host": bad}, "snapshot")
        with self.assertRaises(Refusal):
            remote_argv(route, "unit", "unit;bad")

    def test_detach_registers_first_and_fails_closed(self):
        contract = self.root / "contract.json"
        contract.write_bytes(b"contract")
        fake = FakeProcess()
        def launch(out):
            return detached_launch(fake, python="/python", repo="/repo", contract=contract,
                stage="outcome", out=out, job="exp7-test", session="ses_realid", approval=approval(), check_monitor_pin=lambda: None)
        launch(self.root / "launched")
        self.assertEqual([c[0] for c in fake.calls], ["run", "spawn"])
        self.assertTrue(fake.calls[1][2]["start_new_session"])
        self.assertFalse(fake.calls[1][2]["shell"])
        fake.calls.clear(); fake.fail_monitor = True
        with self.assertRaises(RuntimeError):
            launch(self.root / "failed")
        self.assertEqual([c[0] for c in fake.calls], ["run"])
        self.assertEqual(strict((self.root / "failed/status.json").read_bytes())["exit_code"], 1)

    def test_dry_run_authenticates_without_dispatch_and_once_retains_claim(self):
        contract = self.root / "contract.json"
        contract.write_bytes(b"contract")
        calls = []
        class FakeComposition:
            def authenticate(self, stage, data):
                calls.append("auth")
                return approval(stage)
            def dry_run(self, stage, auth):
                calls.append("dry")
                return {"planned": 26}
            def execute(self, stage, auth, beat):
                calls.append("execute")
                beat({"completed": 0, "total": 26})
                return {"state": "COMPLETE", "done": True}
        args = dict(composition=FakeComposition(), contract_path=contract, output=self.root, pid=99, now=lambda: "fixture-time",
                    heartbeat_service=FakeHeartbeatService(FakeClock()))
        argv = ["outcome", "--contract", str(contract)]
        self.assertEqual(stage_main(argv + ["--dry-run"], **args), {"planned": 26})
        self.assertEqual(calls, ["auth", "dry"])
        stage_main(argv, **args)
        with self.assertRaises(FileExistsError):
            stage_main(argv, **args)
        self.assertEqual(calls.count("execute"), 1)
        for extra in ("--B=3", ";bad", "--python=bad"):
            with self.assertRaises(Refusal):
                stage_main(argv + [extra], **args)

    def test_scientific_refusal_and_halted_never_publish_operator_success(self):
        contract = self.root / "contract.json"; contract.write_bytes(b"contract")
        for case in ("refusal", "halted"):
            out = self.root / case; out.mkdir()
            class Composition:
                def authenticate(self, stage, data):
                    return approval(stage)
                def execute(self, stage, auth, beat):
                    if case == "halted":
                        once(out / "HALTED.json", {"state": "INSUFFICIENT_DATA"})
                        return {"state": "COMPLETE"}
                    return {"state": "INSUFFICIENT_DATA"}
            with self.assertRaises(Refusal):
                stage_main(["outcome", "--contract", str(contract)], composition=Composition(),
                    contract_path=contract, output=out, pid=99, now=lambda: "time",
                    heartbeat_service=FakeHeartbeatService(FakeClock()))
            self.assertTrue((out / "operator.CLAIM").exists())
            self.assertTrue((out / "HALTED.json").exists())
            self.assertFalse((out / "COMPLETE.json").exists())

    def test_whole_unit_hashes_rederived_then_immutable(self):
        calls = []
        check = lambda unit, data: calls.append(unit)
        data = payload()
        land_unit(self.root, "unit", data, verify=check)
        land_unit(self.root, "unit", data, verify=check)
        self.assertEqual(calls, ["unit", "unit"])
        bad = {**data, "raw.jsonl": b"changed"}
        with self.assertRaises(Refusal):
            land_unit(self.root, "bad", bad, verify=check)
        self.assertFalse((self.root / "bad").exists())
        (self.root / "unit/extra").write_bytes(b"unrecognized")
        with self.assertRaises(Refusal):
            land_unit(self.root, "unit", data, verify=check)

    def test_git_explicit_paths_and_remote_receipt(self):
        path = "experiments/exp7/results/unit.json"
        target = self.root / path
        target.parent.mkdir(parents=True); target.write_text("{}")
        calls = []
        class Git:
            def index_lock(self, repo):
                return nullcontext()
            def run(self, argv, **kw):
                self_outer.assertFalse(kw["shell"])
                calls.append(argv)
                if "rev-parse" in argv:
                    return "a"*40
                if "ls-remote" in argv:
                    return "a"*40 + "\trefs/heads/master\n"
                return ""
        self_outer = self
        self.assertEqual(publish_git(Git(), self.root, [path]), "a"*40)
        add = next(c for c in calls if "add" in c)
        self.assertEqual(add[-2:], ["--", path])
        self.assertTrue(all(c[0] == "/opt/homebrew/bin/git" for c in calls))
        with self.assertRaises(Refusal):
            publish_git(Git(), self.root, ["../other"])

    def test_heartbeat_ticks_every_five_minutes_with_minute_beats(self):
        from exp7ops.heartbeat import HeartbeatSession
        clock, calls = FakeClock(), []
        def tick():
            calls.append(clock.value)
            return {"terminal": len(calls) == 2}
        beats = []
        heartbeat = HeartbeatSession(self.root, pid=123, stage="watch", now=lambda:clock.value,
                                    service=FakeHeartbeatService(clock, beats))
        heartbeat.start()
        heartbeat_loop(tick=tick, heartbeat=heartbeat, clock=lambda:clock.value, wait=clock.advance)
        heartbeat.finish(exit_code=0, stage="complete")
        self.assertEqual(calls, [0, 300])
        self.assertLessEqual(max(b-a for a,b in zip(beats, beats[1:])), 60)

    def test_unknown_snapshot_and_missing_final_inventory_fail(self):
        for value in ({}, {"units": [], "terminal": None}, {"units": {"unknown": "a"*64}, "terminal": None}):
            with self.assertRaises(Refusal):
                validate_snapshot(value, ("unit",))

    def test_watcher_full_pull_verify_publish_secure_release_order(self):
        data, calls = payload(), []
        terminal = {"exit_code": 0, "controller_live": False, "group_live": False, "kind": "complete"}
        class Transport:
            def snapshot(self):
                return {"units": {"unit": digest(data["DONE.json"])}, "terminal": terminal}
            def unit(self, unit):
                calls.append("pull"); return data
            def final_evidence(self):
                return {"files": {"raw-and-logs": digest(b"everything")}, "payload": {"raw-and-logs": b"everything"}, "terminal": terminal}
        class Composition:
            def verify_unit(self, stage, unit, payload):
                calls.append("verify")
            def verify_final(self, root, term):
                calls.append("final-verify")
                return {"scientific_state": "COMPLETE", "failures": [], "inventory_sha256": "a"*64}
        def secure(*args):
            calls.append("secure")
            receipt = self.root / "independent.json"; once(receipt, {"fixture": True}); return receipt
        def release_saved(path):
            calls.append("release"); return {"instance": 42}
        land, out = self.root / "land", self.root / "out"
        land.mkdir(); out.mkdir()
        watcher = Watcher(approval=approval(), transport=Transport(), provider=FakeProvider(), composition=Composition(),
            root=land, out=out, expected_units=("unit",), publish=lambda p: calls.append("publish"),
            independently_secure=secure, release_secured=release_saved, forecast_remaining=lambda n: 1, reserve=2, now=lambda: "time")
        self.assertTrue(watcher.tick()["terminal"])
        self.assertEqual(calls, ["pull", "verify", "publish", "final-verify", "secure", "release"])
        with self.assertRaises(Refusal):
            watcher.tick()

    def test_independent_verifier_rederives_remote_inventory_and_git_bytes(self):
        evidence = self.root / "independent-tree"; evidence.mkdir()
        once(evidence / "data", b"raw, failed units, host records and logs")
        files = snapshot(evidence)
        observed = {"exit_code": 2, "controller_live": False, "group_live": False, "kind": "error"}
        class Reader:
            remote = "d"*40
            data = (evidence / "data").read_bytes()
            def remote_master(self):
                return self.remote
            def committed_file(self, head, name):
                return self.data
            def terminal_observation(self):
                return observed
            def required_inventory(self, terminal):
                return dict(files)
            def check_verifier_source(self):
                return "c"*64
        reader = Reader()
        paths = {"data": "experiments/exp7/operations/evidence/data"}
        output = self.root / "independent-receipt.json"
        write_secured(approval=approval(), reader=reader, root=evidence, files=files,
            evidence_commit="d"*40, observed_terminal=observed, publication_paths=paths, output=output)
        data = output.read_bytes()
        self.assertEqual(reverify_secured(data, approval=approval(), reader=reader, root=evidence, publication_paths=paths), digest(data))
        reader.remote = "e"*40
        with self.assertRaises(Refusal):
            reverify_secured(data, approval=approval(), reader=reader, root=evidence, publication_paths=paths)
        reader.remote = "d"*40; reader.data = b"corrupt committed blob"
        with self.assertRaises(Refusal):
            reverify_secured(data, approval=approval(), reader=reader, root=evidence, publication_paths=paths)

    def test_remote_wire_full_units_only_and_constant_operations(self):
        unit = "units/outcome/40000"
        data = payload()
        land_unit(self.root, unit, data, verify=lambda u,p: None)
        observed = {"exit_code": 0, "controller_live": False, "group_live": False, "kind": "complete"}
        kwargs = dict(root=self.root, allowed_units=(unit,), inventory=lambda: tuple(snapshot(self.root)),
            observe_terminal=lambda: observed, stop_path=self.root / "STOP_NEW_WORK", check_bindings=lambda: None)
        snap = remote_main(["snapshot"], **kwargs)
        self.assertEqual(snap["units"], {unit: digest(data["DONE.json"])})
        self.assertEqual(decode("unit", remote_main(["unit", unit], **kwargs)), data)
        final = decode("final-evidence", remote_main(["final-evidence"], **kwargs))
        self.assertEqual(set(final["files"]), set(final["payload"]))
        for argv in (["snapshot", "bad"], ["unit", "../../secrets"], ["sh", "-c", "bad"]):
            with self.assertRaises(Refusal):
                remote_main(argv, **kwargs)
        remote_main(["stop-new-work"], **kwargs)
        self.assertTrue((self.root / "STOP_NEW_WORK").exists())
