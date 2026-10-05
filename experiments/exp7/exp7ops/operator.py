"""Operations state machine. Every live effect is an explicit bound capability.

No constructor creates a rental, grants authority, launches a process or reads a
credential. Tests inject fakes. Deployment supplies authenticated approvals and
independently pinned composition; a JSON 'approved': true is never consulted.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import os
from .evidence import (require, Refusal, canonical, strict, digest, pin, commit,
    identifier, number, path_in, once, state, verify_files, selected_instances,
    selected_credit)

STAGES = ("predictor-preflight", "predictor", "seal", "power", "outcome-preflight",
          "outcome", "verdict", "watch")
PROGRAM = {stage: ("experiments/exp7/run/stage_7.py", stage) for stage in STAGES}
GIT = "/opt/homebrew/bin/git"
FOLLOW_UP = "Inspect Experiment 7 durable evidence; retain contact, verdict and propagation gates."

class ProcessPort(Protocol):
    def index_lock(self, repo): ...
    def run(self, argv, *, cwd, shell, timeout): ...
    def spawn(self, argv, *, cwd, shell, start_new_session, stdin, stdout, stderr): ...
    def session_id(self, pid): ...
    def own_session_id(self): ...
    def terminate(self, pid): ...

class Composition(Protocol):
    def authenticate(self, stage, contract_bytes): ...
    def dry_run(self, stage, approval): ...
    def execute(self, stage, approval, heartbeat): ...
    def verify_unit(self, stage, unit_id, payload): ...
    def verify_final(self, archive_root, terminal): ...

class Provider(Protocol):
    # instances() must preserve HTTP/parse success through
    # evidence.successful_instance_response; no exception/error reply -> [] path.
    # Raw reply/error bodies must be sanitized before exceptions reach stderr.
    def instances(self): ...
    def credit(self): ...
    def delete(self, instance): ...

@dataclass(frozen=True)
class Approval:
    """Only composition.authenticate returns this after independent grant checks."""
    contract_sha256: str
    grant_sha256: str
    stage: str
    instance: int | None
    machine: int | None
    label: str | None
    credit_before: float
    cap: float
    verifier_code_sha256: str

    def __post_init__(self):
        pin(self.contract_sha256); pin(self.grant_sha256); pin(self.verifier_code_sha256)
        require(self.stage in STAGES, "unapproved stage")
        number(self.credit_before, "credit baseline"); number(self.cap, "cost cap")
        require(self.cap <= 25, "cap exceeds ruled planning bound")
        if self.instance is not None:
            require(type(self.instance) is int and self.instance > 0
                    and type(self.machine) is int and self.machine > 0, "rental binding")
            identifier(self.label)
        else:
            require(self.machine is None and self.label is None, "partial rental binding")

def stage_argv(python, repo, stage, contract):
    require(stage in PROGRAM, "constant stage required")
    require(Path(python).is_absolute() and Path(repo).is_absolute()
            and Path(contract).is_absolute(), "absolute deployment paths")
    script, fixed_stage = PROGRAM[stage]
    return [str(python), "-I", "-B", str(Path(repo) / script), fixed_stage,
            "--contract", str(contract)]

def monitor_argv(python, repo, *, job, session, status):
    identifier(job)
    require(type(session) is str and session.startswith("ses_")
            and session[4:].isalnum(), "actual session ID required")
    require(Path(status).is_absolute(), "absolute status path")
    return [str(python), str(Path(repo) / "tools/experiment_monitor.py"), "watch", job,
            "--session", session, "--status", str(status), "--pid-command", "stage_7.py",
            "--stale-seconds", "900", "--follow-up", FOLLOW_UP]

def detached_launch(process, *, python, repo, contract, stage, out, job, session,
                    approval, check_monitor_pin):
    require(isinstance(approval, Approval) and approval.stage == stage, "stage approval")
    require(digest(Path(contract).read_bytes()) == approval.contract_sha256, "contract drift")
    require(callable(check_monitor_pin) and check_monitor_pin() is None, "monitor source pin")
    out = Path(out)
    out.mkdir()  # launch directories/claims never reused by a recovery attempt
    status = out / "status.json"
    once(out / "launch.CLAIM", {"contract": approval.contract_sha256, "stage": stage})
    state(status, {"pid": None, "stage": "registered-awaiting-launch", "exit_code": None})
    spawn_attempted, pid = False, None
    try:
        # Durable registration FIRST. Post-spawn uncertainty has its own record.
        process.run(monitor_argv(python, repo, job=job, session=session, status=status),
                    cwd=repo, shell=False, timeout=60)
        with (out / "operator.log").open("xb") as log:
            spawn_attempted = True
            pid = process.spawn(stage_argv(python, repo, stage, contract), cwd=repo,
                shell=False, start_new_session=True, stdin="DEVNULL", stdout=log,
                stderr="STDOUT")
        require(type(pid) is int and pid > 1, "invalid spawned PID")
        sid = process.session_id(pid)
        if sid == process.own_session_id():
            process.terminate(pid)
            raise Refusal("process did not detach")
        once(out / "launched.json", {"pid": pid, "sid": sid, "job": job,
                                     "contract": approval.contract_sha256})
        # Child owns status once launched; parent never overwrites its terminal.
        return {"pid": pid, "sid": sid, "job": job}
    except BaseException as exc:
        diagnostic = {"pid": pid if type(pid) is int else None,
                      "contract_sha256": approval.contract_sha256,
                      "spawn_attempted": spawn_attempted, "error_type": type(exc).__name__}
        if spawn_attempted:
            # A PID/SID observation failure is not a child exit. A successful
            # fast child, still-running child or uncertain spawn owns status now.
            once(out / "launch-observation.json", {**diagnostic, "child_state": "UNKNOWN"})
        else:
            state(status, {"pid": None, "stage": "launch-refused", "exit_code": 1,
                           "error_type": type(exc).__name__})
        raise

def stage_main(argv, *, composition, contract_path, output, pid, now, heartbeat_service=None):
    """CLI parser injected for tests; contact happens only after authenticate.

    The deployment entry passes the one bound contract path; users cannot supply
    arbitrary program text, module names, command arrays, n/B overrides or flags.
    """
    require(type(argv) is list and len(argv) in (3, 4), "stage CLI shape")
    stage = argv[0]
    require(stage in STAGES and argv[1] == "--contract"
            and argv[2] == str(contract_path), "constant stage/bound contract required")
    dry = len(argv) == 4
    require(not dry or argv[3] == "--dry-run", "unknown option")
    approval = composition.authenticate(stage, Path(contract_path).read_bytes())
    require(isinstance(approval, Approval) and approval.stage == stage, "authentication result")
    if dry:
        return composition.dry_run(stage, approval)
    from .heartbeat import HeartbeatSession
    require(callable(getattr(heartbeat_service, "start", None)), "independent heartbeat service required")
    out = Path(output)
    require(out.is_dir(), "operator directory must already exist")
    # Scientific once-claims belong to G2/G7/G10. This separate claim prevents
    # two operator processes from accidentally dispatching the same stage.
    once(out / "operator.CLAIM", {"stage": stage, "grant": approval.grant_sha256})
    heartbeat = HeartbeatSession(out, pid=pid, stage=stage, now=now, service=heartbeat_service)
    try:
        heartbeat.start()
        # The worker pulses even when execute/power/analyzer does not call update.
        # Collection progress callbacks update only the foreground-owned mailbox.
        result = composition.execute(stage, approval, heartbeat)
        heartbeat.check()
        require(type(result) is dict and result.get("state") == "COMPLETE", "stage did not return verified completion")
        require(not (out / "HALTED.json").exists(), "HALTED dominates completion")
        once(out / "COMPLETE.json", result)
        heartbeat.finish(exit_code=0, stage="complete")
        return result
    except BaseException as exc:
        refusal = {"state": "INSUFFICIENT_DATA", "error_type": type(exc).__name__}
        if not (out / "HALTED.json").exists():
            once(out / "HALTED.json", refusal)
        if not heartbeat.terminal_requested:
            try:
                heartbeat.finish(exit_code=1, stage="error")
            except Exception as status_error:
                once(out / "heartbeat-finalization-error.json", {"error_type": type(status_error).__name__})
        raise

def land_unit(destination, unit_id, payload, *, verify):
    """Transport returns a COMPLETE bytes map, never extracts an untrusted archive."""
    from .wire import unit_name
    unit_name(unit_id)
    require(type(payload) is dict and set(payload) == {"raw.jsonl", "record.json", "DONE.json"}
            and all(type(v) is bytes for v in payload.values()), "full unit required")
    done = strict(payload["DONE.json"])
    require(type(done) is dict and set(done) == {"raw.jsonl", "record.json"}, "completion schema")
    for name, expected in done.items():
        require(digest(payload[name]) == pin(expected), "transfer hash mismatch")
    require(callable(verify) and verify(unit_id, payload) is None, "independent unit rederivation")
    target = path_in(destination, unit_id)
    if target.exists():
        verify_files(target, {n: digest(b) for n, b in payload.items()}, exact=True)
        return tuple(sorted(payload))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    for name in ("raw.jsonl", "record.json", "DONE.json"):
        once(target / name, payload[name])
    return tuple(sorted(payload))

def publish_git(process, repo, paths):
    """A private-repository watcher; no public-release or close-out capability."""
    require(paths and len(set(paths)) == len(paths), "explicit unique git paths")
    for name in paths:
        require(name.startswith("experiments/exp7/"), "publication outside experiment")
        path_in(repo, name)
    def git(*args):
        return process.run([GIT, "-C", str(repo), *args], cwd=repo, shell=False, timeout=240).strip()
    with process.index_lock(repo):
        before = commit(git("rev-parse", "HEAD"))
        staged = git("diff", "--cached", "--name-only").splitlines()
        require(set(staged) <= set(paths), "unrelated staged work")
        git("add", "--", *sorted(paths))
        staged = git("diff", "--cached", "--name-only").splitlines()
        require(set(staged) <= set(paths), "staged set changed")
        if staged:
            # The advisory lock coordinates this tool's publishers. --only is
            # still required against a writer that does not honor our lock.
            git("commit", "--only", "-m", "exp7: publish complete verified evidence",
                "-m", "Agent: OpenAI GPT-6 Astra (OpenCode)", "--", *sorted(paths))
        head = commit(git("rev-parse", "HEAD"))
        if staged:
            require(git("rev-list", "--parents", "-n", "1", head).split() == [head, before], "commit parent changed")
        else:
            require(head == before, "concurrent HEAD change")
        changed = [p for p in git("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", before, head).split("\0") if p]
        require(set(changed) <= set(paths), "actual commit escaped exact publication scope")
        require(commit(git("rev-parse", "HEAD")) == head, "HEAD changed before push")
        # Push the verified immutable commit, not a branch name another writer
        # could advance between observation and push. No force/ref rewrite.
        git("push", "origin", head + ":refs/heads/master")
        remote = git("ls-remote", "origin", "refs/heads/master").split()
        require(remote == [head, "refs/heads/master"], "remote publication not secured")
        return head

def cost_guard(approval, credit_response, *, forecast_remaining, reserve):
    after = selected_credit(credit_response)
    spent = approval.credit_before - after
    require(spent >= 0, "account baseline changed; reconcile top-up/credit")
    projected = spent + number(forecast_remaining, "remaining forecast") + number(reserve, "reserve")
    require(projected <= approval.cap, "cost cap: pause new work and secure evidence")
    return {"credit_before": approval.credit_before, "credit_after": after,
            "spent": spent, "projected": projected, "cap": approval.cap}

def terminal(snapshot):
    require(type(snapshot) is dict and set(snapshot) == {"exit_code", "controller_live", "group_live", "kind"}, "terminal schema")
    require(type(snapshot["exit_code"]) is int and snapshot["kind"] in ("complete", "error", "stopped"), "terminal exit")
    require(snapshot["controller_live"] is False and snapshot["group_live"] is False, "work still live or unknown")

def release(approval, *, provider, evidence_root, secured_receipt, verify_secured, out):
    """Standing release authority applies only after independent secured evidence.

    The operator cannot mint this receipt. verify_secured is the pinned independent
    verifier, revalidating archive/member hashes, complete-or-failed inventory,
    committed bytes and advertised remote commit; it returns the receipt's hash.
    """
    require(isinstance(approval, Approval) and approval.instance is not None, "provided approved instance required")
    receipt_bytes = Path(secured_receipt).read_bytes()
    receipt = strict(receipt_bytes)
    require(type(receipt) is dict and set(receipt) == {"schema", "instance", "machine",
            "contract_sha256", "verifier_code_sha256", "files", "evidence_commit", "terminal"}, "secured receipt schema")
    require(receipt["schema"] == "exp7.independently-secured.v1", "secured receipt schema")
    require(type(receipt["instance"]) is int and receipt["instance"] == approval.instance
            and type(receipt["machine"]) is int and receipt["machine"] == approval.machine, "receipt instance")
    require(receipt["contract_sha256"] == approval.contract_sha256 and
            receipt["verifier_code_sha256"] == approval.verifier_code_sha256, "receipt trust binding")
    terminal(receipt["terminal"])
    commit(receipt["evidence_commit"])
    verify_files(evidence_root, receipt["files"])
    require(callable(verify_secured) and verify_secured(receipt_bytes) == digest(receipt_bytes), "independent secured verification")
    out = Path(out)
    claim = out / "release.CLAIM"
    rows = selected_instances(provider.instances())
    matches = [r for r in rows if r["id"] == approval.instance]
    # On uncertain DELETE a fresh invocation only reconciles absence. It NEVER
    # sends another DELETE under the consumed claim or treats malformed JSON as []
    if claim.exists():
        prior = strict(claim.read_bytes())
        require(prior == {"instance": approval.instance, "receipt_sha256": digest(receipt_bytes)}, "release claim mismatch")
        require(not matches, "DELETE uncertain: instance still present; reconcile manually")
    else:
        require(len(matches) == 1 and matches[0]["machine_id"] == approval.machine
                and matches[0]["label"] == approval.label, "provider instance binding")
        once(claim, {"instance": approval.instance, "receipt_sha256": digest(receipt_bytes)})
        # Exceptions retain the claim. No raw provider exception or reply is saved.
        reply = provider.delete(approval.instance)
        require(type(reply) is dict and reply.get("success") is True, "DELETE unconfirmed; reconcile")
        rows = selected_instances(provider.instances())
        require(not any(r["id"] == approval.instance for r in rows), "release absence not verified")
    credit = selected_credit(provider.credit())
    result = {"instance": approval.instance, "machine": approval.machine,
              "receipt_sha256": digest(receipt_bytes), "evidence_commit": receipt["evidence_commit"],
              "instances_remaining": len(rows), "credit_after": credit,
              "credit_delta_at_check": approval.credit_before - credit,
              "settlement_may_lag": True}
    once(out / "release.json", result)
    return result

def recovery_inventory(root):
    """Read-only reconciliation: never clears claims, HALTED or torn units."""
    from .evidence import snapshot
    files = snapshot(root)
    return {"files": files, "claims": sorted(n for n in files if n.endswith(".CLAIM")),
            "halted": sorted(n for n in files if n.endswith("HALTED.json")),
            "rule": "preserve; new recovery grant and job ID; once-only stages never automatically rerun"}
