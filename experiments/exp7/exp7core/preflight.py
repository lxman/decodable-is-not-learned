"""Future authorized build token checks and post-projection collection preflight.

The current planning tests use fake tokenizers/sessions exclusively.
"""
import time
from .contract import ARMS,FAMILIES,GRID,CAPS,canonical,digest,require
from .records import strict_json
from .scoring import answer,normalize
from .guardio import safe_path,write_once
from .provenance import LIVE,halted,hex40


def validate_caps(battery,tokenizer):
    """Every prompt x both oracle targets. No model or forward pass."""
    require(tokenizer and callable(getattr(tokenizer,'encode',None)) and callable(getattr(tokenizer,'decode',None)),
            'falsy/missing tokenizer injection')
    rows = []
    specials = tuple(sorted(set(tokenizer.all_special_ids)))
    require(specials,'tokenizer terminal IDs')
    for p in battery.pairs:
        for arm,prompt in zip(ARMS,p.prompts):
            enc = tokenizer.encode(prompt,add_special_tokens=True)
            require(enc and enc == tokenizer.encode(prompt,add_special_tokens=False),'plain rendering unexpectedly adds BOS/specials')
            for target in p.targets:
                # A realizable free continuation, with leading whitespace permitted
                # by the frozen scorer. No token is stripped from the measured length.
                tokens = tokenizer.encode(' '+target,add_special_tokens=False)
                require(type(tokens) is list and tokens and all(type(v) is int and v not in specials for v in tokens),
                        'oracle continuation token IDs')
                require(len(tokens) <= CAPS[p.answer_type],'frozen token cap cannot emit oracle answer')
                text = tokenizer.decode(tokens,skip_special_tokens=True)
                require(normalize(text,p.answer_type) == answer(target,p.answer_type),'oracle decode/normalization roundtrip')
                rows.append({'pair':p.pair_id,'arm':arm,'prompt_sha256':digest(prompt.encode()),
                             'target':target,'tokens':tokens,'cap':CAPS[p.answer_type],'prompt_tokens':len(enc)})
    require(len(rows) == 16000,'full tokenizer cap coverage')
    return {'schema':'exp7.cap-validation.v1','battery_sha256':battery.bytes_sha256,'shots':[],
            'caps':CAPS,'comparisons':16000,'rows':rows}


def verify_cap_receipt(c,key):
    """Pure revalidation of the pre-tag tokenizer measurement and exact coverage."""
    if key == 'twin':
        key = 'pythia_1b'
    d = c.trust.data
    path = d['cap_receipts'][key]
    require(d['prereg']['bindings'].get(path) == d['repo_pins'][path],'cap validation not bound before tag')
    value = strict_json(c.trust.read_repo(path))
    require(value['schema'] == 'exp7.cap-validation.v1' and value['battery_sha256'] == c.battery().bytes_sha256
            and value['shots'] == [] and value['caps'] == CAPS and value['comparisons'] == 16000,'cap receipt binding')
    require(value['assets']['repo'] == d['assets'][key]['repo'] and value['assets']['commit'] == d['assets'][key]['commit']
            and value['assets']['files'] == d['assets'][key]['files'],'cap tokenizer source bytes')
    expected = [(p,a,prompt,target) for p in c.battery().pairs for a,prompt in zip(ARMS,p.prompts) for target in p.targets]
    require(len(value['rows']) == len(expected) == 16000,'cap measurement coverage')
    lengths = {}
    for row,(p,arm,prompt,target) in zip(value['rows'],expected):
        require(row['pair'] == p.pair_id and row['arm'] == arm and row['prompt_sha256'] == digest(prompt.encode())
                and row['target'] == target and row['cap'] == CAPS[p.answer_type],'cap measurement address')
        tokens = row['tokens']
        require(type(tokens) is list and 1 <= len(tokens) <= row['cap'] and all(type(t) is int and t >= 0 for t in tokens),
                'cap measured token length')
        require(type(row['prompt_tokens']) is int and row['prompt_tokens'] > 0,'prompt token count')
        require(prompt not in lengths or lengths[prompt] == row['prompt_tokens'],'inconsistent prompt token count')
        lengths[prompt] = row['prompt_tokens']
    return value,lengths


