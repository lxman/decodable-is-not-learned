import guard  # FIRST: direct imports require guarded launcher
import unittest
from dataclasses import replace
from exp7core.contract import Refusal,canonical,digest
from exp7core.records import Address,ExpectedUnit,CONTEXT_KEYS,strict_json,rederive,build_record,validate_record

def fixture(kind='trained'):
    context = {k: 'a' * 64 for k in CONTEXT_KEYS}
    context.update(predictor_seal_sha256=None, power_sha256=None, model={'repo': 'FAKE/model', 'revision_commit': 'fixture-commit', 'tensor_digest': 'b' * 64, 'config_sha256': 'c' * 64, 'tokenizer_files_sha256': 'd' * 64, 'render': 'plain', 'terminal_ids': [0, 1], 'dtype': 'float32', 'init_seed': None})
    if kind == 'outcome':
        context.update(predictor_seal_sha256='e' * 64, power_sha256='f' * 64)
        context['model']['dtype'] = 'float16'
    if kind == 'twin':
        context['model']['init_seed'] = 0
    addresses = tuple((Address('units', f'units:{i:04d}', i, 'q0', digest(f'q{i}'.encode()), None if kind == 'outcome' else i, ('a', 'b'), 'word') for i in range(2)))
    expected = ExpectedUnit(kind, 'fixture', addresses, {'trained': 64, 'twin': 16, 'outcome': 1}[kind], canonical(context).decode())
    raw = b''.join((canonical({**a.public(), 'draws': ['a'] * expected.k}) for a in addresses))
    return (raw, expected)

class RecordTests(unittest.TestCase):

    def test_raw_rederived_all_three_modes(self):
        for kind, k in (('trained', 64), ('twin', 16), ('outcome', 1)):
            raw, expected = fixture(kind)
            r = build_record(raw, expected)
            self.assertIsNone(validate_record(raw, r, expected))
            self.assertEqual(r['n_draws'], 2 * k)

    def test_wrong_metadata_cannot_attest_its_way_through(self):
        raw, expected = fixture()
        record = build_record(raw, expected)
        for key, value in (('n_draws', 999), ('k', 16), ('pass', True), ('unit_id', 'wrong')):
            with self.subTest(field=key), self.assertRaises(Refusal):
                validate_record(raw, {**record, key: value}, expected)
        record['context']['model']['tensor_digest'] = 'e' * 64
        with self.assertRaises(Refusal):
            validate_record(raw, record, expected)

    def test_exact_coverage_duplicate_and_moved_rows_refuse(self):
        raw, expected = fixture()
        lines = raw.splitlines(keepends=True)
        for bad in (lines[0], lines[0] + lines[0], lines[1] + lines[0], raw[:-1]):
            with self.subTest(raw=bad[:20]), self.assertRaises(Refusal):
                rederive(bad, expected)

    def test_outcome_requires_seal_power_and_twin_seed(self):
        _, expected = fixture('outcome')
        context = strict_json(expected.context_json)
        context['predictor_seal_sha256'] = None
        with self.assertRaises(Refusal):
            replace(expected, context_json=canonical(context).decode())
        _, expected = fixture('twin')
        context = strict_json(expected.context_json)
        context['model']['init_seed'] = None
        with self.assertRaises(Refusal):
            replace(expected, context_json=canonical(context).decode())

    def test_shared_stream_and_duplicate_json_keys_refuse(self):
        _, expected = fixture()
        addresses = (expected.addresses[0], replace(expected.addresses[1], stream_seed=0))
        with self.assertRaises(Refusal):
            replace(expected, addresses=addresses)
        with self.assertRaises(Refusal):
            strict_json('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            strict_json('{"a":NaN}')
