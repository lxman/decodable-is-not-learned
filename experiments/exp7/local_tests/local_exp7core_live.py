# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Live(unittest.TestCase):

    def test_contract(self):
        import sys
        from types import ModuleType
        self.assertNotIn('importlib.metadata', sys.modules)
        metadata = ModuleType('importlib.metadata')
        metadata.version = lambda name: self.fail('native version measurement')
        sys.modules['importlib.metadata'] = metadata
        try:
            from exp7core.live import token_facts
        finally:
            del sys.modules['importlib.metadata']
        from exp7core.contract import Refusal

        class Tokenizer:
            all_special_ids = [99]
            bos_token_id = 99
            eos_token_id = 99
            pad_token_id = 99
            padding_side = 'left'

            def __call__(self, text):
                return {'input_ids': [1, 2]}
        self.assertFalse(token_facts(Tokenizer())['adds_bos'])

        class Wrong(Tokenizer):

            def __call__(self, text):
                return {'input_ids': [99, 1]}
        with self.assertRaises(Refusal):
            token_facts(Wrong())


# LIVE-TOKENIZER-1: manifest constants are independent expected data. Acquisition
# below returns conspicuously synthetic bytes, not the genuine pinned assets.
# No tokenizer library, Hub module, native backend or downloader is substituted
# into sys.modules; tests replace only the two application-level callables.
import ast
import hashlib
import json
from pathlib import Path

PYTHIA_FILES = {
    'config.json': '302d6702a29de1039066e41404877fb8c53b7ddc82e88f9aba277f230086cfe0',
    'tokenizer_config.json': '70e38394e494931c6f773ba41e19460dd4436526b852207367f04341b4066d3f',
    'special_tokens_map.json': '6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad',
    'tokenizer.json': 'c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624',
}
PYTHIA_COMMIT = 'f73d7dcc545c8bd326d8559c8ef84ffe92fea6b2'
EOS = '<|endoftext|>'
SYNTHETIC_BYTES = {name: ('SYNTHETIC LIVE-TOKENIZER-1 TEST BYTES: '+name+'\n').encode()
                   for name in PYTHIA_FILES}


def pythia_asset():
    return {'repo': 'EleutherAI/pythia-1b', 'commit': PYTHIA_COMMIT,
            'files': dict(PYTHIA_FILES), 'pad_id': 0}


class SyntheticTokenizer:
    def __init__(self, *, pad=0, eos=0, eos_text=EOS, plain=None):
        self.bos_token_id = eos
        self.eos_token_id = eos
        self.eos_token = eos_text
        self.pad_token_id = pad
        self.padding_side = 'right'
        self.all_special_ids = [0, 1, 0]
        self.plain = [7, 8] if plain is None else plain
        self.plain_calls = []
        self.pad_assignments = []
        self._pad_token = None

    @property
    def pad_token(self):
        return self._pad_token

    @pad_token.setter
    def pad_token(self, value):
        self.pad_assignments.append(value)
        self._pad_token = value
        self.pad_token_id = 128004 if value == '<|finetune_right_pad_id|>' else self.eos_token_id

    def __call__(self, text):
        self.plain_calls.append(text)
        return {'input_ids': self.plain}


