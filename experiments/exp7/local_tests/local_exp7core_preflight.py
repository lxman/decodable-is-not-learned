# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from types import SimpleNamespace as NS

class Preflight(unittest.TestCase):

    def test_contract(self):
        from exp7core.preflight import validate_caps
        from exp7core.contract import Refusal

        class Tokenizer:
            all_special_ids = [99]

            def encode(self, text, **kwargs):
                return [2] if text == ' alpha' else [3] if text == ' beta' else [1]

            def decode(self, tokens, **kwargs):
                return {2: 'alpha', 3: 'beta'}[tokens[0]]
        rows = tuple((NS(pair_id=str(i), prompts=('a', 'b', 'c', 'd'), targets=('alpha', 'beta'), answer_type='word') for i in range(2000)))
        result = validate_caps(NS(pairs=rows, bytes_sha256='a' * 64), Tokenizer())
        self.assertEqual(result['comparisons'], 16000)
        bad = Tokenizer()
        bad.decode = lambda *a, **k: 'wrong'
        with self.assertRaises(Refusal):
            validate_caps(NS(pairs=rows, bytes_sha256='a' * 64), bad)


# PROVENANCE-1: data captured by this task's capture_git.py from two genuine
# local commits. Synthetic authority only. Embedded so no later fixture or task
# evidence import/read is needed. Only Git.call is replaced; Git.blob is exact.
import json
from pathlib import Path
import tempfile
from exp7core.contract import Refusal, canonical, digest
from exp7core.provenance import Git
from testing_paths import WORK

CAPTURED = json.loads(r'''{
  "commits": {
    "before": "0e5eb69fce81c381679786e11060ff5daaacf991",
    "grant": "7a8e0326e34323ee20ad18c5518358a1e6273503"
  },
  "owner_evidence": "SYNTHETIC FIXTURE ONLY: authorize tiny fake tokenizer check; not a real owner grant.\n",
  "asset": {
    "repo": "synthetic/tokenizer",
    "commit": "cccccccccccccccccccccccccccccccccccccccc",
    "files": {"config.json": "836a905e5051a33569371d61474a807435e3888a0df301cdca53f07e6b21d18e"}
  },
  "names": ["pythia_1b", "olmo2_1b", "outcome/40000", "outcome/80000", "outcome/120000", "outcome/160000", "outcome/200000", "outcome/240000", "outcome/280000", "outcome/320000", "outcome/360000", "outcome/400000", "outcome/600000", "outcome/800000", "outcome/1000000", "outcome/1200000", "outcome/1400000", "outcome/1600000", "outcome/1800000", "outcome/2000000", "outcome/2200000", "outcome/2400000", "outcome/2600000", "outcome/2800000", "outcome/3000000", "outcome/3200000", "outcome/3400000", "outcome/3440000"],
  "battery_sha256": "0698612e2f80d1a4fe61d6d73037dc5c637a6d2ca6a5257e396b79ec544b5710",
  "captures": [
    {"args": ["show", "7a8e0326e34323ee20ad18c5518358a1e6273503:grant.json"], "returncode": 0, "stdout": "{\"assets_sha256\":\"5eb9f7678a92c17c2a46581240e4a77d54b226c43a71ae640b296d588a2efc04\",\"battery_sha256\":\"0698612e2f80d1a4fe61d6d73037dc5c637a6d2ca6a5257e396b79ec544b5710\",\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"8233a0daf9ba47a0fd681b61d6ccbae06424db2177a8ab585e5f49a6f3e58272\",\"owner\":\"Michael Jordan\",\"quote\":\"authorize tiny fake tokenizer check\",\"schema\":\"exp7.build-grant.v2\",\"scope\":\"tokenizer-only-build-cap-validation\"}\n", "stderr": ""},
    {"args": ["show", "7a8e0326e34323ee20ad18c5518358a1e6273503:wrong-identities.json"], "returncode": 0, "stdout": "{\"assets_sha256\":\"7e1d4e253deb47a92276c1b60a8e35f32d156ff5da4164fd5a9ee68fe55ee1d4\",\"battery_sha256\":\"0698612e2f80d1a4fe61d6d73037dc5c637a6d2ca6a5257e396b79ec544b5710\",\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"8233a0daf9ba47a0fd681b61d6ccbae06424db2177a8ab585e5f49a6f3e58272\",\"owner\":\"Michael Jordan\",\"quote\":\"authorize tiny fake tokenizer check\",\"schema\":\"exp7.build-grant.v2\",\"scope\":\"tokenizer-only-build-cap-validation\"}\n", "stderr": ""},
    {"args": ["show", "0e5eb69fce81c381679786e11060ff5daaacf991:grant.json"], "returncode": 128, "stdout": "", "stderr": "fatal: path 'grant.json' exists on disk, but not in '0e5eb69fce81c381679786e11060ff5daaacf991'\n"},
    {"args": ["show", "7a8e0326e34323ee20ad18c5518358a1e6273503:absent.json"], "returncode": 128, "stdout": "", "stderr": "fatal: path 'absent.json' does not exist in '7a8e0326e34323ee20ad18c5518358a1e6273503'\n"}
  ]
}''')


