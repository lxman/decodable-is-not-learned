from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
import tempfile
import unittest
from exp7ops.evidence import canonical, digest, Refusal, strict
from exp7ops.operator import Approval
from exp7ops.dispatch import FixedComposition
from exp7integration.deployment import FixedStageDeployment, STAGE_MAP
from exp7integration.bootstrap import write_site_binding
from exp7integration.calibration_copy import copy_accepted_calibration
from exp7integration.security import IndependentSecuredReader
from collection_fixture import ROOT, put


class Callback:
    def __init__(self):
        self.rows = []
    def __call__(self, value):
        self.rows.append(value)
    def check(self):
        return {"fixture": "live independent worker"}


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/"test-work")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)/"repo"
        self.repo.mkdir()
        self.root = self.repo/"experiments/exp7/campaign"; self.root.mkdir(parents=True)
        pins = {}
        for package in ("exp7core", "exp7stats", "exp7ops", "exp7integration", "run"):
            name = f"experiments/exp7/{package}/__init__.py"
            pins[name] = put(self.repo, name, b"# independently pinned fake source\n")
        self.grant = {"scope": "fixture", "evidence": "explicit test double"}
        self.calls, self.events = [], []
        self.config = {"schema": "exp7.fixed-deployment.v1", "repo": str(self.repo), "root": str(self.root),
                       "source_pins": pins, "outcome_host": "fakehost", "python": "/fixed/python", "stages": {}}
        for name in STAGE_MAP:
            raw = canonical({"schema": "exp7.stage-contract.v1", "stage": name, "grant_sha256": digest(canonical(self.grant)),
                             "instance": None, "machine": None, "label": None, "credit_before": 0, "cap": 0,
                             "verifier_code_sha256": digest(b"verifier")})
            path = self.repo/f"{name}.json"; path.write_bytes(raw)
            self.config["stages"][name] = {"trust_path": "independent-trust.json", "trust_sha256": digest(b"trust"),
                "contract_path": str(path), "contract_sha256": digest(raw), "output": str(Path(self.tmp.name)/"supervisors"/name),
                "adapter_authority_path": str(self.repo.parent/"not-read-authority.json"), "adapter_authority_sha256": digest(b"authority")}
        self.config["digest_baseline"] = {"trust_path": "baseline-trust.json", "trust_sha256": digest(b"baseline authority")}
        self.path = self.repo/"deployment.json"
        def collection(root, repo, **kwargs):
            self.calls.append(kwargs)
            return {"state": "COMPLETE", "value": {"fixture": True}}
        def campaign(*args, **kwargs):
            self.events.append("Campaign constructor")
            trust = SimpleNamespace(prereg_projection=lambda: self.events.append("prereg/projection"),
                                    grant=lambda scope: (self.events.append(scope) or deepcopy(self.grant)))
            return SimpleNamespace(root=self.root, repo=self.repo, trust=trust)
        self.collection, self.campaign = collection, campaign
        self.persist()

    def persist(self):
        self.path.write_bytes(canonical(self.config))
        self.deployment = FixedStageDeployment(self.path, digest(self.path.read_bytes()),
                                               collection=self.collection, campaign_factory=self.campaign)

    def approval(self, name):
        p = self.config["stages"][name]
        return self.deployment.authenticate(name, Path(p["contract_path"]).read_bytes())

    def test_authentication_pins_and_formal_grant_before_dispatch(self):
        self.approval("power")
        self.assertEqual(self.events, ["Campaign constructor", "prereg/projection", "power"])
        self.assertEqual(self.calls, [])
        with self.assertRaises(Refusal):
            self.deployment.authenticate("power", b'{"approved":true}')
        self.assertEqual(self.calls, [])

    def test_predictor_order_twin_seal_outcome_and_independent_complete_producer(self):
        heartbeats = Callback()
        self.deployment.predictor_preflight(self.approval("predictor-preflight"), heartbeats)
        self.deployment.predictor(self.approval("predictor"), heartbeats)
        self.deployment.seal(self.approval("seal"), heartbeats)
        self.deployment.outcome_preflight(self.approval("outcome-preflight"), heartbeats)
        self.deployment.outcome(self.approval("outcome"), heartbeats)
        self.assertEqual([(v["stage"], v["subject"]) for v in self.calls],
                         [(stage, model) for stage in ("predictor-preflight", "predictor-collection")
                          for model in ("pythia_1b", "olmo2_1b", "twin")]+[("predictor-seal", None),
                          ("outcome-preflight", "fakehost"), ("outcome-collection", None), ("campaign-complete", None)])
        self.assertTrue(all(callable(v["power_validator"]) for v in self.calls))
        self.assertEqual(heartbeats.rows[-1]["phase"], "campaign-complete")

    def test_digest_baseline_is_separate_fixed_stage_not_missing_value_fallback(self):
        p = self.config["digest_baseline"]
        self.deployment.predictor_digest_baseline(**p)
        self.assertEqual(self.calls[0]["stage"], "predictor-digest-baseline")
        with self.assertRaises(Refusal):
            self.deployment.predictor_digest_baseline(trust_path="arbitrary", trust_sha256=p["trust_sha256"])

    def test_statistics_campaign_unentered_and_no_input_reads(self):
        a = self.deployment.campaign("power", self.approval("power"))
        self.assertEqual(a._stage, None)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.events[-1], "Campaign constructor")

    def test_supervisor_root_is_disjoint_and_rejects_raw_or_extra_contact_files(self):
        self.config["stages"]["power"]["output"] = str(self.root/"operations")
        with self.assertRaisesRegex(Refusal, "disjoint"):
            self.persist()
        out = Path(self.tmp.name)/"power-supervisor"
        self.config["stages"]["power"]["output"] = str(out)
        out.mkdir()
        put(out, "status.json", {"pid": 123, "stage": "power", "exit_code": None})
        self.persist()
        put(out, "outcome-probe.json", {"stage": "outcome"})
        with self.assertRaisesRegex(Refusal, "non-operational"):
            self.deployment.check_sources()

    def test_refusal_stops_next_subject_and_source_drift_stops_dispatch(self):
        def fail(root, repo, **kwargs):
            self.calls.append(kwargs)
            return {"state": "INSUFFICIENT_DATA"}
        self.deployment.collection_run = fail
        with self.assertRaises(Refusal):
            self.deployment.predictor(self.approval("predictor"), Callback())
        self.assertEqual(len(self.calls), 1)
        p = next(iter(self.config["source_pins"]))
        (self.repo/p).write_bytes(b"drift")
        with self.assertRaises(Refusal):
            self.deployment.predictor(self.approval("predictor"), Callback())

    def test_supervisor_waits_for_atomic_staging_without_admitting_partial_bytes(self):
        from exp7integration.supervisor import check_supervisor
        out = Path(self.tmp.name)/"settling"; out.mkdir()
        pending = out/"status.json.next-fake123"; pending.write_bytes(b'{"partial":')
        check_supervisor(out, repo=self.repo, campaign=self.root, stage="power", settle=lambda seconds: pending.unlink())
        pending.write_bytes(b"abandoned")
        with self.assertRaisesRegex(Refusal, "did not settle"):
            check_supervisor(out, repo=self.repo, campaign=self.root, stage="power", settle=lambda seconds: None)

    def test_omitted_source_and_empty_injection_fail_closed(self):
        put(self.repo, "experiments/exp7/exp7stats/hidden.py", b"# omitted\n")
        with self.assertRaises(Refusal):
            self.persist()
        for backend in (None, False, {}, []):
            with self.assertRaises(Refusal):
                FixedStageDeployment(self.path, digest(self.path.read_bytes()), backend=backend)

    def test_site_binding_requires_independent_exact_digest_and_write_once(self):
        value = {"schema": "exp7.site-binding.v1", "config_path": str(self.path),
                 "config_sha256": digest(self.path.read_bytes()), "package_root": str(self.repo/"experiments/exp7")}
        path = self.repo/"site_7.json"
        with self.assertRaises(Refusal):
            write_site_binding(path, config_path=self.path, config_sha256=value["config_sha256"],
                               package_root=value["package_root"], expected_binding_sha256=digest(b"wrong"))
        sha = write_site_binding(path, config_path=self.path, config_sha256=value["config_sha256"],
                                  package_root=value["package_root"], expected_binding_sha256=digest(canonical(value)))
        self.assertEqual(sha, digest(path.read_bytes()))
        with self.assertRaises(FileExistsError):
            write_site_binding(path, config_path=self.path, config_sha256=value["config_sha256"],
                               package_root=value["package_root"], expected_binding_sha256=sha)

    def test_copy_accepted_calibration_exact_bytes_and_existing_path_refusal(self):
        source = self.repo/"pretag-accepted"; source.mkdir()
        # Saved-byte binding fixture only, not a calibration observation. The
        # genuine production semantics are separately checked by stats.power.run.
        files = {"CLAIM.json": canonical({"stage": "calibration"}), "REPORT.md": b"FAKE archived acceptance fixture\n",
                 "calibration.json": canonical({"production": True, "fixture": "saved-binding-only", "state": "NO-DETECTED-CALIBRATION-DEFECT"})}
        files["COMPLETE.json"] = canonical({"files": {n: digest(files[n]) for n in ("calibration.json", "REPORT.md")}})
        pins = {n: digest(v) for n, v in files.items()}
        for name, value in files.items():
            (source/name).write_bytes(value)
        self.assertEqual(copy_accepted_calibration(source, self.root, accepted_files=pins), pins)
        for name, value in files.items():
            self.assertEqual((self.root/"statistics/calibration"/name).read_bytes(), value)
        with self.assertRaises(FileExistsError):
            copy_accepted_calibration(source, self.root, accepted_files=pins)

    def test_independent_security_inventory_keeps_invalid_remote_and_local_diagnostics(self):
        self.config["remote"] = {"evidence_root": str(self.root), "supervisor_stages": list(STAGE_MAP)}
        self.persist()
        root = self.repo/"security"; (root/"remote").mkdir(parents=True); (root/"local").mkdir()
        remote = {"units/bad/raw.jsonl": b"invalid raw", "HALTED.json": b'{"failed":true}\n'}
        remote["supervisor-inventory.json"] = canonical({"schema": "exp7.remote-supervisor-inventory.v1",
            "roots": {name: {"root": row["output"], "exists": False, "files": {}}
                      for name, row in self.config["stages"].items()}})
        hashes = {n: digest(v) for n, v in remote.items()}
        for name, value in remote.items():
            put(root/"remote", name, value)
        observation = {"exit_code": 1, "controller_live": False, "group_live": False, "kind": "error"}
        put(root/"local", "terminal-unit-failures.json", [{"unit": "units/bad", "error_type": "Refusal"}])
        put(root/"local", "final-verification.json", {"scientific_state": "INSUFFICIENT_DATA", "failures": ["invalid raw"],
                                                      "inventory_sha256": digest(canonical(hashes))})
        transport = SimpleNamespace(final_evidence=lambda: {"files": hashes, "payload": remote, "terminal": observation})
        reader = IndependentSecuredReader(self.deployment, None, None, transport, root, "1"*40)
        expected = reader.required_inventory(observation)
        self.assertEqual(len(expected), 5)
        self.assertIn("remote/supervisor-inventory.json", expected)
        self.assertIn("remote/units/bad/raw.jsonl", expected)
        self.assertIn("local/terminal-unit-failures.json", expected)
        (root/"local/terminal-unit-failures.json").unlink()
        with self.assertRaises(FileNotFoundError):
            reader.required_inventory(observation)
