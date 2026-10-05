# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
from exp7stats.common import digest, dumps
from testing_paths import ROOT

def put(root, name, value):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if type(value) is bytes else dumps(value)
    path.write_bytes(raw)
    return digest(raw)
