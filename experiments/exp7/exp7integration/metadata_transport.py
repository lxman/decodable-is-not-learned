"""Fixed per-load metadata transfer before canonical unit admission.

Unit wire payloads stay exactly raw/record/DONE. The separate fixed metadata
program transfers only planned load-receipt paths, never arbitrary filenames.
Validation derives models/hosts from independent collection trust before writes.
"""
from pathlib import Path, PurePosixPath
import shlex
from exp7ops.runtime import BoundSSH, remote_argv
from exp7ops.wire import encode_payload, decode_payload
from exp7ops.evidence import require, strict, digest, canonical, once, pin, path_in
from exp7core.collection_schema import validate_load
from exp7core.referents import verify_model

def fixed_remote_program(deployment, program):
    require(program in ("remote_7.py", "metadata_7.py"), "fixed remote bootstrap")
    root = PurePosixPath(deployment.data["watch"]["remote_package_root"])
    require(root.is_absolute() and ".." not in root.parts and root.parts[-2:] == ("experiments", "exp7"), "direct remote experiment package")
    return "/venv/main/bin/python -I -B "+shlex.quote(str(root/"run"/program))+" --site-sha256 "+pin(deployment.data["watch"]["remote_site_sha256"])


def metadata_reply(deployment):
    deployment.check_sources()
    c = deployment._collection("outcome")
    names = tuple(f"receipts/{load}.json" for load in c.trust.data["loads"])
    actual = {p.relative_to(c.root).as_posix() for p in (c.root/"receipts").glob("*.json")}
    require(actual <= set(names), "unplanned remote load receipt")
    values = {name: path_in(c.root, name).read_bytes() for name in sorted(actual)}
    deployment.check_sources()
    return {"files": {n: digest(v) for n, v in values.items()}, "payload": encode_payload(values) if values else {}}


class DeploymentSSH(BoundSSH):
    def __init__(self, process, route, cwd, decode, deployment):
        super().__init__(process, route, cwd, decode)
        self.deployment = deployment

    def _argv(self, operation, unit=None):
        argv = remote_argv(self.route, operation, unit)
        # Retain the accepted route/unit grammar; bind the concrete program to
        # the installed direct package rather than the upstream placeholder path.
        argv[-1] = fixed_remote_program(self.deployment, "remote_7.py")+" "+operation+(" "+unit if unit is not None else "")
        return argv

    def call(self, operation, unit=None):
        data = self.process.run(self._argv(operation, unit), cwd=self.cwd, shell=False, timeout=300)
        return self.decode(operation, strict(data))


class ReceiptSSH(DeploymentSSH):

    def sync_receipts(self):
        argv = remote_argv(self.route, "snapshot")
        argv[-1] = fixed_remote_program(self.deployment, "metadata_7.py")
        data = strict(self.process.run(argv, cwd=self.cwd, shell=False, timeout=300))
        require(type(data) is dict and set(data) == {"files", "payload"}, "load metadata envelope")
        values = decode_payload(data["payload"]) if data["payload"] else {}
        require(set(values) == set(data["files"]), "load metadata coverage")
        with self.deployment._collection("watch") as c:
            d = c.trust.data
            names = {f"receipts/{load}.json": load for load in d["loads"]}
            require(set(values) <= set(names), "metadata only independently planned loads")
            for name, raw in values.items():
                require(digest(raw) == data["files"][name], "load receipt transfer hash")
                load = names[name]; spec = d["loads"][load]
                verify_model(c, spec["model"])
                validate_load(strict(raw), expected_model=d["models"][spec["model"]], expected_host=d["hosts"][spec["host"]],
                              loader=spec["loader"], load_id=load, source_sha=d["source_manifest_sha256"],
                              code_sha=d["code_manifest_sha256"], token_facts=d["tokenizers"][spec["model"]])
                c.trust.git.ancestor(d["projection"]["commit"], spec["launch_git_commit"])
                path = c.root/name
                path.parent.mkdir(exist_ok=True)
                if path.exists():
                    require(c.trust.read_root(name) == raw, "load metadata changed after landing")
                else:
                    once(path, raw)
                c.load_receipt(load)
        self.deployment.check_sources()

    def snapshot(self):
        result = super().snapshot()
        observation = result.get("terminal")
        if observation is None or observation["exit_code"] == 0 and observation["kind"] == "complete":
            self.sync_receipts()
        # Failed terminals go straight to full evidence, including invalid
        # receipt bytes; no metadata admission can hide that failure inventory.
        return result
