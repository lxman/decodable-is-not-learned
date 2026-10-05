"""Certified immutable full-003 -> normalized core. No item generation."""
from collections import Counter
import itertools
import random
from .contract import ARMS, FAMILIES, canonical, digest, require, decode_battery
from .records import strict_json
from .scoring import score_draws
from .certified.audit import audit
from .certified.baselines import report, METHODS
from .certified.sources import Sources

PREFIX = 'experiments/exp7/feasibility/runs/full-003/'
RAW_SHA = '361a89652222df8131185f946ded5b8962eb213b42e18890223c7f2eb349fe1b'
CERT_SHA = '00238fa53b313bbefc2cbe75c4dd2ef19054823234d78f9573244b23a1029c96'
BASELINE_SHA = 'acc0959ee71fb82ce6766391b44beed78defdd8d20aafe6f2f8b2a5fa61b43bf'
FINAL_RECEIPT = 'experiments/exp7/feasibility/runs/f6-verification-003-004.json'
FINAL_RECEIPT_SHA = '17488fa066d42335725ea68340f777cd1f0fe2d28874098ea03fc2d0bc4723f7'


def verify_history(read,git):
    """Git OBJECT reads, no historical imports; distinct from current source pins.

    The exact independently certified receipt pins the already reviewed module
    inventory (including absence of historical namespace __init__.py files).
    Recheck every historical launch/source blob, never compare old launch code
    pins to the later hardened working-tree verifier bytes.
    """
    raw = read(FINAL_RECEIPT)
    require(digest(raw) == FINAL_RECEIPT_SHA,'historical certificate trust root')
    final = strict_json(raw)
    prefix = 'experiments/exp7/feasibility/'
    for name,sha in final['verification_code_pins'].items():
        git.blob(final['verification_head'],prefix+name,sha)
    inv = strict_json(read(prefix+'source_inventory.json'))
    for run in ('full-003','full-004'):
        start = strict_json(read(prefix+'runs/'+run+'/receipt-start.json'))
        require(start['head'] == '5ad3ccb078b559d275c6f505bad0a9d42414aa8e','certified historical launch commit')
        launch = strict_json(read(prefix+'runs/'+run+'/launch-pins.json'))
        certificate = strict_json(read(prefix+'runs/'+run+'/certificate.json'))
        require(launch == certificate['code_and_spec_pins'] and certificate['source_pins'] == inv['pins'],
                'historical certificate/code/source binding')
        for name,sha in launch.items():
            git.blob(start['head'],prefix+name,sha)
        for path,sha in inv['pins'].items():
            git.blob(start['head'],path,sha)
            git.blob(inv['snapshot'],path,sha)


def schedule(family):
    """SPEC exact per-slot schedules, not just balanced histogram checks."""
    def rng(purpose):
        return random.Random(int(digest(f'2026100407|{family}|{purpose}'.encode()),16))
    orientation = [0]*250+[1]*250
    rng('orientation').shuffle(orientation)
    orders = list(itertools.permutations(ARMS))*20+list(itertools.permutations(ARMS))[:20]
    rng('render').shuffle(orders)
    if family == 'deduction':
        positions = [(g, (a,b) if (k+g+j)%2 == 0 else (b,a))
                     for g in range(2) for j,(a,b) in enumerate(itertools.combinations(range(5),2))
                     for k in range(25)]
    else:
        positions = list(itertools.permutations(range(5),2))*25
    rng('positions').shuffle(positions)
    return orientation, positions, orders


def require_schedule(rows):
    for f in ('words','deduction','units','shapes'):
        group = [p for p in rows if p['family'] == f]
        require([p['slot'] for p in group] == list(range(500)), 'exact slot order')
        orientation, positions, orders = schedule(f)
        for p in group:
            i = p['slot']
            require(type(p['orientation']) is int and p['orientation'] == orientation[i], 'exact orientation schedule')
            require(tuple(p['render_order']) == orders[i], 'exact render schedule')
            if f != 'words':
                got = tuple(p['options'].index(p[a]) for a in ('a0','a1'))
                want = positions[i]
                if f == 'deduction':
                    require(type(p['latent']['graph']) is int and p['latent']['graph'] == want[0], 'graph schedule')
                    want = want[1]
                require(got == want, 'exact target position schedule')


def level(row):
    """No pooling: certified blocks already have >=25. Explicit ordinal axes."""
    b = row['base_block']
    if row['family'] == 'words':
        length, tercile = b.split(':')
        return tercile, int(length[6:])-4
    if row['family'] == 'deduction':
        graph, distance, positions = b.split(':')
        return graph+':'+positions, int(distance[8:])
    if row['family'] == 'units':
        digits = b.split(':')[-1]
        # Incomparable digit pairs are NOMINAL, never lexicographically merged.
        return 'multiply_divide:'+digits, 2
    return ':'.join(sorted((row['a0'],row['a1']))), 4


