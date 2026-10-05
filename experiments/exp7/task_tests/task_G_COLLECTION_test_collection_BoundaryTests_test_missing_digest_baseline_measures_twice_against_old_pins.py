# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import canonical, digest
from exp7core.baseline import derive_pythia_baseline, TRAINED_FP16_RECORD, TWIN_FP16_RECORD
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_missing_digest_baseline_measures_twice_against_old_pins(self):
        for path, value in [(TRAINED_FP16_RECORD, {'tensor_digest': digest(b'old fp16 trained')}), (TWIN_FP16_RECORD, {'checks': [{'check': 'untrained twin constructs 1b seed=0', 'state_sha256': digest(b'old fp16 twin')}]})]:
            p = self.repo / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(canonical(value))
            self.f.data['repo_pins'][path] = digest(p.read_bytes())
        calls = []

        def measure(c, mode):
            calls.append(mode)
            return {'dtype': 'float32', 'mode': mode, 'tensor_digest': digest(('fp32 ' + mode).encode()), 'fp16_modern_digest': digest(b'old fp16 trained'), 'fp16_legacy_digest': digest(b'old fp16 twin')}
        with self.f.campaign() as c:
            value = derive_pythia_baseline(c, measurement=measure)
            self.assertEqual(calls, ['trained', 'trained', 'untrained', 'untrained'])
            self.assertEqual(value['readings']['trained']['tensor_digest'], digest(b'fp32 trained'))
            self.assertFalse((c.root / 'units/predictor').exists())
            with self.assertRaises(FileExistsError):
                derive_pythia_baseline(c, measurement=measure)
