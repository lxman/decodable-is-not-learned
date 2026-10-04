"""Compare two write-once runs, binding all deterministic artifacts."""
import argparse
import json

from .run import dump
from .sources import HERE, Sources, digest


def compare(first, second, output):
    source = Sources()
    dirs = [HERE/'runs'/name for name in (first,second)]
    for d in dirs:
        if json.loads((d/'receipt-end.json').read_text())['status'] != 'PASS':
            raise ValueError('cannot compare a refused run')
        for name,sha in json.loads((d/'artifacts.json').read_text()).items():
            if digest((d/name).read_bytes()) != sha:
                raise ValueError(f'artifact drift {d.name}/{name}')
    names = sorted(p.name for p in dirs[0].iterdir() if not p.name.startswith('receipt-'))
    if names != sorted(p.name for p in dirs[1].iterdir() if not p.name.startswith('receipt-')):
        raise ValueError('artifact coverage differs')
    records = {name:{'equal':(dirs[0]/name).read_bytes()==(dirs[1]/name).read_bytes(),
                       'sha256':digest((dirs[0]/name).read_bytes())} for name in names}
    record = {'ok':all(x['equal'] for x in records.values()),'first':first,'second':second,
              'artifacts':records,'source_pins_rechecked':len(source.inventory['pins']),
              'excluded_from_byte_comparison':['receipt-start.json','receipt-end.json']}
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
