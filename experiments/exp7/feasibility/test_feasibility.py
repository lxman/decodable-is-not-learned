"""Known answers and adversarial fixtures; no predecessor/model imports."""
import copy
import unittest
import random
import tempfile
from pathlib import Path

from experiments.exp7.feasibility.oracle import solve, geometry, parse_path
from experiments.exp7.feasibility.audit import audit
from experiments.exp7.feasibility.generate import generate
from experiments.exp7.feasibility.sources import Sources, geometry_key
from experiments.exp7.feasibility.baselines import predict, reading, report
from experiments.exp7.feasibility.generate import unit_question, deduction_question, shape_question
from experiments.exp7.feasibility.run import dump


class OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = Sources()

    def test_words_known_and_ambiguous(self):
        self.assertEqual(solve('words', 'Unscramble these letters into one English word: ecnics e.', self.src)['ok'], False)
        self.assertFalse(solve('words', 'Unscramble these letters into one English word: stop.', self.src)['ok'])

    def test_geometry_partition(self):
        self.assertEqual(geometry([(0, 0), (2, 0), (2, 2), (0, 2)]), 'square')
        self.assertEqual(geometry([(0, 0), (3, 0), (3, 2), (0, 2)]), 'rectangle')
        self.assertEqual(geometry([(0, 0), (3, 1), (4, 4), (1, 3)]), 'rhombus')
        self.assertEqual(geometry([(0, 3), (2, 0), (0, -4), (-2, 0)]), 'kite')
        self.assertEqual(geometry([(0, 0), (4, 0), (3, 2), (1, 2)]), 'trapezoid')
        for pts in [[(0,0),(2,2),(0,2),(2,0)], [(0,0),(1,0),(2,0),(0,1)],
                    [(0,0),(2,0),(2,0),(0,2)], [(0,0),(2,0),(1,1),(0,3)]]:
            with self.assertRaises(ValueError):
                geometry(pts)

    def test_closed_path_and_invariant(self):
        p = parse_path('M 0,0 L 2,0 L 2,2 L 0,2 L 0,0')
        self.assertEqual(geometry_key(p), geometry_key([(8,9),(8,11),(6,11),(6,9)]))
        with self.assertRaises(ValueError):
            parse_path('M 0,0 L 2,0 L 2,2 L 0,2')

    def test_oracle_totality(self):
        for fam in ('words', 'deduction', 'units', 'shapes', 'unknown'):
            for q in (None, 0, [], {}, '', '\x00', 'Options: 1, 1'):
                self.assertFalse(solve(fam, q, self.src)['ok'])

    def test_units_known_roles_and_exactness(self):
        opts = ['50','18','30','15','8']
        q = unit_question(3,5,30,opts)
        self.assertEqual(solve('units',q,self.src)['answer'],'50')
        self.assertEqual(solve('units',unit_question(5,3,30,opts,True),self.src)['answer'],'18')
        for bad in (q.replace('makes 3','makes 0'),q.replace('50, 18','50, 50'),
                    q.replace('50, 18','51, 18'),q.replace('30 parts.','31 parts.')):
            self.assertFalse(solve('units',bad,self.src)['ok'])

    def test_deduction_exhaustive_known(self):
        names = ['red','green','blue','white','black']
        lines = [f'The {a} book is before the {b} book.' for a,b in zip(names,names[1:])]
        for ask,expected in [('leftmost','red'),('rightmost','black')]:
            f = solve('deduction',deduction_question(names,lines,ask,list(reversed(names))),self.src)
            self.assertTrue(f['ok'])
            self.assertEqual(f['answer'],expected)
            self.assertEqual(f['exhaustive_orders'],120)
        for badlines in (lines[:-1],lines+['The black book is before the red book.'],
                         lines+['The red book is leftmost.']):
            self.assertFalse(solve('deduction',deduction_question(names,badlines,'leftmost',names),self.src)['ok'])

    def test_shape_convention_and_options(self):
        q = shape_question([[0,0],[2,0],[2,2],[0,2]],['square','rectangle','rhombus','kite','trapezoid'])
        self.assertEqual(solve('shapes',q,self.src)['answer'],'square')
        self.assertFalse(solve('shapes',q.replace('square, rectangle','circle, rectangle'),self.src)['ok'])
        self.assertFalse(solve('shapes',q.replace('first applicable','any applicable'),self.src)['ok'])

    def test_fuzz_refusals_are_total(self):
        rng = random.Random(17)
        for _ in range(200):
            q = ''.join(rng.choice('012abc<>?.,\n MLOptions:-') for _ in range(rng.randrange(100)))
            for family in ('words','deduction','units','shapes'):
                self.assertFalse(solve(family,q,self.src)['ok'])


