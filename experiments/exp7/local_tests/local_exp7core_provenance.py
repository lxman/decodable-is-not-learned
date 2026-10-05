# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import os
import tempfile
import unittest
import json
from exp7core.contract import Refusal, canonical, digest
from exp7core.provenance import Git, Trace, Trust
from testing_paths import WORK

class ReadWriteTraceTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.root = self.repo / 'campaign'
        self.root.mkdir()
        self.pinned = self.repo / 'pinned.txt'
        self.pinned.write_bytes(b'pinned bytes')
        self.unknown = self.repo / 'unknown.txt'
        self.unknown.write_bytes(b'unpinned input')

    def trace(self):
        return Trace(self.repo, self.root, {'pinned.txt': digest(b'pinned bytes')})

    def readwrite(self, path, mode):
        if isinstance(mode, str):
            with path.open(mode) as handle:
                return handle.read()
        fd = os.open(path, mode)
        try:
            return os.read(fd, 100)
        finally:
            os.close(fd)

    def test_pinned_readwrite_read_is_traced_and_passes_unchanged(self):
        for mode in ('r+', 'r+b', os.O_RDWR, os.O_RDWR | os.O_APPEND, os.O_RDWR | os.O_CREAT):
            with self.subTest(mode=mode):
                trace = self.trace()
                trace.start()
                try:
                    value = self.readwrite(self.pinned, mode)
                    self.assertIn(value, ('pinned bytes', b'pinned bytes'))
                    self.assertIn(str(self.pinned), trace.reads)
                finally:
                    trace.stop()


