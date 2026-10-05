# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import FAMILIES, Refusal, canonical
from exp7core.collection_schema import predictor_units, outcome_units
from exp7core.collectors import collect_predictor, collect_endpoint, collect_outcomes, seal_predictors, complete_campaign
from exp7core.preflight import predictor_preflight
from collection_fixtures import fixture, FakeBackend
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class FullProducerContractTests(unittest.TestCase):

    def test_full_shape_producer_seal_campaign_outcome_contract(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            f = fixture(Path(tmp), with_caps=True)
            with f.campaign() as c:
                for model in ('pythia_1b', 'olmo2_1b', 'twin'):
                    preflight_backend = FakeBackend(c)
                    preflight = predictor_preflight(c, model, backend=preflight_backend)
                    self.assertEqual(preflight['additional_draws'], 32128 if model == 'twin' else 128512)
                    self.assertTrue(all((s.closed for s in preflight_backend.opened)))
                    backend = FakeBackend(c)
                    collect_predictor(c, model, backend=backend)
                    self.assertTrue(all((s.closed for s in backend.opened)))
                    resumed = FakeBackend(c)
                    collect_predictor(c, model, backend=resumed)
                    self.assertEqual(sum((len(s.calls) for s in resumed.opened)), 0)
                data = c.predictor_data()
                self.assertEqual(set(data), {'pythia_1b', 'olmo2_1b', 'twin'})
                self.assertEqual(len(data['pythia_1b']['deduction'][0]), 500)
                seal = seal_predictors(c)
                self.assertEqual((seal['new_units'], seal['new_draws'], seal['anchor_draws']), (48, 1152000, 144000))
            f.refresh_seal()
            f.stage_grant('power')
            claim = f.root / 'statistics/power'
            claim.mkdir(parents=True)
            (claim / 'CLAIM.json').write_bytes(canonical({'stage': 'power', 'production': True}))
            c = f.campaign()
            with c.entryexit('power'):
                self.assertEqual(c.seal_bindings()['seal_sha256'], f.data['predictor_seal']['sha256'])
            self.assertTrue((f.root / 'claims/power.CLAIM').exists())
            f.power()
            with f.campaign() as c:
                self.assertEqual(c.verify_predictor_seal(), seal)
                power = c.verify_power()
                self.assertEqual(power['seal_sha256'], f.data['predictor_seal']['sha256'])

                def power_semantics(record, campaign):
                    self.assertEqual(record['declarations'], {'fake': {'status': 'FORECAST-POWERED'}})
                b = FakeBackend(c)
                collect_endpoint(c, 'fakehost', backend=b, power_validator=power_semantics)
                self.assertEqual([s.spec['loader'] for s in b.opened], ['thin', 'candidate'])
                collect_outcomes(c, backend=b, power_validator=power_semantics)
                c.verify_complete()
                outcomes = c.outcomes()
                self.assertEqual(set(outcomes), set(FAMILIES))
                self.assertTrue(all((len(rows) == 500 for rows in outcomes.values())))
                self.assertEqual(outcomes['unscrambling'][0]['y'], 26)
                self.assertEqual(outcomes['unscrambling'][25]['y'], 1)
                self.assertEqual(len(outcomes['unscrambling'][0]['bits']), 26)
                self.assertTrue(all((s.closed for s in b.opened)))
                self.assertEqual(len(predictor_units()), 48)
                self.assertEqual(len(outcome_units()), 26)
                complete_campaign(c)
            f.refresh_complete()
            f.stage_grant('analysis')
            claim = f.root / 'statistics/analysis'
            claim.mkdir(parents=True)
            (claim / 'CLAIM.json').write_bytes(canonical({'stage': 'analysis', 'production': True}))
            c = f.campaign()
            with c.entryexit('analysis'):
                self.assertEqual(c.complete_bindings()['complete_sha256'], f.data['complete']['sha256'])
            self.assertTrue((f.root / 'claims/analysis.CLAIM').exists())
            path = f.root / 'units/predictor/pythia_1b/deduction/q0/raw.jsonl'
            raw = path.read_bytes().replace(b'"red"', b'" red"', 1)
            path.write_bytes(raw)
            with self.assertRaises(Refusal):
                with f.campaign() as c:
                    c.verify_predictor_seal()
