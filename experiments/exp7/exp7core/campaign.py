"""Pure verified production data context. No model/tokenizer/statistic execution."""
from pathlib import Path
from contextlib import contextmanager
from .contract import ARMS, FAMILIES, GRID, canonical, digest, pin, require
from .records import strict_json, validate_record
from .guardio import safe_path, load_unit, write_once
from .provenance import Trust, LIVE, halted
from .battery_adapter import load_certified,verify_history
from .collection_schema import (MODELS, ANCHORS, predictor_units, outcome_units, expected_sample,
                                 expected_outcome, context, validate_load)
from .anchors import validate_anchor, greedy_anchor, old_stream
from .scoring import score_draws, outcome_counts


class Campaign:
    def __init__(self, root, repo, *, trust_path, trust_sha256, git=LIVE):
        self.root,self.repo = Path(root),Path(repo)
        self.trust = Trust(root,repo,trust_path,trust_sha256,git=git)
        self._active = False
        self._battery = self._baselines = None

    def __enter__(self):
        halted(self.root)
        self.trust.trace.start()
        try:
            self.trust.prereg_projection()
            d = self.trust.data
            require(set(d['sample_loads']) == set(MODELS),'predictor load-plan coverage')
            require(set(d['outcome_loads']) == set(map(str,GRID)),'outcome plan full grid')
            self._verify_manifests()
            self._active = True
            self.battery()
            return self
        except BaseException:
            self._active = False
            self.trust.trace.stop()
            raise

    def __exit__(self,typ,value,tb):
        try:
            halted(self.root)
        finally:
            self._active = False
            self.trust.trace.stop()
        return False

    def _ready(self):
        require(self._active,'Campaign requires verified entry/exit context')
        halted(self.root)

    def _verify_manifests(self):
        d = self.trust.data
        for name in ('source_manifest','code_manifest'):
            mapping = d[name]
            require(type(mapping) is dict and mapping and digest(canonical(mapping)) == pin(d[name+'_sha256']),name)
            for path,sha in mapping.items():
                require(d['repo_pins'].get(path) == sha,'manifest not independently pinned')
        require(any(p.endswith('/scoring.py') and h == d['normalizer_sha256']
                    for p,h in d['code_manifest'].items()),'normalizer source missing')

    def battery(self):
        self._ready()
        if self._battery is None:
            verify_history(self.trust.read_repo,self.trust.git)
            b,data,levels,baselines = load_certified(self.trust.read_repo)
            require(b.bytes_sha256 == pin(self.trust.data['battery_sha256']) and
                    digest(levels) == pin(self.trust.data['levels_sha256']),'normalized certified battery/levels pin')
            self._battery,self._baselines = b,baselines
        return self._battery

    def baselines(self):
        self.battery()
        return self._baselines

    def baseline_draws(self):
        """Raw k1 model-free outputs; abstentions remain None, never Score -> raw."""
        self.battery()
        from .battery_adapter import PREFIX
        rows = [strict_json(x) for x in self.trust.read_repo(PREFIX+'baseline-outputs.jsonl').splitlines()]
        by_old = {strict_json(p.metadata_json)['id']:p for p in self.battery().pairs}
        out = {}
        for r in rows:
            p = by_old[r['pair']]
            values = r['predictions']
            require(type(values) is list and len(values) == 4 and all(v is None or type(v) is str for v in values),
                    'baseline raw values/abstentions')
            out.setdefault(r['method'],{}).setdefault(p.family,{})[p.pair_id] = dict(zip(ARMS,values))
        return {m:{f:tuple(values[p.pair_id] for p in self.battery().family(f)) for f,values in families.items()}
                for m,families in out.items()}

    def baseline_catalog(self):
        self.battery()
        from .battery_adapter import PREFIX
        rows = strict_json(self.trust.read_repo(PREFIX+'baselines.json'))
        return {m:{('unscrambling' if r['family'] == 'words' else r['family']):
                   {'applicable':r['applicable'],'reason':r['reason'],'abstentions':r['abstentions'],
                    'emissions':r['emissions'],'prompts':r['prompts']}
                   for r in rows if r['method'] == m} for m in sorted({r['method'] for r in rows})}

    def base_assignments(self):
        """Tagged metadata-only levels, zero predictor/outcome reads."""
        from .strata import merge_levels
        out = {}
        for f in FAMILIES:
            pairs = self.battery().family(f)
            assigned,_ = merge_levels([p.nominal for p in pairs],[p.ordinal for p in pairs])
            out[f] = tuple(canonical(v).decode().strip() for v in assigned)
        return out

    def require_preoutcome(self):
        """Actual collector tree names, including failed/torn contacts and load receipts."""
        halted(self.root)
        require(not any(scope.startswith('outcome') for scope in self.trust.data['grants']),
                'outcome grant precedes power')
        for prefix in ('units/outcome','units/endpoint','units/outcome-anchors','outcomes','contacts/outcome'):
            require(not safe_path(self.root,prefix).exists(),'outcome contact precedes power: '+prefix)
        for load,spec in self.trust.data['loads'].items():
            if spec['loader'] != 'predictor':
                require(not safe_path(self.root,f'receipts/{load}.json').exists(),'outcome load receipt precedes power')
        claims = safe_path(self.root,'claims')
        if claims.exists():
            require(not any(p.name.startswith('outcome') for p in claims.iterdir()),'outcome claim precedes power')

    @contextmanager
    def entryexit(self,stage):
        """Stats uses its own exclusive once claim BEFORE calling this context.

        This also consumes the independently evidenced owner grant BEFORE
        source/raw entry checks. Both claims remain consumed on refusal. The
        statistics producer alone publishes its final result, AFTER this exits.
        """
        require(stage in ('analysis','power','calibration'),'statistics stage')
        require(not self._active,'stage authorization must precede Campaign entry')
        halted(self.root)
        claim = safe_path(self.root,f'statistics/{stage}/CLAIM.json')
        require(claim.is_file(),'statistics once-only claim must precede stage entry')
        self.trust.read_root(f'statistics/{stage}/CLAIM.json')
        if stage == 'calibration':
            require(not self.trust.data.get('prereg',{}).get('object'),'calibration belongs before prereg tag')
            self.require_preoutcome()
            for path in ('units/predictor','units/anchors','predictor-seal.json','preflight','contacts/predictor',
                         'pythia-digest-baseline.json','claims/predictor-digest-baseline.CLAIM'):
                require(not safe_path(self.root,path).exists(),'calibration after predictor contact')
            self.trust.build_grant(stage,consume=True)
            self.trust.trace.start()
            try:
                self._verify_manifests()
                yield self.bindings_unopened()
                self.require_preoutcome()
                halted(self.root)
            finally:
                self.trust.trace.stop()
        else:
            self.trust.grant(stage,consume=True)
            if stage == 'power':
                self.require_preoutcome()
            with self:
                if stage == 'power':
                    self.verify_predictor_seal()
                else:
                    self.complete_bindings()
                yield self.bindings()
                if stage == 'power':
                    self.require_preoutcome()
                    self.verify_predictor_seal()
                else:
                    self.complete_bindings()

    def bindings_unopened(self):
        return {'trust_sha256':self.trust.sha,**{k:self.trust.data[k] for k in
                ('battery_sha256','source_manifest_sha256','code_manifest_sha256')}}

    def statistics_bindings(self,stage):
        """Adapter-ready provenance using independent metadata, never output guesses."""
        require(stage in ('calibration','power','analysis'),'statistics binding stage')
        d = self.trust.data
        inputs = {'battery':d['battery_sha256'],'source_manifest':d['source_manifest_sha256'],
                  'code_manifest':d['code_manifest_sha256'],'normalizer':d['normalizer_sha256']}
        if stage in ('power','analysis'):
            e = d['calibration']
            raw = self.trust.read_root(e['path'])
            require(digest(raw) == pin(e['sha256']),'independently pinned calibration record')
            path = (self.root.resolve()/e['path']).relative_to(self.repo.resolve()).as_posix()
            self.trust.git.blob(e['commit'],path,e['sha256'])
            require(d['prereg']['bindings'].get(path) == e['sha256'],'calibration not bound before prereg tag')
            inputs['calibration'] = e['sha256']
            inputs['predictor_seal'] = d['predictor_seal']['sha256']
        if stage == 'analysis':
            inputs['power'] = d['power']['sha256']
            inputs['complete'] = d['complete']['sha256']
        return {'provenance_sha256':self.trust.sha,'input_sha256':inputs}

    def load_receipt(self,load_id):
        self._ready()
        d = self.trust.data
        spec = d['loads'][load_id]
        require(set(spec) == {'model','host','loader','launch_git_commit'},'independent load-plan fields')
        from .referents import verify_model
        verify_model(self,spec['model'])
        raw = self.trust.read_root(f'receipts/{load_id}.json')
        receipt = strict_json(raw)
        validate_load(receipt,expected_model=d['models'][spec['model']],expected_host=d['hosts'][spec['host']],
                      loader=spec['loader'],load_id=load_id,source_sha=d['source_manifest_sha256'],
                      code_sha=d['code_manifest_sha256'],token_facts=d['tokenizers'][spec['model']])
        self.trust.git.ancestor(d['projection']['commit'],spec['launch_git_commit'])
        return raw,receipt

    def _context(self,load_id,outcome=False):
        raw,receipt = self.load_receipt(load_id)
        return context(self.trust,self.battery(),raw,receipt,outcome=outcome)

    def expected(self,name):
        self._ready()
        d = self.trust.data
        parts = name.split('/')
        if name in predictor_units():
            _,_,model,family,arm = parts
            load_id = d['sample_loads'][model]
            require(d['loads'][load_id]['model'] == model and d['loads'][load_id]['loader'] == 'predictor',
                    'predictor load assignment')
            return expected_sample(self.battery(),model,family,arm,self._context(load_id))
        if name in outcome_units():
            step = parts[-1]
            load_id = d['outcome_loads'][step]
            require(d['loads'][load_id]['model'] == 'outcome/'+step and d['loads'][load_id]['loader'] == 'candidate',
                    'checkpoint load assignment')
        else:
            require(len(parts) == 4 and parts[:2] == ['units','endpoint'] and parts[3] in ('thin','candidate'),
                    'canonical unit name')
            host,loader = parts[2:]
            load_id = d['endpoint_loads'][host][loader]
            require(d['loads'][load_id]['model'] == 'outcome/3440000' and d['loads'][load_id]['loader'] == loader
                    and d['loads'][load_id]['host'] == host,'endpoint load assignment')
        return expected_outcome(self.battery(),name,self._context(load_id,outcome=True))

    def unit(self,name,validator):
        self._ready()
        folder = safe_path(self.root,name)
        if not folder.exists():
            return None
        require(folder.is_dir() and {p.name for p in folder.iterdir()} == {'raw.jsonl','record.json','DONE.json'},
                'torn/extra unit files')
        for file in ('raw.jsonl','record.json','DONE.json'):
            self.trust.read_root(name+'/'+file)
        # Strict duplicate JSON check before the generic primitive's json.loads.
        for file in ('record.json','DONE.json'):
            strict_json(self.trust.read_root(name+'/'+file))
        return load_unit(self.root,name,validator=validator)

    def raw_unit(self,name):
        expected = self.expected(name)
        got = self.unit(name,lambda raw,rec:validate_record(raw,rec,expected))
        require(got is not None,'missing required unit: '+name)
        return got

    def verify_anchors(self,model):
        require(model in MODELS,'predictor model')
        if model == 'twin':
            # Twin still depends on the separately measured trained-host anchor gate.
            model = 'pythia_1b'
        d = self.trust.data
        ctx = self._context(d['sample_loads'][model])
        out = {}
        for rung in ANCHORS+(('ctrl_copy',) if model == 'pythia_1b' else ()):
            name = f'units/anchors/{model}/{rung}'
            got = self.unit(name,lambda raw,rec,r=rung:validate_anchor(raw,rec,read=self.trust.read_repo,
                                        model=model,rung=r,context_json=ctx))
            require(got is not None,'missing full predictor anchor')
            out[name] = digest(got[0])
        return out

    def predictor_draws(self):
        self._ready()
        out,streams = {},set()
        for model in MODELS:
            self.verify_anchors(model)
            out[model] = {}
            for family in FAMILIES:
                arms = []
                for arm in ARMS:
                    name = f'units/predictor/{model}/{family}/{arm}'
                    raw,rec = self.raw_unit(name)
                    rows = [strict_json(r) for r in raw.splitlines()]
                    for r in rows:
                        require(r['stream_seed'] not in streams,'shared global sampling stream')
                        streams.add(r['stream_seed'])
                    arms.append(rows)
                out[model][family] = tuple(tuple(tuple(arms[j][i]['draws']) for j in range(4)) for i in range(500))
        require(len(streams) == 24000,'full new stream cardinality')
        old = {old_stream(r,s,z,i) for s in ('1b','olmo1b') for r in ANCHORS for z in (0,) for i in range(500)}
        old |= {old_stream('ctrl_copy','1b',z,i) for z in range(4) for i in range(500)}
        require(not streams & old,'new stream collides with old anchor stream')
        # No unlisted units; all 48 required canonical addresses, no extras.
        self._exact_leaf_set('units/predictor',set(predictor_units()))
        return out

    def _exact_leaf_set(self,prefix,expected):
        root = safe_path(self.root,prefix)
        require(root.is_dir(),'missing unit tree')
        got = set()
        for p in root.rglob('*'):
            require(not p.is_symlink(),'symlink in unit tree')
            if p.is_file():
                require(p.name in ('raw.jsonl','record.json','DONE.json'),'unexpected unit artifact')
                got.add(p.parent.relative_to(self.root).as_posix())
        require(got == expected,'production unit address set differs')

    def predictor_data(self):
        raw = self.predictor_draws()
        return {m:{f:(self.battery().family(f),tuple(score_draws(dict(zip(ARMS,rows)),p.targets,p.answer_type,
                                            k=16 if m == 'twin' else 64)
                               for p,rows in zip(self.battery().family(f),values)))
                   for f,values in families.items()} for m,families in raw.items()}

    def seal_payload(self):
        from .collectors import verify_preflight
        self.predictor_draws()  # complete rescoring and raw anchor comparison above
        names = list(predictor_units())+[f'units/anchors/{m}/{r}' for m in MODELS[:2]
                    for r in ANCHORS+(('ctrl_copy',) if m == 'pythia_1b' else ())]
        bindings = {f'{n}/{f}':digest(self.trust.read_root(f'{n}/{f}'))
                    for n in names for f in ('raw.jsonl','record.json','DONE.json')}
        for model in MODELS:
            verify_preflight(self,model)
            name = f"receipts/{self.trust.data['sample_loads'][model]}.json"
            bindings[name] = digest(self.trust.read_root(name))
            name = f'preflight/{model}.json'
            bindings[name] = digest(self.trust.read_root(name))
            for f in FAMILIES:
                for suffix in ('.jsonl','.repeat.jsonl'):
                    name = f'preflight/{model}/{f}/q0{suffix}'
                    bindings[name] = digest(self.trust.read_root(name))
        return {'schema':'exp7.predictor-seal.v1','battery_sha256':self.battery().bytes_sha256,
                'source_manifest_sha256':self.trust.data['source_manifest_sha256'],
                'code_manifest_sha256':self.trust.data['code_manifest_sha256'],
                'new_units':48,'new_rows':24000,'new_draws':1152000,'anchor_draws':144000,'bindings':bindings}

    def verify_predictor_seal(self):
        self._ready()
        e = self.trust.data['predictor_seal']
        raw = self.trust.read_root(e['path'])
        require(digest(raw) == pin(e['sha256']),'predictor seal byte pin')
        got = strict_json(raw)
        require(canonical(got) == canonical(self.seal_payload()),'predictor seal not rederived')
        self.trust.tag('predictor_tag')
        prefix = self.root.resolve().relative_to(self.repo.resolve()).as_posix()
        required = {prefix+'/'+p:s for p,s in got['bindings'].items()}
        required[prefix+'/'+e['path']] = e['sha256']
        bound = self.trust.data['predictor_tag']['bindings']
        require(all(bound.get(p) == s for p,s in required.items()),'seal tag misses raw/record/receipt/marker bytes')
        return got

    def verify_power(self):
        self.verify_predictor_seal()
        d = self.trust.data
        e = d['power']
        raw = self.trust.read_root(e['path'])
        require(digest(raw) == pin(e['sha256']),'power immutable byte pin')
        value = strict_json(raw)
        require(value['schema'] == 'exp7.statistics.v2' and value['stage'] == 'power' and value['production'] is True
                and value['seal_sha256'] == d['predictor_seal']['sha256']
                and value['battery_sha256'] == self.battery().bytes_sha256
                and value['source_bindings']['code_manifest'] == d['code_manifest_sha256']
                and value['source_bindings']['source_manifest'] == d['source_manifest_sha256'],'power input binding')
        self.trust.git.ancestor(d['predictor_tag']['commit'],e['commit'])
        path = (self.root.resolve()/e['path']).relative_to(self.repo.resolve()).as_posix()
        self.trust.git.blob(e['commit'],path,e['sha256'])
        # Full finite-grid semantic validation belongs the power producer/analyzer.
        return value

    def outcome_anchor(self,load_id,step):
        ctx = self._context(load_id,outcome=True)
        def validate(raw,record):
            want = {'schema':'exp7.greedy-anchors.v1','load_id':load_id,'step':step,
                    'context':strict_json(ctx),**greedy_anchor(raw,read=self.trust.read_repo,step=step)}
            require(canonical(record) == canonical(want),'outcome anchor receipt does not rederive')
        got = self.unit('units/outcome-anchors/'+load_id,validate)
        require(got is not None,'missing per-load old anchors')
        return got

    def verify_endpoint(self,host):
        d = self.trust.data
        specs = d['endpoint_loads'][host]
        require(set(specs) == {'thin','candidate'} and specs['thin'] != specs['candidate'],'two distinct loader paths')
        readings = [self.raw_unit(f'units/endpoint/{host}/{path}') for path in ('thin','candidate')]
        require(readings[0][0] == readings[1][0],'full endpoint raw identity')
        a = [self.outcome_anchor(specs[path],3440000)[0] for path in ('thin','candidate')]
        require(a[0] == a[1],'full endpoint anchor identity')
        # validate_record rescored BOTH target bits across ALL 8,000 prompts.
        return readings[1][0]

    def verify_complete(self):
        self.verify_power()
        d = self.trust.data
        used = {d['loads'][load]['host'] for load in d['outcome_loads'].values()}
        require(used == set(d['endpoint_loads']),'host qualification coverage')
        endpoints = {h:self.verify_endpoint(h) for h in sorted(used)}
        for step in GRID:
            load = d['outcome_loads'][str(step)]
            raw,rec = self.raw_unit(f'units/outcome/{step}')
            self.outcome_anchor(load,step)
            if step == 3440000:
                require(raw == endpoints[d['loads'][load]['host']],'endpoint reuse identity')
        self._exact_leaf_set('units/outcome',set(outcome_units()))
        halted(self.root)

    def outcome_draws(self):
        self.verify_complete()
        out = {f:[[] for i in range(500)] for f in FAMILIES}
        for step in GRID:
            raw,_ = self.raw_unit(f'units/outcome/{step}')
            rows = [strict_json(x) for x in raw.splitlines()]
            for j,p in enumerate(self.battery().pairs):
                out[p.family][p.index].append(tuple(rows[4*j+a]['draws'][0] for a in range(4)))
        return {f:tuple(tuple(v) for v in values) for f,values in out.items()}

    def outcomes(self):
        values = self.outcome_draws()
        return {f:tuple(outcome_counts({step:dict(zip(ARMS,r)) for step,r in zip(GRID,rows)},
                                       p.targets,p.answer_type,steps=GRID)
                       for p,rows in zip(self.battery().family(f),family)) for f,family in values.items()}

    def bindings(self):
        self._ready()
        # Administrative/frozen-input trust, never a digest synthesized from
        # whatever raw output happens to be present. Stage-specific methods below
        # verify first, then return exact authoritative bound file maps.
        return self.bindings_unopened()

    def seal_bindings(self):
        value = self.verify_predictor_seal()
        return {'seal_sha256':self.trust.data['predictor_seal']['sha256'],
                'battery_sha256':self.battery().bytes_sha256,'bindings':dict(value['bindings'])}

    def power_bindings(self):
        record = self.verify_power()
        e = self.trust.data['power']
        return {'power_sha256':e['sha256'],'record':record,'bindings':{e['path']:e['sha256']}}

    def complete_payload(self):
        """Producer's validated inventory; independent commit pin is added later."""
        self.verify_complete()
        d = self.trust.data
        names = list(outcome_units())+[f'units/endpoint/{h}/{p}' for h in d['endpoint_loads'] for p in ('thin','candidate')]
        load_ids = set(d['outcome_loads'].values()) | {v for e in d['endpoint_loads'].values() for v in e.values()}
        names += ['units/outcome-anchors/'+load for load in sorted(load_ids)]
        bound = {f'{n}/{f}':digest(self.trust.read_root(f'{n}/{f}')) for n in names
                 for f in ('raw.jsonl','record.json','DONE.json')}
        for load in sorted(load_ids):
            n = 'receipts/'+load+'.json'
            bound[n] = digest(self.trust.read_root(n))
        return {'schema':'exp7.complete.v1','predictor_seal_sha256':d['predictor_seal']['sha256'],
                'power_sha256':d['power']['sha256'],'bindings':bound}

    def complete_bindings(self):
        """Independent secured completion receipt checked against full rederivation."""
        want = self.complete_payload()
        e = self.trust.data['complete']
        raw = self.trust.read_repo(e['path'])
        require(digest(raw) == e['sha256'],'authoritative complete receipt pin')
        require(canonical(strict_json(raw)) == canonical(want),'complete map does not rederive')
        self.trust.git.blob(e['commit'],e['path'],e['sha256'])
        return {'complete_sha256':e['sha256'],'bindings':want['bindings']}
