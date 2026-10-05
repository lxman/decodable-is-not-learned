"""Independent byte trust, annotated git bindings, grants and execution/read trace."""
from pathlib import Path
import os
import re
import sys
from importlib.machinery import PathFinder
from .contract import Refusal, canonical, digest, pin, require
from .guardio import safe_path, write_once
from .records import strict_json

LIVE = object()
ACTIVE = []
HOOK_INSTALLED = False


def hex40(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{40}',value) and value != '0'*40,'Git object ID')
    return value


class Git:
    def __init__(self, repo):
        self.repo = str(repo)

    def call(self, *args):
        import subprocess
        executable = '/opt/homebrew/bin/git' if sys.platform == 'darwin' else '/usr/bin/git'
        return subprocess.check_output([executable,'--no-optional-locks',*args],cwd=self.repo)

    def tag(self, name, object_id, commit, bindings):
        require(re.fullmatch('exp7-(preregistered|predictor-sealed)',name),'tag name')
        require(self.call('rev-parse',f'refs/tags/{name}').decode().strip() == hex40(object_id),'tag object drift')
        require(self.call('cat-file','-t',object_id).strip() == b'tag','annotated tag required')
        require(self.call('rev-parse',f'{object_id}^{{commit}}').decode().strip() == hex40(commit),'tag peeled commit')
        require(bindings,'empty tag bindings')
        for path, sha in bindings.items():
            require(not path.startswith('/') and '..' not in path.split('/'),'tag path')
            require(digest(self.call('show',f'{commit}:{path}')) == pin(sha),'tag blob differs: '+path)

    def ancestor(self, older, newer):
        self.call('merge-base','--is-ancestor',hex40(older),hex40(newer))

    def blob(self, commit, path, sha):
        require(digest(self.call('show',f'{hex40(commit)}:{path}')) == pin(sha),'committed evidence differs')


def _audit(event,args):
    for trace in tuple(ACTIVE):
        trace.event(event,args)


class Trace:
    """Audit hook records EXECUTED filename, including aliases later removed.

    Reads under repo/root are only allowed from explicit independent pins or
    enrolled raw evidence. Bytecode under either root refuses: use a clean -B
    deployment checkout. Read enrollment is a TOCTOU snapshot, not validity.
    """
    def __init__(self, repo, root, repo_pins):
        self.repo,self.root = Path(repo).resolve(),Path(root).resolve()
        self.allowed = {str(safe_path(self.repo,k)):pin(v) for k,v in repo_pins.items()}
        self.reads,self.executed = set(),set()
        self.busy = False

    def covered(self,path):
        return path.is_relative_to(self.repo) or path.is_relative_to(self.root)

    def find_spec(self,fullname,path=None,target=None):
        spec = PathFinder.find_spec(fullname,path,target)
        if spec is None:
            return None
        origin = None if spec.origin in (None,'built-in','frozen') else Path(spec.origin).resolve()
        repository_name = fullname == 'experiments' or fullname.startswith('experiments.')
        if repository_name:
            if origin is None:
                require(spec.submodule_search_locations and all(Path(p).resolve().is_relative_to(self.repo)
                    for p in spec.submodule_search_locations),'experiment namespace escaped pinned repository')
            else:
                require(origin.is_relative_to(self.repo),'experiment import escaped pinned repository')
        if origin is not None and self.covered(origin):
            require(origin.suffix == '.py' and str(origin) in self.allowed,'unpinned module resolution')
            self.check_one(origin)
            return spec  # bind the inspected path, not an arbitrary later finder
        return spec if repository_name else None

    def event(self,event,args):
        if self.busy:
            return
        if event == 'open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            flags = args[2]
            # CPython supplies OS access flags for both open() and os.open().
            # O_RDWR (r+/w+/a+ included) can read input; only O_WRONLY is exempt.
            readable = (flags & os.O_ACCMODE) != os.O_WRONLY
            if self.covered(path) and readable:
                if path.is_dir() and not path.is_symlink():
                    return  # directory fd used for fsync, never input bytes
                if path.suffix == '.pyc' and not path.exists():
                    return  # normal cold loader cache probe; no bytes exist to read
                require(path.suffix != '.pyc','repository bytecode refused')
                require(str(path) in self.allowed,'unregistered read: '+str(path))
                self.reads.add(str(path))
        elif event == 'exec':
            name = args[0].co_filename
            if name.startswith('<'):
                return
            path = Path(name).resolve()
            if self.covered(path):
                require(str(path) in self.allowed,'unpinned execution: '+str(path))
                self.check_one(path)
                self.executed.add(str(path))

    def check_one(self,path):
        self.busy = True
        try:
            require(not path.is_symlink() and digest(path.read_bytes()) == self.allowed[str(path)],
                    'read/import byte drift: '+str(path))
        finally:
            self.busy = False

    def enroll(self,path):
        self.busy = True
        try:
            data = path.read_bytes()
        finally:
            self.busy = False
        key = str(path)
        require(key not in self.allowed or self.allowed[key] == digest(data),'input changed on reread')
        self.allowed[key] = digest(data)
        self.reads.add(key)
        return data

    def pin_external(self,path,sha):
        """Explicit immutable config/tokenizer cache inputs; never an inferred pin."""
        path = Path(path).resolve(strict=True)
        require(not self.covered(path),'external asset inside protected repository')
        key = str(path)
        require(key not in self.allowed or self.allowed[key] == pin(sha),'external asset pin changed')
        self.allowed[key] = pin(sha)
        self.check_one(path)
        self.reads.add(key)

    def check(self):
        for p in tuple(self.allowed):
            self.check_one(Path(p))
        # Snapshot complements exec trace for modules imported BEFORE entry.
        for module in tuple(sys.modules.values()):
            name = getattr(module,'__file__',None)
            if name:
                p = Path(name).resolve()
                module_name = getattr(module,'__name__','')
                if module_name == 'experiments' or module_name.startswith('experiments.'):
                    require(p.is_relative_to(self.repo),'preloaded experiment module outside pinned repository')
                if self.covered(p):
                    require(str(p) in self.allowed,'unpinned preloaded module/alias: '+str(p))
                    self.check_one(p)

    def start(self):
        global HOOK_INSTALLED
        if not HOOK_INSTALLED:
            sys.addaudithook(_audit)
            HOOK_INSTALLED = True
        self.check()
        ACTIVE.append(self)
        # Keep the synthetic launcher's absolute first-position refusal first.
        sys.meta_path.insert(1,self)

    def stop(self):
        try:
            self.check()
        finally:
            if self in ACTIVE:
                ACTIVE.remove(self)
            if self in sys.meta_path:
                sys.meta_path.remove(self)


class Trust:
    def __init__(self, root, repo, path, expected_sha256, *, git=LIVE):
        self.root,self.repo = Path(root).resolve(strict=True),Path(repo).resolve(strict=True)
        raw = safe_path(self.repo,path).read_bytes()
        require(digest(raw) == pin(expected_sha256),'independent trust digest')
        self.sha = expected_sha256
        self.data = strict_json(raw)
        require(self.data['schema'] == 'exp7.trust.v1','trust schema')
        require(git is LIVE or (git and all(callable(getattr(git,n,None)) for n in ('tag','ancestor','blob'))),
                'invalid Git injection')
        self.git = Git(self.repo) if git is LIVE else git
        pins = self.data['repo_pins']
        require(type(pins) is dict and pins and path not in pins,'trust pin map')
        self.trace = Trace(self.repo,self.root,{**pins,path:expected_sha256})

    def read_repo(self,path):
        require(path in self.data['repo_pins'],'unlisted repository input: '+path)
        return self.trace.enroll(safe_path(self.repo,path))

    def read_root(self,path):
        return self.trace.enroll(safe_path(self.root,path))

    def tag(self,key):
        e = self.data[key]
        self.git.tag(e['name'],e['object'],e['commit'],e['bindings'])
        for path,sha in e['bindings'].items():
            require(digest(self.read_repo(path)) == sha,'tag/worktree mismatch: '+path)

    def prereg_projection(self):
        binding = self.data['prereg']['bindings']
        for name in ('source_manifest','code_manifest'):
            require(all(binding.get(p) == sha for p,sha in self.data[name].items()),'prereg tag omits '+name)
        self.tag('prereg')
        p = self.data['projection']
        self.git.blob(p['commit'],p['path'],p['sha256'])
        require(digest(self.read_repo(p['path'])) == p['sha256'],'projection worktree drift')
        self.git.ancestor(self.data['prereg']['commit'],p['commit'])

    def _grant_binding(self,scope):
        """The later-written pinned trust envelope binds an immutable grant body."""
        grants = self.data.get('grants')
        require(type(grants) is dict and scope in grants,'missing grant binding')
        e = grants[scope]
        require(type(e) is dict and set(e) == {'path','canonical_sha256','commit'},'grant binding schema')
        require(type(e['path']) is str and e['path'],'grant binding path')
        pin(e['canonical_sha256'])
        return e,hex40(e['commit'])

    def grant(self,scope, *, consume=False):
        """Formal record is owner evidence, never an authorization invented here.

        Management supplies a pinned transcript/export reference and records the
        scope. A boolean pass/approved flag alone is not accepted evidence.
        """
        e,commit = self._grant_binding(scope)
        g = strict_json(self.read_repo(e['path']))
        require(digest(canonical(g)) == pin(e['canonical_sha256']),'grant pin')
        require(type(g) is dict and set(g) == {'schema','owner','scope','evidence_path','evidence_sha256','quote',
                           'prereg_tag_object','projection_commit','predictor_seal_sha256','power_sha256'},
                'grant schema')
        require(g['schema'] == 'exp7.owner-grant.v2' and g['owner'] == 'Michael Jordan' and g['scope'] == scope,
                'grant identity/scope')
        evidence = self.read_repo(g['evidence_path'])
        require(digest(evidence) == pin(g['evidence_sha256']) and type(g['quote']) is str and g['quote'].strip()
                and g['quote'].encode() in evidence,'missing formal owner evidence')
        self.git.blob(commit,e['path'],digest(self.read_repo(e['path'])))
        require(g['prereg_tag_object'] == self.data['prereg']['object'] and
                g['projection_commit'] == self.data['projection']['commit'],'grant stage binding')
        self.git.ancestor(g['projection_commit'],commit)
        if scope.startswith('outcome'):
            require(g['predictor_seal_sha256'] == self.data['predictor_seal']['sha256'] and
                    g['power_sha256'] == self.data['power']['sha256'],'outcome grant preceding seal/power')
            self.git.ancestor(self.data['power']['commit'],commit)
        if scope in ('power','analysis'):
            require(g['predictor_seal_sha256'] == self.data['predictor_seal']['sha256'],'statistics grant seal binding')
            self.git.ancestor(self.data['predictor_tag']['commit'],commit)
            if scope == 'power':
                require(g['power_sha256'] is None,'power grant cannot presuppose future power output')
            else:
                require(g['power_sha256'] == self.data['power']['sha256'],'analysis grant power binding')
                self.git.ancestor(self.data['complete']['commit'],commit)
        if consume:
            folder = safe_path(self.root,'claims')
            folder.mkdir(exist_ok=True)
            write_once(folder/(scope+'.CLAIM'),canonical({'grant_sha256':digest(canonical(g))}))
        return g

    def build_grant(self,scope, *, consume=False):
        """Pre-tag calibration authority; no fictitious prereg/projection gate."""
        e,commit = self._grant_binding(scope)
        raw = self.read_repo(e['path'])
        g = strict_json(raw)
        require(digest(canonical(g)) == pin(e['canonical_sha256']),'build grant pin')
        require(type(g) is dict and set(g) == {'schema','owner','scope','evidence_path','evidence_sha256','quote',
                           'source_manifest_sha256','code_manifest_sha256'},'build grant schema')
        require(g['schema'] == 'exp7.build-grant.v2' and g['owner'] == 'Michael Jordan' and g['scope'] == scope,
                'build grant scope')
        evidence = self.read_repo(g['evidence_path'])
        require(g['quote'] and g['quote'].encode() in evidence and digest(evidence) == pin(g['evidence_sha256']),
                'build owner evidence')
        require(g['source_manifest_sha256'] == self.data['source_manifest_sha256'] and
                g['code_manifest_sha256'] == self.data['code_manifest_sha256'],'build grant exact frozen inputs')
        self.git.blob(commit,e['path'],digest(raw))
        if consume:
            folder = safe_path(self.root,'claims')
            folder.mkdir(exist_ok=True)
            write_once(folder/(scope+'.CLAIM'),canonical({'grant_sha256':digest(canonical(g))}))
        return g


def halted(root):
    root = Path(root)
    require(not any(p.name in ('HALTED','HALTED.json') for p in root.rglob('*')),'stage HALTED')


def terminal(root,stage,body):
    try:
        halted(root)
        value = body()
        halted(root)
        return {'state':'COMPLETE','value':value,'failures':[]}
    except BaseException as exc:
        result = {'state':'INSUFFICIENT_DATA','value':None,'failures':[f'{type(exc).__name__}: {exc}']}
        try:
            p = Path(root)/'HALTED.json'
            if not p.exists():
                write_once(p,canonical({'stage':stage,**result}))
        except BaseException as publication:
            result['failures'].append('HALTED not persisted: '+repr(publication))
        return result
