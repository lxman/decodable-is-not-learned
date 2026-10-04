"""Write-once full feasibility run. No model, tokenizer, network or old analyzer."""
import argparse
import datetime
import json
import platform
import subprocess
import sys
import traceback
from collections import Counter

from .audit import audit
from .baselines import report
from .generate import generate
from .sources import HERE, ROOT, Sources, digest


def dump(path, obj):
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,sort_keys=True,indent=2,ensure_ascii=False)
        f.write('\n')


def jsonline(f, obj):
    f.write(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n')


def code_pins():
    return {p.name:digest(p.read_bytes()) for p in sorted(HERE.glob('*.py'))} | {
        p:digest((HERE/p).read_bytes()) for p in ('SPEC.md','PLAN.md','source_inventory.json')}


def run(run_id):
    if not run_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in run_id):
        raise ValueError('invalid run id')
    folder = HERE/'runs'/run_id
    folder.mkdir(parents=True,exist_ok=False)
    receipt = {'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'command':sys.argv,'python':platform.python_version(),'executable':sys.executable,
               'head':subprocess.check_output(['/opt/homebrew/bin/git','rev-parse','HEAD'],cwd=ROOT).decode().strip()}
    dump(folder/'receipt-start.json',receipt)
    pins = code_pins()
    dump(folder/'launch-pins.json',pins)
    try:
        source = Sources()
        with (folder/'attempts.jsonl').open('x',encoding='utf-8') as f:
            pairs,attempts = generate(source,lambda row:jsonline(f,row))
        with (folder/'pairs.jsonl').open('x',encoding='utf-8') as f:
            for pair in pairs:
                jsonline(f,pair)
        certificate,parsed = audit(pairs,source)
        certificate['attempt_counts'] = dict(Counter(a['family']+':'+a['reason'] for a in attempts))
        certificate['code_and_spec_pins'] = pins
        certificate['source_pins'] = source.inventory['pins']
        with (folder/'oracles.jsonl').open('x',encoding='utf-8') as f:
            for p in parsed:
                jsonline(f,p)
        dump(folder/'certificate.json',certificate)
        if not certificate['ok']:
            raise ValueError('generation certificate refused: '+repr(certificate['failures'][:5]))
        rows,outputs = report(pairs,source)
        dump(folder/'baselines.json',rows)
        with (folder/'baseline-outputs.jsonl').open('x',encoding='utf-8') as f:
            for row in outputs:
                jsonline(f,row)
        source.verify()
        if pins != code_pins():
            raise ValueError('prototype/spec changed during execution')
        dump(folder/'artifacts.json',{p.name:digest(p.read_bytes()) for p in sorted(folder.iterdir()) if p.name!='receipt-start.json'})
        dump(folder/'receipt-end.json',{'status':'PASS','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        print(json.dumps({'status':'PASS','directory':str(folder.relative_to(ROOT)),
                          'pairs':certificate['pairs_by_family'],'prompts':certificate['questions'],
                          'attempts':certificate['attempt_counts']},sort_keys=True,indent=2))
        return 0
    except Exception as exc:
        dump(folder/'receipt-end.json',{'status':'REFUSED','reason':repr(exc),
              'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'traceback':traceback.format_exc()})
        print(traceback.format_exc(),file=sys.stderr)
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.run_id))
