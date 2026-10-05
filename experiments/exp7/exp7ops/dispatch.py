"""Fixed production stage map, parameterized on the final composition interface.

This is an operational dispatch boundary, not a replacement for G2 grants or
G7/G10 scientific once-claims. There is deliberately no import-by-user-string.
"""
from typing import Protocol
from .evidence import require, digest
from .operator import Approval, STAGES

class Deployment(Protocol):
    """Pinned production binding, independently reviewed before any live grant."""
    def authenticate(self, stage, contract_bytes): ...
    def dry_plan(self, stage, approval): ...
    def predictor_preflight(self, approval, heartbeat): ...
    def predictor(self, approval, heartbeat): ...
    def seal(self, approval, heartbeat): ...
    def outcome_preflight(self, approval, heartbeat): ...
    def outcome(self, approval, heartbeat): ...
    def watch(self, approval, heartbeat): ...
    def campaign(self, stage, approval): ...
    def stage_result(self, stage, result): ...
    def verify_unit(self, stage, unit_id, payload): ...
    def verify_final(self, archive_root, terminal): ...

class FixedComposition:
    def __init__(self, deployment, *, power_run, analyzer_run):
        require(callable(power_run) and callable(analyzer_run), "bound statistics entrypoints")
        self.deployment, self.power_run, self.analyzer_run = deployment, power_run, analyzer_run

    def authenticate(self, stage, contract_bytes):
        require(stage in STAGES and type(contract_bytes) is bytes, "fixed stage contract")
        approval = self.deployment.authenticate(stage, contract_bytes)
        require(isinstance(approval, Approval) and approval.stage == stage
                and approval.contract_sha256 == digest(contract_bytes), "authenticated contract binding")
        return approval

    def dry_run(self, stage, approval):
        require(stage in STAGES and approval.stage == stage, "dry stage")
        return self.deployment.dry_plan(stage, approval)

    def execute(self, stage, approval, heartbeat):
        require(stage in STAGES and approval.stage == stage, "execute stage")
        actions = {"predictor-preflight": self.deployment.predictor_preflight,
            "predictor": self.deployment.predictor, "seal": self.deployment.seal,
            "outcome-preflight": self.deployment.outcome_preflight,
            "outcome": self.deployment.outcome, "watch": self.deployment.watch}
        if stage in actions:
            return actions[stage](approval, heartbeat)
        # The statistics author's public API is run(campaign). The finalized
        # campaign supplies G2 entryexit, authentic grants and independent raw
        # interfaces; the writer owns scientific once-claim consumption.
        campaign = self.deployment.campaign(stage, approval)
        heartbeat({"phase": stage})
        result = (self.power_run if stage == "power" else self.analyzer_run)(campaign)
        return self.deployment.stage_result(stage, result)

    def verify_unit(self, stage, unit_id, payload):
        return self.deployment.verify_unit(stage, unit_id, payload)

    def verify_final(self, archive_root, terminal):
        return self.deployment.verify_final(archive_root, terminal)
