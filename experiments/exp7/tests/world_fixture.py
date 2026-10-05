"""Concrete production-producer world fixture; full runs are future freeze only.

Imports are fixed test helpers. All model/Git/owner ports are fabricated. Actual
certified battery/baselines and actual collection serializers/validators are used.
No expected verdict is stored as an authoritative input. A genuine independently
accepted pre-tag calibration directory is mandatory for the full-default route.
"""
from pathlib import Path
from dataclasses import replace
from copy import deepcopy
import json
from exp7core.contract import ARMS, FAMILIES, GRID, canonical, require
from exp7core.battery_adapter import load_certified, PREFIX
from exp7core.preflight import predictor_preflight, validate_caps
from exp7core.collectors import collect_predictor, seal_predictors, collect_endpoint, collect_outcomes, complete_campaign
from exp7stats.common import stage, digest, dumps, decode, Shape
from exp7stats.data import load_battery, load_predictors
from exp7stats import power, analyzer
from exp7integration.adapter import StatsCampaignAdapter, collection_power_validator, sealed_predictor_geometry
from exp7integration.calibration_copy import copy_accepted_calibration
from collection_fixtures import fixture, FakeGit, C
from collection_fixture import ROOT, put
from test_real_composition import (SyntheticPowerCampaign, FullCardinalityMiniatureAdapter, CertifiedSession,
                                   MINI_POWER, verify_miniature_power, authority)


class RecipeSession(CertifiedSession):
    def __init__(self, c, load, recipe):
        super().__init__(c, load)
        self.recipe = recipe
    def translate(self, value, pair):
        return pair.targets[0] if value == "alpha" else pair.targets[1] if value == "beta" else value
    def sample(self, prompt, **kw):
        if kw["rung"] in ("add_base8", "sub_base8", "ctrl_copy"):
            return super().sample(prompt, **kw)
        p, j = self.lookup[prompt]
        row = self.recipe["families"][p.family][p.index]
        model = self.spec["model"]
        values = row["twin"] if model == "twin" else row["trained"][model]
        draws = [self.translate(v, p) for v in values[ARMS[j]]]
        require(len(draws) == kw["draws_per_seed"], "world raw draw coverage")
        return {s: list(draws) for s in kw["seeds"]}
    def greedy(self, prompts, cap):
        step = self.spec["model"].split("/")[1]
        result = []
        for prompt in prompts:
            if prompt not in self.lookup:
                result.append("1")
            else:
                p, j = self.lookup[prompt]
                value = self.recipe["families"][p.family][p.index]["outputs"][step][ARMS[j]]
                result.append(self.translate(value, p))
        return result


class RecipeBackend:
    def __init__(self, c, recipe):
        self.c, self.recipe = c, recipe
    def open(self, load):
        return RecipeSession(self.c, load, self.recipe)


class FullDefaultAdapter(FullCardinalityMiniatureAdapter):
    def _dimensions(self):
        return 500, GRID, True


