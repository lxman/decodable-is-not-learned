# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class CandidateAudit(unittest.TestCase):

    def test_contract(self):
        from exp7stats.candidate_audit import CandidateAudit, code_hash
        from exp7core.contract import Refusal
        allowed = compile('def f(): return 1', '<fake-generator>', 'exec')
        changed = compile('def f(): return 2', '<fake-generator>', 'exec')
        audit = object.__new__(CandidateAudit)
        audit.known_code_objects = {}
        audit.allowed_codes = {code_hash(allowed)}
        audit.execs = set()
        audit.allow_code(allowed)
        self.assertEqual(audit.execs, {'<fake-generator>'})
        with self.assertRaises(Refusal):
            audit.allow_code(changed)
