"""Old raw streams / items read only; raw equality, never self-attested counts."""
import gzip
from hashlib import sha256
from .contract import canonical, digest, require
from .records import strict_json
from .scoring import normalize

ITEMS = {'add_base8':'experiments/exp2b/battery/items/add_base8.json',
         'sub_base8':'experiments/exp2c/battery/items/sub_base8.json',
         'ctrl_copy':'experiments/exp2c/battery/items/ctrl_copy.json'}


def render(question,shots):
    return '\n\n'.join([f'Q: {q}\nA: {a}' for q,a in shots]+[f'Q: {question}\nA:'])


def old_items(read,rung):
    cap = strict_json(read(ITEMS[rung]))
    items,shots = cap['eval_items'],cap['shots'][:2]
    require(len(items) == 500 and len(shots) == 2,'old anchor item/shot coverage')
    kind = 'word' if rung == 'ctrl_copy' else 'number'
    return tuple((render(it['question'],shots),it['answer'],kind) for it in items)


def anchor_spec(model,rung):
    require(model in ('pythia_1b','olmo2_1b'),'anchor model')
    if rung == 'ctrl_copy':
        require(model == 'pythia_1b','copy control only Pythia')
        base = 'experiments/exp3/results/sampling/1b_trained/'
        seeds,dps,cap = (0,1,2,3),8,12
    else:
        require(rung in ('add_base8','sub_base8'),'anchor rung')
        base = ('experiments/exp2k/results/k256/1b_trained/' if model == 'pythia_1b'
                else 'experiments/exp2i/results/predictor/olmo1b/')
        seeds,dps,cap = (0,),64,8
    # Numeric anchors use 2d/2k/2i cap8; exp3 copy control uses flat cap12.
    return base+rung, seeds,dps,cap


def old_stream(rung,size,seed,index):
    s = f'exp3|{rung}|{size}|trained|s{seed}|i{index}'
    return int.from_bytes(sha256(s.encode()).digest()[:8],'big') & ((1<<63)-1)


def committed(read,model,rung):
    path,seeds,dps,cap = anchor_spec(model,rung)
    record = strict_json(read(path+'.json'))
    if rung != 'ctrl_copy':
        require(record['max_new_tokens'] == cap,'old sampling token cap')
    else:
        require(record['draws_per_seed'] == 8 and record['seeds'] == list(seeds),'old copy budget')
    rows = [strict_json(x) for x in gzip.decompress(read(path+'.draws.jsonl.gz')).splitlines()]
    require(len(rows) == 500 and [r['item'] for r in rows] == list(range(500)),'old raw coverage/order')
    result = []
    for r in rows:
        draws = {str(s):r['draws'][str(s)] for s in seeds}
        require(all(type(ds) is list and len(ds) == dps and all(type(s) is str for s in ds)
                    for ds in draws.values()),'old anchor exact seed/substream shape')
        result.append({'item':r['item'],'draws':draws})
    return result


def validate_anchor(raw,record, *, read,model,rung,context_json):
    rows = [strict_json(x) for x in raw.splitlines()]
    expected = committed(read,model,rung)
    require(raw.endswith(b'\n') and canonical(rows) == canonical(expected),'full raw anchor equality')
    _,seeds,dps,cap = anchor_spec(model,rung)
    want = {'schema':'exp7.anchor.v1','model':model,'rung':rung,'context':strict_json(context_json),
            'raw_sha256':digest(raw),'rows':500,'draws':500*len(seeds)*dps,'seeds':list(seeds),
            'dps':dps,'cap':cap,'reference_sha256':digest(canonical(expected))}
    require(canonical(record) == canonical(want),'anchor record does not rederive')


def anchor_record(raw, *, read,model,rung,context_json):
    _,seeds,dps,cap = anchor_spec(model,rung)
    result = {'schema':'exp7.anchor.v1','model':model,'rung':rung,'context':strict_json(context_json),
              'raw_sha256':digest(raw),'rows':500,'draws':500*len(seeds)*dps,'seeds':list(seeds),
              'dps':dps,'cap':cap,'reference_sha256':digest(canonical(committed(read,model,rung)))}
    validate_anchor(raw,result,read=read,model=model,rung=rung,context_json=context_json)
    return result


def greedy_anchor(raw, *, read, step):
    rows = [strict_json(x) for x in raw.splitlines()]
    require(len(rows) == 1000 and raw.endswith(b'\n'),'greedy anchor coverage')
    counts,bits = {},{}
    for n,rung in enumerate(('add_base8','sub_base8')):
        items = old_items(read,rung)
        bs = []
        for i,(p,a,kind) in enumerate(items):
            r = rows[n*500+i]
            require(set(r) == {'rung','item','prompt_sha256','continuation'} and r['rung'] == rung
                    and type(r['item']) is int and r['item'] == i and r['prompt_sha256'] == digest(p.encode())
                    and type(r['continuation']) is str,'greedy anchor raw row')
            bs.append(int(normalize(r['continuation'],kind) == normalize(a,kind)))
        old = strict_json(read(f'experiments/exp2m/results/sweep/smollm3_3b/step{step}/{rung}.json'))
        require(len(old['bits']) == 500 and sum(old['bits']) == old['correct'],'old anchor count')
        require(abs(sum(bs)-old['correct']) <= 15,'old Mac anchor tolerance')
        counts[rung],bits[rung] = sum(bs),bs
    return {'counts':counts,'bits':bits,'raw_sha256':digest(raw)}
