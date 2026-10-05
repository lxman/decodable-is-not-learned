from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import canonical, digest, strict, Refusal
from exp7integration.candidate_runtime import propose_runtime, accept_reviewed_runtime, prepare_candidate_manifest
from testing_paths import WORK


class RuntimePreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ("stdlib", "numpy"):
            (self.root/name).mkdir()
        source = self.root/"stdlib/fake.py"; source.write_bytes(b"# fabricated runtime bytes\n")
        self.selection = {"schema": "exp7.runtime-selection.v1", "roots": {k: str(self.root/k) for k in ("stdlib", "numpy")},
                          "files": {str(source): "stdlib"}, "frozen": [], "generated": {}}
        self.path = self.root/"selection.json"; self.path.write_bytes(canonical(self.selection))
        self.proposal = self.root/"proposal.json"
        self.sha = propose_runtime(self.path, digest(self.path.read_bytes()), self.proposal, generated_witnesses={})

    def review(self):
        value = strict(self.proposal.read_bytes()); runtime = value["runtime"]
        artifact = self.root/"independent-reproduction.txt"; artifact.write_bytes(b"FAKE reviewer artifact for interface tests only\n")
        review = {"schema": "exp7.runtime-independent-review.v1", "proposal_sha256": self.sha,
                  "runtime_sha256": value["runtime_sha256"], **{k: runtime[k] for k in ("files", "frozen", "generated")},
                  "evidence": {str(artifact): digest(artifact.read_bytes())}}
        path = self.root/"review.json"; path.write_bytes(canonical(review))
        return path, digest(path.read_bytes())

    def test_measured_proposal_is_not_a_candidate_runtime_or_review(self):
        value = strict(self.proposal.read_bytes())
        self.assertIs(value["authority"], False)
        with self.assertRaises(Refusal):
            accept_reviewed_runtime(self.proposal, self.sha, self.proposal, self.sha, self.root/"runtime.json")
        self.assertFalse((self.root/"runtime.json").exists())

    def test_separately_pinned_review_materializes_exact_runtime_and_refuses_drift(self):
        review, sha = self.review(); output = self.root/"runtime.json"
        receipt = accept_reviewed_runtime(self.proposal, self.sha, review, sha, output)
        self.assertEqual(receipt["runtime_sha256"], digest(output.read_bytes()))
        (self.root/"stdlib/fake.py").write_bytes(b"drift")
        with self.assertRaisesRegex(Refusal, "drift after review"):
            accept_reviewed_runtime(self.proposal, self.sha, review, sha, self.root/"runtime-again.json")

    def test_review_sha_cannot_be_learned_from_modified_review(self):
        review, sha = self.review(); review.write_bytes(b"{}")
        with self.assertRaisesRegex(Refusal, "independent preparation input SHA"):
            accept_reviewed_runtime(self.proposal, self.sha, review, sha, self.root/"runtime.json")

    def test_candidate_preparation_requires_reviewed_complete_cold_source_pins(self):
        repo = self.root/"candidate"; repo.mkdir()
        files = {}
        for package in ("exp7core", "exp7stats", "exp7ops", "exp7integration", "run"):
            name = f"experiments/exp7/{package}/__init__.py"
            path = repo/name; path.parent.mkdir(parents=True); path.write_bytes(b"# fake source\n")
            files[name] = {"kind": "source", "sha256": digest(path.read_bytes())}
        for name, kind in (("design.md", "design"), ("cases.json", "synthetic_spec"), ("runtime.json", "runtime_spec")):
            (repo/name).write_bytes(b"fabricated candidate metadata only\n")
            files[name] = {"kind": kind, "sha256": digest((repo/name).read_bytes())}
        selection = self.root/"candidate-selection.json"
        selection.write_bytes(canonical({"schema": "exp7.candidate-selection.v1", "files": files}))
        sha = digest(selection.read_bytes())
        receipt = prepare_candidate_manifest(repo, selection, sha, output=repo/"manifest.json")
        self.assertFalse(receipt["committed"])
        self.assertEqual(receipt["manifest_sha256"], digest((repo/"manifest.json").read_bytes()))
        (repo/"experiments/exp7/exp7stats/read_boundary.py").write_bytes(b"# omitted input-boundary dependency\n")
        with self.assertRaisesRegex(Refusal, "omitted candidate executable"):
            prepare_candidate_manifest(repo, selection, sha, output=repo/"invalid.json")
