# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from exp7core.contract import canonical, digest
from exp7core.records import Address, ExpectedUnit, CONTEXT_KEYS, build_record, validate_record

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
