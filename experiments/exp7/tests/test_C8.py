import guard  # FIRST: direct imports require guarded launcher
import unittest
from exp7core.contract import Refusal,ARMS
from exp7core.bridge import sample_pair,greedy_prompts
from fixtures import fixture_battery,load_fixture

class BridgeTests(unittest.TestCase):

    def setUp(self):
        self.pair = load_fixture(fixture_battery()).pairs[0]
        self.calls = []

    def loader(self, p, mode, device):
        self.calls.append((p, mode, device))
        return ('FAKE_TOKENIZER', 'FAKE_MODEL', {'digest': 'fixture'})

    def sampler(self, model, tok, prompt, **kw):
        self.assertEqual((model, tok), ('FAKE_MODEL', 'FAKE_TOKENIZER'))
        self.calls.append(kw)
        return {kw['seeds'][0]: ['alpha'] * kw['draws_per_seed']}

    def test_explicit_trained_and_twin_contract(self):
        for twin in (False, True):
            out = sample_pair(self.pair, 'pythia_1b', twin=twin, loader=self.loader, sampler=self.sampler, provenance=lambda x: None, terminal_ids=(0, 1))
            self.assertEqual(set(out), set(ARMS))
            self.assertTrue(all((len(v) == (16 if twin else 64) for v in out.values())))
        self.assertEqual(len({v['rung'] for v in self.calls if type(v) is dict}), 4)

    def test_empty_loader_and_sampler_never_fall_through(self):
        for loader, sampler in ((None, self.sampler), ({}, self.sampler), (self.loader, None), (self.loader, {}), (None, None)):
            with self.subTest(loader=loader, sampler=sampler), self.assertRaises(Refusal):
                sample_pair(self.pair, 'pythia_1b', loader=loader, sampler=sampler, provenance=lambda x: None, terminal_ids=(0,))
        self.assertEqual(self.calls, [])

    def test_shared_or_missing_seed_payload_refuses(self):
        with self.assertRaises(Refusal):
            sample_pair(self.pair, 'pythia_1b', loader=self.loader, sampler=lambda *a, **k: {0: ['a'] * 64}, provenance=lambda x: None, terminal_ids=(0,))

    def test_fake_greedy_and_empty_injections(self):

        class Runner:

            def generate(self, prompts, max_new_tokens):
                return ['a'] * len(prompts)
        out = greedy_prompts(('q0', 'q1'), loader=lambda: ('m', 't', {}), runner_factory=lambda t, m: Runner(), provenance=lambda x: None, cap=12)
        self.assertEqual(out, ('a', 'a'))
        with self.assertRaises(Refusal):
            greedy_prompts(('q0',), loader=None, runner_factory=None, provenance=lambda x: None, cap=12)

    def test_hard_import_guard_installed(self):
        for name in ('torch', 'transformers', 'mlx', 'huggingface_hub', 'tokenizers', 'socket', 'requests', 'urllib.request', 'experiments.exp3.sampler'):
            with self.subTest(module=name), self.assertRaises(ImportError):
                __import__(name)
        import importlib
        with self.assertRaisesRegex(ImportError, 'HARD-REFUSED'):
            importlib.import_module('huggingface_hub')
