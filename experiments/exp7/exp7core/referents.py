"""Reconstruct model expectations from pinned historical or enrolled evidence."""
from .contract import GRID,canonical,digest,require
from .records import strict_json


def verify_model(c,key):
    d = c.trust.data
    m = d['models'][key]
    if key == 'olmo2_1b':
        recs = [strict_json(c.trust.read_repo(f'experiments/exp2i/results/predictor/olmo1b/{r}.json'))
                for r in ('add_base8','sub_base8')]
        require(all(r['commit'] == m['revision_commit'] and r['model_sha'] == m['tensor_digest'] and
                    r['dtype'] == 'float32' for r in recs),'OLMo independent old tensor/revision')
        require(m['repo'] == 'allenai/OLMo-2-0425-1B' and m['init_seed'] is None,'OLMo independent model identity')
    elif key.startswith('outcome/'):
        step = int(key.split('/')[1])
        require(step in GRID,'outcome grid key')
        man = strict_json(c.trust.read_repo('experiments/exp2m/checkpoints_2m.json'))
        require(man['grid_3b'] == list(GRID),'old immutable outcome grid')
        entry = man['entries_3b'][str(step)]
        require(canonical(entry) == canonical(d['checkpoint_entries'][str(step)]),'independent candidate-file entry')
        require(m['repo'] == entry['repo'] and m['revision_commit'] == entry['commit'],'independent outcome revision')
        for rung in ('add_base8','sub_base8'):
            r = strict_json(c.trust.read_repo(f'experiments/exp2m/results/sweep/smollm3_3b/step{step}/{rung}.json'))
            require(r['weight_sha256'] == m['tensor_digest'] and r['commit'] == m['revision_commit'],
                    'independently committed outcome tensor digest')
    else:
        require(key in ('pythia_1b','twin'),'model key')
        r = strict_json(c.trust.read_repo(d['pythia_baseline_path']))
        require(r['schema'] == 'exp7.pythia-baseline.v1' and r['prereg_tag_object'] == d['prereg']['object']
                and r['projection_commit'] == d['projection']['commit'],'baseline tag/projection identity')
        mode = 'untrained' if key == 'twin' else 'trained'
        b = r['readings'][mode]
        for model_key,baseline_key in [('repo','repo'),('revision_commit','commit'),('tensor_digest','tensor_digest'),
                     ('config_sha256','config_sha256'),('tokenizer_files_sha256','tokenizer_files_sha256'),
                     ('dtype','dtype'),('init_seed','init_seed')]:
            require(canonical(m[model_key]) == canonical(b[baseline_key]),'enrolled Pythia baseline differs: '+model_key)
        require(m['repo'] == 'EleutherAI/pythia-1b' and m['revision_commit'] == 'f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2',
                'Pythia historical source')
    asset = d['assets'][key]
    require(asset['repo'] == m['repo'] and asset['commit'] == m['revision_commit'],'asset/model source identity')
    require(m['config_sha256'] == asset['files']['config.json'] and m['tokenizer_files_sha256'] ==
            digest(canonical({n:s for n,s in asset['files'].items() if n != 'config.json'})),'independent asset byte pins')
