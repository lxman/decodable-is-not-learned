"""Proposed separately OWNER-RATIFIED post-projection Pythia baseline stage.

No model invocation during planning. No unset tensor pin is accepted by a
collector. The baseline is committed and enrolled in the independent trust
revision BEFORE predictor preflight/new-item contact.
"""
from hashlib import sha256
from .contract import canonical,digest,pin,require
from .records import strict_json
from .guardio import safe_path,write_once
from .provenance import LIVE,halted

TRAINED_FP16_RECORD = 'experiments/exp4/results/reference/ladder_pythia_1b/_load.json'
TWIN_FP16_RECORD = 'experiments/exp3b/referent_check.json'


def _native(c,mode):
    # Gate precedes even the frozen module import.
    c._ready()
    c.trust.grant('predictor-digest-baseline')
    from experiments.exp6.run.predict_6 import real_loader
    from experiments.exp2g.checkpoints_2g import tensor_digest
    from .live import asset_bytes,token_facts,measure_host
    import torch
    import gc
    name = 'twin' if mode == 'untrained' else 'pythia_1b'
    files = asset_bytes(c.trust.data['assets'][name],c.trust.trace)
    tok,model,info = real_loader('pythia_1b',mode,'mps')
    try:
        require(info['repo'] == 'EleutherAI/pythia-1b' and
                info['commit'] == 'f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2','baseline Pythia revision')
        modern,legacy = sha256(),sha256()
        for key,tensor in sorted(model.state_dict().items()):
            actual = tensor.detach().to('cpu').contiguous()
            if actual.is_floating_point():
                require(actual.dtype == torch.float32 and torch.equal(actual,actual.to(torch.float16).to(torch.float32)),
                        'baseline must be EXACT frozen fp16-upcast weights')
                small = actual.to(torch.float16)
            else:
                small = actual
            modern.update(key.encode())
            modern.update(str(tuple(small.shape)).encode())
            modern.update(str(small.dtype).encode())
            modern.update(small.numpy().tobytes())
            legacy.update(key.encode())
            legacy.update(small.numpy().tobytes())
        return {'repo':info['repo'],'commit':info['commit'],'dtype':'float32','mode':mode,
                'init_seed':0 if mode == 'untrained' else None,'tensor_digest':tensor_digest(model),
                'fp16_modern_digest':modern.hexdigest(),'fp16_legacy_digest':legacy.hexdigest(),
                'config_sha256':digest(files['config.json']),
                'tokenizer_files_sha256':digest(canonical({n:digest(v) for n,v in files.items() if n != 'config.json'})),
                'tokenizer':token_facts(tok,model),'host':measure_host('mps',torch)}
    finally:
        del model,tok
        gc.collect()
        torch.mps.empty_cache()


def derive_pythia_baseline(c, *, measurement=LIVE):
    c._ready()
    c.trust.grant('predictor-digest-baseline',consume=True)
    for path in ('units/predictor','preflight','contacts/predictor','predictor-seal.json'):
        require(not safe_path(c.root,path).exists(),'baseline must precede all new-item sampling')
    old_train = strict_json(c.trust.read_repo(TRAINED_FP16_RECORD))['tensor_digest']
    twin_record = strict_json(c.trust.read_repo(TWIN_FP16_RECORD))
    old_twin = [r['state_sha256'] for r in twin_record['checks'] if r['check'] == 'untrained twin constructs 1b seed=0']
    require(len(old_twin) == 1,'old twin referent coverage')
    if measurement is LIVE:
        measurement = _native
    else:
        require(measurement and callable(measurement),'falsy baseline measurement injection')
    readings = {}
    for mode in ('trained','untrained'):
        first,second = measurement(c,mode),measurement(c,mode)
        require(canonical(first) == canonical(second),'two-load baseline byte identity')
        require(first['fp16_modern_digest'] == old_train if mode == 'trained'
                else first['fp16_legacy_digest'] == old_twin[0],'Pythia baseline differs from independently committed fp16 evidence')
        require(first['dtype'] == 'float32' and first['mode'] == mode,'baseline dtype/mode')
        pin(first['tensor_digest'])
        readings[mode] = first
    value = {'schema':'exp7.pythia-baseline.v1','prereg_tag_object':c.trust.data['prereg']['object'],
             'projection_commit':c.trust.data['projection']['commit'],'readings':readings,
             'source_manifest_sha256':c.trust.data['source_manifest_sha256'],
             'code_manifest_sha256':c.trust.data['code_manifest_sha256']}
    c.trust.trace.check()
    halted(c.root)
    write_once(safe_path(c.root,'pythia-digest-baseline.json'),canonical(value))
    return value
