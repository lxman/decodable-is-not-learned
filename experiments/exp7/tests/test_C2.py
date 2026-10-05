import guard  # FIRST: direct imports require guarded launcher
import copy,random,unittest
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
from exp7core.contract import ARMS,Refusal
from exp7core.scoring import normalize,answer,Table,Score,score_draws,outcome_counts
from fixtures import fixture_battery,load_fixture

class ContractTests(unittest.TestCase):

    def test_immutable_adapter(self):
        b = load_fixture(fixture_battery())
        self.assertEqual(len(b.pairs), 8)
        self.assertEqual(len(b.family('units')), 2)
        with self.assertRaises(FrozenInstanceError):
            b.pairs[0].index = 8

    def test_unset_pins_refuse(self):
        for p in ('', '0' * 64, 'x' * 64):
            with self.subTest(pin=p), self.assertRaises(Refusal):
                load_fixture(fixture_battery(), pin_override=p)

    def test_schema_and_coverage_refusals(self):
        for mutate in (lambda o: o['pairs'].pop(), lambda o: o['pairs'][0]['questions'].pop('q0s'), lambda o: o['pairs'][0].update(index=True), lambda o: o['pairs'][0].update(targets=['a', 'A!']), lambda o: o['pairs'][1].update(source_ids=['source-0']), lambda o: o['pairs'][0].update(targets=['two words', 'beta']), lambda o: o['pairs'][0].update(pass_field=True)):
            o = fixture_battery()
            mutate(o)
            with self.subTest(mutation=mutate), self.assertRaises((Refusal, ValueError)):
                load_fixture(o)

class ScoreTests(unittest.TestCase):

    def test_total_normalizer_and_criterion(self):
        cases = ['', '\t\r', '\n', '.!?', '  ALPHA\nwrong', '\x00', '💡', None, 7, {}]
        for s in cases:
            for kind in ('word', 'number', 'span'):
                self.assertIn(type(normalize(s, kind)), (str, type(None)))
        self.assertEqual(normalize('Answer is -1,200.', 'number'), '-1200')
        self.assertEqual(normalize(' TWO   WORDS.\nnext', 'span'), 'two words')
        with self.assertRaises(Refusal):
            answer('1.5', 'number')
        with self.assertRaises(Refusal):
            answer('\t', 'word')

    def test_fixed_odds_counterexample(self):
        t = Table(18, 2, 9, 1, 100)
        s = Score(t, t)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.d, F(1, 25))
        self.assertEqual(s.rate, (s.u + s.d) / 2)

    def test_render_average_not_pool(self):
        a = Table(9, 1, 1, 9, 100)
        b = Table(1, 99, 0, 1, 100)
        self.assertEqual(Score(a, b).x, F(81, 200))
        pooled = F(10, 110) - F(1, 11)
        self.assertEqual(pooled, 0)
        self.assertNotEqual(Score(a, b).x, pooled)

    def test_unsupported_is_zero_not_dropped(self):
        a, b = (Table(0, 0, 0, 8, 8), Table(8, 0, 0, 8, 8))
        s = Score(a, b)
        self.assertEqual(s.x, F(1, 2))
        self.assertEqual(s.unsupported, 1)
        self.assertEqual(s.row_totals, (0, 8, 8, 8))

    def test_exact_identity_and_label_reversal(self):
        rng = random.Random(7)
        for _ in range(200):
            ts = []
            for _ in range(2):
                m, n = (rng.randrange(65), rng.randrange(65))
                a, b = (rng.randrange(m + 1), rng.randrange(n + 1))
                ts.append(Table(a, m - a, b, n - b, 64))
            s = Score(*ts)
            r = s.reversed_labels()
            self.assertEqual(r.x, -s.x)
            self.assertEqual(r.d, -s.d)
            self.assertEqual(r.u, s.u)
            self.assertEqual(s.rate, (s.u + s.d) / 2)

    def test_draw_scoring_preserves_raw_and_is_disjoint(self):
        rows = {'q0': ['alpha', 'alpha', 'beta', 'other'], 'q1': ['beta'] * 4, 'q0s': ['other'] * 4, 'q1s': ['beta'] * 4}
        before = copy.deepcopy(rows)
        s = score_draws(rows, ('alpha', 'beta'), 'word', k=4)
        r = score_draws(rows, ('beta', 'alpha'), 'word', k=4)
        self.assertEqual(rows, before)
        self.assertEqual(s.x, F(1, 3))
        self.assertEqual(r.x, -s.x)
        self.assertEqual(r.d, -s.d)
        self.assertEqual(r.u, s.u)
        rows['q0'].pop()
        with self.assertRaises(Refusal):
            score_draws(rows, ('alpha', 'beta'), 'word', k=4)

    def test_outcome_joint_first_and_later_losses(self):
        right = dict(zip(ARMS, ('a', 'b', 'a', 'b')))
        wrong = dict.fromkeys(ARMS, 'a')
        rows = {1: right, 2: wrong, 3: right}
        r = outcome_counts(rows, ('a', 'b'), 'word', steps=(1, 2, 3))
        self.assertEqual(r['y'], 2)
        self.assertEqual(r['first_order_score'], 3)
        self.assertEqual(r['later_losses'], 1)
        with self.assertRaises(Refusal):
            outcome_counts(rows, ('a', 'b'), 'word', steps=(1, 2, 3, 4))
