"""Future full-default synthetic producer export; planning never invokes main."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import guard
from pathlib import Path
import argparse
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent/"tests"))
from exp7ops.evidence import require, strict, digest
from exp7ops.worlds import make_recipe
from world_fixture import ProducerWorldFixture


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(digest(args.spec.read_bytes()) == args.spec_sha256, "independent synthetic setup spec")
    value = strict(args.spec.read_bytes())
    require(set(value) == {"schema", "source_repo", "source_pins", "calibration_directory", "calibration_files"}
            and value["schema"] == "exp7.full-synthetic-setup.v1", "fixed synthetic setup schema")
    require(args.output.parent.resolve().is_relative_to(Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode")), "scratch export only")
    require(not args.output.exists(), "export write once")
    root = Path(tempfile.mkdtemp(prefix="full-producer-", dir=args.output.parent))
    fixture = ProducerWorldFixture(**{k: value[k] for k in ("source_repo", "source_pins", "calibration_directory", "calibration_files")}, miniature=False)
    fixture.install(root, make_recipe("INPUT-SENSITIVE-FORECAST", "INPUT-SENSITIVE-FORECAST"))
    sha = fixture.export(root, args.output)
    print(sha)


if __name__ == "__main__":
    main()
