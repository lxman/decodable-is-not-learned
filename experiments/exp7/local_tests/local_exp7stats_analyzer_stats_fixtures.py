# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from exp7stats.common import ARMS, FAMILIES, PREDICTORS, digest, CONTACT_ROOTS
from testing_paths import WORK

def payloads(n=24, grid=(1, 2, 3), mode='directed'):
    battery = {'schema': 'exp7.analysis-battery.v1', 'sha256': 'a' * 64, 'certificate_sha256': 'b' * 64, 'levels_sha256': 'c' * 64, 'baseline_ids': {}, 'baseline_coverage': {'applicable_cells': 8, 'not_applicable_cells': 4}, 'families': {}}
    predictors = {'schema': 'exp7.analysis-predictors.v1', 'trained': {p: {} for p in PREDICTORS}, 'twin': {}}
    outcomes = {'schema': 'exp7.analysis-outcomes.v1', 'grid': list(grid), 'families': {}}
    for f in FAMILIES:
        battery['baseline_ids'][f] = ['constant', 'tracks_target', 'not_applicable']
        battery['families'][f] = []
        outcomes['families'][f] = []
        predictors['twin'][f] = []
        for p in PREDICTORS:
            predictors['trained'][p][f] = []
        for i in range(n):
            pid = f'{f}:{i:04d}'
            pair = {'id': pid, 'index': i, 'targets': ['alpha', 'beta'], 'answer_type': 'word', 'base': f'base{i // 8}', 'prompts_sha256': {a: digest(f'{pid}/{a}'.encode()) for a in ARMS}, 'baselines': {'constant': {'status': 'APPLICABLE', 'na_reason': None, 'outputs': {a: 'alpha' for a in ARMS}, 'abstained': dict.fromkeys(ARMS, False)}, 'tracks_target': {'status': 'APPLICABLE', 'na_reason': None, 'outputs': dict(zip(ARMS, ('alpha', 'beta', 'alpha', 'beta'))), 'abstained': dict.fromkeys(ARMS, False)}, 'not_applicable': {'status': 'NOT_APPLICABLE', 'na_reason': 'synthetic family has no such operation', 'outputs': None, 'abstained': None}}}
            battery['families'][f].append(pair)
            if mode == 'constant':
                a = 32
            elif mode == 'selective_only':
                a = 48
            elif mode == 'order_only':
                a = 9 + 2 * i
            else:
                a = 40 + i
            a = min(64, max(0, a))
            draws = {'q0': ['alpha'] * a + ['beta'] * (64 - a), 'q1': ['alpha'] * (64 - a) + ['beta'] * a, 'q0s': ['alpha'] * a + ['beta'] * (64 - a), 'q1s': ['alpha'] * (64 - a) + ['beta'] * a}
            for p in PREDICTORS:
                predictors['trained'][p][f].append({'id': pid, 'draws': deepcopy(draws)})
            predictors['twin'][f].append({'id': pid, 'draws': {a: ['other'] * 16 for a in ARMS}})
            y = 0 if i < 2 else 1 if i < 9 else 2 if i < 16 else 3
            values = {}
            for j, t in enumerate(grid):
                values[str(t)] = {'q0': 'alpha', 'q1': 'beta' if j < y else 'alpha', 'q0s': 'alpha', 'q1s': 'beta' if j < len(grid) - y else 'alpha'}
            outcomes['families'][f].append({'id': pid, 'outputs': values})
    return (battery, predictors, outcomes)

class FakeCampaign:

    def __init__(self, root, *, mode='directed'):
        self.root, self.repo = (Path(root), Path(root))
        self.b, self.p, self.o = payloads(mode=mode)
        self.events = []
        self.exit_failure = False
        self.entry_failure = False
        self.power_record = {'fixture': True, 'seal_sha256': 'd' * 64, 'battery_sha256': 'a' * 64}
        self.contact_inventory = {'schema': 'exp7.contact-inventory.v1', 'covered_roots': CONTACT_ROOTS, 'entries': []}

    @contextmanager
    def entryexit(self, stage):
        self.events.append(('entry', stage))
        if self.entry_failure:
            raise ValueError('fixture missing owner grant')
        yield {'provenance_sha256': 'e' * 64, 'input_sha256': {'synthetic': 'f' * 64, 'contact_inventory': digest(self.contact_inventory)}, 'contact_inventory': self.contact_inventory}
        self.events.append(('exit', stage))
        if self.exit_failure:
            raise ValueError('fixture source pin changed at exit')

    def battery(self):
        self.events.append('battery')
        return self.b

    def predictor_data(self):
        self.events.append('predictors')
        return self.p

    def outcomes(self):
        self.events.append('outcomes')
        return self.o

    def verify_predictor_seal(self):
        self.events.append('seal')
        return {'seal_sha256': 'd' * 64, 'battery_sha256': 'a' * 64, 'bindings': {'synthetic/raw': 'f' * 64}}

    def verify_power(self):
        self.events.append('power')
        return {'power_sha256': digest(self.power_record), 'record': self.power_record}

    def verify_complete(self):
        self.events.append('complete')
        return {'complete_sha256': '1' * 64, 'bindings': {'synthetic/outcome': '2' * 64}}
