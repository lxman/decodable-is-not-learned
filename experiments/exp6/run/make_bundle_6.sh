#!/usr/bin/env bash
# Exp 6, MAC side: bundle the whole repository (every branch and tag) for the box and print its
# sha256 (check it on the box after scp). No credential is placed on a rented host: the box gets
# the repository by bundle and returns results by rsync pull FROM the Mac.
# Usage: run/make_bundle_6.sh [out]
set -euo pipefail
OUT=${1:-/tmp/exp6.bundle}
cd "${REPO_DIR:-/Users/michaeljordan/emergence-paper}"
git bundle create "$OUT" --all
shasum -a 256 "$OUT"
