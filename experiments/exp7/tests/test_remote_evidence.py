from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from exp7ops.evidence import once, canonical, digest, Refusal
from exp7ops.wire import decode
from exp7integration.remote_evidence import final_evidence
from testing_paths import WORK


class RemoteEvidenceTests(unittest.TestCase):
    def test_failed_terminal_keeps_every_campaign_and_disjoint_supervisor_byte(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root = Path(tmp); repo = root/"repo"; repo.mkdir()
            campaign = repo/"campaign"; campaign.mkdir()
            supervisor = root/"supervisor"; supervisor.mkdir()
            once(campaign/"broken-unit", b"invalid raw bytes retained")
            once(supervisor/"operator.log", b"sanitized failed operator log\n")
            once(supervisor/"HALTED.json", {"state": "INSUFFICIENT_DATA", "error_type": "Refusal"})
            d = SimpleNamespace(repo=repo, root=campaign, check_sources=lambda: None,
                data={"remote": {"evidence_root": str(campaign), "supervisor_stages": ["outcome"]},
                      "stages": {"outcome": {"output": str(supervisor)}}})
            terminal = {"exit_code": 1, "controller_live": False, "group_live": False, "kind": "error"}
            result = decode("final-evidence", final_evidence(d, lambda: terminal))
            self.assertEqual(set(result["payload"]), {"broken-unit", "supervisors/outcome/operator.log", "supervisors/outcome/HALTED.json", "supervisor-inventory.json"})
            self.assertEqual(result["files"], {n: digest(v) for n, v in result["payload"].items()})
            once(supervisor/"outcome-probe.json", {"stage": "outcome"})
            with self.assertRaisesRegex(Refusal, "non-operational"):
                final_evidence(d, lambda: terminal)
