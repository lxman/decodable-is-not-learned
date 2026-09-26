#!/usr/bin/env bash
# Exp 5b, MAC side (final review I-3, exp5): bundle the whole repository (every branch and tag) for
# the box and print its sha256 (check it on the box after scp). Usage: run/make_bundle_5b.sh [out]
set -euo pipefail
OUT=${1:-/tmp/exp5b.bundle}
cd "${REPO_DIR:-/Users/michaeljordan/emergence-paper}"
git bundle create "$OUT" --all
shasum -a 256 "$OUT"
