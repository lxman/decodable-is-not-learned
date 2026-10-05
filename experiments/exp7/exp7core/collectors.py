"""Complete production loops. Live imports occur only after explicit gates.

Public functions require an entered Campaign. All failures should be wrapped
by provenance.terminal at the operator boundary; no destructive recovery.
"""
from .contract import ARMS,FAMILIES,GRID,CAPS,canonical,digest,require,sampler_stream
from .records import strict_json,build_record,validate_record
from .guardio import safe_path,write_once
from .provenance import LIVE,halted
from .collection_schema import MODELS,ANCHORS,key_of,execution_order,validate_load
from .anchors import (old_items,anchor_spec,anchor_record,validate_anchor,greedy_anchor)


def backend_of(c,backend,scope):
    if backend is LIVE:
        from .live import LiveBackend
        return LiveBackend(c,scope)
    if callable(getattr(backend,'bind',None)):
        backend = backend.bind(c,scope)
    require(backend and callable(getattr(backend,'open',None)),'falsy/invalid loader injection refuses')
    return backend


def publish(c,name,raw,record):
    halted(c.root)
    folder = safe_path(c.root,name)
    folder.parent.mkdir(parents=True,exist_ok=True)
    folder.mkdir()  # exclusive unit address claim
    rec = canonical(record)
    write_once(folder/'raw.jsonl',raw)
    write_once(folder/'record.json',rec)
    write_once(folder/'DONE.json',canonical({'raw.jsonl':digest(raw),'record.json':digest(rec)}))
    # Enroll published bytes for entry/exit race checks.
    for n in ('raw.jsonl','record.json','DONE.json'):
        c.trust.read_root(name+'/'+n)


def persist_receipt(c,load_id,receipt):
    d = c.trust.data
    spec = d['loads'][load_id]
    validate_load(receipt,expected_model=d['models'][spec['model']],expected_host=d['hosts'][spec['host']],
        loader=spec['loader'],load_id=load_id,source_sha=d['source_manifest_sha256'],
        code_sha=d['code_manifest_sha256'],token_facts=d['tokenizers'][spec['model']])
    p = safe_path(c.root,f'receipts/{load_id}.json')
    p.parent.mkdir(exist_ok=True)
    if p.exists():
        require(c.trust.read_root(f'receipts/{load_id}.json') == canonical(receipt),'load receipt changed on resume')
    else:
        write_once(p,canonical(receipt))
    c.load_receipt(load_id)


def require_result(got,seeds,dps):
    require(type(got) is dict and set(got) == set(seeds) and all(type(s) is int for s in got), 'exact sampler seed keys')
    require(all(type(v) is list and len(v) == dps and all(type(x) is str for x in v) for v in got.values()),
            'sampler exact draws; no string coercion')


def collect_anchors(c,model,session):
    require(model in MODELS[:2],'anchor trained model')
    ctx = c._context(c.trust.data['sample_loads'][model])
    for rung in ANCHORS+(('ctrl_copy',) if model == 'pythia_1b' else ()):
        name = f'units/anchors/{model}/{rung}'
        check = lambda raw,rec:validate_anchor(raw,rec,read=c.trust.read_repo,model=model,rung=rung,context_json=ctx)
        if c.unit(name,check) is not None:
            continue
        _,seeds,dps,cap = anchor_spec(model,rung)
        rows = []
        for i,(prompt,answer,kind) in enumerate(old_items(c.trust.read_repo,rung)):
            got = session.sample(prompt,rung=rung,size='1b' if model == 'pythia_1b' else 'olmo1b',mode='trained',
                item_idx=i,seeds=seeds,draws_per_seed=dps,max_new_tokens=cap,
                terminal_ids=tuple(session.receipt['model']['terminal_ids']))
            require_result(got,seeds,dps)
            rows.append({'item':i,'draws':{str(s):got[s] for s in seeds}})
        raw = b''.join(canonical(r) for r in rows)
        rec = anchor_record(raw,read=c.trust.read_repo,model=model,rung=rung,context_json=ctx)
        publish(c,name,raw,rec)
    c.verify_anchors(model)


def sample_family(c,model,family,session):
    """500 pairs x certified arm presentation order; canonical storage afterward."""
    by_arm = {a:[] for a in ARMS}
    expected = {a:c.expected(f'units/predictor/{model}/{family}/{a}') for a in ARMS}
    for p,arm in execution_order(c.battery(),family):
        s = sampler_stream(family,arm,key_of(model),p.index,model == 'twin')
        kwargs = {k:v for k,v in s.items() if k != 'stream_seed'}
        got = session.sample(p.prompts[ARMS.index(arm)],**kwargs,max_new_tokens=CAPS[p.answer_type],
                             terminal_ids=tuple(session.receipt['model']['terminal_ids']))
        require_result(got,s['seeds'],s['draws_per_seed'])
        address = expected[arm].addresses[p.index]
        by_arm[arm].append({**address.public(),'draws':got[s['seeds'][0]]})
    return {a:b''.join(canonical(r) for r in by_arm[a]) for a in ARMS}