class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = Sources()
        cls.pairs,cls.attempts = generate(cls.src,per_family=12)

    def test_miniature_all_oracles(self):
        cert,parsed = audit(self.pairs,self.src,full=False)
        self.assertTrue(cert['ok'],cert['failures'])
        self.assertEqual(cert['oracle_questions'],192)

    def test_miniature_byte_determinism(self):
        self.assertEqual((self.pairs,self.attempts),generate(self.src,per_family=12))

    def test_label_reversal_refused(self):
        p = copy.deepcopy(self.pairs[0])
        p['a0'],p['a1'] = p['a1'],p['a0']
        cert,_ = audit([p],self.src,full=False)
        self.assertIn('oracle/label',cert['failures'][0]['reason'])

    def test_different_options_refused(self):
        p = copy.deepcopy(next(p for p in self.pairs if p['family']=='units'))
        text = p['arms']['q1']
        before,opts = text.split('\nOptions: ')
        p['arms']['q1'] = before+'\nOptions: '+', '.join(reversed(opts.split(', ')))
        cert,_ = audit([p],self.src,full=False)
        self.assertIn('option order',cert['failures'][0]['reason'])

    def test_wrong_sham_same_geometry_class(self):
        p = copy.deepcopy(next(p for p in self.pairs if p['family']=='shapes'))
        j = 0 if p['a0']=='square' else 1
        arm = 'q0s' if j==0 else 'q1s'
        pts = [[0,0],[3,0],[3,3],[0,3]]
        p['arms'][arm] = shape_question(pts,p['options'])
        p['content_keys'][2+j] = geometry_key(pts)
        cert,_ = audit([p],self.src,full=False)
        self.assertIn('sham not translation',cert['failures'][0]['reason'])

    def test_duplicate_content_despite_different_text(self):
        p = copy.deepcopy(next(p for p in self.pairs if p['family']=='shapes'))
        other = copy.deepcopy(p)
        other['id']='shapes-0099'
        other['slot']=99
        # A translation produces different prompt bytes but identical structural keys.
        import re
        for arm in other['arms']:
            other['arms'][arm] = re.sub(r'(-?\d+),(-?\d+)',lambda m:f'{int(m[1])+100},{int(m[2])+100}',other['arms'][arm])
        cert,_ = audit([p,other],self.src,full=False)
        self.assertTrue(any('duplicate content' in x['reason'] for x in cert['failures']))

    def test_duplicate_word_even_new_scramble(self):
        p = copy.deepcopy(self.pairs[0])
        other = copy.deepcopy(p)
        other['id']='words-0099'
        other['slot']=99
        import itertools
        from experiments.exp7.feasibility.sources import content
        used = {solve('words',q,self.src)['scrambled'] for q in p['arms'].values()}
        for arm,answer in zip(('q0','q1','q0s','q1s'),(p['a0'],p['a1'],p['a0'],p['a1'])):
            s = next(''.join(chars) for chars in itertools.permutations(answer) if ''.join(chars) not in used|{answer}|self.src.old['words'])
            used.add(s)
            other['arms'][arm]=f'Unscramble these letters into one English word: {s}.'
        other['content_keys']=[content('words',solve('words',other['arms'][a],self.src)) for a in ('q0','q1','q0s','q1s')]
        cert,_ = audit([p,other],self.src,full=False)
        self.assertTrue(any('word reused' in x['reason'] for x in cert['failures']))

    def test_singleton_base_blocks_refused(self):
        cert,_ = audit(self.pairs,self.src,full=True)
        self.assertFalse(cert['ok'])
        self.assertTrue(any(f['reason']=='base-block support/coverage' for f in cert['failures']))

    def test_old_content_gate_not_template_gate(self):
        p = next(p for p in self.pairs if p['family']=='units')
        fs = [solve('units',q,self.src) for q in p['arms'].values()]
        key = p['content_keys'][0]
        self.src.old['units'].add(key)
        try:
            self.assertEqual(self.src.collision('units',list(p['arms'].values()),fs,[]),'old_content')
        finally:
            self.src.old['units'].remove(key)

    def test_baseline_no_default_wrong_for_na(self):
        rows,_ = report(self.pairs,self.src)
        for row in rows:
            if not row['applicable']:
                self.assertIsNone(row['mean_x'])
                self.assertIsNone(row['paired_success_canonical'])
                self.assertEqual(row['prompts'],0)
        endpoint = next(r for r in rows if r['family']=='deduction' and r['method']=='endpoint')
        self.assertEqual(endpoint['paired_success_canonical'],12)

    def test_baseline_reversal_and_unsupported_rows(self):
        r = reading(['a','b','a',None],'a','b')
        rr = reading(['a','b','a',None],'b','a')
        self.assertEqual(r['x'],.5)
        self.assertEqual(r['unsupported_rows'],1)
        self.assertEqual(r['supported_renders'],1)
        self.assertEqual(rr['x'],-r['x'])
        self.assertEqual(rr['d'],-r['d'])
        self.assertEqual(rr['u'],r['u'])

    def test_write_once(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'record.json'
            dump(p,{'x':1})
            with self.assertRaises(FileExistsError):
                dump(p,{'x':2})


if __name__ == '__main__':
    unittest.main()
