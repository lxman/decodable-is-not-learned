from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import unittest
from exp7core.contract import Refusal
from exp7stats.common import digest
from exp7stats.power import PowerSpec, SPEC, verify_power_semantics, fit_target
from exp7stats.saved_math import pack, outcome_summary, BOUND_KEYS, family_counts
from exp7stats.power_validation import verify_fit, main_record
from exp7stats.calibration import verify_envelope_semantics, CalibrationSpec
from exp7stats.kernels import decision
from saved_fixtures import power_record, envelope
import numpy as np

SMALL = PowerSpec(n_sim=2,n_cal=2,n_validate=2,iterations=1,permutations=200,
                  positive_counts=(20,),count_ranges=(3,),targets=(F(1),))


class SavedArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record, cls.geometry = power_record(spec=SMALL, n=24, mode="varying")

    def verify(self, record):
        return verify_power_semantics(record,"d"*64,"a"*64,geometry=self.geometry,spec=SMALL)

    def test_SR2_rearrangement_extrema_match_independent_enumeration(self):
        from itertools import permutations
        from exp7core.inference import somers
        for x,y in (((F(0),F(0),F(1)),(0,1,1)),
                    ((F(0),F(0),F(1),F(2)),(2,1,0,0))):
            strata=("all",)*len(x)
            counts=family_counts(x,strata,pack(np.asarray([y],dtype=np.int64)),1,2,max(y),False)
            nums=[somers(p,y,strata)["numerator"] for p in permutations(x)]
            self.assertEqual((counts[2][0],counts[3][0]),(min(nums),max(nums)))

    def test_SR2_supported_positive_control_and_every_fit_state_mutation(self):
        self.verify(self.record)
        key = next(k for k,v in self.record["rows"].items() if v["target_D"] is not None)
        self.assertEqual(self.record["rows"][key]["status"], "SUPPORTED")
        for mutate in (
            lambda f: f["ceiling_fit"].update(mean_D=F(0)),
            lambda f: f["validation"].update(Ds=[F(-5),F(7)],mean_D=F(1)),
            lambda f: f.update(status="UNSUPPORTED"),
            lambda f: f["evaluations"][2].update(rho=.125),
            lambda f: f.update(rho=.75),
            lambda f: f["final_fit"]["scatter"].update(population_sd=99),
        ):
            bad=deepcopy(self.record); mutate(bad["rows"][key]["fit"])
            with self.assertRaises(Refusal): self.verify(bad)

    def test_SR2_SR4_all_printed_main_arithmetic_mutations_refuse(self):
        key = next(k for k in self.record["rows"] if k.endswith("/null"))
        for name, value in {"Ds":[F(1),F(1)], "mean_D":F(1), "interval95":[1,1],
                            "p_only_interval95":[1,1], "D_scatter":{"mean_defined":999},
                            "eligible_set_counts":{"invented":999}, "status":"UNSUPPORTED",
                            "p_fires":F(1), "fire_count":2, "p_only_count":999,
                            "permutations_consumed":1}.items():
            bad=deepcopy(self.record); bad["rows"][key][name]=value
            with self.assertRaises(Refusal, msg=name): self.verify(bad)

    def test_SR2_default_constant_geometry_is_retained_without_positive_power(self):
        record, geometry = power_record(mode="constant")
        verify_power_semantics(record,"d"*64,"a"*64,geometry=geometry)
        self.assertTrue(record["run_stop_required"])
        self.assertTrue(all(v["status"]=="UNSUPPORTED" for v in record["rows"].values() if v["target_D"] is not None))
        key=next(k for k in record["rows"] if k.endswith("/null"))
        record["rows"][key].update(Ds=[F(3,20)]*128,mean_D=F(3,20))
        with self.assertRaises(Refusal):
            verify_power_semantics(record,"d"*64,"a"*64,geometry=geometry)

    def test_SR2_default_geometry_blockwise_constant_globally_varying(self):
        # Full320 addresses;10240 main MC traces +30720 endpoint-fit Ds,
        # all fabricated by count arithmetic, zero stochastic calls.
        record, geometry = power_record(mode="blocked")
        self.assertTrue(all(len(set(r["x"]))==2 for p in geometry["predictors"].values() for r in p.values()))
        verified=verify_power_semantics(record,"d"*64,"a"*64,geometry=geometry)
        self.assertTrue(verified["run_stop_required"])
        self.assertTrue(all(v["status"]=="UNSUPPORTED" for v in record["rows"].values() if v["target_D"] is not None))
        key=next(k for k in record["rows"] if k.endswith("/null"))
        bad=deepcopy(record)
        b=decision(0,10000,10000)
        bad["rows"][key]["permutation_bounds"][0]={k:b[k] for k in BOUND_KEYS}
        with self.assertRaisesRegex(Refusal,"impossible"):
            verify_power_semantics(bad,"d"*64,"a"*64,geometry=geometry)
        bad=deepcopy(record)
        key=next(k for k,v in bad["rows"].items() if v["target_D"]==F(3,20))
        bad["rows"][key]["fit"].update(status="SUPPORTED",rho=.5,mean_D=F(3,20))
        with self.assertRaises(Refusal): verify_power_semantics(bad,"d"*64,"a"*64,geometry=geometry)

    def test_SR2_independent_geometry_cannot_be_taken_from_saved_support(self):
        with self.assertRaises(Refusal): verify_power_semantics(self.record,"d"*64,"a"*64,spec=SMALL)
        geometry=deepcopy(self.geometry)
        for p in geometry["predictors"].values():
            for row in p.values(): row["x"]=[F(0)]*24
        bad=deepcopy(self.record); bad["geometry_sha256"]=digest(geometry)
        with self.assertRaises(Refusal):
            verify_power_semantics(bad,"d"*64,"a"*64,geometry=geometry,spec=SMALL)

    def test_SR2_exact_subset_loss_requires_None_and_unsupported_main(self):
        key=next(k for k,v in self.record["rows"].items() if v["target_D"] is not None)
        row=deepcopy(self.record["rows"][key]); families=deepcopy(self.geometry["predictors"][row["predictor"]])
        subset=tuple(row["subset"])
        # Saved count shape1, positives20. One family partitions exactly on y.
        spec=replace(SMALL,count_ranges=(1,))
        y=np.asarray([[1]*20+[0]*4]*2,dtype=np.int64)
        families[subset[0]]["strata"]=["yes"]*20+["no"]*4
        yy={f:pack(y) for f in subset}
        summary,elig,_=outcome_summary(families,subset,yy,2,20,1)
        self.assertEqual(summary["Ds"],[None,None])
        base={k:row[k] for k in ("id","predictor","subset","n_positive","max_count","target_D","kernel")}
        base["max_count"]=1
        bounds=[{"status":"EXACT_SUBSET_LOSS","eligible":e["eligible"]} for e in elig]
        got=main_record(base,row["fit"],yy,bounds,families,spec)
        self.assertEqual(got["status"],"UNSUPPORTED")
        self.assertIsNone(got["mean_D"])
        self.assertEqual(got["fire_count"],0)
        bounds[0]["eligible"]=subset
        with self.assertRaises(Refusal): main_record(base,row["fit"],yy,bounds,families,spec)

    def test_SR4_envelope_every_derived_field_and_structural_status(self):
        spec=CalibrationSpec(n=120,replicates=2,permutations=200,envelope_replicates=2)
        rows=envelope(spec)
        verify_envelope_semantics(rows,spec=spec)
        key=next(k for k,v in rows.items() if v["status"]=="SIMULATED")
        fields={"p_only_count":999,"p_only_fraction":F(999),"mean_x":F(999),"mean_u":F(-999),
                "mean_d":F(999),"unsupported_render_fraction":F(-1),"interval95":[1,1],
                "p_only_interval95":[1,1],"expected_x":F(999),"probabilities":[],"target_row_histograms":[],
                "fire_count":2,"p_fires":F(1),"N":999}
        for field,value in fields.items():
            bad=deepcopy(rows);bad[key][field]=value
            with self.assertRaises(Refusal,msg=field):verify_envelope_semantics(bad,spec=spec)
        for status in ("UNSUPPORTED","ANALYTIC-ZERO-SUPPORT"):
            name=next(k for k,v in rows.items() if v["status"]==status)
            for field,value in (("N",128),("probabilities",[]),("mean_u",F(-1))):
                bad=deepcopy(rows);bad[name][field]=value
                with self.assertRaises(Refusal):verify_envelope_semantics(bad,spec=spec)

    def test_SR4_saved_target_counts_out_of_domain_refuse(self):
        spec=CalibrationSpec(n=120,replicates=2,permutations=200,envelope_replicates=2)
        rows=envelope(spec);key=next(k for k,v in rows.items() if v["status"]=="SIMULATED")
        a=np.zeros((120*rows[key]["families"],8),dtype=np.int64);a[:,0]=65
        rows[key]["score_counts"][0]=pack(a)
        with self.assertRaises(Refusal):verify_envelope_semantics(rows,spec=spec)

    def test_SR4_calibration_p_only_full_counts_remain_consistent(self):
        from dataclasses import asdict
        from exp7stats.common import SCHEMA
        from exp7stats.calibration import (SPEC as spec, CASES, TRUE_NULLS, H, ENVELOPE, DELTAS,
                                          rate_summary, verify_calibration_semantics)
        record={"schema":SCHEMA,"stage":"calibration","production":True,"saved_math_version":2,
                "state":"NO-DETECTED-CALIBRATION-DEFECT","spec":asdict(spec),
                "case_table_sha256":digest({"H":H,"nulls":TRUE_NULLS,"E":ENVELOPE,"deltas":DELTAS}),
                "selectivity_envelope":envelope(),"cases":{}}
        for case in CASES:
            record["cases"][case]={"case":case,"status":"NO-DETECTED-DEFECT","N":spec.replicates,
                "components":{f"{p}/{c}":{k:rate_summary(0,spec.replicates,F(1,200)) for k in ("p_reject","fires")}
                              for p,c in TRUE_NULLS[case]},
                "either_predictor_joint":rate_summary(0,spec.replicates,F(1,100))}
        verify_calibration_semantics(record)
        component=next(iter(record["cases"][CASES[0]]["components"].values()))
        component["fires"]=rate_summary(1,spec.replicates,F(1,200))
        with self.assertRaisesRegex(Refusal,"full/p-only"):
            verify_calibration_semantics(record)
