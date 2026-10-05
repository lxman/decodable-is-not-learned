# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import gzip
import json
from exp7core.contract import ARMS, FAMILIES, GRID, Pair, Battery, canonical, digest
from exp7core.battery_adapter import schedule
from exp7core.collection_schema import MODELS
from exp7core.anchors import ITEMS, anchor_spec
from exp7core.campaign import Campaign
H = lambda s: digest(s.encode())
C = '1' * 40
T = '2' * 40

class FakeGit:

    def __init__(self):
        self.calls = []

    def tag(self, *args):
        self.calls.append(('tag', args))

    def ancestor(self, *args):
        self.calls.append(('ancestor', args))

    def blob(self, *args):
        self.calls.append(('blob', args))

def fixture(repo, with_caps=False):
    root = repo / 'campaign'
    root.mkdir()
    pins = {}

    def put(name, value, raw=False):
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = value if raw else canonical(value)
        path.write_bytes(data)
        pins[name] = digest(data)
    pairs = []
    for f in FAMILIES:
        orders = schedule('words' if f == 'unscrambling' else f)[2]
        for i in range(500):
            qs = tuple((f'fake {f} {i} {a}' for a in ARMS))
            pairs.append(Pair(f, i, f'{f}:{i:04d}', qs, tuple((f'Q: {q}\nA:' for q in qs)), ('red', 'blue'), 'word', 'block', i // 100, (f'{f}-{i}',), canonical({'render_order': orders[i]}).decode()))
    battery = Battery(tuple(pairs), H('cert'), H('levels'), H('battery'))
    put('source.txt', b'source', True)
    put('exp7core/scoring.py', b'# pinned synthetic scorer stand-in\n', True)
    put('projection.md', b'FAKE projection\n', True)
    put('owner.txt', b'FAKE ONLY authorized fake scope for synthetic fixture\n', True)
    for rung, path in ITEMS.items():
        answer = 'copy' if rung == 'ctrl_copy' else '1'
        put(path, {'shots': [['shot one', '1'], ['shot two', '2']], 'eval_items': [{'question': f'old {rung} {i}', 'answer': answer} for i in range(500)]})
    for model in MODELS[:2]:
        for rung in ('add_base8', 'sub_base8') + (('ctrl_copy',) if model == 'pythia_1b' else ()):
            base, seeds, dps, cap = anchor_spec(model, rung)
            answer = 'copy' if rung == 'ctrl_copy' else '1'
            raw = b''.join((canonical({'item': i, 'draws': {str(s): [answer] * dps for s in seeds}}) for i in range(500)))
            put(base + '.draws.jsonl.gz', gzip.compress(raw, mtime=0), True)
            put(base + '.json', {'max_new_tokens': cap, 'draws_per_seed': dps, 'seeds': list(seeds)})
    for step in GRID:
        for rung in ('add_base8', 'sub_base8'):
            put(f'experiments/exp2m/results/sweep/smollm3_3b/step{step}/{rung}.json', {'bits': [1] * 500, 'correct': 500})
    source = {'source.txt': pins['source.txt']}
    code = {'exp7core/scoring.py': pins['exp7core/scoring.py']}
    models, loads, tokenizers, assets = ({}, {}, {}, {})
    host = {'host_id': 'fakehost', 'device': 'fake'}
    for name in (*MODELS, *(f'outcome/{s}' for s in GRID)):
        models[name] = {'repo': 'FAKE/' + name, 'revision_commit': C, 'tensor_digest': H(name), 'config_sha256': H('config'), 'tokenizer_files_sha256': H('tokenizer'), 'render': 'plain', 'terminal_ids': [0], 'dtype': 'float16' if '/' in name else 'float32', 'init_seed': 0 if name == 'twin' else None}
        tokenizers[name] = {'fake': True}
        if name in ('pythia_1b', 'twin'):
            models[name]['repo'] = 'EleutherAI/pythia-1b'
            models[name]['revision_commit'] = 'f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2'
        elif name == 'olmo2_1b':
            models[name]['repo'] = 'allenai/OLMo-2-0425-1B'
        files = {'config.json': H('config'), 'tokenizer.json': H('tokenizer'), 'tokenizer_config.json': H('tokconfig')}
        assets[name] = {'repo': models[name]['repo'], 'commit': models[name]['revision_commit'], 'files': files}
        models[name]['tokenizer_files_sha256'] = digest(canonical({n: v for n, v in files.items() if n != 'config.json'}))
    for rung in ('add_base8', 'sub_base8'):
        base, _, _, _ = anchor_spec('olmo2_1b', rung)
        put(base + '.json', {'max_new_tokens': 8, 'commit': C, 'model_sha': models['olmo2_1b']['tensor_digest'], 'dtype': 'float32'})
    entries = {str(s): {'repo': models[f'outcome/{s}']['repo'], 'commit': C, 'files': ['FAKE.safetensors']} for s in GRID}
    put('experiments/exp2m/checkpoints_2m.json', {'grid_3b': list(GRID), 'entries_3b': entries})
    for step in GRID:
        for rung in ('add_base8', 'sub_base8'):
            put(f'experiments/exp2m/results/sweep/smollm3_3b/step{step}/{rung}.json', {'bits': [1] * 500, 'correct': 500, 'weight_sha256': models[f'outcome/{step}']['tensor_digest'], 'commit': C})
    put('baseline.json', {'schema': 'exp7.pythia-baseline.v1', 'prereg_tag_object': T, 'projection_commit': C, 'readings': {mode: {**models[name], 'commit': models[name]['revision_commit']} for name, mode in (('pythia_1b', 'trained'), ('twin', 'untrained'))}})
    samples = {m: 'sample-' + m for m in MODELS}
    outcomes = {str(s): f'outcome-{s}' for s in GRID}
    for m, load in samples.items():
        loads[load] = {'model': m, 'host': 'fakehost', 'loader': 'predictor', 'launch_git_commit': C}
    for s, load in outcomes.items():
        loads[load] = {'model': 'outcome/' + s, 'host': 'fakehost', 'loader': 'candidate', 'launch_git_commit': C}
    loads['thin'] = {'model': 'outcome/3440000', 'host': 'fakehost', 'loader': 'thin', 'launch_git_commit': C}
    d = {'schema': 'exp7.trust.v1', 'repo_pins': pins, 'source_manifest': source, 'source_manifest_sha256': digest(canonical(source)), 'code_manifest': code, 'code_manifest_sha256': digest(canonical(code)), 'normalizer_sha256': pins['exp7core/scoring.py'], 'battery_sha256': battery.bytes_sha256, 'levels_sha256': battery.levels_sha256, 'models': models, 'hosts': {'fakehost': host}, 'loads': loads, 'sample_loads': samples, 'outcome_loads': outcomes, 'endpoint_loads': {'fakehost': {'thin': 'thin', 'candidate': 'outcome-3440000'}}, 'tokenizers': tokenizers, 'prereg': {'name': 'exp7-preregistered', 'object': T, 'commit': C, 'bindings': {**source, **code}}, 'assets': assets, 'checkpoint_entries': entries, 'pythia_baseline_path': 'baseline.json', 'projection': {'path': 'projection.md', 'sha256': pins['projection.md'], 'commit': C}, 'grants': {}, 'predictor_seal': {'path': 'predictor-seal.json', 'sha256': H('not-yet')}, 'power': {'path': 'power.json', 'sha256': H('not-yet'), 'commit': C}}
    d['cap_receipts'] = {}
    if with_caps:
        from exp7core.preflight import validate_caps

        class FakeTokenizer:
            all_special_ids = [0]

            def encode(self, text, add_special_tokens=True):
                return [ord(x) for x in text]

            def decode(self, ids, skip_special_tokens=True):
                return ''.join(map(chr, ids))
        result = validate_caps(battery, FakeTokenizer())
        for name in ('pythia_1b', 'olmo2_1b'):
            value = {**result, 'assets': {'repo': assets[name]['repo'], 'commit': assets[name]['commit'], 'files': assets[name]['files']}}
            path = f'caps/{name}.json'
            put(path, value)
            d['cap_receipts'][name] = path
            d['prereg']['bindings'][path] = pins[path]
    for scope in ('predictor-preflight', 'predictor-collection', 'predictor-digest-baseline'):
        g = {'schema': 'exp7.owner-grant.v2', 'owner': 'Michael Jordan', 'scope': scope, 'evidence_path': 'owner.txt', 'evidence_sha256': pins['owner.txt'], 'quote': 'authorized fake scope', 'prereg_tag_object': T, 'projection_commit': C, 'predictor_seal_sha256': d['predictor_seal']['sha256'] if scope.startswith('outcome') else None, 'power_sha256': d['power']['sha256'] if scope.startswith('outcome') else None}
        path = 'grants/' + scope + '.json'
        put(path, g)
        d['grants'][scope] = {'path': path, 'canonical_sha256': digest(canonical(g)), 'commit': C}
    return Fixture(repo, root, battery, d)

class Fixture:

    def __init__(self, repo, root, battery, data):
        self.repo, self.root, self.battery, self.data = (repo, root, battery, data)
        self.serial = 0

    def campaign(self):
        self.serial += 1
        path = f'trust-{self.serial}.json'
        raw = canonical(self.data)
        (self.repo / path).write_bytes(raw)
        c = Campaign(self.root, self.repo, trust_path=path, trust_sha256=digest(raw), git=FakeGit())
        c._battery = self.battery
        return c

    def refresh_seal(self):
        p = self.root / 'predictor-seal.json'
        self.data['predictor_seal']['sha256'] = digest(p.read_bytes())
        sealed = json.loads(p.read_bytes())
        bound = {'campaign/' + n: s for n, s in sealed['bindings'].items()}
        bound['campaign/predictor-seal.json'] = digest(p.read_bytes())
        self.data['repo_pins'].update(bound)
        self.data['predictor_tag'] = {'name': 'exp7-predictor-sealed', 'object': '3' * 40, 'commit': C, 'bindings': bound}

    def power(self):
        obj = {'schema': 'exp7.statistics.v2', 'stage': 'power', 'production': True, 'seal_sha256': self.data['predictor_seal']['sha256'], 'battery_sha256': self.battery.bytes_sha256, 'source_bindings': {'code_manifest': self.data['code_manifest_sha256'], 'source_manifest': self.data['source_manifest_sha256']}, 'declarations': {'fake': {'status': 'FORECAST-POWERED'}}}
        raw = canonical(obj)
        (self.root / 'power.json').write_bytes(raw)
        self.data['power']['sha256'] = digest(raw)
        for scope in ('outcome-preflight', 'outcome-collection', 'outcome-underpowered-run'):
            self.stage_grant(scope)
        for scope, e in self.data['grants'].items():
            if scope.startswith('outcome'):
                p = self.repo / e['path']
                g = json.loads(p.read_bytes())
                g['predictor_seal_sha256'], g['power_sha256'] = (self.data['predictor_seal']['sha256'], digest(raw))
                p.write_bytes(canonical(g))
                self.data['repo_pins'][e['path']] = digest(p.read_bytes())
                e['canonical_sha256'] = digest(canonical(g))

    def stage_grant(self, scope):
        g = {'schema': 'exp7.owner-grant.v2', 'owner': 'Michael Jordan', 'scope': scope, 'evidence_path': 'owner.txt', 'evidence_sha256': self.data['repo_pins']['owner.txt'], 'quote': 'authorized fake scope', 'prereg_tag_object': T, 'projection_commit': C, 'predictor_seal_sha256': self.data['predictor_seal']['sha256'], 'power_sha256': None if scope == 'power' else self.data['power']['sha256']}
        raw = canonical(g)
        path = 'grants/' + scope + '.json'
        (self.repo / path).write_bytes(raw)
        self.data['repo_pins'][path] = digest(raw)
        self.data['grants'][scope] = {'path': path, 'canonical_sha256': digest(raw), 'commit': C}

    def refresh_complete(self):
        raw = (self.root / 'complete.json').read_bytes()
        self.data['complete'] = {'path': 'campaign/complete.json', 'sha256': digest(raw), 'commit': C}
        self.data['repo_pins']['campaign/complete.json'] = digest(raw)