class ProducerWorldFixture:
    def __init__(self, *, source_repo, source_pins, calibration_directory=None, calibration_files=None, miniature=False):
        require(type(miniature) is bool, "explicit world fixture mode")
        self.source_repo, self.source_pins = Path(source_repo), dict(source_pins)
        self.calibration_directory, self.calibration_files = calibration_directory, calibration_files
        self.miniature, self.worlds, self.statistical_calls = miniature, {}, {}
        self.source_backups = {}
        if not miniature:
            require(calibration_directory is not None and type(calibration_files) is dict, "accepted pre-tag calibration required for full worlds")

    def _read(self, name):
        raw = (self.source_repo/name).read_bytes()
        require(digest(raw) == self.source_pins[name], "certified world source pin")
        return raw

    def install(self, root, recipe):
        root = Path(root)
        require(recipe["pairs"] == 500 and tuple(recipe["grid"]) == GRID, "worlds use full production cardinality")
        # Restore a prior synthetic source poison only in this disposable package.
        self.restore_sources()
        repo = root/"repo"; repo.mkdir()
        b, _, _, baselines = load_certified(self._read)
        f = fixture(repo, with_caps=False)
        f.battery = b
        f.data["battery_sha256"], f.data["levels_sha256"] = b.bytes_sha256, b.levels_sha256
        for name in ("baseline-outputs.jsonl", "baselines.json"):
            f.data["repo_pins"][PREFIX+name] = put(repo, PREFIX+name, self._read(PREFIX+name))
        class Characters:
            all_special_ids = [0]
            def encode(self, text, add_special_tokens=True): return list(map(ord, text))
            def decode(self, ids, skip_special_tokens=True): return "".join(map(chr, ids))
        caps = validate_caps(b, Characters())
        for key in ("pythia_1b", "olmo2_1b"):
            path = f"caps/{key}.json"
            sha = put(repo, path, {**caps, "assets": f.data["assets"][key]})
            f.data["cap_receipts"][key] = path
            f.data["repo_pins"][path] = f.data["prereg"]["bindings"][path] = sha
        if self.miniature:
            sha = put(f.root, "statistics/calibration/calibration.json", {"fixture": True, "production": False, "stage": "calibration"})
        else:
            copied = copy_accepted_calibration(self.calibration_directory, f.root, accepted_files=self.calibration_files)
            sha = copied["calibration.json"]
        path = "statistics/calibration/calibration.json"
        f.data["calibration"] = {"path": path, "sha256": sha, "commit": C}
        f.data["repo_pins"]["campaign/"+path] = f.data["prereg"]["bindings"]["campaign/"+path] = sha
        def campaign():
            from exp7core.campaign import Campaign
            original = f.campaign()
            cls = SyntheticPowerCampaign if self.miniature else Campaign
            c = cls(f.root, repo, trust_path=f"trust-{f.serial}.json", trust_sha256=original.trust.sha, git=FakeGit())
            c._battery, c._baselines = b, baselines
            return c
        with campaign() as c:
            for model in ("pythia_1b", "olmo2_1b", "twin"):
                predictor_preflight(c, model, backend=RecipeBackend(c, recipe))
                collect_predictor(c, model, backend=RecipeBackend(c, recipe))
            seal_predictors(c)
        f.refresh_seal(); f.stage_grant("power")
        c = campaign()
        adapter = authority(c, root/"power-authority.json", "power", adapter_class=FullCardinalityMiniatureAdapter if self.miniature else FullDefaultAdapter)
        if not self.miniature:
            result = power.run(adapter)
        else:
            def operation(provenance):
                battery = load_battery(adapter.battery())
                predictors = load_predictors(adapter.predictor_data(), battery)
                return {**power.assemble(predictors, battery, adapter.verify_predictor_seal(), provenance, spec=MINI_POWER), "fixture": True}
            result = stage(adapter, "power", operation, production=False)
        require(result["state"] == "COMPLETE", "world power setup refused")
        path = "statistics/power/power.json"
        f.data["power"] = {"path": path, "sha256": digest((f.root/path).read_bytes()), "commit": C}
        for scope in ("outcome-preflight", "outcome-collection", "outcome-underpowered-run"):
            f.stage_grant(scope)
        def power_check(record, c):
            if self.miniature:
                _, geometry = sealed_predictor_geometry(c)
                return verify_miniature_power(record, f.data["predictor_seal"]["sha256"], b.bytes_sha256, geometry=geometry)
            return collection_power_validator(record, c)
        with campaign() as c:
            collect_endpoint(c, "fakehost", backend=RecipeBackend(c, recipe), power_validator=power_check)
            collect_outcomes(c, backend=RecipeBackend(c, recipe), power_validator=power_check)
            complete_campaign(c)
        f.refresh_complete(); f.stage_grant("analysis")
        c = campaign()
        adapter = authority(c, root/"analysis-authority.json", "analysis", adapter_class=FullCardinalityMiniatureAdapter if self.miniature else FullDefaultAdapter)
        self.worlds[str(root)] = {"fixture": f, "adapter": adapter, "poison": None}
        self.statistical_calls[str(root)] = 0

    def export(self, root, output):
        """Immutable ready-to-analyze raw fixture for separate cold workers.

        Workers copy the same sealed bytes, including actual preflight timings;
        regenerating a producer twice would conflate timing with numerical RNG.
        """
        from exp7ops.evidence import snapshot, once
        item = self.worlds[str(root)]; f, a = item["fixture"], item["adapter"]
        require(not (f.root/"statistics/analysis").exists(), "export before one-time analysis")
        value = {"schema": "exp7.synthetic-producer-export.v1", "miniature": self.miniature,
                 "repo": str(f.repo), "repo_files": snapshot(f.repo),
                 "trust_path": f"trust-{f.serial}.json", "trust_sha256": a.collection.trust.sha,
                 "authority": a._authority_read(), "source_repo": str(self.source_repo), "source_pins": self.source_pins,
                 "fake_git": True, "fake_model_outputs": True}
        once(output, value)
        return digest(Path(output).read_bytes())

    def analyze(self, root):
        key = str(root); item = self.worlds[key]; adapter = item["adapter"]
        original = analyzer.analyze_loaded
        def observed(*args, **kwargs):
            self.statistical_calls[key] += 1
            result = original(*args, **kwargs)
            if item["poison"] == "HALTED-before-final":
                put(item["fixture"].root, "HALTED.json", {"fixture": "late synthetic fault"})
            if item["poison"] == "entry-only-pin":
                (item["fixture"].repo/"source.txt").write_bytes(b"late source drift")
            return result
        analyzer.analyze_loaded = observed
        before = self.statistical_calls[key]
        try:
            if self.miniature:
                shape = Shape(n=500, grid=GRID, permutations=3, bootstraps=1)
                result = stage(adapter, "analysis", lambda p: analyzer._operation(adapter, p, shape, production=False), production=False)
            else:
                result = analyzer.run(adapter)
        finally:
            analyzer.analyze_loaded = original
        # Harness-only observation, never supplied as input or to the analyzer.
        return {"report": result, "statistics_executed": self.statistical_calls[key] > before}

    def summarize(self, wrapper):
        report = wrapper["report"]
        if report["state"] == "INSUFFICIENT_DATA":
            return {"states": {p: "INSUFFICIENT_DATA" for p in ("pythia_1b", "olmo2_1b")}, "secondaries": [],
                    "licence": "does not identify an internal algorithm", "statistics_executed": wrapper["statistics_executed"]}
        require(len(report["secondaries"]) == 8, "world report omitted a secondary")
        return {"states": {p: v["state"] for p, v in report["primary"].items()}, "secondaries": list(range(1, 9)),
                "licence": "On this fixed battery; does not identify an internal algorithm. "+report["primary"]["pythia_1b"]["licence"],
                "statistics_executed": wrapper["statistics_executed"]}

    def scientific_inputs(self, root):
        from exp7ops.evidence import snapshot
        f = self.worlds[str(root)]["fixture"]
        return {n: sha for n, sha in snapshot(f.root).items() if n.startswith(("units/", "preflight/", "receipts/")) or n == "predictor-seal.json"}

    def restore_sources(self):
        for path, raw in self.source_backups.items():
            path.write_bytes(raw)
        self.source_backups.clear()

    def success_published(self, root):
        directory = self.worlds[str(root)]["fixture"].root/"statistics/analysis"
        return any((directory/name).exists() for name in ("COMPLETE.json", "analysis.json", "REPORT.md"))

    def clone_export(self, export, sha, root):
        from freeze_workers import open_export
        f, adapter = open_export(export, sha, root, miniature=self.miniature)
        self.worlds[str(root)] = {"fixture": f, "adapter": adapter, "poison": None}
        self.statistical_calls[str(root)] = 0

    def claimed(self, root):
        f = self.worlds[str(root)]["fixture"]
        return (f.root/"statistics/analysis/CLAIM.json").is_file() and (f.root/"claims/analysis.CLAIM").is_file()

    def poison(self, root, case):
        item = self.worlds[str(root)]; f = item["fixture"]; item["poison"] = case
        main = f.root/"units/predictor/pythia_1b/deduction/q0"
        if case in ("entry-only-pin", "HALTED-before-final"):
            return  # injected during computation; execution is truthfully counted
        if case == "duplicate-once-claim":
            (f.root/"statistics/analysis").mkdir()
            put(f.root, "statistics/analysis/CLAIM.json", {"fixture": "already claimed"})
            return
        if case in ("missing-sham", "missing-twin", "missing-checkpoint"):
            name = {"missing-sham": "units/predictor/pythia_1b/deduction/q1s/DONE.json",
                    "missing-twin": "units/predictor/twin/deduction/q0/DONE.json", "missing-checkpoint": "units/outcome/40000/DONE.json"}[case]
            (f.root/name).unlink()
            return
        if case == "wrong-target":
            from exp7core.scoring import answer, normalize
            path = main/"raw.jsonl"
            counts = []
            for pair, line in zip(f.battery.family("deduction"), path.read_bytes().splitlines()):
                values = [normalize(v, pair.answer_type) for v in json.loads(line)["draws"]]
                # Coherent stored diagnostic from the WRONG target designation.
                a1, a0 = [answer(v, pair.answer_type) for v in pair.targets]
                counts.append((values.count(a0), values.count(a1)))
            rec = json.loads((main/"record.json").read_bytes())
            rec["counts_sha256"] = digest(canonical(counts))
            (main/"record.json").write_bytes(canonical(rec))
            put(main, "DONE.json", {"raw.jsonl": digest(path.read_bytes()), "record.json": digest((main/"record.json").read_bytes())})
            return
        if case in ("unequal-k", "duplicate-row", "shared-stream"):
            path = main/"raw.jsonl"
            rows = [json.loads(line) for line in path.read_bytes().splitlines()]
            if case == "unequal-k": rows[0]["draws"].pop()
            elif case == "duplicate-row": rows[1] = deepcopy(rows[0])
            elif case == "shared-stream": rows[1]["stream_seed"] = rows[0]["stream_seed"]
            path.write_bytes(b"".join(canonical(row) for row in rows))
            return
        if case in ("wrong-host", "wrong-model-digest", "swapped-loaders"):
            path = f.root/"receipts/outcome-40000.json"
            record = json.loads(path.read_bytes())
            if case == "wrong-host": record["host"]["host_id"] = "wrong"
            elif case == "wrong-model-digest": record["model"]["tensor_digest"] = digest(b"wrong")
            else: record["loader"] = "thin"
            path.write_bytes(canonical(record)); return
        if case in ("endpoint-count-only-match", "anchor-mismatch"):
            name = "units/endpoint/fakehost/thin" if case.startswith("endpoint") else "units/anchors/pythia_1b/add_base8"
            path = f.root/name/"raw.jsonl"
            rows = [json.loads(line) for line in path.read_bytes().splitlines()]
            if case.startswith("endpoint"):
                # Same normalized correctness bits, genuinely different strings.
                rows[0]["draws"][0] = " "+rows[0]["draws"][0]
            else:
                key = next(iter(rows[0]["draws"]))
                rows[0]["draws"][key][0] = " "+rows[0]["draws"][key][0]
            path.write_bytes(b"".join(canonical(row) for row in rows))
            return
        if case in ("seal-after-outcome", "power-after-outcome"):
            # Override only the fake Git observation, not any production method.
            # Independently simulated DAG has this artifact after its consumer.
            git = item["adapter"].collection.trust.git
            original = git.ancestor
            bad_pair = (f.data["predictor_tag"]["commit"], f.data["power"]["commit"]) if case.startswith("seal") else (f.data["power"]["commit"], f.data["complete"]["commit"])
            def chronology(older, newer):
                require((older, newer) != bad_pair, "synthetic Git DAG: sealed artifact is not prior to consumer")
                return original(older, newer)
            git.ancestor = chronology
            return
        if case == "malformed-power":
            put(f.root, "statistics/power/power.json", {"fixture": True, "declarations": {}})
            return
        if case == "self-pin":
            path = f.root/"predictor-seal.json"
            value = json.loads(path.read_bytes())
            value["bindings"]["predictor-seal.json"] = digest(path.read_bytes())
            path.write_bytes(canonical(value))
            return
        if case in ("transient-unpinned-import", "unpinned-read"):
            c = item["adapter"].collection
            original = c.statistics_bindings
            def touched(stage):
                path = f.repo/("transient_helper.py" if case.startswith("transient") else "unpinned-input.txt")
                path.write_bytes(b"VALUE = 7\n")
                try:
                    if case.startswith("transient"):
                        # Executed-filename tracing also covers a removed alias.
                        import sys
                        from types import ModuleType
                        alias = ModuleType("world_transient_helper")
                        alias.__file__ = str(path)
                        sys.modules[alias.__name__] = alias
                        try:
                            exec(compile(b"VALUE = 7\n", str(path), "exec"), alias.__dict__)
                        finally:
                            sys.modules.pop(alias.__name__, None)
                    else:
                        path.read_bytes()
                finally:
                    path.unlink()
                return original(stage)
            c.statistics_bindings = touched
            return
        if case in ("changed-init", "missing-secondary"):
            import exp7stats
            folder = Path(exp7stats.__file__).resolve().parent
            marker = folder.parent/"DISPOSABLE-SYNTHETIC-SOURCE.json"
            require(marker.is_file() and json.loads(marker.read_bytes()) == {"synthetic_only": True},
                    "source poison requires disposable worker package")
            path = folder/("__init__.py" if case == "changed-init" else "secondaries.py")
            before = path.read_bytes(); self.source_backups[path] = before
            if case == "changed-init":
                path.write_bytes(before+b"\nSYNTHETIC_POISON = True\n")
            else:
                needle = b"    return report, main_intervals"
                require(before.count(needle) == 1, "exact secondary source mutation")
                path.write_bytes(before.replace(needle, b"    report.pop('S8_label_reversal')\n"+needle))
            return
        raise ValueError("unknown full-world poison")
