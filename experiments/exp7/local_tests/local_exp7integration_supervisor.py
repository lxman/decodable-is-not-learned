# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
from pathlib import Path

class Supervisor(unittest.TestCase):

    def test_contract(self):
        from exp7integration.supervisor import check_supervisor
        from exp7ops.evidence import Refusal, canonical
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / 'repo'
            repo.mkdir()
            campaign = repo / 'campaign'
            campaign.mkdir()
            out = root / 'supervisor'
            out.mkdir()
            pending = out / 'status.json.next-fake'
            pending.write_bytes(b'{partial')
            check_supervisor(out, repo=repo, campaign=campaign, stage='power', settle=lambda seconds: pending.unlink())
            pending.write_bytes(b'abandoned')
            with self.assertRaisesRegex(Refusal, 'did not settle'):
                check_supervisor(out, repo=repo, campaign=campaign, stage='power', settle=lambda seconds: None)
            pending.unlink()
            (out / 'unexpected-outcome.json').write_bytes(canonical({'stage': 'outcome'}))
            with self.assertRaisesRegex(Refusal, 'non-operational'):
                check_supervisor(out, repo=repo, campaign=campaign, stage='power')
            with self.assertRaises(Refusal):
                check_supervisor(campaign, repo=repo, campaign=campaign, stage='power')
