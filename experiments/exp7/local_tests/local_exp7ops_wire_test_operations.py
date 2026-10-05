# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from exp7ops.evidence import canonical, digest

def payload():
    raw, record = (b'{"draw":"alpha"}\n', b'{"rows":1}\n')
    return {'raw.jsonl': raw, 'record.json': record, 'DONE.json': canonical({'raw.jsonl': digest(raw), 'record.json': digest(record)})}
