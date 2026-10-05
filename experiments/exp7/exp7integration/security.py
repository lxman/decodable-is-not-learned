"""Independent evidence/process/Git binding and complete watcher composition."""
from pathlib import Path
import shutil
import tempfile
from exp7ops.evidence import require, strict, digest, canonical, snapshot, once, verify_files, pin
from exp7ops.operator import publish_git, release, terminal, GIT
from exp7ops.runtime import SystemProcess, BoundSSH
from exp7ops.wire import decode
from exp7ops.secured import write_secured, reverify_secured
from exp7ops.watcher import Watcher
from exp7core.campaign import Campaign
from exp7core.provenance import Git
from .heartbeat_service import NativeHeartbeatOS, utc
from .provider import BoundProvider


class NativeObservation:
    def __init__(self):
        self.os = NativeHeartbeatOS()

    def identity(self, pid):
        return self.os.identity(pid)

    def group_members(self, group):
        import subprocess
        result = subprocess.run(["/bin/ps", "-axo", "pid=,pgid="], capture_output=True, text=True, timeout=10)
        require(result.returncode == 0, "process-group observation unavailable")
        rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
        require(all(len(row) == 2 and all(v.isdigit() for v in row) for row in rows), "process-group observation malformed")
        return [int(pid) for pid, pg in rows if int(pg) == group]


class TerminalObserver:
    def __init__(self, *, identity, group, status_path, heartbeat_identity_sha256, observer=None):
        require(type(identity) is dict and type(identity.get("pid")) is int and len(identity) > 1, "independent process start identity")
        require(type(group) is int and group > 1, "bound process group")
        self.identity, self.group = identity, group
        self.path, self.heartbeat_identity_sha256 = Path(status_path), pin(heartbeat_identity_sha256)
        self.observer = NativeObservation() if observer is None else observer

    def __call__(self):
        observed = self.observer.identity(self.identity["pid"])
        live = observed == self.identity
        members = self.observer.group_members(self.group)
        require(type(members) is list and all(type(p) is int and p > 0 for p in members), "group observation")
        if live or members or not self.path.is_file():
            return None
        value = strict(self.path.read_bytes())
        require(not {"token", "heartbeat_token"} & set(value), "legacy heartbeat status fields")
        require(value.get("pid") == self.identity["pid"] and value.get("heartbeat_identity_sha256") == self.heartbeat_identity_sha256, "terminal bound heartbeat identity")
        if type(value.get("exit_code")) is not int or value.get("stage") not in ("complete", "error"):
            return None
        result = {"exit_code": value["exit_code"], "controller_live": False, "group_live": False,
                  "kind": "complete" if value["exit_code"] == 0 and value["stage"] == "complete" else "error"}
        terminal(result)
        return result


def validate_archive(deployment, archive_root):
    """Recreate the SAME relative repo/root layout in a fresh validation sandbox.

    Annotated-tag paths remain valid. Only independently pinned inputs are copied
    from repo; archive bytes replace their relative campaign paths for actual G1–6
    verification. The sandbox and any refusal evidence are retained by default.
    No analyzer or model backend is called.
    """
    from .remote_evidence import INVENTORY, verify_supervisor_archive
    verify_supervisor_archive(deployment, {n: (Path(archive_root)/n).read_bytes() for n in snapshot(archive_root)})
    plan = deployment.data["stages"]["watch"]
    original = deployment._collection("watch")
    scratch = Path(deployment.data["validation_scratch"])
    approved = Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode")
    require(scratch.is_absolute() and scratch.is_relative_to(approved) and scratch.is_dir(), "approved validation sandbox")
    mirror = Path(tempfile.mkdtemp(prefix="archive-validation-", dir=scratch))
    root_relative = deployment.root.relative_to(deployment.repo)
    for name, sha in original.trust.data["repo_pins"].items():
        source = deployment.repo/name
        require(digest(source.read_bytes()) == sha, "validation reference pin")
        target = mirror/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    trust_file = mirror/plan["trust_path"]
    trust_file.parent.mkdir(parents=True, exist_ok=True)
    trust_file.write_bytes((deployment.repo/plan["trust_path"]).read_bytes())
    target_root = mirror/root_relative
    target_root.mkdir(parents=True, exist_ok=True)
    for name, sha in snapshot(archive_root).items():
        if name == INVENTORY:
            continue  # authenticated operational inventory, not a scientific input
        if name.startswith("supervisors/"):
            require(len(Path(name).parts) == 3 and Path(name).parts[1] in deployment.data["remote"]["supervisor_stages"], "unbound supervisor archive namespace")
            continue  # retained/hash-verified by independent full archive gate;
                      # never reinstalled as a scientific campaign input
        target = target_root/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((Path(archive_root)/name).read_bytes())
        require(digest(target.read_bytes()) == sha, "archive mirror byte identity")
    with Campaign(target_root, mirror, trust_path=plan["trust_path"], trust_sha256=plan["trust_sha256"], git=Git(deployment.repo)) as c:
        c.verify_complete()
        from .adapter import collection_power_validator
        collection_power_validator(c.verify_power(), c)
        completion = c.trust.read_root("complete.json")
        require(strict(completion) == c.complete_payload(), "archive completion producer did not rederive")
    deployment.check_sources()
    return mirror


