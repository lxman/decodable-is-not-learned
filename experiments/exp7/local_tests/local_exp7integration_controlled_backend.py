# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7integration.controlled_backend import ControlledBackend
from local_exp7integration_controlled_backend_collection_fixtures import fixture
from local_exp7integration_controlled_backend_collection_fixture import ROOT, put

class O8CompositionTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'test-work')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)

    def test_controlled_backend_uses_real_campaign_grant_and_stop_before_next_family(self):
        f = fixture(self.repo)
        checks, samples = ([], [])

        class Beat:

            def check(self):
                checks.append('check')

            def __call__(self, detail):
                checks.append(detail)

        class Session:
            receipt = {'fixture': True}

            def sample(self, prompt, **kw):
                samples.append(prompt)
                return {0: [prompt]}

            def close(self):
                checks.append('close')

        class Backend:

            def open(self, load):
                checks.append(load)
                return Session()
        stop = f.root / 'STOP_NEW_WORK.json'
        with f.campaign() as c:
            from exp7core.collectors import backend_of
            backend = backend_of(c, ControlledBackend(Beat(), stop, backend=Backend()), 'predictor-collection')
            session = backend.open('sample-pythia_1b')
            session.sample('first', rung='exp7/unscrambling/q0')
            put(f.root, 'STOP_NEW_WORK.json', {'reason': 'synthetic stop'})
            session.sample('same-family', rung='exp7/unscrambling/q1')
            with self.assertRaisesRegex(ValueError, 'STOP_NEW_WORK'):
                session.sample('next-family', rung='exp7/deduction/q0')
            session.close()
        self.assertEqual(samples, ['first', 'same-family'])
        self.assertIn('close', checks)
