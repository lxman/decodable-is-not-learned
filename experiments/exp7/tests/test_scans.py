import guard
from pathlib import Path
import tempfile
import sys
import unittest
from exp7ops.scans import ReadImportScan, static_imports
from exp7ops.evidence import digest, Refusal

class ScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "__init__.py"
        self.source.write_text("value = 7\n")
        self.pins = {"__init__.py": digest(self.source.read_bytes())}

    def test_transient_exec_and_alias_are_logged(self):
        code = compile(self.source.read_bytes(), str(self.source), "exec")
        scan = ReadImportScan({self.root: self.pins})
        with scan:
            namespace = {}
            exec(code, namespace)
            sys.modules["transient_alias"] = namespace
            del sys.modules["transient_alias"]
            self.source.read_bytes()
        self.assertEqual(namespace["value"], 7)
        self.assertEqual(scan.receipt()["execs"], [str(self.source)])
        self.assertIn(str(self.source), scan.receipt()["reads"])

    def test_dynamic_unpinned_read_and_exit_mutation_refuse(self):
        unknown = self.root / "dynamic.json"
        unknown.write_text("{}")
        with self.assertRaises(Refusal):
            with ReadImportScan({self.root: self.pins}):
                unknown.read_bytes()
        with self.assertRaises(Refusal):
            with ReadImportScan({self.root: self.pins}):
                self.source.write_text("value = 9\n")

    def test_static_source_import_inventory_without_execution(self):
        self.source.write_text("import torch\nfrom .other import x\nopen('dynamic.json')\n")
        report = static_imports(self.root, ["__init__.py"])
        entries = report["__init__.py"]["imports_and_reads"]
        self.assertTrue(any(r.get("name") == "torch" for r in entries))
        self.assertNotIn("torch", sys.modules)

    def test_generated_code_requires_pinned_named_producer(self):
        self.source.write_text("def emit():\n    ns = {}\n    exec('value = 7', ns)\n    return ns['value']\n")
        self.pins = {"__init__.py": digest(self.source.read_bytes())}
        namespace = {}
        exec(compile(self.source.read_bytes(), str(self.source), "exec"), namespace)
        with self.assertRaises(Refusal):
            with ReadImportScan({self.root: self.pins}):
                namespace["emit"]()
        scan = ReadImportScan({self.root: self.pins}, generated_producers={str(self.source): {"emit"}})
        with scan:
            self.assertEqual(namespace["emit"](), 7)
        self.assertEqual(len(scan.receipt()["generated_exec"]), 1)

    def test_guard_prevents_model_network_and_process_events(self):
        for name in ("torch", "socket", "urllib.request", "transformers", "experiments.exp6"):
            with self.assertRaises(ImportError):
                __import__(name)
        for event in ("subprocess.Popen", "os.system", "os.posix_spawn", "socket.connect"):
            with self.assertRaises(RuntimeError):
                sys.audit(event, None)