class IndependentSecuredReader:
    def __init__(self, deployment, approval, process, transport, security_root, evidence_commit):
        self.deployment, self.approval = deployment, approval
        self.process, self.transport = process, transport
        self.root, self.commit = Path(security_root), evidence_commit

    def check_verifier_source(self):
        self.deployment.check_sources()
        pins = self.deployment.data["verifier_sources"]
        verify_files(self.deployment.repo, pins)
        return digest(canonical(pins))

    def remote_master(self):
        raw = self.process.run([GIT, "-C", str(self.deployment.repo), "ls-remote", "origin", "refs/heads/master"],
                               cwd=self.deployment.repo, shell=False, timeout=120)
        fields = raw.strip().split()
        require(len(fields) == 2 and fields[1] == "refs/heads/master", "independent remote Git observation")
        return fields[0]

    def committed_file(self, commit_sha, relative_path):
        # SystemProcess returns text, whereas evidence may be gzip/binary. Use a
        # separate exact-byte leaf rather than lossy decoding/re-encoding.
        if callable(getattr(self.process, "read_git_blob", None)):
            return self.process.read_git_blob(self.deployment.repo, commit_sha, relative_path)
        import subprocess
        result = subprocess.run([GIT, "-C", str(self.deployment.repo), "show", f"{commit_sha}:{relative_path}"],
                                capture_output=True, timeout=120)
        require(result.returncode == 0, "independent committed blob unavailable")
        return result.stdout

    def terminal_observation(self):
        return self.transport.final_evidence()["terminal"]

    def required_inventory(self, observed_terminal):
        from .remote_evidence import verify_supervisor_archive
        self.deployment.check_sources()
        remote = self.transport.final_evidence()  # independently observed full tree, NOT operator's manifest
        require(remote["terminal"] == observed_terminal and set(remote["files"]) == set(remote["payload"]), "independent remote terminal/inventory")
        verify_supervisor_archive(self.deployment, remote["payload"])
        expected = {}
        for name, sha in remote["files"].items():
            require(digest(remote["payload"][name]) == pin(sha), "independent remote bytes")
            expected["remote/"+name] = sha
        for name in ("terminal-unit-failures.json", "final-verification.json"):
            path = self.root/"local"/name
            value = strict(path.read_bytes())
            if name == "terminal-unit-failures.json":
                require(type(value) is list, "retained unit diagnostics")
            else:
                require(type(value) is dict and value.get("inventory_sha256") == digest(canonical(remote["files"])), "retained final diagnostic inventory")
                if observed_terminal["exit_code"] != 0 or observed_terminal["kind"] != "complete":
                    require(value.get("scientific_state") == "INSUFFICIENT_DATA", "failed campaign scientific state")
                else:
                    # Re-run G1–G6 saved-data gates in this independent process;
                    # a candidate operator's success dictionary is not evidence.
                    independently_checked = self.deployment.verify_final(self.root/"remote", observed_terminal)
                    require(value == independently_checked and value["scientific_state"] == "COMPLETE" and
                            value["failures"] == [], "independent final scientific validation")
                    require(strict((self.root/"local/terminal-unit-failures.json").read_bytes()) == [],
                            "successful terminal retained unit failures")
            expected["local/"+name] = digest(path.read_bytes())
        require(snapshot(self.root) == expected, "security root includes full remote and local failure evidence")
        return expected


