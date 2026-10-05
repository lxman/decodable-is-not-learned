# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from exp7core.contract import Refusal
from exp7core.bridge import sample_pair
from local_exp7core_bridge_fixtures import fixture_battery, load_fixture

class BridgeTests(unittest.TestCase):

    def setUp(self):
        self.pair = load_fixture(fixture_battery()).pairs[0]
        self.calls = []

    def loader(self, p, mode, device):
        self.calls.append((p, mode, device))
        return ('FAKE_TOKENIZER', 'FAKE_MODEL', {'digest': 'fixture'})

    def test_shared_or_missing_seed_payload_refuses(self):
        with self.assertRaises(Refusal):
            sample_pair(self.pair, 'pythia_1b', loader=self.loader, sampler=lambda *a, **k: {0: ['a'] * 64}, provenance=lambda x: None, terminal_ids=(0,))
