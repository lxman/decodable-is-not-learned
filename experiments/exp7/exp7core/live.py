"""Lazy frozen LEAF adapters. Importing this module performs no contact.

Synthetic tests replace tokenizer acquisition/construction callables under the
hard import guard. Live entries take an already verified Campaign or build-
tokenizer authorization. No predecessor runner/analyzer is called.
"""
from pathlib import Path
import gc
import platform
import importlib.metadata
from .contract import canonical,digest,pin,require
from .records import strict_json
from .anchors import old_items
from .collection_schema import validate_load,validate_model
from .provenance import hex40
from .guardio import safe_path,write_once

PACKAGES = ('torch','transformers','numpy','safetensors','tokenizers','huggingface_hub')
ASSET_FILES = {'config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.json','merges.txt',
               'generation_config.json','added_tokens.json'}
# LIVE-TOKENIZER-1: the complete accepted TOKENIZER-9 asset, not new authority.
PYTHIA_EOS_PAD_FILES = {
    'config.json': '302d6702a29de1039066e41404877fb8c53b7ddc82e88f9aba277f230086cfe0',
    'tokenizer_config.json': '70e38394e494931c6f773ba41e19460dd4436526b852207367f04341b4066d3f',
    'special_tokens_map.json': '6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad',
    'tokenizer.json': 'c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624',
}
PYTHIA_EOS_PAD_ASSET_SHA256 = '316641e6c4f762dca571dd9079aeedf120423d084e2b57470ff643b98d3ccb27'


def asset_bytes(asset,trace=None):
    """Only config/tokenizer files, exact pinned repository revision + bytes."""
    from huggingface_hub import hf_hub_download
    hex40(asset['commit'])
    require(set(asset['files']) <= ASSET_FILES and {'config.json','tokenizer.json','tokenizer_config.json'} <= set(asset['files']),
            'config/tokenizer asset names')
    values = {}
    for name,sha in sorted(asset['files'].items()):
        p = Path(hf_hub_download(asset['repo'],name,revision=asset['commit']))
        data = p.read_bytes()
        require(digest(data) == pin(sha),'config/tokenizer byte mismatch: '+name)
        if trace is not None:
            trace.pin_external(p,sha)
        values[name] = data
    return values


def token_facts(tok,model=None):
    plain = tok('Q:')['input_ids']
    require(plain and plain[0] not in tok.all_special_ids,'unexpected BOS/chat rendering')
    return {'bos':tok.bos_token_id,'eos':tok.eos_token_id,'pad':tok.pad_token_id,
            'padding_side':tok.padding_side,'special_ids':sorted(set(tok.all_special_ids)),
            'adds_bos':False,'generation_eos':None if model is None else model.generation_config.eos_token_id}


def _tokenizer_from_pretrained(repo, *, revision, **kwargs):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(repo, revision=revision, **kwargs)


def token_only(asset):
    """Tokenizer-only future build path: no model library constructor here."""
    pythia = asset['repo'] == 'EleutherAI/pythia-1b'
    if pythia:
        require(type(asset) is dict and set(asset) == {'repo','commit','files','pad_id'}
                and asset['commit'] == 'f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2'
                and type(asset['pad_id']) is int and asset['pad_id'] == 0
                and type(asset['files']) is dict and asset['files'] == PYTHIA_EOS_PAD_FILES
                and digest(canonical(asset)) == PYTHIA_EOS_PAD_ASSET_SHA256,
                'exact reviewed Pythia EOS-pad asset required')
    files = asset_bytes(asset)
    if pythia:
        tok = _tokenizer_from_pretrained(asset['repo'],revision=asset['commit'],pad_token='<|endoftext|>')
        require(getattr(tok,'eos_token',None) == '<|endoftext|>'
                and type(getattr(tok,'eos_token_id',None)) is int and tok.eos_token_id == 0,
                'Pythia EOS token/id mismatch')
        require(type(getattr(tok,'pad_token_id',None)) is int,'Pythia integer pad ID required')
    else:
        tok = _tokenizer_from_pretrained(asset['repo'],revision=asset['commit'])
    tok.padding_side = 'left'
    if not pythia and tok.pad_token_id is None:
        tok.pad_token = '<|finetune_right_pad_id|>' if 'SmolLM3' in asset['repo'] else tok.eos_token
    require(tok.pad_token_id == asset['pad_id'],'token-only pad pin')
    return tok, {'repo':asset['repo'],'commit':asset['commit'],'files':{n:digest(b) for n,b in files.items()},
                 'tokenizer':token_facts(tok)}


