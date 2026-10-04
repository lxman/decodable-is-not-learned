"""Review regressions on saved evidence; never generates another full batch."""
import copy
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.exp7.feasibility import compare as comparison
from experiments.exp7.feasibility.audit import audit
from experiments.exp7.feasibility.sources import HERE, Sources, digest


class ScheduleHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Sources()
        cls.pairs = [json.loads(line) for line in (HERE/'runs/full-003/pairs.jsonl').read_text().splitlines()]

    def test_shifted_all_slots_and_ids_are_refused(self):
        pairs = copy.deepcopy(self.pairs)
        for p in pairs:
            p['slot'] += 1000
            p['id'] = f'{p["family"]}-{p["slot"]:04d}'
        cert,_ = audit(pairs,self.source)
        self.assertFalse(cert['ok'])
        self.assertTrue(any('slot' in f['reason'] for f in cert['failures']))

    def test_swapped_render_schedule_is_refused(self):
        pairs = copy.deepcopy(self.pairs)
        a = pairs[0]
        b = next(p for p in pairs[1:] if p['family']==a['family'] and p['render_order']!=a['render_order'])
        a['render_order'],b['render_order'] = b['render_order'],a['render_order']
        cert,_ = audit(pairs,self.source)
        self.assertFalse(cert['ok'])
        self.assertTrue(any('seeded render' in f['reason'] for f in cert['failures']))

    def test_coherent_target_reorientation_is_refused(self):
        p = copy.deepcopy(self.pairs[0])
        p['orientation'] = 1-p['orientation']
        p['a0'],p['a1'] = p['a1'],p['a0']
        for a,b in (('q0','q1'),('q0s','q1s')):
            p['arms'][a],p['arms'][b] = p['arms'][b],p['arms'][a]
        k = p['content_keys']
        p['content_keys'] = [k[1],k[0],k[3],k[2]]
        cert,_ = audit([p],self.source,full=False)
        self.assertFalse(cert['ok'])
        self.assertTrue(any('seeded orientation' in f['reason'] for f in cert['failures']))

    def test_coherent_option_repositioning_is_refused(self):
        p = copy.deepcopy(next(p for p in self.pairs if p['family']=='units'))
        old = ', '.join(p['options'])
        p['options'] = p['options'][1:]+p['options'][:1]
        for arm,q in p['arms'].items():
            p['arms'][arm] = q.replace('\nOptions: '+old,'\nOptions: '+', '.join(p['options']))
        cert,_ = audit([p],self.source,full=False)
        self.assertFalse(cert['ok'])
        self.assertTrue(any('seeded option' in f['reason'] for f in cert['failures']))


class EvidenceHardeningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.here = Path(self.temp.name)
        (self.here/'runs').mkdir()

    def rewrite(self, folder, name, value, rehash=True):
        (folder/name).write_text(json.dumps(value,sort_keys=True)+'\n')
        if rehash and name not in ('artifacts.json','receipt-start.json','receipt-end.json'):
            manifest = json.loads((folder/'artifacts.json').read_text())
            manifest[name] = digest((folder/name).read_bytes())
            (folder/'artifacts.json').write_text(json.dumps(manifest))

    def copies(self):
        out = []
        for name in ('first','second'):
            folder = self.here/'runs'/name
            shutil.copytree(HERE/'runs/full-003',folder)
            receipt=json.loads((folder/'receipt-start.json').read_text())
            receipt['command'][-1]=name
            self.rewrite(folder,'receipt-start.json',receipt,False)
            out.append(folder)
        return out

    def must_refuse(self, reason):
        with patch.object(comparison,'HERE',self.here), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError,reason):
                comparison.compare('first','second','check.json')
        self.assertFalse((self.here/'runs/check.json').exists())

    def test_jointly_empty_evidence_refused(self):
        for name in ('first','second'):
            folder = self.here/'runs'/name
            folder.mkdir()
            self.rewrite(folder,'receipt-end.json',{'status':'PASS'},False)
            self.rewrite(folder,'artifacts.json',{},False)
        self.must_refuse('artifact inventory')

    def test_jointly_missing_artifact_refused_even_if_rehashed(self):
        for folder in self.copies():
            (folder/'oracles.jsonl').unlink()
            manifest=json.loads((folder/'artifacts.json').read_text())
            del manifest['oracles.jsonl']
            self.rewrite(folder,'artifacts.json',manifest,False)
        self.must_refuse('artifact inventory')

    def test_forged_launch_head_refused(self):
        for folder in self.copies():
            receipt=json.loads((folder/'receipt-start.json').read_text())
            receipt['head']='0'*40
            self.rewrite(folder,'receipt-start.json',receipt,False)
        self.must_refuse('launch HEAD')

    def test_self_consistent_forged_launch_pins_refused(self):
        for folder in self.copies():
            pins=json.loads((folder/'launch-pins.json').read_text())
            pins['audit.py']='0'*64
            cert=json.loads((folder/'certificate.json').read_text())
            cert['code_and_spec_pins']=pins
            self.rewrite(folder,'launch-pins.json',pins)
            self.rewrite(folder,'certificate.json',cert)
        self.must_refuse('launch pins')

    def test_certificate_source_pin_or_field_omission_refused(self):
        for folder in self.copies():
            cert=json.loads((folder/'certificate.json').read_text())
            cert['source_pins'].pop(next(iter(cert['source_pins'])))
            self.rewrite(folder,'certificate.json',cert)
        self.must_refuse('certificate source pins')

    def test_false_certificate_pass_refused(self):
        for folder in self.copies():
            cert=json.loads((folder/'certificate.json').read_text())
            cert['ok']=False
            self.rewrite(folder,'certificate.json',cert)
        self.must_refuse('certificate is not a clean PASS')

    def test_source_inventory_metadata_fields_are_exact(self):
        self.copies()
        source=Sources()
        source.inventory['computations']='substituted narrative with identical source pins'
        with patch.object(comparison,'Sources',return_value=source):
            self.must_refuse('exact source inventory fields')

    def test_extra_certificate_field_is_refused(self):
        for folder in self.copies():
            cert=json.loads((folder/'certificate.json').read_text())
            cert['unverified_extra_field']=True
            self.rewrite(folder,'certificate.json',cert)
        self.must_refuse('certificate fields differ')

    def test_jointly_empty_baseline_outputs_refused(self):
        for folder in self.copies():
            (folder/'baseline-outputs.jsonl').write_text('')
            manifest=json.loads((folder/'artifacts.json').read_text())
            manifest['baseline-outputs.jsonl']=digest(b'')
            self.rewrite(folder,'artifacts.json',manifest,False)
        self.must_refuse('saved baseline output coverage')

    def test_historical_pins_survive_current_verifier_changes(self):
        self.copies()
        historical=json.loads((HERE/'runs/full-003/launch-pins.json').read_text())
        self.assertNotEqual(historical['audit.py'],digest((HERE/'audit.py').read_bytes()))
        with patch.object(comparison,'HERE',self.here), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(comparison.compare('first','second','check.json'),0)
        result=json.loads((self.here/'runs/check.json').read_text())
        self.assertTrue(result['ok'])
        self.assertFalse(result['full_generation_performed'])
        for row in result['verified_archives'].values():
            self.assertEqual(row['historical_launch_pins'],12)
            self.assertEqual(row['source_git_blobs'],103)
            self.assertEqual(row['exact_seeded_option_assignments'],1500)
            self.assertEqual(row['oracle_arms'],8000)


if __name__=='__main__':
    unittest.main()