class TokenOnlyTests(unittest.TestCase):
    def setUp(self):
        # Same inert stdlib metadata dependency as the retained original test.
        # Restore both module-table and parent-package state for standalone runs.
        import importlib
        import sys
        from types import ModuleType
        self.assertNotIn('importlib.metadata', sys.modules)
        missing = object()
        previous = vars(importlib).get('metadata', missing)
        metadata = ModuleType('importlib.metadata')
        metadata.version = lambda name: self.fail('native version measurement')
        sys.modules['importlib.metadata'] = metadata
        try:
            from exp7core import live
        finally:
            del sys.modules['importlib.metadata']
            if previous is missing:
                vars(importlib).pop('metadata', None)
            else:
                importlib.metadata = previous
        from exp7core.contract import Refusal
        self.live, self.Refusal = live, Refusal

    def replace(self, name, value):
        original = getattr(self.live, name)
        self.addCleanup(setattr, self.live, name, original)
        setattr(self.live, name, value)

    def no_effect(self, *args, **kwargs):
        self.fail('drifted Pythia reached acquisition or construction')

    def ports(self, factory):
        events = []

        def acquire(asset):
            events.append(('assets', asset))
            return dict(SYNTHETIC_BYTES)

        def construct(repo, *, revision, **kwargs):
            events.append(('constructor', repo, revision, dict(kwargs)))
            return factory(repo, revision, kwargs)

        self.replace('asset_bytes', acquire)
        self.replace('_tokenizer_from_pretrained', construct)
        return events

    def test_pythia_manifest_drift_refuses_before_acquisition(self):
        # RED-capable against the unchanged installed function: no new helper
        # is referenced, and failure is the observed forbidden acquisition call.
        asset = pythia_asset()
        asset['commit'] = 'a'*40
        self.replace('asset_bytes', self.no_effect)
        with self.assertRaisesRegex(self.Refusal, 'exact reviewed Pythia EOS-pad asset required'):
            self.live.token_only(asset)

    def test_pythia_constructor_override_wiring(self):
        # Honest source-wiring RED, not an attempted forbidden-library import.
        tree = ast.parse(Path(self.live.__file__).read_bytes())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'token_only')
        values = [keyword.value.value for node in ast.walk(function) if isinstance(node, ast.Call)
                  for keyword in node.keywords if keyword.arg == 'pad_token'
                  and isinstance(keyword.value, ast.Constant)]
        self.assertEqual(values, [EOS], 'Pythia construction requires its explicit EOS-pad keyword')

    def test_pythia_explicit_override_beats_default_pad_one_and_binds_receipt(self):
        asset = pythia_asset()
        raw = (json.dumps(asset, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                          allow_nan=False)+'\n').encode('ascii')
        self.assertEqual(len(raw), 454)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '316641e6c4f762dca571dd9079aeedf120423d084e2b57470ff643b98d3ccb27')

        def constructor(repo, revision, kwargs):
            # Models the relevant constructor default and keyword precedence.
            return SyntheticTokenizer(pad=0 if kwargs.get('pad_token') == EOS else 1)

        events = self.ports(constructor)
        tok, receipt = self.live.token_only(asset)
        self.assertEqual(events, [('assets', asset), ('constructor', asset['repo'], PYTHIA_COMMIT,
                                                     {'pad_token': EOS})])
        self.assertEqual(tok.pad_token_id, 0)
        self.assertIs(type(tok.pad_token_id), int)
        self.assertEqual(tok.pad_assignments, [])
        self.assertEqual(tok.plain_calls, ['Q:'])
        self.assertEqual(tok.padding_side, 'left')
        self.assertEqual(receipt, {
            'repo': asset['repo'], 'commit': PYTHIA_COMMIT,
            'files': {name: hashlib.sha256(raw).hexdigest() for name, raw in SYNTHETIC_BYTES.items()},
            'tokenizer': {'bos': 0, 'eos': 0, 'pad': 0, 'padding_side': 'left',
                          'special_ids': [0, 1], 'adds_bos': False, 'generation_eos': None},
        })
        self.assertNotEqual(receipt['files'], asset['files'], 'fake acquisition is explicitly synthetic')
        self.assertEqual(asset, pythia_asset())

    def test_pythia_full_asset_guard_refusals(self):
        self.replace('asset_bytes', self.no_effect)
        self.replace('_tokenizer_from_pretrained', self.no_effect)
        cases = []
        for value in (1, False, True, None, '0', 0.0):
            asset = pythia_asset()
            asset['pad_id'] = value
            cases.append(('pad '+repr(value), asset))
        for key in ('commit', 'files', 'pad_id'):
            asset = pythia_asset()
            del asset[key]
            cases.append(('missing '+key, asset))
        asset = pythia_asset()
        asset['extra'] = 'unexpected'
        cases.append(('extra asset field', asset))
        for name in PYTHIA_FILES:
            asset = pythia_asset()
            asset['files'][name] = 'a'*64
            cases.append(('changed '+name, asset))
            asset = pythia_asset()
            del asset['files'][name]
            cases.append(('missing '+name, asset))
        asset = pythia_asset()
        asset['files']['added_tokens.json'] = 'a'*64
        cases.append(('extra file', asset))
        for value in (None, list(PYTHIA_FILES.items())):
            asset = pythia_asset()
            asset['files'] = value
            cases.append(('file map type '+repr(value), asset))

        class DictSubclass(dict):
            pass

        cases.append(('asset dict subclass', DictSubclass(pythia_asset())))
        asset = pythia_asset()
        asset['files'] = DictSubclass(asset['files'])
        cases.append(('file map dict subclass', asset))
        for label, asset in cases:
            with self.subTest(case=label):
                with self.assertRaisesRegex(self.Refusal, 'exact reviewed Pythia EOS-pad asset required'):
                    self.live.token_only(asset)

    def test_pythia_returned_pad_refusals_without_fallback(self):
        for value in (1, None, False, True, '0', 0.0, -1, 'missing'):
            with self.subTest(pad=value):
                tok = SyntheticTokenizer(pad=value)
                if value == 'missing':
                    del tok.pad_token_id
                events = self.ports(lambda *args: tok)
                with self.assertRaises(self.Refusal):
                    self.live.token_only(pythia_asset())
                self.assertEqual(len(events), 2)
                self.assertEqual(events[1][3], {'pad_token': EOS})
                self.assertEqual(tok.pad_assignments, [])
                self.assertEqual(tok.plain_calls, [])

    def test_pythia_returned_eos_refusals(self):
        cases = [('eos_token', value) for value in ('wrong', None, 'missing')]
        cases += [('eos_token_id', value) for value in (1, None, False, True, '0', 0.0, 'missing')]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                tok = SyntheticTokenizer()
                if value == 'missing':
                    delattr(tok, field)
                else:
                    setattr(tok, field, value)
                events = self.ports(lambda *args: tok)
                with self.assertRaisesRegex(self.Refusal, 'Pythia EOS token/id mismatch'):
                    self.live.token_only(pythia_asset())
                self.assertEqual(len(events), 2)
                self.assertEqual(tok.pad_assignments, [])
                self.assertEqual(tok.plain_calls, [])

    def test_acquisition_failure_prevents_constructor(self):
        failure = RuntimeError('synthetic acquisition failure')
        events = []

        def acquire(asset):
            events.append('assets')
            raise failure

        self.replace('asset_bytes', acquire)
        self.replace('_tokenizer_from_pretrained', self.no_effect)
        with self.assertRaises(RuntimeError) as caught:
            self.live.token_only(pythia_asset())
        self.assertIs(caught.exception, failure)
        self.assertEqual(events, ['assets'])

    def test_constructor_failure_is_not_retried(self):
        failure = RuntimeError('synthetic constructor failure')

        def constructor(*args):
            raise failure

        events = self.ports(constructor)
        with self.assertRaises(RuntimeError) as caught:
            self.live.token_only(pythia_asset())
        self.assertIs(caught.exception, failure)
        self.assertEqual([row[0] for row in events], ['assets', 'constructor'])
        self.assertEqual(events[1][3], {'pad_token': EOS})

    def test_other_repository_padding_and_call_shapes(self):
        # Synthetic revisions/IDs test forwarding and fallback, not native facts.
        cases = (
            ('allenai/OLMo-2-0425-1B', 'b'*40, 100277, 100257, 100277, []),
            ('allenai/OLMo-2-0425-1B', 'c'*40, None, 100277, 100277, [EOS]),
            ('HuggingFaceTB/SmolLM3-3B-checkpoints', 'd'*40, 128004, 128001, 128004, []),
            ('HuggingFaceTB/SmolLM3-3B-checkpoints', 'e'*40, None, 128001, 128004,
             ['<|finetune_right_pad_id|>']),
        )
        for repo, revision, pad, eos, expected, assigned in cases:
            with self.subTest(repo=repo, revision=revision):
                asset = {'repo': repo, 'commit': revision, 'files': {}, 'pad_id': expected}
                tok = SyntheticTokenizer(pad=pad, eos=eos)
                events = self.ports(lambda *args: tok)
                actual, receipt = self.live.token_only(asset)
                self.assertIs(actual, tok)
                self.assertEqual(events, [('assets', asset), ('constructor', repo, revision, {})])
                self.assertEqual(tok.pad_token_id, expected)
                self.assertEqual(tok.pad_assignments, assigned)
                self.assertEqual(tok.padding_side, 'left')
                self.assertEqual(receipt['repo'], repo)
                self.assertEqual(receipt['commit'], revision)
                self.assertEqual(receipt['tokenizer']['pad'], expected)

    def test_other_repository_wrong_nonmissing_pad_refuses(self):
        for repo, pad in (('allenai/OLMo-2-0425-1B', 100277),
                          ('HuggingFaceTB/SmolLM3-3B-checkpoints', 128004)):
            with self.subTest(repo=repo):
                tok = SyntheticTokenizer(pad=1)
                events = self.ports(lambda *args: tok)
                with self.assertRaisesRegex(self.Refusal, 'token-only pad pin'):
                    self.live.token_only({'repo': repo, 'commit': 'b'*40, 'files': {}, 'pad_id': pad})
                self.assertEqual(len(events), 2)
                self.assertEqual(events[1][3], {})
                self.assertEqual(tok.pad_assignments, [])

    def test_plain_rendering_refuses_empty_or_leading_special(self):
        for plain in ([], [0, 7], [1, 7]):
            with self.subTest(plain=plain):
                tok = SyntheticTokenizer(plain=plain)
                events = self.ports(lambda *args: tok)
                with self.assertRaisesRegex(self.Refusal, 'unexpected BOS/chat rendering'):
                    self.live.token_only(pythia_asset())
                self.assertEqual(len(events), 2)
                self.assertEqual(tok.padding_side, 'left')
                self.assertEqual(tok.pad_assignments, [])
                self.assertEqual(tok.plain_calls, ['Q:'])

    def test_default_acquisition_is_guarded(self):
        import builtins
        import guard
        import sys
        old_import = builtins.__import__
        builtins.__import__ = guard.guarded_import
        try:
            start = len(guard.attempts)
            with self.assertRaisesRegex(ImportError, 'HARD-REFUSED: huggingface_hub'):
                self.live.token_only(pythia_asset())
            self.assertEqual(guard.attempts[start:], ['huggingface_hub'])
            self.assertFalse(any(guard.forbidden(name) for name in sys.modules))
        finally:
            builtins.__import__ = old_import

    def test_default_constructor_is_guarded_after_fake_acquisition(self):
        import builtins
        import guard
        import sys
        acquired = []

        def acquire(asset):
            acquired.append(asset)
            return dict(SYNTHETIC_BYTES)

        self.replace('asset_bytes', acquire)
        old_import = builtins.__import__
        builtins.__import__ = guard.guarded_import
        try:
            start = len(guard.attempts)
            asset = pythia_asset()
            with self.assertRaisesRegex(ImportError, 'HARD-REFUSED: transformers'):
                self.live.token_only(asset)
            self.assertEqual(acquired, [asset])
            self.assertEqual(guard.attempts[start:], ['transformers'])
            self.assertFalse(any(guard.forbidden(name) for name in sys.modules))
        finally:
            builtins.__import__ = old_import

    def test_default_wrapper_and_preflight_wiring_are_static(self):
        tree = ast.parse(Path(self.live.__file__).read_bytes())
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        expected = ast.parse('''def _tokenizer_from_pretrained(repo, *, revision, **kwargs):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(repo, revision=revision, **kwargs)
''').body[0]
        self.assertEqual(ast.dump(functions['_tokenizer_from_pretrained']), ast.dump(expected))
        body = functions['token_only']
        self.assertEqual([arg.arg for arg in body.args.args], ['asset'])
        self.assertEqual(body.args.kwonlyargs, [])
        self.assertIsNone(body.args.vararg)
        self.assertIsNone(body.args.kwarg)
        calls = [node for node in ast.walk(body) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        self.assertEqual(sum(node.func.id == 'asset_bytes' for node in calls), 1)
        self.assertEqual(sum(node.func.id == '_tokenizer_from_pretrained' for node in calls), 2)
        preflight = ast.parse(Path(self.live.__file__).with_name('preflight.py').read_bytes())
        build = next(node for node in preflight.body if isinstance(node, ast.FunctionDef)
                     and node.name == 'build_tokenizer_checks')
        branch = next(node for node in build.body if isinstance(node, ast.If)
                      and ast.unparse(node.test) == 'loader is LIVE')
        expected_branch = ast.parse('from .live import token_only\nloader = token_only').body
        self.assertEqual([ast.dump(node) for node in branch.body], [ast.dump(node) for node in expected_branch])
