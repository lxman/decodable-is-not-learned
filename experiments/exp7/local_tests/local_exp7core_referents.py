# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from types import SimpleNamespace as NS

class Referents(unittest.TestCase):

    def test_contract(self):
        from exp7core.referents import verify_model
        from exp7core.contract import canonical, digest, Refusal
        files = {'config.json': 'a' * 64, 'tokenizer.json': 'b' * 64}
        model = {'repo': 'allenai/OLMo-2-0425-1B', 'revision_commit': 'c' * 40, 'tensor_digest': 'd' * 64, 'dtype': 'float32', 'init_seed': None, 'config_sha256': files['config.json'], 'tokenizer_files_sha256': digest(canonical({'tokenizer.json': files['tokenizer.json']}))}
        data = {'models': {'olmo2_1b': model}, 'assets': {'olmo2_1b': {'repo': model['repo'], 'commit': model['revision_commit'], 'files': files}}}
        reads = []

        def read(name):
            reads.append(name)
            return canonical({'commit': 'c' * 40, 'model_sha': 'd' * 64, 'dtype': 'float32'})
        c = NS(trust=NS(data=data, read_repo=read))
        verify_model(c, 'olmo2_1b')
        self.assertEqual(len(reads), 2)
        model['tensor_digest'] = 'e' * 64
        with self.assertRaises(Refusal):
            verify_model(c, 'olmo2_1b')