def build_tokenizer_checks(*, battery, read, git, grant_path, grant_sha256, grant_commit, assets, output_root, loader=LIVE):
    """RUN DURING LATER AUTHORIZED BUILD, BEFORE PREREG TAG (design §4).

    No prereg/projection prerequisite is invented for this tokenizer-only build
    gate. A separately evidenced build grant and frozen source/asset inputs are
    required; this API has no weight loader. Failure returns for a ruling.
    The caller supplies the independently bound containing commit separately;
    the immutable v2 grant body must not embed its own publication commit.
    """
    grant_commit = hex40(grant_commit)
    raw = read(grant_path)
    require(digest(raw) == grant_sha256,'build grant pin')
    grant = strict_json(raw)
    require(type(grant) is dict and set(grant) == {'schema','owner','scope','evidence_path','evidence_sha256','quote',
                        'battery_sha256','assets_sha256'},'build grant schema')
    require(grant['schema'] == 'exp7.build-grant.v2' and grant['owner'] == 'Michael Jordan'
            and grant['scope'] == 'tokenizer-only-build-cap-validation','build grant scope')
    evidence = read(grant['evidence_path'])
    require(type(grant['quote']) is str and grant['quote'].strip() and
            digest(evidence) == grant['evidence_sha256'] and grant['quote'].encode() in evidence,'build grant evidence')
    git.blob(grant_commit,grant_path,grant_sha256)
    require(grant['battery_sha256'] == battery.bytes_sha256 and grant['assets_sha256'] == digest(canonical(assets)),
            'build grant data binding')
    require(set(assets) == {'pythia_1b','olmo2_1b',*(f'outcome/{s}' for s in GRID)},
            'exact two predictor + 26 outcome asset identities')
    if loader is LIVE:
        from .live import token_only
        loader = token_only
    else:
        require(loader and callable(loader),'falsy tokenizer loader refused')
    out = safe_path(output_root,'cap-validation')
    out.mkdir()
    records = {}
    for name,asset in sorted(assets.items()):
        tok,measurements = loader(asset)
        require(all(measurements[k] == asset[k] for k in ('repo','commit','files')),'measured tokenizer asset binding')
        result = validate_caps(battery,tok)
        result['assets'] = measurements
        data = canonical(result)
        # Trust keys retain outcome/<step>; storage uses a fixed slash-free name.
        write_once(out/(name.replace('/','-')+'.json'),data)
        records[name] = digest(data)
    require(len(records) == 28,'2 predictor + 26 outcome tokenizer revision checks')
    write_once(out/'DONE.json',canonical(records))
    return records


def predictor_preflight(c,model, *, backend=LIVE):
    from .collectors import (backend_of,persist_receipt,collect_anchors,sample_preflight_unit,verify_preflight)
    c._ready()
    require(model in ('pythia_1b','olmo2_1b','twin'),'preflight model')
    require(not safe_path(c.root,'predictor-seal.json').exists(),'predictor sealed')
    c.trust.grant('predictor-preflight')
    load = c.trust.data['sample_loads'][model]
    session = backend_of(c,backend,'predictor-preflight').open(load)
    try:
        persist_receipt(c,load,session.receipt)
        if model != 'twin':
            collect_anchors(c,model,session)
        else:
            c.verify_anchors('pythia_1b')
        # All 8 longest NEW prompts are probed only after full old-anchor replay.
        _,lengths = verify_cap_receipt(c,model)
        prompts = sorted(lengths,key=lambda p:(-lengths[p],p))[:8]
        probe = session.probe(prompts)
        require(probe['positions'] == 8 and probe['logits'] > 0 and type(probe['nonfinite']) is int
                and probe['nonfinite'] == 0,'longest-prompt nonfinite preflight')
        families = {}
        for f in FAMILIES:
            folder = safe_path(c.root,f'preflight/{model}/{f}')
            folder.mkdir(parents=True)  # write-once whole family preflight
            t0 = time.monotonic()
            first = sample_preflight_unit(c,model,f,session)
            seconds = time.monotonic()-t0
            second = sample_preflight_unit(c,model,f,session,endpoints=True)
            lines = first.splitlines(keepends=True)
            require(second == lines[0]+lines[-1],'first/last complete-prompt deterministic replay')
            write_once(folder/'q0.jsonl',first)
            write_once(folder/'q0.repeat.jsonl',second)
            families[f] = {'pairs':500,'arm':'q0','seconds':seconds,'raw_sha256':digest(first)}
        value = {'schema':'exp7.predictor-preflight.v1','model':model,'battery_sha256':c.battery().bytes_sha256,
                 'families':families,'longest_prompt_probe':probe,'longest_prompt_sha256':[digest(p.encode()) for p in prompts],
                 'additional_draws':128512 if model != 'twin' else 32128}
        halted(c.root)
        write_once(safe_path(c.root,f'preflight/{model}.json'),canonical(value))
        verify_preflight(c,model)
        return value
    finally:
        session.close()
