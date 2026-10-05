# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from types import SimpleNamespace as NS

class CollectionSchema(unittest.TestCase):

    def test_contract(self):
        from exp7core.collection_schema import addresses, predictor_units, outcome_units, key_of
        from exp7core.contract import ARMS, Refusal
        rows = tuple((NS(family='unscrambling', pair_id=f'unscrambling:{i:04d}', index=i, prompts=tuple((f'{i}-{a}' for a in ARMS)), targets=('cat', 'dog'), answer_type='word') for i in range(500)))
        battery = NS(family=lambda f: rows)
        trained = addresses(battery, 'pythia_1b', 'unscrambling', 'q0')
        twin = addresses(battery, 'twin', 'unscrambling', 'q0')
        self.assertEqual(len(trained), 500)
        self.assertNotEqual(trained, twin)
        self.assertEqual(len(set(predictor_units())), 48)
        self.assertEqual(len(outcome_units()), 26)
        with self.assertRaises(Refusal):
            key_of('unknown')
