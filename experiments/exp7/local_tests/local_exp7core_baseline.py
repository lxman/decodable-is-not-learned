# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

class Baseline(unittest.TestCase):

    def test_contract(self):
        from exp7core.baseline import derive_pythia_baseline, TRAINED_FP16_RECORD
        from exp7core.contract import canonical, Refusal
        with tempfile.TemporaryDirectory() as tmp:
            calls = []

            def read(name):
                return canonical({'tensor_digest': 'old'}) if name == TRAINED_FP16_RECORD else canonical({'checks': [{'check': 'untrained twin constructs 1b seed=0', 'state_sha256': 'old-twin'}]})
            trust = NS(grant=lambda *a, **k: calls.append((a, k)), read_repo=read, trace=NS(check=lambda: None), data={'prereg': {'object': 'tag'}, 'projection': {'commit': 'projection'}, 'source_manifest_sha256': 'a' * 64, 'code_manifest_sha256': 'b' * 64})
            c = NS(_ready=lambda: None, root=Path(tmp), trust=trust)

            def measurement(c, mode):
                return {'fp16_modern_digest': 'old', 'fp16_legacy_digest': 'old-twin', 'dtype': 'float32', 'mode': mode, 'tensor_digest': 'c' * 64}
            value = derive_pythia_baseline(c, measurement=measurement)
            self.assertEqual(set(value['readings']), {'trained', 'untrained'})
            self.assertEqual(calls[0], (('predictor-digest-baseline',), {'consume': True}))
            (Path(tmp) / 'predictor-seal.json').write_bytes(b'blocked')
            with self.assertRaises(Refusal):
                derive_pythia_baseline(c, measurement=lambda *a: self.fail('contact after seal'))