def sample_preflight_unit(c,model,family,session, *, endpoints=False):
    """One exact 500-row q0 unit/family; first/last prompt replay separately."""
    e = c.expected(f'units/predictor/{model}/{family}/q0')
    rows = []
    for p,arm in execution_order(c.battery(),family):
        if arm != 'q0' or (endpoints and p.index not in (0,499)):
            continue
        s = sampler_stream(family,arm,key_of(model),p.index,model == 'twin')
        got = session.sample(p.prompts[0],**{k:v for k,v in s.items() if k != 'stream_seed'},
                             max_new_tokens=CAPS[p.answer_type],terminal_ids=tuple(session.receipt['model']['terminal_ids']))
        require_result(got,s['seeds'],s['draws_per_seed'])
        rows.append({**e.addresses[p.index].public(),'draws':got[s['seeds'][0]]})
    return b''.join(canonical(r) for r in rows)


def _require_preflight_q0(c,model,family,raw):
    """One same-stream relation for fresh collection, resume and seal readers."""
    require(raw == c.trust.read_root(f'preflight/{model}/{family}/q0.jsonl'),
            'collected stream differs from preflight complete q0 unit')


def verify_preflight(c,model):
    from .preflight import verify_cap_receipt
    _,lengths = verify_cap_receipt(c,model)
    raw = c.trust.read_root(f'preflight/{model}.json')
    value = strict_json(raw)
    require(value['schema'] == 'exp7.predictor-preflight.v1' and value['model'] == model
            and value['battery_sha256'] == c.battery().bytes_sha256,'preflight binding')
    require(set(value['families']) == set(FAMILIES),'preflight full-family timings')
    longest = sorted(lengths,key=lambda p:(-lengths[p],p))[:8]
    require(value['longest_prompt_sha256'] == [digest(p.encode()) for p in longest],'longest tokenized prompt coverage')
    probe = value['longest_prompt_probe']
    require(probe['positions'] == 8 and type(probe['logits']) is int and probe['logits'] > 0
            and type(probe['nonfinite']) is int and probe['nonfinite'] == 0,'preflight finite full probe')
    require(value['additional_draws'] == (128512 if model != 'twin' else 32128),'fixed preflight budget')
    for f,entry in value['families'].items():
        require(entry['pairs'] == 500 and type(entry['seconds']) in (int,float) and entry['seconds'] > 0,'whole-unit timing')
        require(entry['arm'] == 'q0','frozen preflight arm')
        path = f'preflight/{model}/{f}/q0.jsonl'
        data = c.trust.read_root(path)
        e = c.expected(f'units/predictor/{model}/{f}/q0')
        require(digest(data) == entry['raw_sha256'],'preflight raw pin')
        build_record(data,e)  # complete 500-row production unit, no miniature n
        repeat = c.trust.read_root(f'preflight/{model}/{f}/q0.repeat.jsonl')
        lines = data.splitlines(keepends=True)
        require(repeat == lines[0]+lines[-1],'preflight first/last complete prompt replay')
        names = [f'units/predictor/{model}/{f}/{a}' for a in ARMS]
        present = [safe_path(c.root,n).exists() for n in names]
        # No primary family is legitimate during precollection preflight. A
        # partial family is torn; a completed q0 must match ALL diagnostic bytes.
        require(not any(present) or all(present),'torn four-arm family publication')
        if all(present):
            _require_preflight_q0(c,model,f,c.raw_unit(names[0])[0])
    c.verify_anchors(model)
    return value


def collect_predictor(c,model, *, backend=LIVE):
    c._ready()
    require(model in MODELS,'predictor name')
    require(not safe_path(c.root,'predictor-seal.json').exists(),'predictor already sealed')
    c.trust.grant('predictor-collection')
    verify_preflight(c,model)
    b = backend_of(c,backend,'predictor-collection')
    load = c.trust.data['sample_loads'][model]
    session = b.open(load)
    try:
        persist_receipt(c,load,session.receipt)
        if model != 'twin':
            collect_anchors(c,model,session)
        else:
            c.verify_anchors('pythia_1b')
        for family in FAMILIES:
            names = [f'units/predictor/{model}/{family}/{a}' for a in ARMS]
            present = [safe_path(c.root,n).exists() for n in names]
            require(not any(present) or all(present),'torn four-arm family publication')
            if all(present):
                for n in names:
                    c.raw_unit(n)
                continue
            claim = safe_path(c.root,f'claims/{model}-{family}.CLAIM')
            claim.parent.mkdir(exist_ok=True)
            write_once(claim,canonical({'model':model,'family':family}))
            raws = sample_family(c,model,family,session)
            _require_preflight_q0(c,model,family,raws['q0'])
            for arm,n in zip(ARMS,names):
                publish(c,n,raws[arm],build_record(raws[arm],c.expected(n)))
                c.raw_unit(n)
        halted(c.root)
    finally:
        session.close()


