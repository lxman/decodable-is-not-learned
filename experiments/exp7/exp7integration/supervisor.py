"""Independently configured supervisor-only root; no scientific/contact inputs.

Ruling: mutable heartbeat status is separate from the immutable power inventory.
Paths are bound by deployment SHA; only these fixed operational artifacts may
appear. Campaign/contact/grant/probe/load/phase/claim roots remain fully scanned.
"""
from pathlib import Path
from exp7ops.evidence import require, strict, digest, canonical, pin
from exp7ops.dispatch import FixedComposition

KEYS = {
    "launch.CLAIM": {"contract", "stage"},
    "launched.json": {"pid", "sid", "job", "contract"},
    "launch-observation.json": {"pid", "contract_sha256", "spawn_attempted", "error_type", "child_state"},
    "operator.CLAIM": {"stage", "grant"},
    "heartbeat-config.json": {"root", "pid", "stage", "heartbeat_identity_sha256"},
    "heartbeat-writer.CLAIM": {"root", "pid", "stage", "heartbeat_identity_sha256"},
    "heartbeat-parent.json": {"config_sha256", "parent"},
    "heartbeat-mailbox.json": {"heartbeat_identity_sha256", "pid", "stage", "sequence", "exit_code", "detail", "ended_utc"},
    "heartbeat-error.json": {"error_type"},
    "heartbeat-parent-absent.json": {"pid", "child_exit"},
    "heartbeat-finalization-error.json": {"error_type"},
    "HALTED.json": {"state", "error_type"},
    "COMPLETE.json": {"state", "stage", "result_sha256"},
}
LOGS = {"operator.log", "heartbeat-worker.log"}
STATUS_FIELDS = {"pid", "stage", "exit_code", "heartbeat_utc", "heartbeat_identity_sha256", "sequence", "ended_utc", "completed", "total", "phase", "error_type"}


def check_supervisor(root, *, repo, campaign, stage, settle=None):
    root, repo, campaign = (Path(p).absolute() for p in (root, repo, campaign))
    require(not root.is_relative_to(repo) and not root.is_relative_to(campaign) and
            not repo.is_relative_to(root) and not campaign.is_relative_to(root), "supervisor root must be disjoint from repository/campaign")
    require(root.resolve() == root and all(not p.is_symlink() for p in (root, *root.parents)), "supervisor symlink/alias")
    if not root.exists():
        return
    require(root.is_dir(), "supervisor directory")
    # The sole status writer atomically renames a short-lived staging file.
    # Wait for it to settle; never exempt its unknown/partial bytes as an input.
    import re
    import time
    settle = time.sleep if settle is None else settle
    for attempt in range(5):
        paths = list(root.iterdir())
        staging = [p for p in paths if re.fullmatch(r"(?:status|heartbeat-mailbox)\.json\.next-[A-Za-z0-9_-]+", p.name)]
        if not staging:
            break
        require(all(not p.is_symlink() for p in staging), "supervisor staging symlink")
        settle(.01)
    else:
        require(False, "supervisor atomic publication did not settle")
    for path in paths:
        require(not path.is_symlink() and path.is_file(), "supervisor admits no directories/symlinks")
        if path.name in LOGS:
            continue  # outputs of the fixed stage/heartbeat programs only
        value = strict(path.read_bytes())
        if path.name == "status.json":
            require(type(value) is dict and {"pid", "stage", "exit_code"} <= set(value) <= STATUS_FIELDS, "supervisor status schema")
        else:
            require(path.name in KEYS and type(value) is dict and set(value) == KEYS[path.name], "unrecognized/non-operational supervisor artifact")
        if "stage" in value:
            require(value["stage"] in (stage, "complete", "error", "registered-awaiting-launch", "launch-refused"), "supervisor stage binding")
        if path.name in ("heartbeat-config.json", "heartbeat-writer.CLAIM"):
            require(value["root"] == str(root) and value["heartbeat_identity_sha256"] == digest(canonical({k:value[k] for k in ("root", "pid", "stage")})), "supervisor heartbeat identity")
        if path.name == "COMPLETE.json":
            require(value["state"] == "COMPLETE", "supervisor complete state")
            pin(value["result_sha256"])
        if path.name == "heartbeat-mailbox.json":
            from exp7ops.heartbeat import check_detail
            check_detail(value["detail"])


class OperationalComposition(FixedComposition):
    def execute(self, stage, approval, heartbeat):
        result = super().execute(stage, approval, heartbeat)
        # Scientific records stay at their canonical write-once campaign path.
        # The supervisor gets only a completion identity, never a second report.
        from exp7stats.common import dumps
        return {"state": "COMPLETE", "stage": stage, "result_sha256": digest(dumps(result))}