def normalize_rows(rows, certificate_sha256):
    require_schedule(rows)
    levels = {p['id']: {'nominal':level(p)[0], 'ordinal':level(p)[1], 'raw_block':p['base_block']}
              for p in rows}
    level_bytes = canonical({'schema':'exp7.levels.v1','pairs':levels,'merges':[],
                             'shots':[], 'render':'Q: {question}\nA:'})
    normalized = []
    for p in rows:
        f = 'unscrambling' if p['family'] == 'words' else p['family']
        # Use independent content IDs, not pair IDs as a tautological uniqueness check.
        ss = [p['a0'],p['a1']] if f == 'unscrambling' else sorted(set(p['content_keys']))
        n,o = level(p)
        normalized.append(dict(family=f,index=p['slot'],pair_id=f"{f}:{p['slot']:04d}",
            questions=p['arms'],prompts={a:f"Q: {p['arms'][a]}\nA:" for a in ARMS},
            targets=[p['a0'],p['a1']],answer_type='number' if f == 'units' else 'word',
            nominal=n,ordinal=o,source_ids=ss,metadata=p))
    data = canonical({'schema':'exp7.normalized-pairs.v1','certificate_sha256':certificate_sha256,
                      'levels_sha256':digest(level_bytes),'pairs':normalized})
    battery = decode_battery(data,expected_sha256=digest(data),certificate_sha256=certificate_sha256,
                             levels_sha256=digest(level_bytes))
    return battery, data, level_bytes


def load_certified(read):
    """read is an already independent pin-enforcing repository reader."""
    final = strict_json(read(FINAL_RECEIPT))
    require(digest(read(FINAL_RECEIPT)) == FINAL_RECEIPT_SHA,'independent final certification receipt pin')
    # Pins/measurements are rechecked below; the receipt's `ok` is never a gate.
    require(final['verification_head'] == '78ffc8c991dcfb856739a42851e88e8db7dc638a','final verifier source commit')
    for name,row in final['artifacts'].items():
        first = read(PREFIX+name)
        require(digest(first) == row['sha256'] and first == read(PREFIX.replace('full-003','full-004')+name),
                'fixed certified archive artifact/repeat')
    raw, cert_raw, baseline_raw = (read(PREFIX+n) for n in ('pairs.jsonl','certificate.json','baselines.json'))
    require(digest(raw) == RAW_SHA and digest(cert_raw) == CERT_SHA and digest(baseline_raw) == BASELINE_SHA,
            'immutable full-003 literal pins')
    for name, data in [('pairs.jsonl',raw),('certificate.json',cert_raw),('baselines.json',baseline_raw)]:
        require(read(PREFIX.replace('full-003','full-004')+name) == data, 'full-004 repeat differs')
    rows = [strict_json(line) for line in raw.splitlines()]
    require_schedule(rows)
    source = Sources(read)
    facts, parsed = audit(rows, source, full=True)
    require(not facts['failures'] and facts['questions'] == 8000 and facts['oracle_questions'] == 8000,
            'independent oracle/semantic/collision failure')
    cert = strict_json(cert_raw)
    # Certificate fields are evidence to RE-DERIVE, never authority to pass.
    require(canonical(facts) == canonical({k:cert[k] for k in facts}), 'certificate does not rederive')
    require(canonical(parsed) == canonical([strict_json(x) for x in read(PREFIX+'oracles.jsonl').splitlines()]),
            'raw oracle evidence differs')
    baseline_rows, outputs = report(rows, source)
    require(canonical(baseline_rows) == canonical(strict_json(baseline_raw)), 'baseline table does not rederive')
    require(canonical(outputs) == canonical([strict_json(x) for x in read(PREFIX+'baseline-outputs.jsonl').splitlines()]),
            'baseline raw output differs')
    battery, data, levels = normalize_rows(rows,CERT_SHA)
    by_old = {strict_json(p.metadata_json)['id']:p for p in battery.pairs}
    results = {m:{f:None for f in FAMILIES} for m in METHODS}
    for r in outputs:
        p = by_old[r['pair']]
        # Abstention is the empty generated string. Raw None remains in bound evidence.
        draws = {a:('' if s is None else s,) for a,s in zip(ARMS,r['predictions'])}
        if results[r['method']][p.family] is None:
            results[r['method']][p.family] = []
        results[r['method']][p.family].append(score_draws(draws,p.targets,p.answer_type,k=1))
    for m in results:
        for f, values in results[m].items():
            if values is not None:
                require(len(values) == 500,'baseline cardinality')
                results[m][f] = tuple(values)
    return battery, data, levels, results
