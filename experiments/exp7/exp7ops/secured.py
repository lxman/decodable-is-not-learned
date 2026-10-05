"""Independent secured-evidence verifier, run as a distinct guarded process.

Its trusted reader port performs fixed git reads and an authenticated terminal
observation. Production source pins and trust inputs are supplied independently
of the candidate operator receipt. This module has no delete capability.
"""
from pathlib import Path
from typing import Protocol
from .evidence import require, canonical, strict, digest, once, pin, commit, verify_files
from .operator import terminal, Approval

class SecuredReader(Protocol):
    def remote_master(self): ...
    def committed_file(self, commit_sha, relative_path): ...
    def terminal_observation(self): ...
    def required_inventory(self, terminal): ...
    def check_verifier_source(self): ...

def verify_contents(*, approval, reader, root, files, evidence_commit, observed_terminal,
                    publication_paths):
    require(isinstance(approval, Approval), "authenticated independent approval")
    require(reader.check_verifier_source() == approval.verifier_code_sha256, "independent verifier source drift")
    terminal(observed_terminal)
    require(reader.terminal_observation() == observed_terminal, "independent terminal changed")
    expected = reader.required_inventory(observed_terminal)
    # The remote inventory includes all raw/record/completion/host/anchor/gate
    # files AND logs, failure diagnostics, claims and HALTED. It is not derived
    # by trusting the candidate operator manifest, and may include failed units.
    require(type(expected) is dict and expected and expected == files, "independent inventory mismatch")
    verify_files(root, files, exact=True)
    require(type(publication_paths) is dict and set(publication_paths) == set(files), "publication coverage")
    head = commit(evidence_commit)
    require(reader.remote_master() == head, "remote evidence commit not secured")
    for name, want in files.items():
        rel = publication_paths[name]
        require(type(rel) is str and rel.startswith("experiments/exp7/")
                and all(p not in ("", ".", "..") for p in rel.split("/")), "explicit evidence git path")
        data = reader.committed_file(head, rel)
        require(type(data) is bytes and digest(data) == pin(want), "committed evidence mismatch")
    require(reader.check_verifier_source() == approval.verifier_code_sha256, "independent exit source drift")

def write_secured(*, approval, reader, root, files, evidence_commit, observed_terminal,
                  publication_paths, output):
    verify_contents(approval=approval, reader=reader, root=root, files=files,
        evidence_commit=evidence_commit, observed_terminal=observed_terminal, publication_paths=publication_paths)
    receipt = {"schema": "exp7.independently-secured.v1", "instance": approval.instance,
        "machine": approval.machine, "contract_sha256": approval.contract_sha256,
        "verifier_code_sha256": approval.verifier_code_sha256, "files": files,
        "evidence_commit": evidence_commit, "terminal": observed_terminal}
    once(output, receipt)
    return digest(canonical(receipt))

def reverify_secured(data, *, approval, reader, root, publication_paths):
    receipt = strict(data)
    require(receipt["schema"] == "exp7.independently-secured.v1"
            and receipt["instance"] == approval.instance and receipt["machine"] == approval.machine
            and receipt["contract_sha256"] == approval.contract_sha256
            and receipt["verifier_code_sha256"] == approval.verifier_code_sha256, "receipt binding")
    verify_contents(approval=approval, reader=reader, root=root, files=receipt["files"],
        evidence_commit=receipt["evidence_commit"], observed_terminal=receipt["terminal"], publication_paths=publication_paths)
    return digest(data)
