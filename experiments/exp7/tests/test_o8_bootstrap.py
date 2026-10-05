"""Execute fixed bootstrap pre-import verification, with dispatch replaced by a recorder."""
from pathlib import Path
from types import SimpleNamespace
import runpy
import sys
import tempfile
import unittest
from exp7ops.evidence import canonical, digest, strict
from exp7ops.operator import stage_argv
from exp7integration.launch import SiteBoundProcess
from exp7integration import bootstrap
from collection_fixture import ROOT, put
from testing_paths import PACKAGE


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/"test-work")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.package = self.repo/"experiments/exp7"
        self.pins = {}
        for name in ("exp7core", "exp7stats", "exp7ops", "exp7integration", "run"):
            file = f"experiments/exp7/{name}/__init__.py"
            self.pins[file] = put(self.repo, file, b"# fake immutable package\n")
        file = "experiments/exp7/run/stage_7.py"
        self.pins[file] = put(self.repo, file, (PACKAGE/"run/stage_7.py").read_bytes())
        self.program = self.repo/file
        self.config = {"repo": str(self.repo), "source_pins": self.pins}
        self.config_path = self.repo/"deployment.json"
        self.config_path.write_bytes(canonical(self.config))
        self.site = {"schema": "exp7.site-binding.v1", "package_root": str(self.package),
                     "config_path": str(self.config_path), "config_sha256": digest(self.config_path.read_bytes())}
        self.site_path = self.program.with_name("site_7.json")
        self.site_path.write_bytes(canonical(self.site))
        self.sha = digest(self.site_path.read_bytes())

    def invoke(self, *args):
        recorded = []
        old_main, old_argv, old_path = bootstrap.main, sys.argv, list(sys.path)
        old_meta_path = list(sys.meta_path)
        bootstrap.main = lambda *values: (recorded.append(values) or 0)
        sys.argv = [str(self.program), *args]
        try:
            with self.assertRaises(SystemExit) as exit:
                runpy.run_path(str(self.program), run_name="__main__")
            self.assertEqual(exit.exception.code, 0)
        finally:
            bootstrap.main, sys.argv, sys.path[:] = old_main, old_argv, old_path
            sys.meta_path[:] = old_meta_path
        return recorded

    def test_independent_sha_removed_from_scientific_arguments_after_pin_checks(self):
        calls = self.invoke("--site-sha256", self.sha, "power", "--contract", "/fake/contract")
        self.assertEqual(calls, [("stage_7.py", ["power", "--contract", "/fake/contract"], self.site_path, self.sha)])

    def test_coherent_site_and_config_replacement_fails_original_launch_pin(self):
        self.config["source_pins"] = {}
        self.config_path.write_bytes(canonical(self.config))
        self.site["config_sha256"] = digest(self.config_path.read_bytes())
        self.site_path.write_bytes(canonical(self.site))
        with self.assertRaisesRegex(RuntimeError, "independent launch site SHA"):
            self.invoke("--site-sha256", self.sha, "power")

    def test_omitted_helper_and_existing_bytecode_refuse_before_dispatch(self):
        for name in ("exp7integration/extra.py", "exp7integration/__pycache__/extra.pyc"):
            target = self.package/name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(b"untrusted helper")
            try:
                with self.assertRaises(RuntimeError):
                    self.invoke("--site-sha256", self.sha, "power")
            finally:
                target.unlink()

    def test_missing_administrative_pin_refuses(self):
        with self.assertRaisesRegex(RuntimeError, "independent launch --site-sha256"):
            self.invoke("power", "--contract", "/fake/contract")

    def test_load_bound_checks_the_independent_sha_before_constructing_deployment(self):
        from exp7ops.evidence import Refusal
        old = bootstrap.FixedStageDeployment
        calls = []
        bootstrap.FixedStageDeployment = lambda *args: calls.append(args) or SimpleNamespace()
        try:
            with self.assertRaisesRegex(Refusal, "independent launch site SHA"):
                bootstrap.load_bound(self.site_path, "e"*64)
            self.assertEqual(calls, [])
        finally:
            bootstrap.FixedStageDeployment = old

    def test_detached_port_adds_same_pin_only_to_exact_stage_command(self):
        calls = []
        d = SimpleNamespace(repo=self.repo, data={"python": "/fixed/python"}, site_path=self.site_path,
                            site_sha256=self.sha, check_sources=lambda: None)
        p = SimpleNamespace(spawn=lambda argv, **kw: (calls.append((argv, kw)) or 123))
        bound = SiteBoundProcess(p, d, "power", "/fake/contract")
        argv = stage_argv("/fixed/python", self.repo, "power", "/fake/contract")
        self.assertEqual(bound.spawn(argv, start_new_session=True), 123)
        self.assertEqual(calls[0][0][4:6], ["--site-sha256", self.sha])
        with self.assertRaises(ValueError):
            bound.spawn(argv+["--arbitrary"])
        self.assertEqual(len(calls), 1)

    def test_calibration_uses_v3_cold_helper_before_real_default_context(self):
        from exp7stats import read_boundary
        events = []
        old_close, old_context, old_run = read_boundary.close_cli_stdin, bootstrap.CalibrationContext, bootstrap.calibration.run
        try:
            read_boundary.close_cli_stdin = lambda stream: events.append(("close", stream is sys.stdin))
            def context(*args, **kwargs):
                events.append(("context", args, kwargs))
                return "fake candidate context"
            bootstrap.CalibrationContext = context
            bootstrap.calibration.run = lambda value: events.append(("run", value)) or {"state": "NO-DETECTED-CALIBRATION-DEFECT"}
            plan = {"output": "/fake/calibration", "candidate_commit": "1"*40,
                    "manifest_path": "candidate.json", "manifest_sha256": "2"*64}
            d = SimpleNamespace(repo=self.repo, data={"calibration": plan})
            result = bootstrap.calibration_entry([], d)
            self.assertEqual(result["state"], "NO-DETECTED-CALIBRATION-DEFECT")
            self.assertEqual([row[0] for row in events], ["close", "context", "run"])
            self.assertTrue(events[0][1])
            self.assertNotIn("read_port", events[1][2])
            self.assertEqual(events[-1], ("run", "fake candidate context"))
        finally:
            read_boundary.close_cli_stdin, bootstrap.CalibrationContext, bootstrap.calibration.run = old_close, old_context, old_run