class CapturedCommandFailure(RuntimeError):
    def __init__(self, record):
        self.returncode = record['returncode']
        self.output = record['stdout'].encode()
        self.stderr = record['stderr'].encode()
        super().__init__(f"captured Git exit {self.returncode}: {record['args']}")


class CapturedGit(Git):
    def __init__(self, repo, events):
        super().__init__(repo)
        self.calls, self.events = [], events

    def call(self, *args):
        self.calls.append(args)
        self.events.append(('git', args))
        for record in CAPTURED['captures']:
            if tuple(record['args']) == args:
                if record['returncode']:
                    raise CapturedCommandFailure(record)
                return record['stdout'].encode()
        raise AssertionError(('uncaptured Git command', args))


class TinyTokenizer:
    all_special_ids = [99]

    def __init__(self, events):
        self.events = events
        self.target_length = 1

    def encode(self, text, **kwargs):
        self.events.append(('encode', text))
        return ([2] if text == ' alpha' else [3])*self.target_length if text.startswith(' ') else [1]

    def decode(self, tokens, **kwargs):
        self.events.append(('decode', tuple(tokens)))
        return {2: 'alpha', 3: 'beta'}[tokens[0]]


class ExternalTokenizerGrantTests(unittest.TestCase):
    def make(self, path='grant.json'):
        temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        events = []
        port = CapturedGit(root, events)
        raw = next(r['stdout'].encode() for r in CAPTURED['captures']
                   if r['args'] == ['show', CAPTURED['commits']['grant']+':'+path])
        files = {path: raw, 'owner.txt': CAPTURED['owner_evidence'].encode()}
        tok = TinyTokenizer(events)
        loads = []

        def loader(asset):
            # Assert order at the consumption boundary, not merely after return.
            self.assertEqual(port.calls, [('show', CAPTURED['commits']['grant']+':'+path)])
            events.append(('loader', asset['repo']))
            loads.append(asset)
            return tok, dict(asset)

        assets = {name: json.loads(json.dumps(CAPTURED['asset'])) for name in CAPTURED['names']}
        if path == 'wrong-identities.json':
            assets['twin'] = assets.pop('pythia_1b')
        pair = NS(pair_id='tiny:0', prompts=('a', 'b', 'c', 'd'), targets=('alpha', 'beta'), answer_type='word')
        kwargs = dict(battery=NS(pairs=(pair,), bytes_sha256=CAPTURED['battery_sha256']), read=files.__getitem__,
                      git=port, grant_path=path, grant_sha256=digest(raw), grant_commit=CAPTURED['commits']['grant'],
                      assets=assets, output_root=root, loader=loader)
        return NS(root=root, files=files, port=port, events=events, loads=loads, tok=tok, kwargs=kwargs)

    def body(self, fixture, value):
        raw = canonical(value)
        fixture.files[fixture.kwargs['grant_path']] = raw
        fixture.kwargs['grant_sha256'] = digest(raw)

    def reject(self, fixture, message, kind=Refusal):
        from exp7core.preflight import build_tokenizer_checks
        with self.assertRaisesRegex(kind, message) as caught:
            build_tokenizer_checks(**fixture.kwargs)
        self.assertEqual(fixture.loads, [])
        self.assertFalse(any(event[0] in ('loader', 'encode', 'decode') for event in fixture.events))
        self.assertFalse((fixture.root/'cap-validation').exists())
        return caught.exception

    def test_captured_v2_grant_reaches_loader_then_real_cap_coverage_gate(self):
        from exp7core.preflight import build_tokenizer_checks
        self.assertIs(CapturedGit.blob, Git.blob)
        fixture = self.make()
        self.assertNotIn('commit', json.loads(fixture.files['grant.json']))
        self.assertEqual(len(fixture.kwargs['assets']), 28)
        # Positive GRANT control, deliberately not a full cap measurement: one
        # fake pair exercises 8 real cap/roundtrip checks, then coverage refuses.
        # No cap validator is patched, and no 448,000-comparison run is needed.
        with self.assertRaisesRegex(Refusal, 'full tokenizer cap coverage'):
            build_tokenizer_checks(**fixture.kwargs)
        self.assertEqual(len(fixture.loads), 1)
        self.assertEqual([e[0] for e in fixture.events[:2]], ['git', 'loader'])
        self.assertEqual(sum(e[0] == 'decode' for e in fixture.events), 8)
        self.assertEqual(list((fixture.root/'cap-validation').iterdir()), [])

    def test_external_commit_is_required_and_hex40_validated(self):
        fixture = self.make()
        fixture.kwargs.pop('grant_commit')
        self.reject(fixture, 'grant_commit', TypeError)
        self.assertEqual(fixture.port.calls, [])
        for value in (None, '0'*40, 'z'*40, '1'*39):
            with self.subTest(commit=value):
                fixture = self.make()
                fixture.kwargs['grant_commit'] = value
                self.reject(fixture, 'Git object ID')
                self.assertEqual(fixture.port.calls, [])

    def test_legacy_mixed_missing_extra_and_nondict_schemas_refuse(self):
        for case in ('legacy', 'mixed', 'missing', 'extra', 'nondict'):
            with self.subTest(case=case):
                fixture = self.make()
                body = json.loads(fixture.files['grant.json'])
                if case == 'legacy':
                    body['schema'] = 'exp7.build-grant.v1'
                elif case == 'mixed':
                    body['commit'] = CAPTURED['commits']['grant']
                elif case == 'missing':
                    body.pop('quote')
                elif case == 'extra':
                    body['source_manifest_sha256'] = 'a'*64
                else:
                    body = []
                self.body(fixture, body)
                self.reject(fixture, 'build grant (scope|schema)')
                self.assertEqual(fixture.port.calls, [])

    def test_raw_pin_altered_bytes_commit_and_path_refuse_before_loader(self):
        for case in ('pin', 'bytes', 'commit', 'path'):
            with self.subTest(case=case):
                fixture = self.make()
                if case == 'pin':
                    fixture.kwargs['grant_sha256'] = '1'*64
                    self.reject(fixture, 'build grant pin')
                    self.assertEqual(fixture.port.calls, [])
                elif case == 'bytes':
                    # Canonical meaning unchanged and read-pin coherently updated;
                    # production Git.blob must still reject the exact-byte drift.
                    fixture.files['grant.json'] = b' '+fixture.files['grant.json']
                    fixture.kwargs['grant_sha256'] = digest(fixture.files['grant.json'])
                    self.reject(fixture, 'committed evidence differs')
                    self.assertEqual(fixture.port.calls, [('show', CAPTURED['commits']['grant']+':grant.json')])
                else:
                    if case == 'commit':
                        fixture.kwargs['grant_commit'] = CAPTURED['commits']['before']
                    else:
                        fixture.files['absent.json'] = fixture.files['grant.json']
                        fixture.kwargs['grant_path'] = 'absent.json'
                    caught = self.reject(fixture, 'captured Git exit 128', CapturedCommandFailure)
                    self.assertEqual(caught.returncode, 128)
                    self.assertEqual(caught.output, b'')
                    self.assertIn(b'fatal: path', caught.stderr)
                    self.assertEqual(fixture.port.calls, [('show', fixture.kwargs['grant_commit']+':'+fixture.kwargs['grant_path'])])

    def test_owner_scope_quote_and_evidence_remain_required(self):
        cases = [('owner', 'Synthetic impostor', 'scope'), ('scope', 'calibration', 'scope'),
                 ('quote', '   ', 'evidence'), ('quote', 'absent quotation', 'evidence'),
                 ('evidence', b'altered evidence', 'evidence')]
        for field, value, message in cases:
            with self.subTest(field=field, value=value):
                fixture = self.make()
                if field == 'evidence':
                    fixture.files['owner.txt'] = value
                else:
                    body = json.loads(fixture.files['grant.json'])
                    body[field] = value
                    self.body(fixture, body)
                self.reject(fixture, 'build grant '+message)
                self.assertEqual(fixture.port.calls, [])

    def test_battery_assets_and_exact_28_identities_remain_required(self):
        for case in ('battery', 'assets', 'identities'):
            with self.subTest(case=case):
                fixture = self.make('wrong-identities.json' if case == 'identities' else 'grant.json')
                if case == 'battery':
                    fixture.kwargs['battery'].bytes_sha256 = 'a'*64
                elif case == 'assets':
                    fixture.kwargs['assets']['pythia_1b']['commit'] = 'd'*40
                else:
                    self.assertEqual(len(fixture.kwargs['assets']), 28)
                message = 'exact two predictor' if case == 'identities' else 'build grant data binding'
                self.reject(fixture, message)
                self.assertEqual(fixture.port.calls, [('show', CAPTURED['commits']['grant']+':'+fixture.kwargs['grant_path'])])

    def test_measured_assets_refuse_before_fake_tokenizer_use(self):
        from exp7core.preflight import build_tokenizer_checks
        fixture = self.make()
        original = fixture.kwargs['loader']

        def drifted(asset):
            tok, measurements = original(asset)
            measurements['files'] = {}
            return tok, measurements

        fixture.kwargs['loader'] = drifted
        with self.assertRaisesRegex(Refusal, 'measured tokenizer asset binding'):
            build_tokenizer_checks(**fixture.kwargs)
        self.assertEqual(len(fixture.loads), 1)
        self.assertEqual([e[0] for e in fixture.events], ['git', 'loader'])
        self.assertEqual(list((fixture.root/'cap-validation').iterdir()), [])

    def test_cap_overflow_still_refuses_after_valid_external_binding(self):
        from exp7core.preflight import build_tokenizer_checks
        fixture = self.make()
        fixture.tok.target_length = 13
        with self.assertRaisesRegex(Refusal, 'frozen token cap cannot emit oracle answer'):
            build_tokenizer_checks(**fixture.kwargs)
        self.assertEqual(len(fixture.loads), 1)
        self.assertFalse(any(e[0] == 'decode' for e in fixture.events))
        self.assertEqual(list((fixture.root/'cap-validation').iterdir()), [])