# PROVENANCE-1: captured by fix_grant_fixture.py in a tiny external Git repo.
# This self-contained data is synthetic authority only, never a real owner grant.
# The full generator/command receipts are task evidence; tests never open them.
CAPTURED = json.loads(r'''{
  "captures": [
    {"args": ["show", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630:predictor-preflight.json"], "returncode": 0, "stderr": "", "stdout": "{\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"power_sha256\":null,\"predictor_seal_sha256\":null,\"prereg_tag_object\":\"3333333333333333333333333333333333333333\",\"projection_commit\":\"ec53a957bc4b2171d994ab01b7c0ef5928124a56\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.owner-grant.v2\",\"scope\":\"predictor-preflight\"}\n"},
    {"args": ["show", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630:outcome-preflight.json"], "returncode": 0, "stderr": "", "stdout": "{\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"power_sha256\":\"4b68f20f95c4da95c2161ac0cb4485289ce8cbe5bda080215b7fdb096f2d0659\",\"predictor_seal_sha256\":\"aa234b27aa0072046a62f9eb5c791160148bc97251f4607ae24e817be588f116\",\"prereg_tag_object\":\"3333333333333333333333333333333333333333\",\"projection_commit\":\"ec53a957bc4b2171d994ab01b7c0ef5928124a56\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.owner-grant.v2\",\"scope\":\"outcome-preflight\"}\n"},
    {"args": ["show", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630:power.json"], "returncode": 0, "stderr": "", "stdout": "{\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"power_sha256\":null,\"predictor_seal_sha256\":\"aa234b27aa0072046a62f9eb5c791160148bc97251f4607ae24e817be588f116\",\"prereg_tag_object\":\"3333333333333333333333333333333333333333\",\"projection_commit\":\"ec53a957bc4b2171d994ab01b7c0ef5928124a56\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.owner-grant.v2\",\"scope\":\"power\"}\n"},
    {"args": ["show", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630:analysis.json"], "returncode": 0, "stderr": "", "stdout": "{\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"power_sha256\":\"4b68f20f95c4da95c2161ac0cb4485289ce8cbe5bda080215b7fdb096f2d0659\",\"predictor_seal_sha256\":\"aa234b27aa0072046a62f9eb5c791160148bc97251f4607ae24e817be588f116\",\"prereg_tag_object\":\"3333333333333333333333333333333333333333\",\"projection_commit\":\"ec53a957bc4b2171d994ab01b7c0ef5928124a56\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.owner-grant.v2\",\"scope\":\"analysis\"}\n"},
    {"args": ["show", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630:calibration.json"], "returncode": 0, "stderr": "", "stdout": "{\"code_manifest_sha256\":\"e7b94c92481828a381945afb68caf8a17445cc6629817e2be984d7cf5c507300\",\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.build-grant.v2\",\"scope\":\"calibration\",\"source_manifest_sha256\":\"39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133\"}\n"},
    {"args": ["show", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630:power-presupposed.json"], "returncode": 0, "stderr": "", "stdout": "{\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"power_sha256\":\"4b68f20f95c4da95c2161ac0cb4485289ce8cbe5bda080215b7fdb096f2d0659\",\"predictor_seal_sha256\":\"aa234b27aa0072046a62f9eb5c791160148bc97251f4607ae24e817be588f116\",\"prereg_tag_object\":\"3333333333333333333333333333333333333333\",\"projection_commit\":\"ec53a957bc4b2171d994ab01b7c0ef5928124a56\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.owner-grant.v2\",\"scope\":\"power\"}\n"},
    {"args": ["show", "9741334137900b04bcfb5968600c7fe1fc48ee1e:predictor-preflight.json"], "returncode": 0, "stderr": "", "stdout": "{\"evidence_path\":\"owner.txt\",\"evidence_sha256\":\"0ab18317e233a68ac002f8ef59cda72a3f9fbcfcba5123e9fcbcb3e648ffa7cd\",\"owner\":\"Michael Jordan\",\"power_sha256\":null,\"predictor_seal_sha256\":null,\"prereg_tag_object\":\"3333333333333333333333333333333333333333\",\"projection_commit\":\"ec53a957bc4b2171d994ab01b7c0ef5928124a56\",\"quote\":\"authorize fake scope\",\"schema\":\"exp7.owner-grant.v2\",\"scope\":\"predictor-preflight\"}\n"},
    {"args": ["show", "ec53a957bc4b2171d994ab01b7c0ef5928124a56:predictor-preflight.json"], "returncode": 128, "stderr": "fatal: path 'predictor-preflight.json' exists on disk, but not in 'ec53a957bc4b2171d994ab01b7c0ef5928124a56'\n", "stdout": ""},
    {"args": ["show", "ec53a957bc4b2171d994ab01b7c0ef5928124a56:calibration.json"], "returncode": 128, "stderr": "fatal: path 'calibration.json' exists on disk, but not in 'ec53a957bc4b2171d994ab01b7c0ef5928124a56'\n", "stdout": ""},
    {"args": ["merge-base", "--is-ancestor", "ec53a957bc4b2171d994ab01b7c0ef5928124a56", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630"], "returncode": 0, "stderr": "", "stdout": ""},
    {"args": ["merge-base", "--is-ancestor", "fd19430548b8ec08c0665fee65991a1bb1ad0d4a", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630"], "returncode": 0, "stderr": "", "stdout": ""},
    {"args": ["merge-base", "--is-ancestor", "58bed6fc93a6d4c9067244b55655726bf11e9d93", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630"], "returncode": 0, "stderr": "", "stdout": ""},
    {"args": ["merge-base", "--is-ancestor", "aba3358b565352748ba7ca54177a34cf81b713a3", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630"], "returncode": 0, "stderr": "", "stdout": ""},
    {"args": ["merge-base", "--is-ancestor", "67027fdab0456ce2dd826a35a0d048dac96581e3", "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630"], "returncode": 1, "stderr": "", "stdout": ""},
    {"args": ["merge-base", "--is-ancestor", "ec53a957bc4b2171d994ab01b7c0ef5928124a56", "9741334137900b04bcfb5968600c7fe1fc48ee1e"], "returncode": 1, "stderr": "", "stdout": ""}
  ],
  "commits": {
    "complete": "aba3358b565352748ba7ca54177a34cf81b713a3",
    "grant": "c82cc2e95a391d5653d2c9d835f40b5ff4ee7630",
    "later": "67027fdab0456ce2dd826a35a0d048dac96581e3",
    "power": "58bed6fc93a6d4c9067244b55655726bf11e9d93",
    "projection": "ec53a957bc4b2171d994ab01b7c0ef5928124a56",
    "seal": "fd19430548b8ec08c0665fee65991a1bb1ad0d4a",
    "unrelated": "9741334137900b04bcfb5968600c7fe1fc48ee1e"
  },
  "metadata": {
    "code_manifest_sha256": "e7b94c92481828a381945afb68caf8a17445cc6629817e2be984d7cf5c507300",
    "complete": {"commit": "aba3358b565352748ba7ca54177a34cf81b713a3"},
    "power": {"commit": "58bed6fc93a6d4c9067244b55655726bf11e9d93", "sha256": "4b68f20f95c4da95c2161ac0cb4485289ce8cbe5bda080215b7fdb096f2d0659"},
    "predictor_seal": {"sha256": "aa234b27aa0072046a62f9eb5c791160148bc97251f4607ae24e817be588f116"},
    "predictor_tag": {"commit": "fd19430548b8ec08c0665fee65991a1bb1ad0d4a"},
    "prereg": {"object": "3333333333333333333333333333333333333333"},
    "projection": {"commit": "ec53a957bc4b2171d994ab01b7c0ef5928124a56"},
    "source_manifest_sha256": "39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133"
  },
  "owner_evidence": "SYNTHETIC FIXTURE ONLY: authorize fake scope; not a real owner grant.\n",
  "paths": {"analysis": "analysis.json", "calibration": "calibration.json", "outcome-preflight": "outcome-preflight.json", "power": "power.json", "predictor-preflight": "predictor-preflight.json"},
  "synthetic_only": true
}''')