def measure_host(device,torch):
    cuda = device.startswith('cuda')
    if cuda:
        model = torch.cuda.get_device_name(device)
        runtime = torch.version.cuda
        import subprocess
        driver = subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total',
                                          '--format=csv,noheader'],timeout=20).decode().strip()
        require(driver and '\n' not in driver,'one measured GPU driver/runtime')
    else:
        require(device == 'mps' and torch.backends.mps.is_available(),'frozen predictor backend')
        model = platform.machine()
        runtime = platform.mac_ver()[0]
        driver = runtime
    return {'host_id':platform.node(),'system':platform.system(),'release':platform.release(),
            'machine':platform.machine(),'python':platform.python_version(),
            'packages':{p:importlib.metadata.version(p) for p in PACKAGES},'device':device,
            'device_model':model,'runtime':runtime,'driver':driver,'torch_cuda':torch.version.cuda,
            'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),
            'cudnn_deterministic':bool(torch.backends.cudnn.deterministic),
            'cudnn_benchmark':bool(torch.backends.cudnn.benchmark),
            'matmul_allow_tf32':bool(torch.backends.cuda.matmul.allow_tf32)}


def probe(model,tok,prompts):
    import torch
    require(len(prompts) == 8,'fixed probe coverage')
    n,bad = 0,0
    for p in prompts:
        enc = tok(p,return_tensors='pt').to(model.device)
        with torch.no_grad():
            value = model(**enc,use_cache=False,logits_to_keep=1).logits
        n += value.numel()
        bad += int((~torch.isfinite(value)).sum().item())
    return {'positions':8,'logits':n,'nonfinite':bad}


def authorize(c,load_id,scope):
    c._ready()
    require(scope in ('predictor-preflight','predictor-collection','outcome-preflight','outcome-collection'),'live scope')
    spec = c.trust.data['loads'][load_id]
    require(scope.startswith('predictor') == (spec['loader'] == 'predictor'),'live grant/loader class')
    c.trust.grant(scope)
    from .referents import verify_model
    from .preflight import verify_cap_receipt
    verify_model(c,spec['model'])
    m = c.trust.data['models'][spec['model']]
    validate_model(m,m)  # total pin/schema check BEFORE lazy model imports
    verify_cap_receipt(c,spec['model'])
    if spec['loader'] == 'predictor':
        require(not (c.root/'predictor-seal.json').exists(),'predictor sealed')
    else:
        c.verify_power()
    c.trust.trace.check()


