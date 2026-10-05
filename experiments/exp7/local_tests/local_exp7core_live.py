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
