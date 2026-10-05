"""Strict fabricated implementation of ONLY the published collection contract.

Uses copied immutable core types and statistics raw fixture generator. Nothing
imports collection source. Miniature dimensions live in this TEST file only.
"""
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path
from copy import deepcopy
import json
from exp7core.contract import Battery, Pair
from exp7core.scoring import score_draws, outcome_counts
from exp7stats.common import (ARMS, FAMILIES, PREDICTORS, GRID, CONTACT_ROOTS, SCHEMA,
                              digest, dumps, require, require_preoutcome)
from exp7integration.adapter import StatsCampaignAdapter
from stats_fixtures import payloads

from testing_paths import ROOT, PACKAGE


def put(root, name, value):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if type(value) is bytes else dumps(value)
    path.write_bytes(raw)
    return digest(raw)


class StrictCollection:
    def __init__(self, root, *, n=24, grid=(1, 2, 3), stage="analysis", orientation=False):
        self.root, self.repo = Path(root), Path(root).parent / "repository"
        self.repo.mkdir()
        self.n, self.grid = n, grid
        self.events, self.hooks = [], {}
        self.active = False
        self.grant = True
        self.consumed = False
        self.fail_exit = False
        self.methods = tuple(f"baseline_{i:02d}" for i in range(21))
        b, p, o = payloads(n=n, grid=grid)
        pairs = []
        self.base = {}
        for f in FAMILIES:
            self.base[f] = tuple(json.dumps([f, i//8], separators=(",", ":")) for i in range(n))
            for row in b["families"][f]:
                pid = row["id"]
                pairs.append(Pair(f, row["index"], pid, tuple(f"question:{pid}:{a}" for a in ARMS),
                                  tuple(f"{pid}/{a}" for a in ARMS), tuple(row["targets"]), row["answer_type"],
                                  "synthetic_nominal", row["index"]//8, (f"source:{pid}",), '{"synthetic":true}'))
        self.b = Battery(tuple(pairs), digest(b"fixture certificate"), digest(b"fixture levels"), digest(b"temporary identity"))
        battery_sha = put(self.root, "battery.json", asdict(self.b))
        self.b = replace(self.b, bytes_sha256=battery_sha)
        self.p = {name: {} for name in (*PREDICTORS, "twin")}
        self.o = {}
        for f in FAMILIES:
            for name in self.p:
                src = p["twin"][f] if name == "twin" else p["trained"][name][f]
                self.p[name][f] = tuple(tuple(tuple(row["draws"][a]) for a in ARMS) for row in src)
            self.o[f] = tuple(tuple(tuple(row["outputs"][str(t)][a] for a in ARMS) for t in grid) for row in o["families"][f])
        if orientation:
            self.p = {p: {f: tuple(tuple(tuple(f"{p}/{f}/{i}/{a}/{j}" for j in range(16 if p == "twin" else 64))
                                           for a in ARMS) for i in range(n)) for f in FAMILIES} for p in self.p}
            self.o = {f: tuple(tuple(tuple(f"{f}/{i}/{t}/{a}" for a in ARMS) for t in grid) for i in range(n)) for f in FAMILIES}
        self.catalog, self.raw_baselines = {}, {}
        for m, name in enumerate(self.methods):
            self.catalog[name], self.raw_baselines[name] = {}, {}
            for fi, f in enumerate(FAMILIES):
                applicable = fi*21+m < 49
                if applicable:
                    rows = tuple({a: None if (i+j+m)%11 == 0 else "" if (i+j+m)%13 == 0
                                  else ("alpha" if j%2 == 0 else "beta") for j, a in enumerate(ARMS)} for i in range(n))
                    self.raw_baselines[name][f] = rows
                    abst = sum(v is None for r in rows for v in r.values())
                    self.catalog[name][f] = {"applicable": True, "reason": None, "abstentions": abst,
                                            "emissions": 4*n-abst, "prompts": 4*n}
                else:
                    self.catalog[name][f] = {"applicable": False, "reason": f"certified N/A {name}/{f}",
                                            "abstentions": None, "emissions": None, "prompts": None}
        self.binding_values = {
            "trust_sha256": put(self.root, "trust.json", {"fixture": "independent trust"}),
            "battery_sha256": battery_sha,
            "source_manifest_sha256": put(self.root, "source-manifest.json", {"fixture": "source pins"}),
            "code_manifest_sha256": put(self.root, "code-manifest.json", {"fixture": "code pins"})}
        self.seal_sha = put(self.root, "seal.json", {"fixture": "sealed predictors", "battery_sha256": battery_sha})
        self.seal = {"seal_sha256": self.seal_sha, "battery_sha256": battery_sha,
                     "bindings": {"seal.json": self.seal_sha, "battery.json": battery_sha}}
        self.power_record = {"fixture": True, "seal_sha256": self.seal_sha, "battery_sha256": battery_sha,
                             "source_bindings": {"code_manifest": self.binding_values["code_manifest_sha256"],
                                                 "source_manifest": self.binding_values["source_manifest_sha256"]}}
        self.power = None
        self.complete = None
        self.stage = stage
        if stage == "analysis":
            power_sha = put(self.root, "statistics/power/power.json", self.power_record)
            self.power = {"power_sha256": power_sha, "record": self.power_record,
                          "bindings": {"statistics/power/power.json": power_sha}}
            complete_sha = put(self.root, "complete.json", {"fixture": "independent complete"})
            self.complete = {"complete_sha256": complete_sha, "bindings": {"complete.json": complete_sha}}
        else:
            put(self.root, "statistics/calibration/calibration.json", {"fixture": "accepted SHA only, no calibration claim"})
            put(self.root, "grants/power.json", {"schema": "fixture.grant", "stage": "power"})
        self.authority_name = self.root.parent / f"{self.root.name}-authority.json"
        self.authority = self.make_authority()
        self.save_authority()

    def make_authority(self):
        source_root = PACKAGE / "exp7integration"
        entries = []
        if self.stage == "power":
            for path in sorted(self.root.rglob("*")):
                if path.is_file():
                    name = path.relative_to(self.root).as_posix()
                    phase = "calibration" if name.startswith("statistics/calibration/") else "power" if name.startswith("grants/") else "predictor"
                    entries.append({"path": name, "phase": phase, "kind": "grant" if name.startswith("grants/") else "operation", "sha256": digest(path.read_bytes())})
            entries.append({"path": "claims/power.json", "phase": "power", "kind": "phase",
                            "sha256": digest({"stage": "power", "consumed": True})})
        return {"schema": "exp7.adapter-authority.v1", "collection_bindings": deepcopy(self.binding_values),
                "adapter_sources": {p.relative_to(PACKAGE).as_posix(): digest(p.read_bytes()) for p in source_root.glob("*.py")},
                "receipts": {"seal_sha256": self.seal_sha, **({"power_sha256": self.power["power_sha256"], "complete_sha256": self.complete["complete_sha256"]} if self.power else {})},
                "power_inventory": {"covered_roots": list(CONTACT_ROOTS), "repository_roots": list(CONTACT_ROOTS)+["receipts", "preflight"], "entries": entries},
                "calibration_sha256": digest((self.root / "statistics/calibration/calibration.json").read_bytes()) if self.stage == "power" else None}

    def save_authority(self):
        self.authority_sha = put(self.authority_name.parent, self.authority_name.name, self.authority)

    def adapter(self, *, miniature=True):
        cls = MiniatureAdapter if miniature else FullDimensionAdapter
        return cls(self, authority_path=self.authority_name, authority_sha256=self.authority_sha)

    def event(self, name):
        require(self.active, f"fake collection unauthorized read: {name}")
        self.events.append(name)
        if name in self.hooks:
            self.hooks[name](self)

    @contextmanager
    def entryexit(self, stage):
        require(not self.active and not self.consumed, "UNENTERED unused collection authority required")
        require((self.root / f"statistics/{stage}/CLAIM.json").is_file(), "stats claim first")
        self.events.append("claim_observed")
        require(self.grant, "independent grant absent")
        self.consumed = True
        self.events.append("grant_consumed")
        if stage == "power":
            put(self.root, "claims/power.json", {"stage": "power", "consumed": True})
        self.active = True
        try:
            self.events.append("entered")
            yield deepcopy(self.binding_values)
        finally:
            self.events.append("exit")
            if "exit" in self.hooks:
                self.hooks["exit"](self)
            self.active = False
            require(not self.fail_exit, "collection exit source/receipt drift")

    def bindings(self):
        self.event("bindings")
        return deepcopy(self.binding_values)

    def statistics_bindings(self, stage):
        self.event("statistics_bindings")
        return {"provenance_sha256": self.binding_values["trust_sha256"], "input_sha256": {
            "battery": self.binding_values["battery_sha256"],
            "code_manifest": self.binding_values["code_manifest_sha256"],
            "source_manifest": self.binding_values["source_manifest_sha256"],
            "normalizer": digest(b"fixture-normalizer"),
            **({"calibration": self.authority["calibration_sha256"]} if stage == "power" else {})}}

    def battery(self):
        self.event("battery")
        return self.b

    def base_assignments(self):
        self.event("base_assignments")
        return deepcopy(self.base)

    def baseline_catalog(self):
        self.event("baseline_catalog")
        return deepcopy(self.catalog)

    def baseline_draws(self):
        self.event("baseline_draws")
        return deepcopy(self.raw_baselines)

    def predictor_draws(self):
        self.event("predictor_draws")
        return deepcopy(self.p)

    def outcome_draws(self):
        self.event("outcome_draws")
        self.verify_complete()
        return deepcopy(self.o)

    def predictor_data(self):
        self.event("SCORES_MUST_NOT_BE_USED")
        return {p: {f: (self.b.family(f), tuple(score_draws(dict(zip(ARMS, row)), pair.targets, pair.answer_type,
                                                         k=16 if p == "twin" else 64) for pair, row in zip(self.b.family(f), rows)))
                    for f, rows in families.items()} for p, families in self.p.items()}

    def baselines(self):
        self.event("SCORES_MUST_NOT_BE_USED")
        return {name: {f: None if f not in families else tuple(score_draws({a: [row[a] or ""] for a in ARMS}, pair.targets, pair.answer_type, k=1)
                                                             for pair, row in zip(self.b.family(f), families[f])) for f in FAMILIES}
                for name, families in self.raw_baselines.items()}

    def outcomes(self):
        self.event("SCORES_MUST_NOT_BE_USED")
        return {f: tuple(outcome_counts({t: dict(zip(ARMS, arm)) for t, arm in zip(self.grid, row)}, pair.targets, pair.answer_type, steps=self.grid)
                         for pair, row in zip(self.b.family(f), rows)) for f, rows in self.o.items()}

    def verify_predictor_seal(self):
        self.event("verify_predictor_seal")
        return {"schema": "fixture-original-seal"}

    def seal_bindings(self):
        self.verify_predictor_seal()
        return deepcopy(self.seal)

    def verify_power(self):
        self.event("verify_power")
        return deepcopy(self.power_record)

    def power_bindings(self):
        self.verify_power()
        return deepcopy(self.power)

    def verify_complete(self):
        self.event("verify_complete")
        self.verify_predictor_seal()
        self.verify_power()
        return None

    def complete_payload(self):
        self.verify_complete()
        return {"schema": "exp7.complete.v1", "fixture": True}

    def complete_bindings(self):
        self.verify_complete()
        return deepcopy(self.complete)

    def require_preoutcome(self):
        self.event("require_preoutcome")
        require_preoutcome(self.root)


class MiniatureAdapter(StatsCampaignAdapter):
    """Test-only override: never shipped as a production entrypoint."""
    def _dimensions(self):
        return self.collection.n, self.collection.grid, False

    def _source_paths(self):
        # Pure source bytes live outside an intentionally tiny fake repo.
        return {p.relative_to(PACKAGE).as_posix(): p for p in (PACKAGE/"exp7integration").glob("*.py")}


class FullDimensionAdapter(MiniatureAdapter):
    def _dimensions(self):
        return StatsCampaignAdapter._dimensions(self)