class LiveSession:
    def __init__(self,c,load_id,scope):
        authorize(c,load_id,scope)
        # Durable inventory BEFORE the first lazy model/tokenizer contact. A
        # failed load is contact evidence too and prevents later power runs.
        category = 'predictor' if scope.startswith('predictor') else 'outcome'
        folder = safe_path(c.root,f'contacts/{category}/{load_id}')
        folder.mkdir(parents=True,exist_ok=True)
        index = len(tuple(folder.iterdir()))
        write_once(folder/f'{index:04d}.json',canonical({'scope':scope,'load_id':load_id}))
        self.c,self.load_id = c,load_id
        self.model = self.tok = self.runner = None
        self.sampler = None
        self.cache = self.manifest = None
        d = c.trust.data
        spec = d['loads'][load_id]
        self.spec = spec
        expected = d['models'][spec['model']]
        device = d['hosts'][spec['host']]['device']
        files = asset_bytes(d['assets'][spec['model']],c.trust.trace)
        try:
            if spec['loader'] == 'predictor':
                from experiments.exp6.run.predict_6 import real_loader,real_sampler
                name = 'pythia_1b' if spec['model'] == 'twin' else spec['model']
                require(name in ('pythia_1b','olmo2_1b'),'predictor leaf name')
                # Frozen Pythia loader ignores device and uses MPS: assert rather than mislabel it.
                require(device == 'mps','predictor must use frozen Mac path')
                self.tok,self.model,info = real_loader(name,'untrained' if spec['model'] == 'twin' else 'trained',device)
                self.sampler = real_sampler()
            else:
                from experiments.exp6 import families_6 as fm
                manifest = fm.manifest('smollm3_3b')
                self.manifest = manifest
                step = int(spec['model'].split('/')[1])
                entry = fm.entry('smollm3_3b',manifest,step)
                require(canonical(entry) == canonical(d['checkpoint_entries'][str(step)]),'candidate-file entry drift')
                if spec['loader'] == 'thin':
                    require(step == 3440000,'thin endpoint only')
                    self.model,self.tok,info = fm.load_thin('smollm3_3b',manifest,device=device)
                else:
                    require(spec['loader'] == 'candidate','outcome loader name')
                    cache = Path(d['cache_root']).expanduser().resolve()
                    require(cache.name == 'ckpt_cache_7' and not cache.is_relative_to(c.repo.resolve()),'explicit Exp7 cache')
                    self.cache = cache
                    self.model,self.tok,info = fm.load_checkpoint('smollm3_3b',manifest,step,device=device,cache_root=cache)
                self.runner = fm.runner('smollm3_3b',self.tok,self.model)
            import torch
            from experiments.exp2g.checkpoints_2g import tensor_digest
            measured_dtype = {str(p.dtype).removeprefix('torch.') for p in self.model.parameters() if p.is_floating_point()}
            require(measured_dtype == {expected['dtype']},'actual tensor dtype')
            require(info['repo'] == expected['repo'] and info['commit'] == expected['revision_commit'],'native loader identity')
            measured = {'repo':info['repo'],'revision_commit':info['commit'],
                'tensor_digest':tensor_digest(self.model),'config_sha256':digest(files['config.json']),
                'tokenizer_files_sha256':digest(canonical({n:digest(b) for n,b in files.items() if n != 'config.json'})),
                'render':'plain','terminal_ids':sorted(set(self.tok.all_special_ids)),
                'dtype':next(iter(measured_dtype)),'init_seed':0 if spec['model'] == 'twin' else None}
            if 'tensor_digest' in info:
                require(info['tensor_digest'] == measured['tensor_digest'],'native tensor digest vs fresh measurement')
            # Config FILE identity alone cannot prove the constructed model used it.
            # Compare EVERY source config field except fixed runtime provenance /
            # dtype fields (dtype was measured directly above), never a caller-
            # supplied optional/empty subset of architecture fields.
            actual_config = self.model.config.to_dict()
            config_fields = strict_json(files['config.json'])
            ignored = {'_name_or_path','_commit_hash','transformers_version','torch_dtype','dtype'}
            rope_map = {'rotary_emb_base':'rope_theta','rope_theta':'rope_theta','rotary_pct':'partial_rotary_factor'}
            require(type(config_fields) is dict and config_fields.get('model_type'),'complete source config')
            for key,value in config_fields.items():
                if key in ignored:
                    continue
                got = actual_config.get(key)
                if got is None and key in rope_map and type(actual_config.get('rope_parameters')) is dict:
                    got = actual_config['rope_parameters'].get(rope_map[key])
                require(canonical(got) == canonical(value),'loaded config semantic drift: '+key)
            token_source = strict_json(files['tokenizer.json'])
            vocab = token_source['model']['vocab']
            require(type(vocab) is dict,'frozen BPE tokenizer vocabulary')
            vocab = {**vocab,**{r['content']:r['id'] for r in token_source['added_tokens']}}
            require(canonical(self.tok.get_vocab()) == canonical(vocab),'loaded tokenizer vocabulary differs from pinned file')
            old = old_items(c.trust.read_repo,'add_base8')
            prompts = [p for p,a,k in sorted(old,key=lambda row:(-len(row[0]),row[0]))[:8]]
            self.receipt = {'schema':'exp7.load.v1','host':measure_host(device,torch),'model':measured,
                'loader':spec['loader'],'load_id':load_id,'source_manifest_sha256':d['source_manifest_sha256'],
                'code_manifest_sha256':d['code_manifest_sha256'],'probe':probe(self.model,self.tok,prompts),
                'tokenizer':token_facts(self.tok,self.model)}
            validate_load(self.receipt,expected_model=expected,expected_host=d['hosts'][spec['host']],
                loader=spec['loader'],load_id=load_id,source_sha=d['source_manifest_sha256'],
                code_sha=d['code_manifest_sha256'],token_facts=d['tokenizers'][spec['model']])
        except BaseException:
            self.close()
            raise

    def sample(self,prompt,**kwargs):
        require(self.sampler is not None,'sampler unavailable for outcome load')
        return self.sampler(self.model,self.tok,prompt,**kwargs)

    def greedy(self,prompts,cap):
        require(self.runner is not None,'greedy unavailable for predictor load')
        return self.runner.generate(prompts,cap)

    def probe(self,prompts):
        return probe(self.model,self.tok,prompts)

    def close(self):
        # Release every local strong reference BEFORE allocator cache clear.
        self.runner = self.sampler = self.model = self.tok = None
        gc.collect()
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif torch.backends.mps.is_available():
            torch.mps.empty_cache()
        self.c.trust.trace.check()  # includes explicitly pinned cached metadata
        if self.cache is not None and self.manifest is not None:
            from experiments.exp6 import families_6 as fm
            fm.free('smollm3_3b',self.manifest,int(self.spec['model'].split('/')[1]),cache_root=self.cache)
            self.cache = None


class LiveBackend:
    def __init__(self,c,scope):
        c._ready()
        c.trust.trace.check()
        self.c = c
        require(scope in ('predictor-preflight','predictor-collection','outcome-preflight','outcome-collection'),
                'live contact scope')
        self.scope = scope

    def open(self,load_id):
        self.c._ready()
        require(load_id in self.c.trust.data['loads'],'unplanned load')
        loader = self.c.trust.data['loads'][load_id]['loader']
        require(self.scope.startswith('predictor') == (loader == 'predictor'),'grant/loader class')
        self.c.trust.grant(self.scope)
        if loader == 'predictor':
            require(not (self.c.root/'predictor-seal.json').exists(),'predictor sealed')
        else:
            self.c.verify_power()
        return LiveSession(self.c,load_id,self.scope)
