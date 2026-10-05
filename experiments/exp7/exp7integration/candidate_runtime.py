"""Two-step runtime preparation: measured proposal, then independently pinned review.

No live-file discovery establishes authority. The explicit selection is reviewed
administrative input; measured bytes/fingerprints are only a proposal until a
separate reviewer reproduces them and the launch enrollment supplies that review's
SHA. No calibration, model import, dynamic import or generated-code execution.
"""
from pathlib import Path
import _imp
import types
from exp7ops.evidence import canonical, digest, strict, once, require, pin
from exp7stats.candidate_audit import code_hash


def _read(path, expected):
    path = Path(path)
    require(not path.is_symlink(), "runtime preparation symlink")
    raw = path.read_bytes()
    require(digest(raw) == pin(expected), "independent preparation input SHA")
    return strict(raw)


def propose_runtime(selection_path, selection_sha256, output, *, generated_witnesses):
    """Explicit CodeType witnesses are observed cold-import artifacts, not trusted.

    selection: roots, files(path->role), frozen(list), generated(fingerprint->producer).
    The independent reviewer must reproduce each generated witness from its named
    pinned producer; handing this function an arbitrary CodeType cannot approve it.
    """
    selection = _read(selection_path, selection_sha256)
    require(set(selection) == {"schema", "roots", "files", "frozen", "generated"} and
            selection["schema"] == "exp7.runtime-selection.v1", "explicit runtime selection")
    roots = selection["roots"]
    require(type(roots) is dict and set(roots) == {"stdlib", "numpy"}, "runtime root roles")
    require(all(Path(p).is_dir() and str(Path(p).resolve()) == p for p in roots.values()), "canonical runtime roots")
    files = {}
    for name, role in selection["files"].items():
        path = Path(name)
        require(role in ("stdlib", "numpy", "helper") and str(path.resolve()) == name and path.is_file(), "selected runtime file")
        require(role == "helper" or path.is_relative_to(Path(roots[role])), "selected runtime root membership")
        files[name] = {"role": role, "sha256": digest(path.read_bytes())}
    require(files, "empty runtime file proposal")
    require(type(selection["frozen"]) is list and len(set(selection["frozen"])) == len(selection["frozen"]), "explicit frozen modules")
    frozen = {}
    for name in selection["frozen"]:
        require(_imp.is_frozen(name), "selected interpreter frozen module")
        frozen[name] = code_hash(_imp.get_frozen_object(name))
    require(type(generated_witnesses) is dict and set(generated_witnesses) == set(selection["generated"]), "exact generated witness inventory")
    generated = {}
    for fingerprint, producer in selection["generated"].items():
        require(isinstance(generated_witnesses[fingerprint], types.CodeType) and
                code_hash(generated_witnesses[fingerprint]) == pin(fingerprint), "generated witness fingerprint")
        require(producer in files and Path(producer).suffix == ".py", "selected generated-code producer source")
        generated[fingerprint] = {"producer": producer, "producer_sha256": files[producer]["sha256"]}
    runtime = {"schema": "exp7.calibration-runtime.v1", "roots": roots, "files": files, "frozen": frozen, "generated": generated}
    proposal = {"schema": "exp7.runtime-proposal.v1", "authority": False, "selection_sha256": pin(selection_sha256),
                "runtime": runtime, "runtime_sha256": digest(canonical(runtime))}
    once(output, proposal)
    return digest(canonical(proposal))


def accept_reviewed_runtime(proposal_path, proposal_sha256, review_path, review_sha256, output):
    """Administrative SHA inputs must come from independent candidate review.

    The review names its evidence artifact hashes, checked file pins, separately
    recomputed frozen hashes and reproduced generated fingerprints. It is not an
    owner model-contact grant, and grants no calibration execution by itself.
    """
    proposal, review = _read(proposal_path, proposal_sha256), _read(review_path, review_sha256)
    require(proposal.get("schema") == "exp7.runtime-proposal.v1" and proposal.get("authority") is False, "proposal only")
    runtime = proposal["runtime"]
    expected = digest(canonical(runtime))
    require(proposal["runtime_sha256"] == expected, "proposal runtime hash")
    require(type(review) is dict and set(review) == {"schema", "proposal_sha256", "runtime_sha256", "files", "frozen", "generated", "evidence"}
            and review["schema"] == "exp7.runtime-independent-review.v1", "independent runtime review schema")
    require(review["proposal_sha256"] == proposal_sha256 and review["runtime_sha256"] == expected, "independent runtime review binding")
    for key in ("files", "frozen", "generated"):
        require(review[key] == runtime[key], "independent runtime reproduction differs: "+key)
    require(type(review["evidence"]) is dict and review["evidence"], "independent reproduction artifacts required")
    for name, sha in review["evidence"].items():
        path = Path(name)
        require(path.is_absolute() and not path.is_symlink() and digest(path.read_bytes()) == pin(sha), "runtime review evidence byte binding")
    for name, row in runtime["files"].items():
        require(digest(Path(name).read_bytes()) == row["sha256"], "runtime drift after review")
    for name, sha in runtime["frozen"].items():
        require(_imp.is_frozen(name) and code_hash(_imp.get_frozen_object(name)) == sha, "interpreter drift after review")
    once(output, runtime)
    return {"runtime_sha256": expected, "proposal_sha256": pin(proposal_sha256), "review_sha256": pin(review_sha256)}


def prepare_candidate_manifest(repo, selection_path, selection_sha256, *, output):
    """Materialize reviewed candidate pins before their subsequent Git commit.

    selection is independently reviewed exact metadata, not discovered authority:
    schema exp7.candidate-selection.v1; files matches CalibrationContext's schema.
    The output's actual future commit/manifest SHA must be independently enrolled
    in the calibration deployment after source/runtime review. No Git write here.
    """
    from exp7ops.evidence import path_in
    repo = Path(repo).resolve(strict=True)
    selection = _read(selection_path, selection_sha256)
    require(set(selection) == {"schema", "files"} and selection["schema"] == "exp7.candidate-selection.v1", "reviewed candidate selection")
    files = selection["files"]
    require(type(files) is dict and files, "candidate file pins")
    kinds = []
    for name, row in files.items():
        require(type(row) is dict and set(row) == {"kind", "sha256"} and row["kind"] in ("source", "design", "synthetic_spec", "runtime_spec"), "candidate role")
        require(digest(path_in(repo, name).read_bytes()) == pin(row["sha256"]), "reviewed candidate byte pin")
        kinds.append(row["kind"])
    require("source" in kinds and "design" in kinds and kinds.count("synthetic_spec") == kinds.count("runtime_spec") == 1, "candidate role coverage")
    for package in ("exp7core", "exp7stats", "exp7ops", "exp7integration", "run"):
        folder = repo/"experiments/exp7"/package
        require(folder.is_dir() and not any(folder.rglob("*.pyc")), "cold full candidate package required")
        for path in folder.rglob("*.py"):
            name = path.relative_to(repo).as_posix()
            require(not path.is_symlink() and name in files and files[name]["kind"] == "source", "omitted candidate executable")
    manifest = {"schema": "exp7.calibration-candidate.v1", "files": files}
    once(output, manifest)
    return {"manifest_sha256": digest(canonical(manifest)), "selection_sha256": pin(selection_sha256), "committed": False}
