"""Test paths independent of annex/install layout; all writes stay in scratch."""
from pathlib import Path
PACKAGE = Path(__file__).resolve().parent
APPROVED = Path("/private/var/folders/mf/s8lnfd3j5s3ggxkr32n1ftnw0000gn/T/opencode")
ROOT = PACKAGE.parent if PACKAGE.parent.is_relative_to(APPROVED) else APPROVED/"exp7-integration-tests"
WORK = ROOT/"test-work"
WORK.mkdir(parents=True, exist_ok=True)
CONTRACTS = PACKAGE/"contracts"
