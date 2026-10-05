import guard
import unittest
from exp7ops.dispatch import FixedComposition
from exp7ops.operator import STAGES
from exp7ops.evidence import Refusal
from test_operations import approval

class DispatchTests(unittest.TestCase):
    def test_constant_live_stage_mapping_with_fake_deployment(self):
        calls = []
        class Deployment:
            def authenticate(self, stage, data):
                calls.append(("authenticate", stage)); return approval(stage)
            def dry_plan(self, stage, auth):
                calls.append(("dry", stage)); return {"stage": stage}
            def predictor_preflight(self, auth, heartbeat):
                calls.append(("predictor-preflight", auth.stage)); return {}
            def predictor(self, auth, heartbeat):
                calls.append(("predictor", auth.stage)); return {}
            def seal(self, auth, heartbeat):
                calls.append(("seal", auth.stage)); return {}
            def outcome_preflight(self, auth, heartbeat):
                calls.append(("outcome-preflight", auth.stage)); return {}
            def outcome(self, auth, heartbeat):
                calls.append(("outcome", auth.stage)); return {}
            def watch(self, auth, heartbeat):
                calls.append(("watch", auth.stage)); return {}
            def campaign(self, stage, auth):
                calls.append(("campaign", stage)); return {"stage": stage}
            def stage_result(self, stage, result):
                return {"state": "COMPLETE", "fixture": True}
        composition = FixedComposition(Deployment(), power_run=lambda c: calls.append(("power", c["stage"])),
                                       analyzer_run=lambda c: calls.append(("verdict", c["stage"])))
        for stage in STAGES:
            auth = composition.authenticate(stage, b"contract")
            composition.dry_run(stage, auth)
            self.assertNotIn((stage, stage), calls)
            composition.execute(stage, auth, lambda value: None)
            self.assertIn((stage, stage), calls)
        with self.assertRaises(Refusal):
            composition.execute("create", approval(), lambda value: None)