def publication_paths(deployment, security_root, files):
    root = Path(security_root).relative_to(deployment.repo)
    require(root.as_posix().startswith("experiments/exp7/"), "security publication within exp7")
    return {name: (root/name).as_posix() for name in files}


def independent_secure_main(deployment, approval, *, process=None, transport=None):
    process = SystemProcess() if process is None else process
    watch = deployment.data["watch"]
    from .metadata_transport import DeploymentSSH
    transport = DeploymentSSH(process, watch["route"], deployment.repo, decode, deployment) if transport is None else transport
    out = Path(watch["output"])
    request = strict((out/"secured-request.json").read_bytes())
    root = out/"secured-evidence"
    reader = IndependentSecuredReader(deployment, approval, process, transport, root, request["evidence_commit"])
    files = reader.required_inventory(request["terminal"])
    return write_secured(approval=approval, reader=reader, root=root, files=files,
                         evidence_commit=request["evidence_commit"], observed_terminal=request["terminal"],
                         publication_paths=publication_paths(deployment, root, files), output=out/"secured.json")


def build_watcher(deployment, approval, *, process=None, transport=None, provider=None):
    process = SystemProcess() if process is None else process
    watch = deployment.data["watch"]
    from .metadata_transport import ReceiptSSH
    transport = ReceiptSSH(process, watch["route"], deployment.repo, decode, deployment) if transport is None else transport
    provider = BoundProvider(instance=approval.instance, credential_path=watch["credential_path"]) if provider is None else provider
    out = Path(watch["output"])
    def publish(paths):
        return publish_git(process, deployment.repo, [p.relative_to(deployment.repo).as_posix() for p in paths])
    def secure(archive, files, observation, verification):
        root = out/"secured-evidence"; root.mkdir()
        shutil.copytree(archive, root/"remote")
        (root/"local").mkdir()
        for name in ("terminal-unit-failures.json", "final-verification.json"):
            shutil.copyfile(out/name, root/"local"/name)
        all_files = snapshot(root)
        paths = publication_paths(deployment, root, all_files)
        commit = publish_git(process, deployment.repo, list(paths.values()))
        once(out/"secured-request.json", {"evidence_commit": commit, "terminal": observation})
        process.run([deployment.data["python"], "-I", "-B", str(deployment.repo/"experiments/exp7/run/secured_7.py"),
                     "--site-sha256", deployment.site_sha256],
                    cwd=deployment.repo, shell=False, timeout=900)
        require((out/"secured.json").is_file(), "independent secured process did not publish receipt")
        return out/"secured.json"
    def release_verified(receipt_path):
        receipt = strict(Path(receipt_path).read_bytes())
        root = out/"secured-evidence"
        reader = IndependentSecuredReader(deployment, approval, process, transport, root, receipt["evidence_commit"])
        def reverify(raw):
            return reverify_secured(raw, approval=approval, reader=reader, root=root,
                                   publication_paths=publication_paths(deployment, root, receipt["files"]))
        return release(approval, provider=provider, evidence_root=root, secured_receipt=receipt_path,
                       verify_secured=reverify, out=out)
    return Watcher(approval=approval, transport=transport, provider=provider, composition=deployment,
                   root=deployment.root, out=out, expected_units=tuple(watch["expected_units"]), publish=publish,
                   independently_secure=secure, release_secured=release_verified,
                   forecast_remaining=lambda completed: max(0, len(watch["expected_units"])-completed)*watch["measured_remaining_per_unit"]+watch["measured_fixed_remaining"],
                   reserve=watch["reserve"], now=utc)
