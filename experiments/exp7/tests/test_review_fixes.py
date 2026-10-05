import guard
from pathlib import Path
from contextlib import nullcontext
import importlib.util
import inspect
import sys
import tempfile
import unittest
from exp7ops.evidence import once, state, strict, canonical, digest, snapshot, Refusal, selected_instances
from exp7ops.operator import detached_launch, publish_git
from exp7ops.scans import ReadImportScan
from exp7ops.watcher import Watcher, heartbeat_loop
from exp7ops.wire import remote_main
from test_operations import approval, payload, FakeProcess

# Written into each review receipt; deterministic fake-clock observations only.
OBSERVATIONS = {}

TERMINAL = {"exit_code": 2, "controller_live": False, "group_live": False, "kind": "error"}

class ReviewFixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_R1_fast_terminal_and_unknown_child_status_survive_sid_failure(self):
        for finished in (True, False):
            with self.subTest(finished=finished):
                case = self.root / str(finished); case.mkdir()
                contract = case / "contract"; once(contract, b"contract")
                out = case / "launch"
                class Child(FakeProcess):
                    def spawn(self, argv, **kwargs):
                        saved = {"pid": 123, "stage": "complete" if finished else "outcome", "exit_code": 0 if finished else None}
                        state(out / "status.json", saved)
                        if finished:
                            once(out / "COMPLETE.json", {"state": "COMPLETE"})
                        return 123
                    def session_id(self, pid):
                        raise ProcessLookupError("synthetic uncertain SID")
                    def terminate(self, pid):
                        raise AssertionError("must not signal unknown/exited child")
                try:
                    detached_launch(Child(), python="/python", repo="/repo", contract=contract,
                        stage="outcome", out=out, job="exp7-review", session="ses_fake", approval=approval(), check_monitor_pin=lambda: None)
                except ProcessLookupError:
                    pass
                self.assertEqual(strict((out / "status.json").read_bytes())["exit_code"], 0 if finished else None)
                self.assertEqual(strict((out / "launch-observation.json").read_bytes())["child_state"], "UNKNOWN")
                if finished:
                    self.assertEqual(strict((out / "COMPLETE.json").read_bytes()), {"state":"COMPLETE"})

    def test_R1_bound_child_handle_checks_exit_before_sid_or_termination(self):
        from exp7ops.runtime import SystemProcess
        port = SystemProcess()
        class ExitedChild:
            def poll(self):
                return 0
            def terminate(self):
                raise AssertionError("exited bound child must not be signaled")
        port.children[123] = ExitedChild()
        # Early bound-child poll prevents any real SID query or signal.
        with self.assertRaises(ProcessLookupError):
            port.session_id(123)
        port.terminate(123)
        with self.assertRaises(Refusal):
            port.terminate(456)

    def test_R2_invalid_done_failed_campaign_is_preserved_not_admitted(self):
        bad = payload(); bad["raw.jsonl"] = b"invalid hash\n"
        files = {"unit/"+k: v for k,v in bad.items()}
        files["unit/error.log"] = b"failed writer diagnostic"
        calls = []
        class Transport:
            def snapshot(self):
                return {"units": {"unit": digest(bad["DONE.json"])}, "terminal": TERMINAL}
            def unit(self, unit):
                return bad
            def final_evidence(self):
                calls.append("archive")
                return {"files": {n:digest(v) for n,v in files.items()}, "payload": files, "terminal": TERMINAL}
        class Composition:
            def verify_unit(self, *args):
                return None
            def verify_final(self, *args):
                return {"scientific_state": "INSUFFICIENT_DATA", "failures": ["bad raw hash"], "inventory_sha256": "a"*64}
        def secure(*args):
            calls.append("secure")
            saved = self.root / "independent.json"; once(saved, {"fixture": True}); return saved
        land, out = self.root / "land", self.root / "out"
        land.mkdir(); out.mkdir()
        watch = Watcher(approval=approval(), transport=Transport(), provider=None, composition=Composition(), root=land, out=out,
            expected_units=("unit",), publish=lambda p: calls.append("publish"), independently_secure=secure,
            release_secured=lambda p: calls.append("release") or {"instance":42}, forecast_remaining=lambda n:1, reserve=2, now=lambda:"time")
        error = None
        try:
            watch.tick()
        except Refusal as exc:
            error = str(exc)
        self.assertIsNone(error, "failed scientific unit must not prevent preservation")
        self.assertEqual(calls, ["archive", "secure", "release"])
        self.assertFalse((land / "unit").exists())
        self.assertEqual((out / "preserved-final/unit/error.log").read_bytes(), files["unit/error.log"])
        self.assertTrue(strict((out / "final-verification.json").read_bytes())["failures"])

    def test_R2_remote_failed_terminal_survives_extra_done_diagnostic(self):
        unit = self.root / "unit"; unit.mkdir()
        for name, data in payload().items():
            once(unit / name, data)
        once(unit / "error.log", b"diagnostic")
        error, result = None, None
        try:
            result = remote_main(["snapshot"], root=self.root, allowed_units=("unit",), inventory=lambda:tuple(snapshot(self.root)),
                observe_terminal=lambda:TERMINAL, stop_path=self.root/"STOP", check_bindings=lambda:None)
        except Refusal as exc:
            error = str(exc)
        self.assertIsNone(error)
        self.assertEqual(result["terminal"], TERMINAL)

    def test_R3_failed_list_envelope_never_establishes_absence(self):
        for response in ({"success":False,"error":"secret synthetic failure","instances":[]},
                         {"success":True,"error":"synthetic failure","instances":[]},
                         {"success":0,"instances":[]}, {"errors":["failure"],"instances":[]}):
            with self.subTest(response=response), self.assertRaises(Refusal):
                selected_instances(response)

    def test_R4_commit_is_scoped_despite_racing_index_and_diff_checked_before_push(self):
        rel = "experiments/exp7/evidence.json"
        path = self.root / rel; path.parent.mkdir(parents=True); once(path,b"{}")
        class Git:
            def __init__(self):
                self.index, self.committed, self.calls, self.diffs = {rel}, [], [], 0
            def index_lock(self, repo):
                return nullcontext()
            def run(self, argv, **kwargs):
                self.calls.append(argv)
                cmd = argv[3:]
                if cmd[:3] == ["diff", "--cached", "--name-only"]:
                    self.diffs += 1; observed = "\n".join(sorted(self.index))
                    if self.diffs == 2:
                        self.index.add("user-unrelated.txt")
                    return observed
                if cmd[0] == "commit":
                    self.committed = cmd[cmd.index("--")+1:] if "--only" in cmd and "--" in cmd else sorted(self.index)
                if cmd[0] == "rev-parse":
                    return "d"*40 if self.committed else "a"*40
                if cmd[0] == "rev-list":
                    return "d"*40 + " " + "a"*40
                if cmd[0] == "diff-tree":
                    return "\0".join(self.committed) + "\0"
                if cmd[0] == "ls-remote":
                    return "d"*40 + "\trefs/heads/master"
                return ""
        fake = Git(); publish_git(fake,self.root,[rel])
        self.assertEqual(fake.committed,[rel])
        commands = [c[3] for c in fake.calls]
        self.assertIn("diff-tree",commands)
        self.assertLess(commands.index("diff-tree"),commands.index("push"))

    def test_R5_actual_cold_source_loader_allows_absent_cache_and_tracks_alias(self):
        source = self.root / "fixture.py"; once(source,b"value = 7\n")
        scan = ReadImportScan({self.root:{"fixture.py":digest(source.read_bytes())}})
        error, module = None, None
        try:
            with scan:
                spec = importlib.util.spec_from_file_location("temporary_fix_alias",source)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                del sys.modules[spec.name]
        except Refusal as exc:
            error = str(exc)
        finally:
            sys.modules.pop("temporary_fix_alias",None)
        self.assertIsNone(error)
        self.assertEqual(module.value,7)
        self.assertIn(str(source),scan.receipt()["execs"])
        self.assertFalse((self.root/"__pycache__").exists())

    def test_R6_independent_service_beats_during_901_second_blocking_tick(self):
        from heartbeat_fakes import FakeClock, FakeHeartbeatService
        clock, calls = FakeClock(), []
        def tick():
            calls.append(clock.value); clock.advance(901)
            return {"terminal":len(calls)==2}
        beats = []
        kwargs = dict(tick=tick,clock=lambda:clock.value,wait=clock.advance)
        if "heartbeat" in inspect.signature(heartbeat_loop).parameters:
            from exp7ops.heartbeat import HeartbeatSession
            service = FakeHeartbeatService(clock, beats)
            heartbeat = HeartbeatSession(self.root, pid=123, stage="watch", now=lambda:clock.value, service=service)
            heartbeat.start()
            heartbeat_loop(heartbeat=heartbeat, **kwargs)
            heartbeat.finish(exit_code=0,stage="complete")
        else:
            heartbeat_loop(beat=lambda:beats.append(clock.value), **kwargs)
        self.assertGreaterEqual(len(beats),3)
        self.assertLessEqual(max(b-a for a,b in zip(beats,beats[1:])),60)
        OBSERVATIONS["R6_blocking_tick"] = {"beats": beats, "max_gap":max(b-a for a,b in zip(beats,beats[1:])), "work_calls":calls}

    def test_R3_transport_status_and_failed_post_delete_list_block_receipt(self):
        from exp7ops.evidence import successful_instance_response
        from exp7ops.operator import release
        from test_operations import FakeProvider
        for status in (False, "200", 199, 300, 401, 500):
            with self.assertRaises(Refusal):
                successful_instance_response(status,{"instances":[]})
        self.assertEqual(successful_instance_response(200,{"instances":[]}),{"success":True,"instances":[]})
        evidence = self.root / "evidence"; evidence.mkdir(); once(evidence/"raw",b"secured failure")
        receipt = self.root / "secured.json"
        once(receipt,{"schema":"exp7.independently-secured.v1","instance":42,"machine":7,
            "contract_sha256":approval().contract_sha256,"verifier_code_sha256":"c"*64,
            "files":snapshot(evidence),"evidence_commit":"d"*40,"terminal":TERMINAL})
        provider = FakeProvider(); provider.after = {"success":False,"error":"do not persist this text","instances":[]}
        kwargs = dict(provider=provider,evidence_root=evidence,secured_receipt=receipt,verify_secured=digest,out=self.root)
        with self.assertRaises(Refusal):
            release(approval(),**kwargs)
        self.assertTrue((self.root/"release.CLAIM").exists())
        self.assertFalse((self.root/"release.json").exists())
        provider.rows = {"success":True,"instances":[]}
        release(approval(),**kwargs)
        self.assertEqual(provider.deletes,[42])

    def test_R2_invalid_claimed_success_is_archived_but_never_secured_or_released(self):
        term={**TERMINAL,"exit_code":0,"kind":"complete"}
        data=payload(); data["raw.jsonl"]=b"bad hash"
        archive={"unit/"+n:b for n,b in data.items()}
        calls=[]
        class Transport:
            def snapshot(self):
                return {"units":{"unit":digest(data["DONE.json"])},"terminal":term}
            def unit(self, unit):
                return data
            def final_evidence(self):
                calls.append("archive")
                return {"files":{n:digest(b) for n,b in archive.items()},"payload":archive,"terminal":term}
        class Composition:
            def verify_unit(self,*args):
                return None
            def verify_final(self,*args):
                raise Refusal("bad scientific data")
        land,out=self.root/"land",self.root/"out";land.mkdir();out.mkdir()
        watch=Watcher(approval=approval(),transport=Transport(),provider=None,composition=Composition(),root=land,out=out,
            expected_units=("unit",),publish=lambda p:calls.append("publish"),independently_secure=lambda *a:calls.append("secure"),
            release_secured=lambda p:calls.append("release"),forecast_remaining=lambda n:1,reserve=2,now=lambda:"time")
        with self.assertRaisesRegex(Refusal,"success claims incomplete"):
            watch.tick()
        self.assertEqual(calls,["archive"])
        self.assertEqual((out/"preserved-final/unit/raw.jsonl").read_bytes(),b"bad hash")
        self.assertEqual(strict((out/"final-verification.json").read_bytes())["scientific_state"],"INSUFFICIENT_DATA")
        self.assertFalse((land/"unit").exists())

    def test_R6_worker_stops_on_bound_parent_loss_without_inventing_terminal(self):
        from exp7ops.heartbeat import heartbeat_worker
        config={"root":str(self.root),"pid":123,"stage":"watch"}
        config["heartbeat_identity_sha256"]=digest(canonical(config));once(self.root/"config.json",config)
        state(self.root/"status.json",{"pid":123,"stage":"watch","exit_code":None})
        before=(self.root/"status.json").read_bytes()
        result=heartbeat_worker(self.root/"config.json",now=lambda:0,wait=lambda s:self.fail("wait after parent loss"),parent_alive=lambda p:False)
        self.assertEqual(result["state"],"INSUFFICIENT_DATA")
        self.assertEqual((self.root/"status.json").read_bytes(),before)

    def test_R4_actual_commit_diff_outside_scope_blocks_push(self):
        rel = "experiments/exp7/evidence.json"
        path = self.root/rel; path.parent.mkdir(parents=True); once(path,b"{}")
        calls = []
        class Git:
            changed = False
            def index_lock(self, repo):
                return nullcontext()
            def run(self, argv, **kw):
                cmd = argv[3:]; calls.append(cmd)
                if cmd[0] == "rev-parse":
                    return ("d" if self.changed else "a")*40
                if cmd[0] == "diff":
                    return rel
                if cmd[0] == "commit":
                    self.changed = True
                if cmd[0] == "rev-list":
                    return "d"*40 + " " + "a"*40
                if cmd[0] == "diff-tree":
                    return rel + "\0user-unrelated.txt\0"
                return ""
        with self.assertRaisesRegex(Refusal,"actual commit escaped"):
            publish_git(Git(),self.root,[rel])
        self.assertFalse(any(c[0]=="push" for c in calls))

    def test_R5_existing_unpinned_bytecode_is_refused_and_source_exit_drift_detected(self):
        source = self.root/"fixture.py"; once(source,b"value = 7\n")
        cached = Path(importlib.util.cache_from_source(str(source)))
        cached.parent.mkdir(); once(cached,b"untrusted cached code")
        pins = {"fixture.py":digest(source.read_bytes())}
        def load(scan):
            with scan:
                spec = importlib.util.spec_from_file_location("existing_cache_alias",source)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        with self.assertRaises(Refusal):
            load(ReadImportScan({self.root:pins}))
        cached.unlink(); cached.parent.rmdir()
        with self.assertRaises(Refusal):
            with ReadImportScan({self.root:pins}):
                spec = importlib.util.spec_from_file_location("drift_alias",source)
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                source.write_bytes(b"value = 9\n")

    def test_R6_single_status_writer_terminal_is_stable_and_state_staging_is_unique(self):
        from heartbeat_fakes import FakeClock, FakeHeartbeatService
        from exp7ops.heartbeat import HeartbeatWriter, HeartbeatSession
        import exp7ops.evidence as ev
        clock = FakeClock(); session = HeartbeatSession(self.root,pid=123,stage="watch",now=lambda:clock.value,service=FakeHeartbeatService(clock))
        session.start()
        other = HeartbeatWriter.from_config(self.root/"heartbeat-config.json",now=lambda:clock.value)
        with self.assertRaises(FileExistsError):
            other.start()
        session.update({"completed":1,"total":2})
        clock.advance(60)
        session.finish(exit_code=0,stage="complete")
        saved = (self.root/"status.json").read_bytes()
        with self.assertRaises(Refusal):
            session.update({"phase":"late"})
        clock.advance(120)
        self.assertEqual((self.root/"status.json").read_bytes(),saved)
        path = self.root/"interleaved.json"; original_fsync=ev.os.fsync; nested=[]
        def interleave(fd):
            if not nested:
                nested.append(True); state(path,{"writer":"inner"})
            original_fsync(fd)
        try:
            ev.os.fsync=interleave
            state(path,{"writer":"outer"})
        finally:
            ev.os.fsync=original_fsync
        self.assertEqual(strict(path.read_bytes()),{"writer":"outer"})
        self.assertEqual(list(self.root.glob("interleaved.json.next*")),[])

    def test_R6_long_collection_power_and_verdict_are_covered_without_cooperative_callbacks(self):
        from heartbeat_fakes import FakeClock, FakeHeartbeatService
        from exp7ops.dispatch import FixedComposition
        from exp7ops.operator import stage_main
        for stage in ("predictor","power","verdict","watch"):
            with self.subTest(stage=stage):
                root = self.root/stage; root.mkdir(); contract=root/"contract"; once(contract,b"contract")
                clock, beats = FakeClock(), []
                class Deployment:
                    def authenticate(self, stage, data):
                        return approval(stage)
                    def work(self, auth, update):
                        update({"phase":"collection"})
                        if auth.stage == "watch":
                            def tick():
                                clock.advance(901)
                                return {"terminal":True}
                            heartbeat_loop(tick=tick,heartbeat=update,clock=lambda:clock.value,wait=clock.advance)
                        else:
                            clock.advance(901)
                        return {"state":"COMPLETE"}
                    predictor_preflight = predictor = seal = outcome_preflight = outcome = watch = work
                    def campaign(self, stage, auth):
                        return {"stage":stage}
                    def stage_result(self, stage, result):
                        return result
                def stats(campaign):
                    clock.advance(901); return {"state":"COMPLETE"}
                composition=FixedComposition(Deployment(),power_run=stats,analyzer_run=stats)
                stage_main([stage,"--contract",str(contract)],composition=composition,contract_path=contract,
                    output=root,pid=123,now=lambda:clock.value,heartbeat_service=FakeHeartbeatService(clock,beats))
                self.assertLessEqual(max(b-a for a,b in zip(beats,beats[1:])),60)
                self.assertEqual(strict((root/"status.json").read_bytes())["exit_code"],0)
                OBSERVATIONS["R6_long_"+stage]={"beats":beats,"max_gap":max(b-a for a,b in zip(beats,beats[1:]))}
