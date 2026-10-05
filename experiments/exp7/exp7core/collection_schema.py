"""Frozen production address/cardinality mapping and independent load validation."""
from .contract import ARMS, FAMILIES, GRID, PREDICTORS, CAPS, canonical, digest, pin, require, sampler_stream
from .records import Address, ExpectedUnit, strict_json, MODEL_KEYS
from .provenance import hex40

MODELS = PREDICTORS+('twin',)
ANCHORS = ('add_base8','sub_base8')


def predictor_units():
    return tuple(f'units/predictor/{m}/{f}/{a}' for m in MODELS for f in FAMILIES for a in ARMS)


def outcome_units():
    return tuple(f'units/outcome/{s}' for s in GRID)


def key_of(model):
    require(model in MODELS,'predictor identity')
    return 'pythia_1b' if model == 'twin' else model


def addresses(battery, model=None, family=None, arm=None):
    if model is not None:
        require(model in MODELS and family in FAMILIES and arm in ARMS,'sample unit address')
        rows = battery.family(family)
    else:
        rows = battery.pairs
    require(len(rows) == (500 if model is not None else 2000),'production pair cardinality')
    out = []
    for p in rows:
        for a in ((arm,) if model is not None else ARMS):
            stream = None if model is None else sampler_stream(p.family,a,key_of(model),p.index,model == 'twin')['stream_seed']
            out.append(Address(p.family,p.pair_id,p.index,a,digest(p.prompts[ARMS.index(a)].encode()),
                               stream,p.targets,p.answer_type))
    return tuple(out)


def execution_order(battery, family=None):
    """The certified seeded render schedule controls actual contact order."""
    pairs = battery.pairs if family is None else battery.family(family)
    return tuple((p,a) for p in pairs for a in strict_json(p.metadata_json)['render_order'])


def validate_model(model, expected):
    require(type(model) is dict and set(model) == MODEL_KEYS,'model fields')
    require(canonical(model) == canonical(expected),'measured model differs from independent pin')
    hex40(model['revision_commit'])
    for k in ('tensor_digest','config_sha256','tokenizer_files_sha256'):
        pin(model[k])


def validate_load(receipt, *, expected_model, expected_host, loader, load_id, source_sha, code_sha, token_facts):
    require(type(receipt) is dict and set(receipt) == {'schema','host','model','loader','load_id',
            'source_manifest_sha256','code_manifest_sha256','probe','tokenizer'},'load receipt schema')
    require(receipt['schema'] == 'exp7.load.v1' and receipt['loader'] == loader and receipt['load_id'] == load_id,
            'single load identity/path')
    validate_model(receipt['model'],expected_model)
    require(canonical(receipt['host']) == canonical(expected_host),'measured host/stack drift')
    require(receipt['source_manifest_sha256'] == source_sha and receipt['code_manifest_sha256'] == code_sha,
            'load source binding')
    require(canonical(receipt['tokenizer']) == canonical(token_facts),'measured tokenizer/render/stop drift')
    probe = receipt['probe']
    require(type(probe) is dict and set(probe) == {'positions','logits','nonfinite'},'probe coverage schema')
    require(type(probe['positions']) is int and probe['positions'] == 8 and type(probe['logits']) is int
            and probe['logits'] > 0 and type(probe['nonfinite']) is int and probe['nonfinite'] == 0,'nonfinite/incomplete probe')


def context(trust, battery, receipt_bytes, receipt, *, outcome=False):
    d = trust.data
    return canonical(dict(battery_sha256=battery.bytes_sha256, normalizer_sha256=d['normalizer_sha256'],
        source_manifest_sha256=d['source_manifest_sha256'],code_manifest_sha256=d['code_manifest_sha256'],
        host_receipt_sha256=digest(receipt_bytes),host_id=receipt['host']['host_id'],
        launch_git_commit=hex40(d['loads'][receipt['load_id']]['launch_git_commit']),prereg_tag_object=hex40(d['prereg']['object']),
        projection_commit=hex40(d['projection']['commit']),model=receipt['model'],
        predictor_seal_sha256=d['predictor_seal']['sha256'] if outcome else None,
        power_sha256=d['power']['sha256'] if outcome else None)).decode()


def expected_sample(battery, model, family, arm, context_json):
    return ExpectedUnit('twin' if model == 'twin' else 'trained',f'units/predictor/{model}/{family}/{arm}',
                         addresses(battery,model,family,arm),16 if model == 'twin' else 64,context_json)


def expected_outcome(battery, unit_id, context_json):
    return ExpectedUnit('outcome',unit_id,addresses(battery),1,context_json)
