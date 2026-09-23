#!/usr/bin/env bash
# Exp 5, BOX side (final review I-3): move the box's checkout to the Mac's stage-2 bundle (the targets
# seal tag + the projection commit), replacing the plan's old `git fetch <bundle>
# 'refs/heads/*:refs/heads/*'` recipe — git refuses to fetch into the checked-out master, and the
# reset that followed silently stayed on the OLD commit. Refuses (exit 2) unless the seal tag is
# present and the projection's adding commit is an ancestor of the new HEAD.
# Usage (on the box): run/rebundle_box_5.sh /workspace/exp5-stage2.bundle
set -euo pipefail
BUNDLE=${1:?usage: rebundle_box_5.sh <bundle>}
cd "${REPO_DIR:-/workspace/emergence-paper}"
git bundle verify "$BUNDLE" >/dev/null
git fetch --quiet "$BUNDLE" master --tags
git reset --hard FETCH_HEAD
echo "HEAD $(git rev-parse HEAD)"
tag=$(git tag --list exp5-targets-sealed)
echo "targets seal tag: ${tag:-MISSING}"
[ -n "$tag" ] || { echo "REFUSING: exp5-targets-sealed is not in the bundle"; exit 2; }
pc=$(git log --diff-filter=A --format=%H -- experiments/exp5/projection.md | tail -1)
echo "projection adding commit: ${pc:-MISSING}"
[ -n "$pc" ] || { echo "REFUSING: experiments/exp5/projection.md was never added"; exit 2; }
if git merge-base --is-ancestor "$pc" HEAD; then
  echo "projection ${pc} is an ancestor of HEAD"
else
  echo "REFUSING: the projection is not an ancestor of HEAD"; exit 2
fi
git tag --list 'exp5-*'
