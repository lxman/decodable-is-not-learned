# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from pathlib import Path

class BatteryAdapter(unittest.TestCase):

    def test_contract(self):
        from exp7core.battery_adapter import load_certified
        from exp7core.contract import digest, Refusal
        from exp7core.records import strict_json
        from testing_paths import CONTRACTS
        pins = strict_json((CONTRACTS / 'collection-source-pins.json').read_bytes())
        repo = Path('/Users/michaeljordan/emergence-paper')

        def read(name):
            raw = (repo / name).read_bytes()
            self.assertEqual(digest(raw), pins[name])
            return raw
        b, raw, levels, baselines = load_certified(read)
        self.assertEqual(len(b.pairs), 2000)
        self.assertEqual({f: len(b.family(f)) for f in ('unscrambling', 'deduction', 'units', 'shapes')}, dict.fromkeys(('unscrambling', 'deduction', 'units', 'shapes'), 500))
