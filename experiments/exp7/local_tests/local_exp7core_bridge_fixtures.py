# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from exp7core.contract import FAMILIES, ARMS, canonical, digest, decode_battery

def fixture_battery(n=2):
    rows = []
    for f in FAMILIES:
        for i in range(n):
            rows.append({'family': f, 'index': i, 'pair_id': f'{f}:{i:04d}', 'questions': {a: f'{f}-{i}-{a}?' for a in ARMS}, 'prompts': {a: f'Q: {f}-{i}-{a}?\nA:' for a in ARMS}, 'targets': ['alpha', 'beta'], 'answer_type': 'word', 'nominal': 'class', 'ordinal': i, 'source_ids': [f'source-{i}'], 'metadata': {'oracle': 'SYNTHETIC', 'source_index': i}})
    return {'schema': 'exp7.normalized-pairs.v1', 'certificate_sha256': 'a' * 64, 'levels_sha256': 'b' * 64, 'pairs': rows}

def load_fixture(obj, n=2, pin_override=None):
    b = canonical(obj)
    return decode_battery(b, expected_sha256=digest(b) if pin_override is None else pin_override, certificate_sha256='a' * 64, levels_sha256='b' * 64, expected_per_family=n)
