# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from copy import deepcopy
from exp7stats.common import ARMS, FAMILIES, PREDICTORS, digest

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
