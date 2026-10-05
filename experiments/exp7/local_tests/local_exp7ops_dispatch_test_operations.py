# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from exp7ops.evidence import digest
from exp7ops.operator import Approval

def approval(stage='outcome'):
    return Approval(digest(b'contract'), 'b' * 64, stage, 42, 7, 'exp7-outcome', 100, 25, 'c' * 64)
