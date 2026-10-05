"""Pure pre-tag candidate binding, independent of collection Campaign.

No predictor seal, projection, preregistration tag or model-contact grant is
required. Instead the committed candidate manifest, design, synthetic cases
and complete source closure are required. No live Campaign is constructed.
"""
from contextlib import contextmanager
from pathlib import Path
import re
import sys
import os
from exp7core.records import strict_json
from exp7core.guardio import safe_path
from .common import require, pin, digest, decode
from .candidate_audit import CandidateAudit

_UNSET = object()


def git_blob(repo, commit, path):
    import subprocess
    result = subprocess.run(["/opt/homebrew/bin/git", "-C", str(repo), "show", f"{commit}:{path}"],
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout


def prereg_exists(repo):
    import subprocess
    result = subprocess.run(["/opt/homebrew/bin/git", "-C", str(repo), "rev-parse", "--quiet", "--verify",
                             "refs/tags/exp7-preregistered"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(result.returncode in (0, 1), "cannot determine prereg tag state")
    return result.returncode == 0


class CalibrationContext:
    def __init__(self, root, repo, *, candidate_commit, manifest_path, manifest_sha256,
                 blob_reader=_UNSET, tag_probe=_UNSET, read_port=None):
        self.root, self.repo = Path(root), Path(repo).resolve()
        require(type(candidate_commit) is str and re.fullmatch("[0-9a-f]{40}", candidate_commit), "candidate commit")
        self.commit = candidate_commit
        self.manifest_path = manifest_path
        self.manifest_sha = pin(manifest_sha256)
        self.blob_reader = git_blob if blob_reader is _UNSET else blob_reader
        self.tag_probe = prereg_exists if tag_probe is _UNSET else tag_probe
        self.read_port = read_port  # None is the actual platform backend; explicit fakes only in tests.
        require(callable(self.blob_reader) and callable(self.tag_probe), "empty candidate binding injection")
        self._busy = False

    def _manifest(self):
        path = safe_path(self.repo, self.manifest_path)
        raw = path.read_bytes()
        require(digest(raw) == self.manifest_sha, "candidate manifest pin")
        require(self.blob_reader(self.repo, self.commit, self.manifest_path) == raw, "manifest not at committed candidate")
        manifest = strict_json(raw)
        require(type(manifest) is dict and set(manifest) == {"schema", "files"}
                and manifest["schema"] == "exp7.calibration-candidate.v1"
                and type(manifest["files"]) is dict and manifest["files"], "candidate manifest schema")
        kinds = []
        for name, row in manifest["files"].items():
            require(type(row) is dict and set(row) == {"kind", "sha256"}, "candidate file schema")
            require(row["kind"] in ("source", "design", "synthetic_spec", "runtime_spec"), "candidate file role")
            pin(row["sha256"])
            safe_path(self.repo, name)
            kinds.append(row["kind"])
        require("source" in kinds and "design" in kinds and kinds.count("synthetic_spec") == 1
                and kinds.count("runtime_spec") == 1, "source/design/one synthetic and one runtime specification required")
        return manifest

    def _check(self, manifest):
        require(self.tag_probe(self.repo) is False, "calibration must precede preregistration tag")
        require(not self.root.resolve().is_relative_to(self.repo), "calibration output root must be separate from candidate repository")
        for path in self._source_inventory():
            require(path.is_relative_to(self.repo), f"calibration module outside candidate repository: {path}")
            relative = path.relative_to(self.repo).as_posix()
            require(relative in manifest["files"] and manifest["files"][relative]["kind"] == "source",
                    f"candidate omitted executable package source: {relative}")
        for name in ("units", "outcomes", "predictor_seal.json", "predictor-seal.json", "seal.json",
                     "statistics/power", "statistics/analysis"):
            require(not (self.root/name).exists(), f"pre-tag calibration after collection/analysis state: {name}")
        for name, row in manifest["files"].items():
            raw = safe_path(self.repo, name).read_bytes()
            require(digest(raw) == row["sha256"] and self.blob_reader(self.repo, self.commit, name) == raw,
                    f"candidate source/design/spec binding: {name}")
        for module in tuple(sys.modules.values()):
            filename = getattr(module, "__file__", None)
            if not filename:
                continue
            path = Path(filename).resolve()
            if path.is_relative_to(self.repo):
                relative = path.relative_to(self.repo).as_posix()
                require(relative in manifest["files"] and manifest["files"][relative]["kind"] == "source",
                        f"unbound candidate import: {relative}")
                cached = getattr(module, "__cached__", None)
                require(not cached or not Path(cached).exists(), "cold calibration requires absent project bytecode cache")

    def _source_inventory(self):
        import exp7core
        roots = (Path(__file__).resolve().parent, Path(exp7core.__file__).resolve().parent)
        paths = []
        for root in roots:
            require(not any(root.rglob("*.pyc")), "cold candidate package contains bytecode")
            for path in root.rglob("*.py"):
                require(not path.is_symlink(), "candidate source symlink")
                paths.append(path.resolve())
        return paths

    @contextmanager
    def entryexit(self, stage):
        require(stage == "calibration" and not self._busy, "pre-tag context is calibration-only")
        require(self.root.is_dir() and self.repo.is_dir(), "calibration directories")
        manifest = self._manifest()
        self._check(manifest)
        expected = {name: row["sha256"] for name, row in manifest["files"].items()}
        expected[self.manifest_path] = self.manifest_sha
        runtime_path = next(name for name, row in manifest["files"].items() if row["kind"] == "runtime_spec")
        runtime = strict_json(safe_path(self.repo, runtime_path).read_bytes())
        guard = CandidateAudit({str((self.repo/name).resolve()): sha for name, sha in expected.items()},
                               [self.repo/name for name, row in manifest["files"].items() if row["kind"] == "source"], runtime,
                               read_port=self.read_port)
        self._busy = True
        try:
            with guard:
                spec_path = next(name for name, row in manifest["files"].items() if row["kind"] == "synthetic_spec")
                spec_raw = safe_path(self.repo, spec_path).read_bytes()
                yield {"provenance_sha256": digest({"candidate_commit": self.commit, "manifest_sha256": self.manifest_sha}),
                       "input_sha256": {**expected, "synthetic_spec": expected[spec_path]},
                       "candidate_commit": self.commit, "synthetic_spec": decode(strict_json(spec_raw))}
        finally:
            self._busy = False
            require(self._manifest() == manifest, "candidate manifest changed at exit")
            self._check(manifest)
