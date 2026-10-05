"""INTR-1..4 reproduced at the real seams; native/authority ports remain fake."""
import guard
import sys
import io
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from contextlib import contextmanager, redirect_stdout
from fractions import Fraction
from copy import deepcopy
from importlib.machinery import PathFinder
from exp7ops.evidence import canonical, digest, strict, Refusal, snapshot
from testing_paths import WORK, PACKAGE

@contextmanager
def replace(obj,name,value):
    old=getattr(obj,name);setattr(obj,name,value)
    try: yield
    finally: setattr(obj,name,old)

class IntegrationReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=WORK);self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def test_INTR1_actual_miniature_science_and_supervisor_complete_together(self):
        from exp7ops.operator import Approval,stage_main
        from exp7integration.supervisor import OperationalComposition
        from exp7integration.deployment import FixedStageDeployment
        from exp7stats.analyzer import synthetic_run
        from exp7stats.common import Shape,dumps
        from stats_fixtures import FakeCampaign
        from heartbeat_fakes import FakeClock,FakeHeartbeatService
        root=self.root/'campaign';root.mkdir();out=self.root/'supervisor';out.mkdir()
        campaign=FakeCampaign(root);calls=[]
        shape=Shape(n=24,grid=(1,2,3),permutations=3,bootstraps=1)
        contract=self.root/'contract';contract.write_bytes(canonical({'synthetic':True,'stage':'verdict'}))
        approval=Approval(digest(contract.read_bytes()),'a'*64,'verdict',None,None,None,0,0,'b'*64)
        def run(c):
            result=synthetic_run(c,shape);calls.append(result);return result
        deployment=NS(root=root,check_sources=lambda:None,authenticate=lambda *a:approval,campaign=lambda *a:campaign)
        for name in ('predictor_preflight','predictor','seal','outcome_preflight','outcome','watch'):
            setattr(deployment,name,lambda *a:None)
        deployment.stage_result=lambda stage,result:FixedStageDeployment.stage_result(deployment,stage,result)
        composition=OperationalComposition(deployment,power_run=lambda c:self.fail('unexpected power'),analyzer_run=run)
        clock=FakeClock()
        stage_main(['verdict','--contract',str(contract)],composition=composition,contract_path=contract,output=out,pid=123,now=lambda:clock.value,heartbeat_service=FakeHeartbeatService(clock))
        self.assertEqual(len(calls),1);self.assertEqual(calls[0]['state'],'COMPLETE')
        scientific=root/'statistics/analysis'
        self.assertTrue((scientific/'COMPLETE.json').is_file())
        self.assertFalse((out/'HALTED.json').exists())
        self.assertEqual(strict((out/'status.json').read_bytes())['exit_code'],0)
        self.assertEqual(dumps(calls[0]),(scientific/'analysis.json').read_bytes())
        self.assertEqual(strict((out/'COMPLETE.json').read_bytes())['result_sha256'],digest((scientific/'analysis.json').read_bytes()))

    def test_INTR1_calibration_cli_preserves_fraction_result_with_exit_zero(self):
        from exp7integration import bootstrap
        from exp7stats.calibration import rate_summary
        from exp7stats.common import dumps,decode
        result={'state':'NO-DETECTED-CALIBRATION-DEFECT','rate':rate_summary(0,2,Fraction(1,200))}
        site=self.root/'site';site.write_bytes(canonical({'synthetic_only':True}))
        checks=[];entry=bootstrap.ENTRIES['calibration_7.py'];out=io.StringIO()
        bootstrap.ENTRIES['calibration_7.py']=lambda *a:result
        try:
            with replace(bootstrap,'load_bound',lambda *a:NS(check_sources=lambda:checks.append('exit'))),redirect_stdout(out):
                code=bootstrap.main('calibration_7.py',[],site,digest(site.read_bytes()))
        finally: bootstrap.ENTRIES['calibration_7.py']=entry
        self.assertEqual(code,0);self.assertEqual(checks,['exit'])
        self.assertEqual(out.getvalue().encode(),dumps(result))
        restored=decode(strict(out.getvalue()))
        self.assertIsInstance(restored['rate']['null_rate'],Fraction)
        self.assertEqual(restored['rate']['null_rate'],Fraction(1,200))
        self.assertEqual(restored['rate']['binomial_excess_p'],result['rate']['binomial_excess_p'])

    def test_INTR2_all_eight_installed_bootstraps_bind_native_namespace_metadata_only(self):
        from exp7integration import bootstrap
        repo=self.root/'repo';package=repo/'experiments/exp7';pins={}
        for name in ('exp7core','exp7stats','exp7ops','exp7integration','run'):
            p=package/name/'__init__.py';p.parent.mkdir(parents=True);p.write_bytes(b'# pinned fake package\n');pins[p.relative_to(repo).as_posix()]=digest(p.read_bytes())
        native=repo/'experiments/exp6/fake_leaf.py';native.parent.mkdir();native.write_bytes(b'raise AssertionError("native module must never execute")\n');pins[native.relative_to(repo).as_posix()]=digest(native.read_bytes())
        unknown=native.with_name('unbound.py');unknown.write_bytes(b'raise AssertionError("unbound module must never execute")\n')
        programs=[]
        for source in sorted((PACKAGE/'run').glob('*_7.py')):
            p=package/'run'/source.name;p.write_bytes(source.read_bytes());pins[p.relative_to(repo).as_posix()]=digest(p.read_bytes());programs.append(p)
        self.assertEqual(len(programs),8)
        config=repo/'deployment.json';config.write_bytes(canonical({'repo':str(repo),'source_pins':pins}))
        site=package/'run/site_7.json';site.write_bytes(canonical({'schema':'exp7.site-binding.v1','config_path':str(config),'config_sha256':digest(config.read_bytes()),'package_root':str(package)}))
        observed=[]
        def dispatch(program,*args):
            self.assertIn(str(repo),sys.path)
            spec=PathFinder.find_spec('experiments',sys.path)
            self.assertIn(str(repo/'experiments'),list(spec.submodule_search_locations))
            finder=next(x for x in sys.meta_path if type(x).__name__=='_BoundRepositoryImports')
            self.assertEqual(finder.find_spec('experiments.exp6.fake_leaf',[str(native.parent)]).origin,str(native))
            with self.assertRaisesRegex(ImportError,'unpinned repository executable'):
                finder.find_spec('experiments.exp6.unbound',[str(native.parent)])
            before=native.read_bytes();native.write_bytes(b'# source drift\n')
            try:
                with self.assertRaisesRegex(ImportError,'unpinned repository executable'):
                    finder.find_spec('experiments.exp6.fake_leaf',[str(native.parent)])
            finally:native.write_bytes(before)
            self.assertFalse(any(n=='experiments' or n.startswith('experiments.') for n in sys.modules))
            self.assertLess(next(i for i,x in enumerate(sys.meta_path) if isinstance(x,guard.Finder)),sys.meta_path.index(finder))
            observed.append(program);return 0
        for program in programs:
            with self.subTest(program=program.name):
                argv,path,meta=sys.argv,list(sys.path),list(sys.meta_path)
                try:
                    sys.argv=[str(program),'--site-sha256',digest(site.read_bytes())]
                    with replace(bootstrap,'main',dispatch),self.assertRaises(SystemExit) as exited:
                        runpy.run_path(str(program),run_name='__main__')
                    self.assertEqual(exited.exception.code,0)
                finally:sys.argv=argv;sys.path[:]=path;sys.meta_path[:]=meta
        self.assertEqual(set(observed),{p.name for p in programs})

    def test_INTR3_venv_symlink_is_execution_identity_recorder_and_hard_guard(self):
        from exp7integration.freeze import GuardedWorkerProcess,deterministic_twice
        python='/Users/michaeljordan/emergence-lab/.venv/bin/python'
        self.assertNotEqual(str(Path(python).resolve()),python)
        native=GuardedWorkerProcess(python,self.root)
        self.assertEqual(native.python,python)
        package=self.root/'package';package.mkdir();(package/'numerical_worker.py').write_bytes(b'# never executed\n')
        calls=[]
        class Recorder:
            def run(self,argv,**kwargs):
                calls.append(argv);Path(argv[argv.index('--output')+1]).write_bytes(b'{"fake":true}\n')
        deterministic_twice(Recorder(),python=python,package=package,fixture=self.root/'fake-export',fixture_sha256='a'*64,output=self.root/'recorder')
        self.assertEqual([a[0] for a in calls],[python,python])
        with self.assertRaisesRegex(ImportError,'HARD-REFUSED: subprocess'):
            native.run(calls[0],cwd=package,shell=False,timeout=86400)

    def test_INTR4_existing_root_omission_refuses_and_complete_archive_secures(self):
        from exp7integration.deployment import FixedStageDeployment,STAGE_MAP
        from exp7integration.remote_evidence import final_evidence,INVENTORY
        from exp7integration.security import IndependentSecuredReader
        from exp7ops.wire import decode
        repo=self.root/'repo';root=repo/'experiments/exp7/campaign';root.mkdir(parents=True)
        (root/'failure.txt').write_bytes(b'fake failed campaign bytes')
        pins={}
        for name in ('exp7core','exp7stats','exp7ops','exp7integration','run'):
            p=repo/f'experiments/exp7/{name}/__init__.py';p.parent.mkdir(parents=True);p.write_bytes(b'# pinned fake\n');pins[p.relative_to(repo).as_posix()]=digest(p.read_bytes())
        stages={stage:{'output':str(self.root/'supervisors'/stage)} for stage in STAGE_MAP}
        for name in ('outcome-preflight','outcome'):
            folder=Path(stages[name]['output']);folder.mkdir(parents=True);(folder/'operator.log').write_bytes(('fake '+name+' log').encode())
        data={'schema':'exp7.fixed-deployment.v1','repo':str(repo),'root':str(root),'source_pins':pins,'stages':stages,'remote':{'evidence_root':str(root),'supervisor_stages':['outcome']}}
        config=repo/'config.json';config.write_bytes(canonical(data))
        with self.assertRaisesRegex(Refusal,'existing bound supervisor omitted'):
            FixedStageDeployment(config,digest(config.read_bytes()))
        data['remote']['supervisor_stages'].append('outcome-preflight');config.write_bytes(canonical(data))
        deployment=FixedStageDeployment(config,digest(config.read_bytes()))
        terminal={'exit_code':1,'controller_live':False,'group_live':False,'kind':'error'}
        observed=decode('final-evidence',final_evidence(deployment,lambda:terminal))
        self.assertIn('supervisors/outcome-preflight/operator.log',observed['payload'])
        self.assertEqual(set(strict(observed['payload'][INVENTORY])['roots']),set(STAGE_MAP))
        security=self.root/'secured';(security/'local').mkdir(parents=True)
        for name,raw in observed['payload'].items():
            p=security/'remote'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        (security/'local/terminal-unit-failures.json').write_bytes(canonical([]))
        (security/'local/final-verification.json').write_bytes(canonical(deployment.verify_final(security/'remote',terminal)))
        reader=IndependentSecuredReader(deployment,None,None,NS(final_evidence=lambda:deepcopy(observed)),security,'a'*40)
        self.assertEqual(reader.required_inventory(terminal),snapshot(security))
        missing='supervisors/outcome-preflight/operator.log'
        del observed['files'][missing];del observed['payload'][missing]
        with self.assertRaisesRegex(Refusal,'incomplete bound supervisor archive bytes'):reader.required_inventory(terminal)
        del observed['files'][INVENTORY];del observed['payload'][INVENTORY]
        with self.assertRaisesRegex(Refusal,'missing complete remote supervisor inventory'):reader.required_inventory(terminal)
