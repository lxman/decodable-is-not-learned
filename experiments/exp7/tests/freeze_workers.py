"""Cold numerical worker on an exported synthetic producer tree only.

The full-default entry is provided for the future freeze; planning tests do not
invoke it. Each process copies identical raw/preflight/seal/power bytes instead
of regenerating timings, then runs exactly one analysis in that disposable copy.
"""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import shutil
from exp7ops.evidence import require, strict, digest, canonical, once, verify_files
from exp7core.battery_adapter import load_certified
from exp7core.campaign import Campaign
from exp7stats import analyzer
from exp7stats.common import stage, Shape, dumps
from collection_fixtures import FakeGit
from test_real_composition import FullCardinalityMiniatureAdapter, SyntheticPowerCampaign
from world_fixture import FullDefaultAdapter


def open_export(fixture_path, fixture_sha256, work, *, miniature):
    raw = Path(fixture_path).read_bytes()
    require(digest(raw) == fixture_sha256, "independently bound synthetic export")
    value = strict(raw)
    require(value.get("schema") == "exp7.synthetic-producer-export.v1" and value.get("fake_git") is True
            and value.get("fake_model_outputs") is True and value.get("miniature") is miniature, "synthetic export only")
    source = Path(value["repo"])
    verify_files(source, value["repo_files"], exact=True)
    require((source/"owner.txt").read_bytes() == b"FAKE ONLY authorized fake scope for synthetic fixture\n",
            "explicit synthetic producer authority marker")
    require(not (source/"campaign/statistics/analysis").exists(), "worker input already analyzed")
    trust = strict((source/value["trust_path"]).read_bytes())
    require(trust["hosts"] == {"fakehost": {"host_id": "fakehost", "device": "fake"}}, "no real host data")
    require(digest((source/value["trust_path"]).read_bytes()) == value["trust_sha256"], "worker trust pin")
    def read(name):
        raw = (Path(value["source_repo"])/name).read_bytes()
        require(digest(raw) == value["source_pins"][name], "worker certified source pin")
        return raw
    battery, _, _, baselines = load_certified(read)
    work = Path(work)
    approved = Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode")
    require(work.resolve().is_relative_to(approved) and work.is_dir(), "worker in approved scratch")
    repo = work/"repo"; shutil.copytree(source, repo)
    cls = SyntheticPowerCampaign if miniature else Campaign
    c = cls(repo/"campaign", repo, trust_path=value["trust_path"], trust_sha256=value["trust_sha256"], git=FakeGit())
    c._battery, c._baselines = battery, baselines
    authority = work/"analysis-authority.json"; once(authority, value["authority"])
    cls = FullCardinalityMiniatureAdapter if miniature else FullDefaultAdapter
    adapter = cls(c, authority_path=authority, authority_sha256=digest(authority.read_bytes()))
    verify_files(source, value["repo_files"], exact=True)
    return SimpleNamespace(repo=repo, root=repo/"campaign", data=trust, battery=battery), adapter


def analysis_worker(fixture_path, fixture_sha256, output, *, miniature=False):
    output = Path(output)
    require(not output.exists(), "worker output write once")
    work = Path(tempfile.mkdtemp(prefix="numerical-worker-", dir=output.parent))
    _, adapter = open_export(fixture_path, fixture_sha256, work, miniature=miniature)
    if miniature:
        shape = Shape(permutations=3, bootstraps=1)
        result = stage(adapter, "analysis", lambda p: analyzer._operation(adapter, p, shape, production=False), production=False)
    else:
        result = analyzer.run(adapter)
    require(result["state"] == "COMPLETE", "determinism worker refused; retained raw tree/diagnostics")
    # Exact complete machine report comparison; no field stripping or rounding.
    once(output, dumps(result))
    value = strict(Path(fixture_path).read_bytes())
    verify_files(Path(value["repo"]), value["repo_files"], exact=True)
    return {"sha256": digest(output.read_bytes()), "miniature": miniature, "work": str(work)}
