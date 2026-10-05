"""Concrete O8 leaves composed with genuine collection and security checks."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from exp7ops.evidence import canonical, digest, strict, Refusal, snapshot
from exp7ops.operator import Approval, release
from exp7ops.secured import write_secured, reverify_secured
from exp7ops.wire import encode_payload, decode
from exp7integration.metadata_transport import ReceiptSSH, metadata_reply
from exp7integration.controlled_backend import ControlledBackend
from exp7integration.security import IndependentSecuredReader, publication_paths
from collection_fixtures import fixture, FakeSession
from collection_fixture import ROOT, put


class O8CompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/"test-work")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)

    def metadata(self):
        f = fixture(self.repo)
        c = f.campaign()
        receipt = FakeSession(c, "outcome-40000").receipt
        checks = []
        d = SimpleNamespace(data={"watch": {"remote_site_sha256": digest(b"remote launch site"), "remote_package_root": "/workspace/repo/experiments/exp7"}},
                            check_sources=lambda: checks.append(True), _collection=lambda stage: f.campaign())
        class Process:
            response = {}
            calls = []
            def run(self, argv, **kwargs):
                self.calls.append(argv)
                return canonical(self.response).decode()
        p = Process()
        route = {"host": "ssh1.vast.ai", "port": 22, "key": "/fake/key", "known_hosts": "/fake/known_hosts"}
        transport = ReceiptSSH(p, route, self.repo, decode, d)
        return f, receipt, d, p, transport

    def test_real_load_metadata_lands_before_expected_unit_and_rejects_changed_receipt(self):
        f, receipt, d, p, transport = self.metadata()
        raw = canonical(receipt)
        name = "receipts/outcome-40000.json"
        p.response = {"files": {name: digest(raw)}, "payload": encode_payload({name: raw})}
        transport.sync_receipts()
        self.assertEqual((f.root/name).read_bytes(), raw)
        self.assertIn("metadata_7.py --site-sha256 "+d.data["watch"]["remote_site_sha256"], p.calls[0][-1])
        self.assertIn("/workspace/repo/experiments/exp7/run/metadata_7.py", p.calls[0][-1])
        self.assertNotIn("exp7_ops", p.calls[0][-1])
        with f.campaign() as c:
            expected = c.expected("units/outcome/40000")
            self.assertEqual(len(expected.addresses), 8000)
        transport.sync_receipts()  # same validated bytes are safe to observe again
        bad = deepcopy(receipt); bad["host"]["host_id"] = "remote-self-claim"
        raw = canonical(bad)
        p.response = {"files": {name: digest(raw)}, "payload": encode_payload({name: raw})}
        with self.assertRaises(ValueError):
            transport.sync_receipts()
        self.assertEqual((f.root/name).read_bytes(), canonical(receipt))

    def test_unplanned_receipt_never_lands(self):
        f, receipt, _, p, transport = self.metadata()
        raw = canonical(receipt); name = "receipts/unplanned.json"
        p.response = {"files": {name: digest(raw)}, "payload": encode_payload({name: raw})}
        with self.assertRaisesRegex(Refusal, "planned loads"):
            transport.sync_receipts()
        self.assertFalse((f.root/name).exists())

    def test_remote_metadata_only_selected_load_receipts(self):
        f, receipt, d, _, _ = self.metadata()
        put(f.root, "receipts/outcome-40000.json", receipt)
        put(f.root, "private-units.txt", b"not metadata")
        result = metadata_reply(d)
        self.assertEqual(set(result["files"]), {"receipts/outcome-40000.json"})
        put(f.root, "receipts/unplanned.json", {})
        with self.assertRaises(Refusal):
            metadata_reply(d)

    def test_controlled_backend_uses_real_campaign_grant_and_stop_before_next_family(self):
        f = fixture(self.repo)
        checks, samples = [], []
        class Beat:
            def check(self): checks.append("check")
            def __call__(self, detail): checks.append(detail)
        class Session:
            receipt = {"fixture": True}
            def sample(self, prompt, **kw): samples.append(prompt); return {0: [prompt]}
            def close(self): checks.append("close")
        class Backend:
            def open(self, load): checks.append(load); return Session()
        stop = f.root/"STOP_NEW_WORK.json"
        with f.campaign() as c:
            from exp7core.collectors import backend_of
            backend = backend_of(c, ControlledBackend(Beat(), stop, backend=Backend()), "predictor-collection")
            session = backend.open("sample-pythia_1b")
            session.sample("first", rung="exp7/unscrambling/q0")
            put(f.root, "STOP_NEW_WORK.json", {"reason": "synthetic stop"})
            session.sample("same-family", rung="exp7/unscrambling/q1")
            with self.assertRaisesRegex(ValueError, "STOP_NEW_WORK"):
                session.sample("next-family", rung="exp7/deduction/q0")
            session.close()
        self.assertEqual(samples, ["first", "same-family"])
        self.assertIn("close", checks)

    def security(self, *, success=False):
        root = self.repo/"experiments/exp7/security"
        remote = {"units/bad/raw.jsonl": b"torn raw evidence", "HALTED.json": canonical({"state": "INSUFFICIENT_DATA"})}
        remote["supervisor-inventory.json"] = canonical({"schema": "exp7.remote-supervisor-inventory.v1",
            "roots": {"outcome": {"root": "/fake/remote-supervisor", "exists": False, "files": {}}}})
        term = {"exit_code": 0 if success else 1, "kind": "complete" if success else "error", "controller_live": False, "group_live": False}
        files = {n: digest(v) for n, v in remote.items()}
        for name, value in remote.items(): put(root/"remote", name, value)
        diagnostics = {"scientific_state": "COMPLETE" if success else "INSUFFICIENT_DATA", "failures": [],
                       "inventory_sha256": digest(canonical(files))}
        put(root/"local", "terminal-unit-failures.json", [])
        put(root/"local", "final-verification.json", diagnostics)
        verifier = "experiments/exp7/verifier.py"
        pins = {verifier: put(self.repo, verifier, b"# pinned fake verifier source\n")}
        calls = []
        d = SimpleNamespace(repo=self.repo, data={"verifier_sources": pins,
                            "stages": {"outcome": {"output": "/fake/remote-supervisor"}},
                            "remote": {"supervisor_stages": ["outcome"]}}, check_sources=lambda: calls.append("sources"),
                            verify_final=lambda archive, observed: (calls.append("independent scientific check") or diagnostics))
        observation = {"files": files, "payload": remote, "terminal": term}
        transport = SimpleNamespace(final_evidence=lambda: deepcopy(observation))
        commit = "1"*40
        class Process:
            def run(self, argv, **kwargs): return commit+"\trefs/heads/master\n"
            def read_git_blob(self, repo, head, path):
                if head != commit: raise ValueError("wrong commit")
                return (repo/path).read_bytes()
        approval = Approval(digest(b"contract"), digest(b"grant"), "watch", 7, 8, "fake-rental", 10, 5, digest(canonical(pins)))
        reader = IndependentSecuredReader(d, approval, Process(), transport, root, commit)
        return root, term, d, observation, reader, approval, calls

    def test_failed_terminal_complete_inventory_secured_then_reverified(self):
        root, term, d, observed, reader, approval, calls = self.security()
        files = reader.required_inventory(term); paths = publication_paths(d, root, files)
        output = self.repo/"secured.json"
        sha = write_secured(approval=approval, reader=reader, root=root, files=files, evidence_commit="1"*40,
                            observed_terminal=term, publication_paths=paths, output=output)
        self.assertEqual(sha, digest(output.read_bytes()))
        self.assertIn("remote/units/bad/raw.jsonl", files)
        observed["payload"]["new-failure.txt"] = b"new failure"
        observed["files"]["new-failure.txt"] = digest(b"new failure")
        with self.assertRaises(Refusal):
            reverify_secured(output.read_bytes(), approval=approval, reader=reader, root=root, publication_paths=paths)
        self.assertNotIn("independent scientific check", calls)

    def test_success_claim_requires_independent_scientific_validation(self):
        root, term, d, observed, reader, approval, calls = self.security(success=True)
        def refuse(*args): raise ValueError("synthetic invalid archive caught independently")
        d.verify_final = refuse
        with self.assertRaisesRegex(ValueError, "independently"):
            reader.required_inventory(term)

    def test_extra_local_failure_file_cannot_be_omitted_from_secured_manifest(self):
        root, term, _, _, reader, _, _ = self.security()
        put(root, "local/forgotten.log", b"failed operation")
        with self.assertRaisesRegex(Refusal, "full remote and local"):
            reader.required_inventory(term)
