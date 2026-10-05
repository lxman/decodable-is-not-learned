"""Fixed stage bindings to delivered collection/statistics; no import-by-string."""
from pathlib import Path
from exp7ops.evidence import require, strict, digest, canonical, pin, verify_files, snapshot, once
from exp7ops.operator import Approval
from exp7core.campaign import Campaign
from exp7core.entrypoints import run_collection
from exp7core.provenance import LIVE
from exp7core.records import validate_record
from .adapter import StatsCampaignAdapter, collection_power_validator

STAGE_MAP = {"predictor-preflight": "predictor-preflight", "predictor": "predictor-collection",
             "seal": "predictor-seal", "power": "power", "outcome-preflight": "outcome-preflight",
             "outcome": "outcome-collection", "verdict": "analysis", "watch": "watch"}
MODELS = ("pythia_1b", "olmo2_1b", "twin")


class FixedStageDeployment:
    """Every configuration byte is fixed by an independently supplied digest.

    Scientific dimensions/backend names are never configuration options. Tests
    inject callables directly; the fixed CLI always uses these named defaults.
    """
    def __init__(self, config_path, config_sha256, *, collection=run_collection,
                 campaign_factory=Campaign, backend=LIVE, git=LIVE, watch_factory=None):
        self.path, self.sha = Path(config_path), pin(config_sha256)
        raw = self.path.read_bytes()
        require(digest(raw) == self.sha, "independent deployment config SHA")
        self.data = strict(raw)
        require(self.data.get("schema") == "exp7.fixed-deployment.v1", "deployment schema")
        self.repo, self.root = Path(self.data["repo"]), Path(self.data["root"])
        require(self.repo.is_absolute() and self.root.is_absolute(), "absolute deployment roots")
        require(set(self.data["stages"]) == set(STAGE_MAP), "complete fixed deployment stage map")
        require(callable(collection) and callable(campaign_factory), "fixed collection ports")
        require(backend is LIVE or backend and callable(getattr(backend, "open", None)), "empty deployment backend")
        self.collection_run, self.campaign_factory = collection, campaign_factory
        self.backend, self.git, self.watch_factory = backend, git, watch_factory
        self.check_sources()

    def check_sources(self):
        require(digest(self.path.read_bytes()) == self.sha, "deployment config drift")
        verify_files(self.repo, self.data["source_pins"])
        # A complete local package/runner closure is required. Frozen external
        # helpers remain in the same independent map and G2's executed trace.
        for prefix in ("experiments/exp7/exp7core", "experiments/exp7/exp7stats",
                       "experiments/exp7/exp7ops", "experiments/exp7/exp7integration", "experiments/exp7/run"):
            root = self.repo/prefix
            require(root.is_dir(), "deployment pure package/runner absent")
            for p in root.rglob("*.py"):
                require(not p.is_symlink() and p.relative_to(self.repo).as_posix() in self.data["source_pins"], "omitted deployment source")
        from .supervisor import check_supervisor
        for name, stage in self.data["stages"].items():
            check_supervisor(stage["output"], repo=self.repo, campaign=self.root, stage=name)
        remote = self.data.get("remote")
        if remote and Path(remote["evidence_root"]).resolve() == self.root.resolve():
            from .remote_evidence import supervisor_inventory
            supervisor_inventory(self)
        return None

    def _collection(self, stage):
        plan = self.data["stages"][stage]
        return self.campaign_factory(self.root, self.repo, trust_path=plan["trust_path"],
                                     trust_sha256=pin(plan["trust_sha256"]), git=self.git)

    def authenticate(self, stage, contract_bytes):
        self.check_sources()
        require(stage in STAGE_MAP, "fixed deployment stage")
        plan = self.data["stages"][stage]
        require(digest(contract_bytes) == pin(plan["contract_sha256"]), "stage contract independent pin")
        contract = strict(contract_bytes)
        require(contract.get("schema") == "exp7.stage-contract.v1" and contract.get("stage") == stage, "stage contract identity")
        c = self._collection(stage)  # constructor only; no battery/raw before stats CLAIM
        c.trust.prereg_projection()
        grant = c.trust.grant(STAGE_MAP[stage])
        grant_sha = digest(canonical(grant))
        require(grant_sha == contract["grant_sha256"], "formal grant/contract binding")
        # The watch contract additionally names independently evidenced rental
        # and standing-release grants. No create capability is supplied here.
        if contract["instance"] is not None:
            rental = contract["rental_evidence"]
            source = c.trust.read_repo(rental["path"])
            require(digest(source) == pin(rental["sha256"]) and rental["quote"].encode() in source, "rental evidence binding")
            c.trust.git.blob(rental["commit"], rental["path"], rental["sha256"])
        approval = Approval(plan["contract_sha256"], grant_sha, stage,
                            contract["instance"], contract["machine"], contract["label"],
                            contract["credit_before"], contract["cap"], contract["verifier_code_sha256"])
        self.check_sources()
        return approval

    def dry_plan(self, stage, approval):
        require(approval.stage == stage, "dry approval scope")
        return {"state": "COMPLETE", "dry_run": True, "stage": stage, "collection_stage": STAGE_MAP[stage],
                "subjects": list(MODELS) if stage in ("predictor", "predictor-preflight") else [],
                "contact": False, "grant_consumed": False}

    def _run(self, stage, collection_stage, subject=None, heartbeat=None):
        self.check_sources()
        plan = self.data["stages"][stage]
        backend = self.backend
        if heartbeat is not None:
            from .controlled_backend import ControlledBackend
            backend = ControlledBackend(heartbeat, self.root/"STOP_NEW_WORK.json", backend=backend)
        result = self.collection_run(self.root, self.repo, trust_path=plan["trust_path"],
                                     trust_sha256=plan["trust_sha256"], stage=collection_stage,
                                     subject=subject, backend=backend,
                                     power_validator=collection_power_validator, git=self.git)
        self.check_sources()
        return self.stage_result(stage, result)

    def predictor_digest_baseline(self, *, trust_path, trust_sha256):
        """Separate explicit B18 stage; pins must be one fixed enrolled plan.

        Called by the separate fixed baseline bootstrap, never auto-triggered by
        a missing value during preflight. A new independent trust revision must
        enroll the measured receipt before the later preflight invocation.
        """
        plan = self.data["digest_baseline"]
        require((trust_path, trust_sha256) == (plan["trust_path"], plan["trust_sha256"]), "fixed digest baseline authority")
        self.check_sources()
        result = self.collection_run(self.root, self.repo, trust_path=trust_path, trust_sha256=trust_sha256,
                                     stage="predictor-digest-baseline", subject=None, backend=self.backend,
                                     power_validator=collection_power_validator, git=self.git)
        self.check_sources()
        return result

    def predictor_preflight(self, approval, heartbeat):
        results = []
        for i, model in enumerate(MODELS):
            heartbeat({"phase": "predictor-preflight", "completed": i, "total": 3})
            results.append(self._run("predictor-preflight", "predictor-preflight", model, heartbeat))
        return {"state": "COMPLETE", "subjects": results}

    def predictor(self, approval, heartbeat):
        results = []
        for i, model in enumerate(MODELS):
            heartbeat({"phase": "predictor-collection", "completed": i, "total": 3})
            results.append(self._run("predictor", "predictor-collection", model, heartbeat))
        return {"state": "COMPLETE", "subjects": results}

    def seal(self, approval, heartbeat):
        heartbeat({"phase": "predictor-seal"})
        return self._run("seal", "predictor-seal")

    def outcome_preflight(self, approval, heartbeat):
        heartbeat({"phase": "outcome-preflight"})
        return self._run("outcome-preflight", "outcome-preflight", self.data["outcome_host"], heartbeat)

    def outcome(self, approval, heartbeat):
        heartbeat({"phase": "outcome-collection"})
        result = self._run("outcome", "outcome-collection", heartbeat=heartbeat)
        heartbeat({"phase": "campaign-complete"})
        complete = self._run("outcome", "campaign-complete")
        return {"state": "COMPLETE", "collection": result, "completion_producer": complete,
                "next": "independently commit/pin complete.json before analysis authority"}

    def campaign(self, stage, approval):
        require(stage in ("power", "verdict") and approval.stage == stage, "statistics stage scope")
        plan = self.data["stages"][stage]
        return StatsCampaignAdapter(self._collection(stage), authority_path=plan["adapter_authority_path"],
                                    authority_sha256=plan["adapter_authority_sha256"])

    def stage_result(self, stage, result):
        require(type(result) is dict and result.get("state") == "COMPLETE", "scientific/collection refusal")
        require(not any(p.name in ("HALTED", "HALTED.json") for p in self.root.rglob("*")), "campaign HALTED")
        if stage in ("power", "verdict"):
            from exp7stats.common import dumps
            name = STAGE_MAP[stage]
            folder = self.root/"statistics"/name
            completion = strict((folder/"COMPLETE.json").read_bytes())
            verify_files(folder, completion["files"])
            require(digest((folder/f"{name}.json").read_bytes()) == digest(dumps(result)), "returned/saved statistical result mismatch")
        self.check_sources()
        return result

    def verify_unit(self, stage, unit_id, payload):
        # Operational metadata synchronization must have landed independently
        # validated per-load receipts first. Never derive expectations from raw.
        with self._collection("watch") as c:
            parts = unit_id.split("/")
            raw, record = payload["raw.jsonl"], strict(payload["record.json"])
            if parts[:2] == ["units", "anchors"]:
                from exp7core.anchors import validate_anchor
                require(len(parts) == 4, "anchor address")
                model, rung = parts[2:]
                validate_anchor(raw, record, read=c.trust.read_repo, model=model, rung=rung,
                                context_json=c._context(c.trust.data["sample_loads"][model]))
            elif parts[:2] == ["units", "outcome-anchors"]:
                from exp7core.anchors import greedy_anchor
                require(len(parts) == 3, "outcome anchor address")
                load = parts[2]
                step = int(c.trust.data["loads"][load]["model"].split("/")[1])
                want = {"schema": "exp7.greedy-anchors.v1", "load_id": load, "step": step,
                        "context": strict(c._context(load, outcome=True)),
                        **greedy_anchor(raw, read=c.trust.read_repo, step=step)}
                require(record == want, "per-load old anchor rederivation")
            else:
                validate_record(raw, record, c.expected(unit_id))
        self.check_sources()
        return None

    def verify_final(self, archive_root, terminal):
        files = snapshot(archive_root)
        from .remote_evidence import verify_supervisor_archive
        verify_supervisor_archive(self, {n: (Path(archive_root)/n).read_bytes() for n in files})
        if terminal["exit_code"] != 0 or terminal["kind"] != "complete":
            return {"scientific_state": "INSUFFICIENT_DATA", "failures": ["observed failed/stopped campaign"], "inventory_sha256": digest(canonical(files))}
        from .security import validate_archive
        validate_archive(self, archive_root)
        return {"scientific_state": "COMPLETE", "failures": [], "inventory_sha256": digest(canonical(files))}

    def watch(self, approval, heartbeat):
        from .security import build_watcher
        from exp7ops.watcher import heartbeat_loop
        import time
        factory = build_watcher if self.watch_factory is None else self.watch_factory
        watcher = factory(self, approval)
        result = heartbeat_loop(tick=watcher.tick, heartbeat=heartbeat, clock=time.monotonic, wait=time.sleep)
        return {"state": "COMPLETE", "watch": result}
