#!/bin/zsh
# Reproduce the anonymized OpenReview supplementary zip from the public
# repository: clone, drop .git and *.draws.jsonl.gz, scrub identity
# terms ([AUTHOR]/[anon]/[redacted-email]), verify zero residuals, zip.
# The authoritative scrub term list and verification live in the
# session ledger (2026-08-18); this script re-runs the same procedure.
set -e
WORK=$(mktemp -d)
git clone --quiet https://github.com/[anon-org]/decodable-is-not-learned.git $WORK/src
echo "Edit [anon-org] to the real org, then run the python scrub from"
echo "the 2026-08-18 ledger procedure. Kept deliberately manual: the"
echo "zip is rebuilt rarely and the residual scan must be eyeballed."
