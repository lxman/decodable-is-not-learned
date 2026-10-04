"""Compare two write-once runs, binding all deterministic artifacts."""
import argparse
import datetime
import json
import re
import subprocess
from collections import Counter
from functools import lru_cache

from .audit import audit
from .baselines import report
from .run import code_pins, dump
from .sources import BB, HERE, ROOT, WORDS, Sources, digest

PREFIX = 'experiments/exp7/feasibility/'
ARTIFACTS = frozenset(('attempts.jsonl','baseline-outputs.jsonl','baselines.json',
                       'certificate.json','launch-pins.json','oracles.jsonl','pairs.jsonl'))
FILES = ARTIFACTS | {'artifacts.json','receipt-start.json','receipt-end.json'}
INVENTORY_FIELDS = {'computations','excluded','item_files','pins','snapshot',
                    'unit_enumeration_capacity_before_old_collisions','word_pair_capacity','word_rows'}
SNAPSHOT = '2d14da44ad882139bc95264697b03d45fe109354'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


@lru_cache(maxsize=None)
def git_bytes(*args):
    """Read actual immutable Git objects, never import historical Python."""
    try:
        return subprocess.check_output(['/opt/homebrew/bin/git',*args],cwd=ROOT,stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise ValueError('unavailable historical Git object') from exc


def load(folder, name):
    return json.loads((folder/name).read_bytes())


def lines(folder, name):
    return [json.loads(line) for line in (folder/name).read_text().splitlines()]


def launch_bindings(folder, source):
    start,end = load(folder,'receipt-start.json'),load(folder,'receipt-end.json')
    require(set(start)=={'command','executable','head','python','started_utc'},'receipt-start fields')
    require(set(end)=={'status','finished_utc'} and end['status']=='PASS','cannot compare a refused/incomplete run')
    head = start['head']
    require(isinstance(head,str) and re.fullmatch('[0-9a-f]{40}',head),'launch HEAD must be a full commit ID')
    try:
        is_commit = git_bytes('cat-file','-t',head).strip()==b'commit'
    except ValueError as exc:
        raise ValueError('launch HEAD not an existing Git commit') from exc
    require(is_commit,'launch HEAD not a Git commit')
    command = start['command']
    require(isinstance(command,list) and len(command)==3 and isinstance(command[0],str)
            and command[0].endswith('/'+PREFIX+'run.py')
            and command[1:]==['--run-id',folder.name],'receipt-start command/run identity')
    require(isinstance(start['python'],str) and re.fullmatch(r'3\.11\.\d+',start['python'])
            and start['executable']=='/Users/michaeljordan/emergence-lab/.venv/bin/python','receipt-start interpreter')
    began = datetime.datetime.fromisoformat(start['started_utc'])
    ended = datetime.datetime.fromisoformat(end['finished_utc'])
    require(began.utcoffset()==ended.utcoffset()==datetime.timedelta(0) and began<=ended,'receipt UTC interval')
    tree = git_bytes('ls-tree','-r','--name-only',head,'--',PREFIX).decode().splitlines()
    names = {p[len(PREFIX):] for p in tree if p.startswith(PREFIX) and '/' not in p[len(PREFIX):]
             and p.endswith('.py')} | {'SPEC.md','PLAN.md','source_inventory.json'}
    actual_pins = {name:digest(git_bytes('show',f'{head}:{PREFIX}{name}')) for name in sorted(names)}
    launch = load(folder,'launch-pins.json')
    require(launch==actual_pins,'launch pins differ from exact historical Git blobs/inventory')
    raw = git_bytes('show',f'{head}:{PREFIX}source_inventory.json')
    inventory = json.loads(raw)
    require(set(inventory)==INVENTORY_FIELDS and inventory==source.inventory
            and raw==source.inventory_bytes,'exact source inventory fields/bytes mismatch')
    require(inventory['snapshot']==SNAPSHOT,'source inventory approval snapshot mismatch')
    snapshot_tree = git_bytes('ls-tree','-r','--name-only',SNAPSHOT).decode().splitlines()
    items = sorted(p for p in snapshot_tree if p.startswith('experiments/') and '/items/' in p
                   and p.endswith('.json') and not p.endswith('scored_battery.json'))
    require(inventory['item_files']==items and set(inventory['pins'])==set(items)|{WORDS,BB},
            'source inventory item/pin coverage')
    for path,sha in inventory['pins'].items():
        require(digest(git_bytes('show',f'{SNAPSHOT}:{path}'))==sha,'source pin differs from approval Git blob: '+path)
        require(digest(git_bytes('show',f'{head}:{path}'))==sha,'source pin differs from launch Git blob: '+path)
    return head,launch,inventory


def validate_archive(folder, source):
    require({p.name for p in folder.iterdir()}==FILES and all((folder/name).is_file() for name in FILES),
            'fixed artifact inventory incomplete or unexpected')
    manifest = load(folder,'artifacts.json')
    require(set(manifest)==ARTIFACTS,'fixed artifact manifest inventory mismatch')
    for name,sha in manifest.items():
        require(digest((folder/name).read_bytes())==sha,f'artifact drift {folder.name}/{name}')
    head,pins,inventory = launch_bindings(folder,source)
    certificate = load(folder,'certificate.json')
    require(certificate.get('code_and_spec_pins')==pins,'certificate code pins differ from launch pins')
    require(certificate.get('source_pins')==inventory['pins'],'certificate source pins differ from exact inventory')
    require(certificate.get('ok') is True and certificate.get('failures')==[],'certificate is not a clean PASS')
    pairs = lines(folder,'pairs.jsonl')
    measured,parsed = audit(pairs,source)
    require(measured['ok'],'saved-pair audit refused: '+repr(measured['failures'][:5]))
    attempts = lines(folder,'attempts.jsonl')
    accepted = [a['pair'] for a in attempts if a['reason']=='accepted']
    require(accepted==pairs,'accepted-attempt evidence differs from saved pairs')
    measured.update(code_and_spec_pins=pins,source_pins=inventory['pins'],
                    attempt_counts=dict(Counter(a['family']+':'+a['reason'] for a in attempts)))
    require(certificate==measured,'certificate fields differ from complete saved-evidence audit')
    require(lines(folder,'oracles.jsonl')==parsed,'saved oracle coverage/content mismatch')
    # These are deterministic checks of archived inputs, not generation/model contact.
    baseline_rows,baseline_outputs = report(pairs,source)
    require(load(folder,'baselines.json')==baseline_rows,'saved baseline table coverage/content mismatch')
    require(lines(folder,'baseline-outputs.jsonl')==baseline_outputs,'saved baseline output coverage/content mismatch')
    return {'launch_head':head,'historical_launch_pins':len(pins),'source_git_blobs':len(inventory['pins']),
            'source_inventory_fields':sorted(inventory),'certificate_fields_exact':True,
            'pairs':len(pairs),'oracle_arms':measured['oracle_questions'],
            'exact_seeded_orientation_assignments':len(pairs),'exact_seeded_render_assignments':len(pairs),
            'exact_seeded_option_assignments':sum(bool(p['options']) for p in pairs),
            'baseline_cells':len(baseline_rows),'baseline_output_records':len(baseline_outputs)}


def compare(first, second, output):
    require(first!=second,'repeatability needs two distinct run directories')
    require(all(re.fullmatch('[a-z0-9-]+',n) for n in (first,second))
            and re.fullmatch(r'[a-z0-9-]+\.json',output),'invalid comparison path')
    source = Sources()
    dirs = [HERE/'runs'/name for name in (first,second)]
    verification_pins = code_pins()
    verified = {d.name:validate_archive(d,source) for d in dirs}
    names = sorted(ARTIFACTS | {'artifacts.json'})
    records = {name:{'equal':(dirs[0]/name).read_bytes()==(dirs[1]/name).read_bytes(),
                       'sha256':digest((dirs[0]/name).read_bytes())} for name in names}
    record = {'ok':all(x['equal'] for x in records.values()),'first':first,'second':second,
              'artifacts':records,'source_pins_rechecked':len(source.inventory['pins']),
              'verified_archives':verified,'verification_code_pins':verification_pins,
              'verification_head':subprocess.check_output(['/opt/homebrew/bin/git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
              'full_generation_performed':False,
              'excluded_from_byte_comparison':['receipt-start.json','receipt-end.json']}
    source.verify()
    require(code_pins()==verification_pins,'verification code changed during saved-evidence audit')
    dump(HERE/'runs'/output,record)
    print(json.dumps(record,sort_keys=True,indent=2))
    return 0 if record['ok'] else 1


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('first')
    p.add_argument('second')
    p.add_argument('--output',default='determinism.json')
    a=p.parse_args()
    raise SystemExit(compare(a.first,a.second,a.output))
