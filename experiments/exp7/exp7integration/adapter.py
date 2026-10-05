"""Collection immutable/raw API -> statistics interface v4; no model imports."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from exp7core.contract import Battery, Pair
from exp7core.records import strict_json
from exp7stats.common import (ARMS, FAMILIES, GRID, PREDICTORS, SCHEMA, decode,
                              digest, pin, require, receipt, entry_receipt)
from .inventory import safe, relative, power_inventory, ReadOnlyCampaign

REQUIRED_BINDINGS = {"trust_sha256", "battery_sha256", "source_manifest_sha256", "code_manifest_sha256"}


def keys(value, wanted, message):
    require(type(value) is dict and set(value) == set(wanted), message)


def sequence(value, n, label):
    require(type(value) in (tuple, list) and len(value) == n, label)
    return value


class StatsCampaignAdapter:
    """The collection Campaign supplied here must still be UNENTERED.

    `authority_sha256` is an independent deployment constant for an externally
    secured adapter-authority file, not learned from campaign outputs. Keeping
    it outside the collection repo avoids a cyclic trust-SHA/manifest pin.
    Production dimensions are literals; no n/grid/B constructor switches exist.
    The collection's entryexit consumes its separate owner grant AFTER the stats
    CLAIM and performs its full source/import/read/provenance gates.
    """
    def __init__(self, campaign, *, authority_path, authority_sha256):
        require(campaign is not None, "missing collection Campaign")
        self.collection = campaign
        self.root, self.repo = Path(campaign.root), Path(campaign.repo)
        self.authority_path = Path(authority_path).absolute()
        require(not self.authority_path.is_relative_to(self.repo.absolute()), "adapter authority must be outside collection repo")
        self.authority_sha256 = pin(authority_sha256)
        self._stage = None
        self._authority = None
        self._entry_bindings = None
        self._battery_identity = None

    def _dimensions(self):
        return 500, GRID, True

    def _access(self, stages=("analysis", "power")):
        require(self._stage in stages, "raw/receipt access outside authorized statistics stage")

    def _source_paths(self):
        return {p.resolve().relative_to(self.repo.resolve()).as_posix(): p
                for p in Path(__file__).parent.glob("*.py")}

    def _authority_read(self):
        raw = safe(Path(self.authority_path.anchor), self.authority_path.relative_to(self.authority_path.anchor).as_posix()).read_bytes()
        require(digest(raw) == self.authority_sha256, "adapter authority SHA mismatch")
        value = strict_json(raw)
        keys(value, ("schema", "collection_bindings", "adapter_sources", "receipts", "power_inventory", "calibration_sha256"),
             "adapter authority schema")
        require(value["schema"] == "exp7.adapter-authority.v1", "adapter authority version")
        require(type(value["adapter_sources"]) is dict and value["adapter_sources"], "adapter source pins required")
        actual_sources = self._source_paths()
        require(set(value["adapter_sources"]) == set(actual_sources), "complete adapter source closure")
        for name, sha in value["adapter_sources"].items():
            require(not actual_sources[name].is_symlink() and digest(actual_sources[name].read_bytes()) == pin(sha), f"adapter source drift: {name}")
        return value

    def _bindings(self):
        value = self.collection.bindings()
        require(type(value) is dict and REQUIRED_BINDINGS <= set(value), "collection named bindings")
        require(all(type(k) is str and k for k in value), "collection binding name")
        for sha in value.values():
            pin(sha)
        require(value == self._authority["collection_bindings"], "independent collection identity/code/source binding")
        if self._entry_bindings is not None:
            require(value == self._entry_bindings, "collection binding drift")
        return deepcopy(value)

    @contextmanager
    def entryexit(self, stage):
        require(stage in ("analysis", "power") and self._stage is None,
                "adapter supports analysis/power only; use standalone CalibrationContext before tag")
        production = self._dimensions()[2]
        claim = strict_json(safe(self.root, f"statistics/{stage}/CLAIM.json").read_bytes())
        require(claim == {"schema": SCHEMA, "stage": stage, "production": production}, "stats CLAIM must precede collection authority")
        guard = None
        entry_inventory = None
        try:
            # Nothing that reads battery/raw/adapter-authority has happened yet.
            with self.collection.entryexit(stage) as collection_receipt:
                self._authority = self._authority_read()
                bindings = self._bindings()
                require(collection_receipt == bindings, "collection entry yields genuine bindings only")
                self._entry_bindings = bindings
                self._stage = stage
                actual = entry_receipt(self.collection.statistics_bindings(stage))
                require(actual["provenance_sha256"] == bindings["trust_sha256"], "statistics provenance identity")
                for field in ("battery", "code_manifest", "source_manifest"):
                    require(actual["input_sha256"].get(field) == bindings[field + "_sha256"], "statistics named source identity")
                inputs = {**actual["input_sha256"], **bindings,
                          "adapter_authority": self.authority_sha256,
                          **{f"adapter_source:{p}": sha for p, sha in self._authority["adapter_sources"].items()}}
                provenance = {"provenance_sha256": bindings["trust_sha256"], "input_sha256": inputs,
                              "collection_bindings": deepcopy(bindings)}
                if stage == "power":
                    self.collection.require_preoutcome()
                    self._inventory_roots()
                    self._register_inventory_inputs()
                    calibration_sha = pin(self._authority["calibration_sha256"])
                    require(actual["input_sha256"].get("calibration") == calibration_sha, "calibration authority identity")
                    require(digest(safe(self.root, "statistics/calibration/calibration.json").read_bytes()) == calibration_sha,
                            "accepted calibration must be copied at immutable campaign path")
                    inputs["calibration"] = calibration_sha
                    inventory, entry_inventory = power_inventory(self.root, self._authority["power_inventory"], production=production, repo=self.repo)
                    provenance["contact_inventory"] = inventory
                    inputs["contact_inventory"] = digest(inventory)
                    guard = ReadOnlyCampaign(self.root, additional_roots=[self.repo / p for p in self._authority["power_inventory"]["repository_roots"]])
                    guard.start()
                try:
                    yield provenance
                finally:
                    require(self._authority_read() == self._authority, "adapter authority changed at exit")
                    self._bindings()
                    require(self.collection.statistics_bindings(stage) == actual, "statistics binding drift at exit")
                    if stage == "power":
                        self.collection.require_preoutcome()
                        inventory, current = power_inventory(self.root, self._authority["power_inventory"], production=production, repo=self.repo)
                        require(current == entry_inventory and inventory == provenance["contact_inventory"], "contact inventory entry/exit drift")
                        guard.check()
            # Collection exit may itself discover or (incorrectly) create state.
            if stage == "power":
                _, current = power_inventory(self.root, self._authority["power_inventory"], production=production, repo=self.repo)
                require(current == entry_inventory, "contact inventory changed in collection exit")
                guard.check()
        finally:
            if guard is not None:
                guard.stop()
            self._stage = self._authority = self._entry_bindings = self._battery_identity = None

    def _inventory_roots(self):
        """Actual G2 grant locations supplement standard root names.

        The trust object was independently loaded by Campaign and its formal
        grants are verified there. Names may be nested anywhere in repo; every
        configured grant parent must be scanned, including unconsumed grants.
        """
        trust = getattr(self.collection, "trust", None)
        if trust is None:
            # Strict fake protocol has no hidden trust internals. Its published
            # methods still supply all pins; actual Campaign always has Trust.
            return
        roots = self._authority["power_inventory"]["repository_roots"]
        for grant in trust.data["grants"].values():
            name = relative(grant["path"])
            require(any(Path(name).is_relative_to(Path(p)) for p in roots), "actual collection grant root omitted from inventory")

    def _register_inventory_inputs(self):
        """Enroll independent expected pins in G2's trace, never observed hashes.

        A new owner CLAIM is created before Campaign entry, so its immutable
        expected bytes can be supplied by the independent deployment inventory.
        This also covers operational receipts not otherwise read by collection.
        Every registered input is rehashed by BOTH inventory and G2 trace exit.
        """
        trust = getattr(self.collection, "trust", None)
        if trust is None:
            return
        for row in self._authority["power_inventory"]["entries"]:
            name = row["path"]
            path = safe(self.repo, name[11:]) if name.startswith("repository/") else safe(self.root, name)
            key, sha = str(path.resolve()), pin(row["sha256"])
            require(key not in trust.trace.allowed or trust.trace.allowed[key] == sha, "inventory conflicts with independent collection pin")
            trust.trace.allowed[key] = sha

    @contextmanager
    def _transform(self):
        self._access()
        before = self._bindings()
        battery = self.collection.battery()
        require(type(battery) is Battery and type(battery.pairs) is tuple, "immutable certified Battery required")
        require(battery.bytes_sha256 == before["battery_sha256"], "battery identity mismatch")
        identity = digest(asdict(battery))
        if self._battery_identity is not None:
            require(identity == self._battery_identity, "battery changed across transforms")
        self._battery_identity = identity
        n = self._dimensions()[0]
        require(len(battery.pairs) == 4*n, "exact battery pair count")
        for f in FAMILIES:
            rows = battery.family(f)
            sequence(rows, n, "family battery coverage")
            for i, p in enumerate(rows):
                require(type(p) is Pair and p.family == f and type(p.index) is int and p.index == i
                        and p.pair_id == f"{f}:{i:04d}", "certified pair identity/order")
                require(type(p.targets) is tuple and len(p.targets) == 2 and
                        all(type(v) is str for v in p.targets), "certified target identity")
                require(type(p.prompts) is tuple and len(p.prompts) == 4 and
                        all(type(v) is str for v in p.prompts), "certified prompts")
        try:
            yield battery
        finally:
            require(self._bindings() == before, "code/battery pins changed during transform")
            require(digest(asdict(battery)) == identity and
                    digest(asdict(self.collection.battery())) == identity, "battery mutated during transform")

    def battery(self):
        with self._transform() as battery:
            n = self._dimensions()[0]
            base = self.collection.base_assignments()
            keys(base, FAMILIES, "certified base families")
            for f in FAMILIES:
                sequence(base[f], n, "exact base assignment coverage")
                require(all(type(v) is str and v for v in base[f]), "certified base IDs")
            catalog = self.collection.baseline_catalog()
            raw = self.collection.baseline_draws()
            require(type(catalog) is dict and len(catalog) == 21 and
                    all(type(v) is str and v for v in catalog), "baseline_missing: all21 methods required")
            keys(raw, catalog, "baseline_missing: raw method inventory")
            counts = {"applicable_cells": 0, "not_applicable_cells": 0}
            for name, families in catalog.items():
                keys(families, FAMILIES, "baseline_missing: all84 catalog cells required")
                applicable = {f for f in FAMILIES if families[f].get("applicable") is True}
                keys(raw[name], applicable, "baseline_missing: applicable raw family inventory")
                for f, cell in families.items():
                    keys(cell, ("applicable", "reason", "abstentions", "emissions", "prompts"), "baseline_missing: catalog cell schema")
                    require(type(cell["applicable"]) is bool, "baseline_missing: unknown applicability")
                    if cell["applicable"]:
                        counts["applicable_cells"] += 1
                        rows = sequence(raw[name][f], n, "baseline_missing: raw pair coverage")
                        abstentions = 0
                        for row in rows:
                            keys(row, ARMS, "baseline_missing: raw arm coverage")
                            require(all(v is None or type(v) is str for v in row.values()), "baseline raw types")
                            abstentions += sum(v is None for v in row.values())
                        require(cell["reason"] is None and type(cell["prompts"]) is int and cell["prompts"] == n*4
                                and type(cell["abstentions"]) is int and cell["abstentions"] == abstentions
                                and type(cell["emissions"]) is int and cell["emissions"] == n*4-abstentions,
                                "baseline catalog abstention/emission counts")
                    else:
                        counts["not_applicable_cells"] += 1
                        require(type(cell["reason"]) is str and cell["reason"].strip(), "baseline N/A explicit reason")
                        # N/A numeric placeholders are preserved in the collection
                        # catalog; no N/A outputs or observed misses are invented.
            require(counts == {"applicable_cells": 49, "not_applicable_cells": 35}, "baseline_missing: certified 49/35 coverage")
            families = {}
            for f in FAMILIES:
                rows = []
                for i, pair in enumerate(battery.family(f)):
                    baselines = {}
                    for name in catalog:
                        cell = catalog[name][f]
                        if cell["applicable"]:
                            values = raw[name][f][i]
                            baselines[name] = {"status": "APPLICABLE", "na_reason": None,
                                               "outputs": {a: "" if values[a] is None else values[a] for a in ARMS},
                                               "abstained": {a: values[a] is None for a in ARMS}}
                        else:
                            baselines[name] = {"status": "NOT_APPLICABLE", "na_reason": cell["reason"],
                                               "outputs": None, "abstained": None}
                    rows.append({"id": pair.pair_id, "index": pair.index, "targets": list(pair.targets),
                                 "answer_type": pair.answer_type, "base": base[f][i],
                                 "prompts_sha256": {a: digest(pair.prompts[j].encode("utf-8")) for j, a in enumerate(ARMS)},
                                 "baselines": baselines})
                families[f] = rows
            return {"schema": "exp7.analysis-battery.v1", "sha256": battery.bytes_sha256,
                    "certificate_sha256": pin(battery.certificate_sha256), "levels_sha256": pin(battery.levels_sha256),
                    "baseline_ids": {f: list(catalog) for f in FAMILIES}, "baseline_coverage": counts, "families": families}

    def predictor_data(self):
        with self._transform() as battery:
            n = self._dimensions()[0]
            source = self.collection.predictor_draws()
            keys(source, (*PREDICTORS, "twin"), "raw predictor identities")
            out = {}
            for p, families in source.items():
                keys(families, FAMILIES, "raw predictor families")
                k = 16 if p == "twin" else 64
                out[p] = {}
                for f in FAMILIES:
                    rows = sequence(families[f], n, "raw predictor pair coverage")
                    converted = []
                    for pair, row in zip(battery.family(f), rows):
                        sequence(row, 4, "raw predictor arm coverage")
                        draws = {}
                        for arm, values in zip(ARMS, row):
                            sequence(values, k, "raw predictor draw coverage")
                            require(all(type(v) is str for v in values), "model raw None/non-string forbidden")
                            draws[arm] = list(values)
                        converted.append({"id": pair.pair_id, "draws": draws})
                    out[p][f] = converted
            return {"schema": "exp7.analysis-predictors.v1", "trained": {p: out[p] for p in PREDICTORS}, "twin": out["twin"]}

    def outcomes(self):
        self._access(("analysis",))
        with self._transform() as battery:
            n, grid, _ = self._dimensions()
            source = self.collection.outcome_draws()
            keys(source, FAMILIES, "outcome family coverage")
            families = {}
            for f in FAMILIES:
                rows = sequence(source[f], n, "outcome pair coverage")
                converted = []
                for pair, row in zip(battery.family(f), rows):
                    sequence(row, len(grid), "outcome exact26 step coverage")
                    outputs = {}
                    for step, arms in zip(grid, row):
                        sequence(arms, 4, "outcome arm coverage")
                        require(all(type(v) is str for v in arms), "model raw None/non-string forbidden")
                        outputs[str(step)] = dict(zip(ARMS, arms))
                    converted.append({"id": pair.pair_id, "outputs": outputs})
                families[f] = converted
            return {"schema": "exp7.analysis-outcomes.v1", "grid": list(grid), "families": families}

    def _receipt(self, method, identity):
        self._access(("analysis",) if identity != "seal_sha256" else ("analysis", "power"))
        before = self._bindings()
        value = deepcopy(getattr(self.collection, method)())
        receipt(value, identity)
        require(value[identity] == pin(self._authority["receipts"].get(identity)), "independent canonical receipt identity")
        require(type(value.get("bindings")) is dict and value["bindings"], "canonical trust bindings required")
        for name, sha in value["bindings"].items():
            require(digest(safe(self.root, name).read_bytes()) == pin(sha), f"forged receipt binding: {name}")
        require(self._bindings() == before, "receipt binding drift")
        return value

    def verify_predictor_seal(self):
        value = self._receipt("seal_bindings", "seal_sha256")
        require(value.get("battery_sha256") == self._entry_bindings["battery_sha256"], "seal battery field/identity")
        return value

    def verify_power(self):
        value = self._receipt("power_bindings", "power_sha256")
        record = decode(value.get("record"))
        require(type(record) is dict and digest(record) == value["power_sha256"], "power record field/digest")
        require(value["bindings"].get("statistics/power/power.json") == value["power_sha256"], "canonical power path/hash")
        require(record.get("seal_sha256") == self._authority["receipts"].get("seal_sha256") and
                record.get("battery_sha256") == self._entry_bindings["battery_sha256"], "power seal/battery fields")
        if self._dimensions()[2]:
            for field in ("code_manifest", "source_manifest"):
                require(record.get("source_bindings", {}).get(field) == self._entry_bindings[field + "_sha256"],
                        f"power source binding field: {field}")
        return {**value, "record": record}

    def verify_complete(self):
        return self._receipt("complete_bindings", "complete_sha256")


class _SealedPredictorView(StatsCampaignAdapter):
    """Reuse the exact raw transforms within an ALREADY authenticated Campaign.

    Collection's outcome-authority callback has no new statistics stage/claim.
    This view reads only battery/control metadata and sealed predictor streams.
    It never calls verify_power, power_bindings or any outcome method.
    """
    def __init__(self, campaign):
        campaign._ready()
        self.collection = campaign
        self._entry_bindings = deepcopy(campaign.bindings())
        self._battery_identity = None

    def _access(self, stages=()):
        self.collection._ready()

    def _bindings(self):
        value = self.collection.bindings()
        require(value == self._entry_bindings and REQUIRED_BINDINGS <= set(value), "sealed raw mapping source drift")
        for sha in value.values():
            pin(sha)
        return deepcopy(value)


def sealed_predictor_geometry(campaign):
    """Independent x/composite-stratum geometry from genuine seal-only raw data."""
    from exp7stats.data import load_battery, load_predictors
    from exp7stats.power import predictor_geometry
    seal = campaign.seal_bindings()
    view = _SealedPredictorView(campaign)
    battery = load_battery(view.battery())
    require(battery.sha256 == seal["battery_sha256"], "geometry battery/seal binding")
    predictors = load_predictors(view.predictor_data(), battery)
    geometry = predictor_geometry(predictors)
    view._bindings()
    return seal, geometry


def collection_power_validator(record, campaign):
    """Saved arithmetic only, with geometry independent of every record field."""
    from exp7stats.power import verify_power_semantics
    seal, geometry = sealed_predictor_geometry(campaign)
    verify_power_semantics(decode(record), seal["seal_sha256"], seal["battery_sha256"], geometry=geometry)
    return None
