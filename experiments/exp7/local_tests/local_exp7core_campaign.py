# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from testing_paths import CONTRACTS
from pathlib import Path
import json
import types
import unittest
import tempfile
from exp7core.contract import FAMILIES, Refusal, digest
from exp7core.battery_adapter import load_certified, require_schedule
from exp7core.records import strict_json
from exp7core.campaign import Campaign
REPO = Path('/Users/michaeljordan/emergence-paper')
from testing_paths import WORK as SCRATCH

class CertifiedTests(unittest.TestCase):

    def test_real_certified_full003_rederives_no_generation(self):
        pins = json.loads((CONTRACTS / 'collection-source-pins.json').read_bytes())

        def read(path):
            data = (REPO / path).read_bytes()
            self.assertEqual(digest(data), pins[path])
            return data
        b, data, levels, baseline = load_certified(read)
        self.assertEqual(len(b.pairs), 2000)
        self.assertEqual({len(b.family(f)) for f in FAMILIES}, {500})
        self.assertEqual(len({p for row in b.pairs for p in row.prompts}), 8000)
        self.assertEqual({p.answer_type for p in b.family('units')}, {'number'})
        self.assertTrue(all((s.x == 1 for s in baseline['endpoint']['deduction'])))
        self.assertEqual({t for p in b.family('shapes') for t in p.targets}, {'square', 'kite', 'rectangle', 'rhombus'})
        self.assertEqual(json.loads(levels)['shots'], [])
        tmp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(tmp.cleanup)
        c = object.__new__(Campaign)
        c.root, c._active, c._battery, c._baselines = (Path(tmp.name), True, b, baseline)
        c.trust = types.SimpleNamespace(read_repo=read)
        raw_baselines = c.baseline_draws()
        self.assertIsNone(raw_baselines['absentoption']['deduction'][0]['q0'])
        self.assertEqual(c.baseline_catalog()['inputcopy']['shapes']['applicable'], False)
        self.assertTrue(c.baseline_catalog()['inputcopy']['shapes']['reason'])
        base = c.base_assignments()
        self.assertEqual({f: len(set(v)) for f, v in base.items()}, {'unscrambling': 15, 'deduction': 20, 'units': 5, 'shapes': 2})
        rows = [strict_json(p.metadata_json) for p in b.pairs]
        rows[0]['render_order'], rows[1]['render_order'] = (rows[1]['render_order'], rows[0]['render_order'])
        with self.assertRaises(Refusal):
            require_schedule(rows)