def greedy_new(c,session):
    rows = {}
    order = execution_order(c.battery())
    # Preserve exact presentation order. Contiguous families share one cap;
    # never regroup across pairs in a way that changes the certified schedule.
    for f in FAMILIES:
        group = [(p,a) for p,a in order if p.family == f]
        cap = CAPS[group[0][0].answer_type]
        require(all(CAPS[p.answer_type] == cap for p,a in group),'family cap')
        got = session.greedy([p.prompts[ARMS.index(a)] for p,a in group],cap)
        require(type(got) is list and len(got) == 2000 and all(type(s) is str for s in got),'greedy full output coverage')
        for (p,a),s in zip(group,got):
            rows[p.pair_id,a] = s
    return rows


def outcome_raw(c,name,values):
    e = c.expected(name)
    return b''.join(canonical({**a.public(),'draws':[values[a.pair_id,a.arm]]}) for a in e.addresses)


def collect_outcome_anchors(c,session,load,step):
    name = 'units/outcome-anchors/'+load
    if safe_path(c.root,name).exists():
        return c.outcome_anchor(load,step)
    rows = []
    for rung in ANCHORS:
        items = old_items(c.trust.read_repo,rung)
        got = session.greedy([p for p,a,k in items],8)
        require(type(got) is list and len(got) == 500 and all(type(x) is str for x in got),'greedy anchor output')
        rows.extend({'rung':rung,'item':i,'prompt_sha256':digest(p.encode()),'continuation':s}
                    for i,((p,a,k),s) in enumerate(zip(items,got)))
    raw = b''.join(canonical(r) for r in rows)
    rec = {'schema':'exp7.greedy-anchors.v1','load_id':load,'step':step,
           'context':strict_json(c._context(load,outcome=True)),**greedy_anchor(raw,read=c.trust.read_repo,step=step)}
    publish(c,name,raw,rec)
    return c.outcome_anchor(load,step)


def outcome_authority(c,scope,power_validator):
    c._ready()
    require(callable(power_validator),'full power semantic verifier required')
    power = c.verify_power()
    require(power_validator(power,c) is None,'power semantic verifier returns None or raises')
    # Operational run/stop evidence is separate from the collection grant.
    if any(v['status'] != 'FORECAST-POWERED' for v in power['declarations'].values()):
        c.trust.grant('outcome-underpowered-run')
    c.trust.grant(scope)


def collect_endpoint(c,host, *, backend=LIVE,power_validator):
    outcome_authority(c,'outcome-preflight',power_validator)
    b = backend_of(c,backend,'outcome-preflight')
    for loader in ('thin','candidate'):
        name = f'units/endpoint/{host}/{loader}'
        load = c.trust.data['endpoint_loads'][host][loader]
        if safe_path(c.root,name).exists():
            c.raw_unit(name)
            c.outcome_anchor(load,3440000)
            continue
        session = b.open(load)
        try:
            persist_receipt(c,load,session.receipt)
            collect_outcome_anchors(c,session,load,3440000)
            values = greedy_new(c,session)
            raw = outcome_raw(c,name,values)
            publish(c,name,raw,build_record(raw,c.expected(name)))
        finally:
            session.close()
    candidate = c.verify_endpoint(host)
    # Reuse the one preassigned candidate endpoint only; never choose a path.
    load = c.trust.data['outcome_loads']['3440000']
    if load == c.trust.data['endpoint_loads'][host]['candidate']:
        name = 'units/outcome/3440000'
        if safe_path(c.root,name).exists():
            require(c.raw_unit(name)[0] == candidate,'endpoint reuse mismatch')
        else:
            publish(c,name,candidate,build_record(candidate,c.expected(name)))


def collect_outcomes(c, *, backend=LIVE,power_validator):
    outcome_authority(c,'outcome-collection',power_validator)
    b = backend_of(c,backend,'outcome-collection')
    for step in GRID:
        load = c.trust.data['outcome_loads'][str(step)]
        host = c.trust.data['loads'][load]['host']
        c.verify_endpoint(host)  # no new checkpoint before its host's full gate
        name = f'units/outcome/{step}'
        if safe_path(c.root,name).exists():
            c.raw_unit(name)
            c.outcome_anchor(load,step)
            continue
        require(step != 3440000,'missing qualified reused endpoint')
        claim = safe_path(c.root,f'claims/outcome-{step}.CLAIM')
        claim.parent.mkdir(exist_ok=True)
        write_once(claim,canonical({'load_id':load,'step':step}))
        session = b.open(load)
        try:
            persist_receipt(c,load,session.receipt)
            collect_outcome_anchors(c,session,load,step)
            raw = outcome_raw(c,name,greedy_new(c,session))
            publish(c,name,raw,build_record(raw,c.expected(name)))
        finally:
            session.close()
    c.verify_complete()


def seal_predictors(c):
    c._ready()
    payload = c.seal_payload()
    halted(c.root)
    c.trust.trace.check()
    write_once(safe_path(c.root,'predictor-seal.json'),canonical(payload))
    return payload


def complete_campaign(c):
    payload = c.complete_payload()
    c.trust.trace.check()
    halted(c.root)
    write_once(safe_path(c.root,'complete.json'),canonical(payload))
    return payload
