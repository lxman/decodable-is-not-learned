"""COL-1/COL-2 regressions. Run only under the before-import hard-guard launchers.

All model outputs, Git objects and power hooks are explicitly synthetic.
Mutations happen BETWEEN Campaign invocations, before enrolling a seal.
"""
from pathlib import Path
import copy
import os
import shutil
import tempfile
import unittest
from fractions import Fraction
from exp7core.contract import ARMS,Refusal,canonical,digest
from exp7core.collectors import (collect_anchors,collect_predictor,persist_receipt,
                                 seal_predictors,verify_preflight)
from exp7core.guardio import write_once
from exp7core.provenance import Trace
from exp7core.records import strict_json,build_record
from exp7core.scoring import score_draws
from collection_fixtures import fixture,Fixture,FakeBackend,FakeSession,write_preflight_fixture

from testing_paths import WORK
WORK.mkdir(exist_ok=True)
NAME = 'units/predictor/pythia_1b/unscrambling/q0'
PREFLIGHT = 'preflight/pythia_1b/unscrambling/q0.jsonl'


class PreflightPrimaryRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=WORK)
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name)/'base'
        cls.base.mkdir()
        f = fixture(cls.base,with_caps=True)
        # The same complete 48-unit producer shape as the independent review.
        with f.campaign() as c:
            for model in ('pythia_1b','olmo2_1b','twin'):
                s = FakeSession(c,c.trust.data['sample_loads'][model])
                persist_receipt(c,s.load,s.receipt)
                if model != 'twin':
                    collect_anchors(c,model,s)
                write_preflight_fixture(c,model,s)
                collect_predictor(c,model,backend=FakeBackend(c))
            cls.expected = c.expected(NAME)
            cls.raw,_ = c.raw_unit(NAME)
            cls.seal = c.seal_payload()
            assert cls.seal['new_units'] == 48 and cls.seal['new_draws'] == 1152000
            cls.first = {a:strict_json(c.raw_unit(NAME.rsplit('/',1)[0]+'/'+a)[0].splitlines()[0])['draws']
                         for a in ARMS}
            cls.pair = c.battery().family('unscrambling')[0]
        cls.battery,cls.data = f.battery,copy.deepcopy(f.data)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)/'repo'
        shutil.copytree(self.base,self.repo)
        self.f = Fixture(self.repo,self.repo/'campaign',self.battery,copy.deepcopy(self.data))

    def _change(self,kind):
        before_pins = canonical(self.f.data)
        preflight = (self.f.root/PREFLIGHT).read_bytes()
        rows = [strict_json(r) for r in self.raw.splitlines()]
        self.assertEqual(len(rows),500)
        for row in rows:
            self.assertEqual(len(row['draws']),64)
            row['draws'] = [' '+v for v in row['draws']] if kind == 'same-normalization' else ['blue']*64
        changed = b''.join(canonical(r) for r in rows)
        record = canonical(build_record(changed,self.expected))
        unit = self.f.root/NAME
        for filename,raw in [('raw.jsonl',changed),('record.json',record),('DONE.json',canonical({
                'raw.jsonl':digest(changed),'record.json':digest(record)}))]:
            (unit/filename).write_bytes(raw)
        self.assertNotEqual(changed,preflight)
        self.assertEqual((self.f.root/PREFLIGHT).read_bytes(),preflight)
        self.assertEqual(canonical(self.f.data),before_pins)
        before = score_draws(self.first,self.pair.targets,self.pair.answer_type,k=64)
        after = score_draws({**self.first,'q0':rows[0]['draws']},self.pair.targets,self.pair.answer_type,k=64)
        self.assertEqual(before.x,Fraction(1,2))
        if kind == 'same-normalization':
            self.assertEqual(after,before)
        else:
            self.assertEqual(after.x,Fraction(1,8))

    def _refuse_all_routes(self,kind):
        self._change(kind)
        for route in ('preflight','resume','seal-payload','seal-producer'):
            with self.subTest(mutation=kind,route=route):
                # Every route starts a genuinely new trace, so old pin snapshots
                # cannot supply the missing semantic relation by accident.
                with self.f.campaign() as c:
                    backend = FakeBackend(c)
                    with self.assertRaisesRegex(Refusal,'collected stream differs from preflight complete q0 unit'):
                        if route == 'preflight':
                            verify_preflight(c,'pythia_1b')
                        elif route == 'resume':
                            collect_predictor(c,'pythia_1b',backend=backend)
                        elif route == 'seal-payload':
                            c.seal_payload()
                        else:
                            seal_predictors(c)
                    self.assertEqual(backend.opened,[])
        # Independent fake authority pins ALL actual mutated bytes, exactly as a
        # coherent pre-existing v1 seal could. No hash mismatch should mask COL-1.
        seal = copy.deepcopy(self.seal)
        for filename in ('raw.jsonl','record.json','DONE.json'):
            path = NAME+'/'+filename
            seal['bindings'][path] = digest((self.f.root/path).read_bytes())
        (self.f.root/'predictor-seal.json').write_bytes(canonical(seal))
        self.f.refresh_seal()
        with self.subTest(mutation=kind,route='sealed-consumer'):
            with self.f.campaign() as c:
                with self.assertRaisesRegex(Refusal,'collected stream differs from preflight complete q0 unit'):
                    c.verify_predictor_seal()

    def test_same_normalization_raw_change_refuses_every_route_in_fresh_context(self):
        self._refuse_all_routes('same-normalization')

    def test_score_changing_raw_change_refuses_every_route_in_fresh_context(self):
        self._refuse_all_routes('score-changing')

    def test_precollection_preflight_valid_without_any_primary_family(self):
        shutil.rmtree(self.f.root/'units/predictor/pythia_1b')
        with self.f.campaign() as c:
            value = verify_preflight(c,'pythia_1b')
            self.assertEqual(value['model'],'pythia_1b')

    def test_partial_q0_only_family_is_torn_not_precollection(self):
        for arm in ARMS[1:]:
            shutil.rmtree(self.f.root/NAME.rsplit('/',1)[0]/arm)
        with self.f.campaign() as c:
            with self.assertRaisesRegex(Refusal,'torn four-arm family publication'):
                verify_preflight(c,'pythia_1b')

    def test_q0_directory_without_done_is_not_complete(self):
        (self.f.root/NAME/'DONE.json').unlink()
        with self.f.campaign() as c:
            with self.assertRaisesRegex(Refusal,'torn/extra unit files'):
                verify_preflight(c,'pythia_1b')

    def test_exact_completed_preflight_and_resume_accept_without_sampling(self):
        with self.f.campaign() as c:
            verify_preflight(c,'pythia_1b')
            backend = FakeBackend(c)
            collect_predictor(c,'pythia_1b',backend=backend)
            self.assertEqual(sum(len(s.calls) for s in backend.opened),0)
            self.assertEqual(c.seal_payload(),self.seal)


class ReadWriteTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.root = self.repo/'campaign'
        self.root.mkdir()
        self.pinned = self.repo/'pinned.txt'
        self.pinned.write_bytes(b'pinned bytes')
        self.unknown = self.repo/'unknown.txt'
        self.unknown.write_bytes(b'unpinned input')

    def trace(self):
        return Trace(self.repo,self.root,{'pinned.txt':digest(b'pinned bytes')})

    def readwrite(self,path,mode):
        if isinstance(mode,str):
            with path.open(mode) as handle:
                return handle.read()
        fd = os.open(path,mode)
        try:
            return os.read(fd,100)
        finally:
            os.close(fd)

    def test_unpinned_readwrite_modes_and_os_flags_refuse_at_open(self):
        modes = ('r+','r+b','a+','w+',os.O_RDWR,os.O_RDWR|os.O_APPEND,
                 os.O_RDWR|os.O_CREAT,os.O_RDWR|os.O_TRUNC)
        trace = self.trace()
        trace.start()
        try:
            with self.assertRaisesRegex(Refusal,'unregistered read'):
                self.unknown.read_bytes()
            for mode in modes:
                with self.subTest(mode=mode):
                    with self.assertRaisesRegex(Refusal,'unregistered read'):
                        self.readwrite(self.unknown,mode)
        finally:
            trace.stop()
        self.assertEqual(self.unknown.read_bytes(),b'unpinned input')

    def test_pinned_readwrite_read_is_traced_and_passes_unchanged(self):
        for mode in ('r+','r+b',os.O_RDWR,os.O_RDWR|os.O_APPEND,os.O_RDWR|os.O_CREAT):
            with self.subTest(mode=mode):
                trace = self.trace()
                trace.start()
                try:
                    value = self.readwrite(self.pinned,mode)
                    self.assertIn(value,('pinned bytes',b'pinned bytes'))
                    self.assertIn(str(self.pinned),trace.reads)
                finally:
                    trace.stop()

    def test_pinned_readwrite_change_refuses_at_exit(self):
        for mode in ('r+','r+b',os.O_RDWR):
            with self.subTest(mode=mode):
                self.pinned.write_bytes(b'pinned bytes')
                trace = self.trace()
                trace.start()
                try:
                    if isinstance(mode,str):
                        with self.pinned.open(mode) as handle:
                            handle.read()
                            handle.seek(0)
                            handle.write(b'CHANGED' if 'b' in mode else 'CHANGED')
                    else:
                        fd = os.open(self.pinned,mode)
                        try:
                            os.read(fd,100)
                            os.lseek(fd,0,os.SEEK_SET)
                            os.write(fd,b'CHANGED')
                        finally:
                            os.close(fd)
                finally:
                    with self.assertRaisesRegex(Refusal,'read/import byte drift'):
                        trace.stop()

    def test_writeonly_exclusive_publication_append_and_directory_fsync_still_pass(self):
        trace = self.trace()
        trace.start()
        try:
            write_once(self.root/'exclusive.json',b'one')
            fd = os.open(self.root/'writeonly.bin',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            try:
                os.write(fd,b'two')
                os.fsync(fd)
            finally:
                os.close(fd)
            with (self.root/'writeonly.bin').open('ab') as handle:
                handle.write(b'three')
            fd = os.open(self.root,os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            self.assertEqual(trace.reads,set())
        finally:
            trace.stop()
        self.assertEqual((self.root/'exclusive.json').read_bytes(),b'one')
        self.assertEqual((self.root/'writeonly.bin').read_bytes(),b'twothree')