class CapturedCommandFailure(RuntimeError):
    """Replay the exact nonzero command status without importing subprocess."""
    def __init__(self, record):
        self.cmd = tuple(record['args'])
        self.returncode = record['returncode']
        self.output = record['stdout'].encode()
        self.stderr = record['stderr'].encode()
        super().__init__(f'captured Git exit {self.returncode}: {self.cmd}')


class CapturedGit(Git):
    """Only the process port is replaced; production blob/ancestor remain active."""
    def __init__(self, repo):
        super().__init__(repo)
        self.calls = []

    def call(self, *args):
        self.calls.append(args)
        for record in CAPTURED['captures']:
            if tuple(record['args']) == args:
                if record['returncode']:
                    raise CapturedCommandFailure(record)
                return record['stdout'].encode()
        raise AssertionError(('uncaptured Git command', args))


class ExternalGrantBindingTests(unittest.TestCase):
    def make(self, scope, *, raw=None, path=None, body_change=None, data_change=None, evidence=None):
        temp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)
        root = repo / 'campaign'
        root.mkdir()
        path = path or CAPTURED['paths'][scope]
        port = CapturedGit(repo)
        if raw is None:
            raw = port.call('show', CAPTURED['commits']['grant'] + ':' + path)
        port.calls.clear()
        body = json.loads(raw)
        if body_change:
            body_change(body)
            raw = canonical(body)
        evidence = CAPTURED['owner_evidence'].encode() if evidence is None else evidence
        (repo / path).write_bytes(raw)
        (repo / 'owner.txt').write_bytes(evidence)
        data = json.loads(json.dumps(CAPTURED['metadata']))
        data.update(schema='exp7.trust.v1', repo_pins={path: digest(raw), 'owner.txt': digest(evidence)},
                    grants={scope: {'path': path, 'canonical_sha256': digest(canonical(body)),
                                    'commit': CAPTURED['commits']['grant']}})
        if data_change:
            data_change(data)
        trust_bytes = canonical(data)
        (repo / 'trust.json').write_bytes(trust_bytes)
        trust = Trust(root, repo, 'trust.json', digest(trust_bytes), git=port)
        return trust, port, body

    def invoke(self, trust, scope, consume=True):
        trust.trace.start()
        try:
            method = trust.build_grant if scope == 'calibration' else trust.grant
            return method(scope, consume=consume)
        finally:
            trust.trace.stop()

    def rejected(self, scope, message, **kwargs):
        trust, port, _ = self.make(scope, **kwargs)
        with self.assertRaisesRegex(Refusal, message):
            self.invoke(trust, scope)
        self.assertFalse((trust.root / 'claims').exists())
        return port

    def test_owner_grants_use_real_external_blob_and_all_stage_ancestors(self):
        self.assertIs(CapturedGit.blob, Git.blob)
        self.assertIs(CapturedGit.ancestor, Git.ancestor)
        stages = {'predictor-preflight': ('projection',), 'outcome-preflight': ('projection', 'power'),
                  'power': ('projection', 'seal'), 'analysis': ('projection', 'seal', 'complete')}
        commits = CAPTURED['commits']
        for scope, required in stages.items():
            with self.subTest(scope=scope):
                trust, port, body = self.make(scope)
                self.assertNotIn('commit', body)
                self.assertEqual(self.invoke(trust, scope, consume=False), body)
                self.assertFalse((trust.root / 'claims').exists())
                self.assertEqual(port.calls, [('show', commits['grant'] + ':' + CAPTURED['paths'][scope])] +
                                 [('merge-base', '--is-ancestor', commits[s], commits['grant']) for s in required])

    def test_build_grant_uses_real_external_blob_before_claim(self):
        trust, port, body = self.make('calibration')
        self.assertNotIn('commit', body)
        self.assertEqual(self.invoke(trust, 'calibration'), body)
        self.assertEqual(port.calls, [('show', CAPTURED['commits']['grant'] + ':calibration.json')])
        claim = json.loads((trust.root / 'claims/calibration.CLAIM').read_bytes())
        self.assertEqual(claim, {'grant_sha256': digest(canonical(body))})

    def test_missing_malformed_external_binding_has_no_body_fallback(self):
        for scope in ('predictor-preflight', 'calibration'):
            changes = [lambda d: d.pop('grants'), lambda d: d['grants'].pop(scope)]
            changes += [lambda d, field=field: d['grants'][scope].pop(field)
                        for field in ('path', 'canonical_sha256', 'commit')]
            changes += [lambda d, value=value: d['grants'].__setitem__(scope, value)
                        for value in (None, [], 'not a binding')]
            changes += [lambda d, value=value: d['grants'][scope].__setitem__('commit', value)
                        for value in (None, 1, '', '0' * 40, 'z' * 40, '1' * 39)]
            changes += [lambda d, value=value: d['grants'][scope].__setitem__('path', value)
                        for value in (None, [], '')]
            changes += [lambda d: d['grants'][scope].__setitem__('canonical_sha256', 'bad'),
                        lambda d: d['grants'][scope].__setitem__('extra', True)]
            for index, change in enumerate(changes):
                with self.subTest(scope=scope, case=index):
                    trust, port, _ = self.make(scope, data_change=change)
                    with self.assertRaises(Refusal):
                        self.invoke(trust, scope)
                    self.assertEqual(port.calls, [])
                    self.assertFalse((trust.root / 'claims').exists())

    def test_legacy_mixed_missing_extra_body_schemas_refuse(self):
        for scope in ('predictor-preflight', 'calibration'):
            for kind in ('legacy', 'mixed', 'missing', 'extra'):
                with self.subTest(scope=scope, kind=kind):
                    def change(body):
                        if kind == 'legacy':
                            body['schema'] = body['schema'].replace('.v2', '.v1')
                            body['commit'] = CAPTURED['commits']['grant']
                        elif kind == 'mixed':
                            body['commit'] = CAPTURED['commits']['grant']
                        elif kind == 'missing':
                            body.pop('quote')
                        else:
                            body['extra'] = True
                    port = self.rejected(scope, 'schema', body_change=change)
                    self.assertEqual(port.calls, [])

    def test_altered_grant_bytes_and_wrong_containing_commit_refuse(self):
        commits = CAPTURED['commits']
        for scope in ('predictor-preflight', 'calibration'):
            with self.subTest(scope=scope, case='altered exact bytes'):
                port = CapturedGit(WORK)
                raw = port.call('show', commits['grant'] + ':' + CAPTURED['paths'][scope])
                refused = self.rejected(scope, 'committed evidence differs', raw=b' ' + raw)
                self.assertEqual(refused.calls, port.calls)
            with self.subTest(scope=scope, case='absent at external commit'):
                trust, port, _ = self.make(scope, data_change=lambda d:
                    d['grants'][scope].__setitem__('commit', commits['projection']))
                with self.assertRaises(CapturedCommandFailure) as caught:
                    self.invoke(trust, scope)
                self.assertEqual(caught.exception.returncode, 128)
                self.assertIn(b'fatal: path', caught.exception.stderr)
                self.assertEqual(port.calls, [('show', commits['projection'] + ':' + CAPTURED['paths'][scope])])
                self.assertFalse((trust.root / 'claims').exists())

    def test_invalid_projection_seal_power_complete_ancestry_refuses(self):
        commits = CAPTURED['commits']
        cases = [('predictor-preflight', 'unrelated'), ('outcome-preflight', 'power'),
                 ('power', 'predictor_tag'), ('analysis', 'predictor_tag'), ('analysis', 'complete')]
        for scope, key in cases:
            with self.subTest(scope=scope, key=key):
                def change(data):
                    if key == 'unrelated':
                        data['grants'][scope]['commit'] = commits['unrelated']
                    else:
                        data[key]['commit'] = commits['later']
                trust, port, _ = self.make(scope, data_change=change)
                with self.assertRaises(CapturedCommandFailure) as caught:
                    self.invoke(trust, scope)
                self.assertEqual(caught.exception.returncode, 1)
                expected = ('merge-base', '--is-ancestor', commits['projection'], commits['unrelated']) if key == 'unrelated' else (
                    'merge-base', '--is-ancestor', commits['later'], commits['grant'])
                self.assertEqual(port.calls[-1], expected)
                self.assertEqual(caught.exception.output, b'')
                self.assertEqual(caught.exception.stderr, b'')
                self.assertFalse((trust.root / 'claims').exists())

    def test_owner_quote_evidence_canonical_and_independent_trust_pins_remain_required(self):
        for scope in ('predictor-preflight', 'calibration'):
            for field, value, message in (('owner', 'Synthetic impostor', 'scope'),
                                          ('scope', 'wrong scope', 'scope'),
                                          ('quote', 'not present in evidence', 'evidence')):
                with self.subTest(scope=scope, field=field):
                    self.rejected(scope, message, body_change=lambda b: b.__setitem__(field, value))
            with self.subTest(scope=scope, field='evidence bytes'):
                self.rejected(scope, 'evidence', evidence=b'altered synthetic evidence')
            with self.subTest(scope=scope, field='canonical pin'):
                self.rejected(scope, 'grant pin', data_change=lambda d:
                    d['grants'][scope].__setitem__('canonical_sha256', '1' * 64))
            with self.subTest(scope=scope, field='independent trust pin'):
                trust, _, _ = self.make(scope)
                with self.assertRaisesRegex(Refusal, 'independent trust digest'):
                    Trust(trust.root, trust.repo, 'trust.json', '1' * 64, git=CapturedGit(trust.repo))
                self.assertFalse((trust.root / 'claims').exists())

    def test_stage_and_manifest_bindings_remain_required(self):
        cases = [('predictor-preflight', 'prereg', 'object', 'stage binding'),
                 ('predictor-preflight', 'projection', 'commit', 'stage binding'),
                 ('outcome-preflight', 'predictor_seal', 'sha256', 'outcome grant preceding'),
                 ('outcome-preflight', 'power', 'sha256', 'outcome grant preceding'),
                 ('power', 'predictor_seal', 'sha256', 'statistics grant seal'),
                 ('analysis', 'predictor_seal', 'sha256', 'statistics grant seal'),
                 ('analysis', 'power', 'sha256', 'analysis grant power')]
        for scope, key, field, message in cases:
            with self.subTest(scope=scope, key=key):
                self.rejected(scope, message, data_change=lambda d: d[key].__setitem__(field, '1' * (40 if field in ('commit', 'object') else 64)))
        for field in ('source_manifest_sha256', 'code_manifest_sha256'):
            with self.subTest(field=field):
                self.rejected('calibration', 'build grant exact frozen inputs',
                              data_change=lambda d: d.__setitem__(field, '1' * 64))
        port = self.rejected('power', 'cannot presuppose future power output', path='power-presupposed.json')
        self.assertEqual(len(port.calls), 3)  # actual blob, projection, sealed-predictor ancestry

    def test_claims_are_last_exact_and_once_only_for_both_routes(self):
        for scope in ('predictor-preflight', 'calibration'):
            with self.subTest(scope=scope):
                trust, port, body = self.make(scope)
                self.assertEqual(self.invoke(trust, scope), body)
                claim = trust.root / 'claims' / (scope + '.CLAIM')
                original = claim.read_bytes()
                self.assertEqual(original, canonical({'grant_sha256': digest(canonical(body))}))
                calls = list(port.calls)
                with self.assertRaises(FileExistsError):
                    self.invoke(trust, scope)
                self.assertEqual(claim.read_bytes(), original)
                self.assertEqual(port.calls, calls + calls)
