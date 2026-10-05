"""Future-freeze full-default worker; no real-tree route and no scientific flags."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import guard
from pathlib import Path
import argparse
sys.path.insert(0, str(Path(__file__).resolve().parent/"tests"))
from freeze_workers import analysis_worker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--fixture-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis_worker(args.fixture, args.fixture_sha256, args.output)


if __name__ == "__main__":
    main()
