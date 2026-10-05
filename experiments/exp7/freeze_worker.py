"""Fixed future-freeze entry: always guarded, only exported synthetic producers."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import guard
from pathlib import Path
import argparse
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent/"tests"))
from exp7ops.evidence import require, strict, digest, once, snapshot
from exp7ops.scans import static_imports
from exp7integration.world_harness import full_worlds
from world_fixture import ProducerWorldFixture
from freeze_workers import open_export


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, choices=("worlds", "import-scan", "read-scan"))
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--fixture-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "freeze receipt once")
    require(digest(args.fixture.read_bytes()) == args.fixture_sha256, "independent export pin")
    value = strict(args.fixture.read_bytes())
    require(value.get("fake_git") is True and value.get("fake_model_outputs") is True and value.get("miniature") is False, "full synthetic export only")
    work = Path(tempfile.mkdtemp(prefix="freeze-worker-", dir=args.output.parent))
    f, adapter = open_export(args.fixture, args.fixture_sha256, work, miniature=False)
    package = Path(__file__).resolve().parent
    if args.task == "worlds":
        calibration = f.root/"statistics/calibration"
        fixture = ProducerWorldFixture(source_repo=value["source_repo"], source_pins=value["source_pins"],
                    calibration_directory=calibration, calibration_files=snapshot(calibration), miniature=False)
        result = {"worlds": full_worlds(fixture, work/"worlds")}
    elif args.task == "import-scan":
        pins = {n: sha for n, sha in snapshot(package).items() if n.endswith(".py")}
        result = {"static_source_inventory": static_imports(package, pins),
                  "scope": "static call/import surface; execution trace is read-scan"}
    else:
        from exp7stats.analyzer import run
        report = run(adapter)
        require(report["state"] == "COMPLETE", "synthetic read scan analysis refused")
        trace = adapter.collection.trust.trace
        trace.check()
        require(set(trace.reads) <= set(trace.allowed) and set(trace.executed) <= set(trace.allowed), "unpinned collection read/exec")
        result = {"reads": sorted(trace.reads), "executed": sorted(trace.executed), "pins": trace.allowed,
                  "adapter_sources": value["authority"]["adapter_sources"], "unpinned": [],
                  "scope": "genuine Campaign read/exec boundary plus entry/exit adapter source closure; installed native runtime remains trusted"}
    require(not any(guard.forbidden(n) for n in sys.modules), "worker loaded forbidden module")
    once(args.output, {"state": "COMPLETE", "task": args.task, "synthetic_only": True, **result})


if __name__ == "__main__":
    main()
