#!/usr/bin/env bash
# Exp 5b, BOX side (Experiment 5's I-3 recipe): move the box's checkout to the Mac's bundle (the
# preregistration tag + the projection commit), replacing the old `git fetch <bundle>
# 'refs/heads/*:refs/heads/*'` recipe — git refuses to fetch into the checked-out master, and the
# reset that followed silently stayed on the OLD commit. Refuses (exit 2) unless `exp5b-preregistered`
# is present and `experiments/exp5b/projection.md`'s adding commit is an ancestor of the new HEAD.
# Usage (on the box): run/rebundle_box_5b.sh /workspace/exp5b.bundle
set -euo pipefail
BUNDLE=${1:?usage: rebundle_box_5b.sh <bundle>}
cd "${REPO_DIR:-/workspace/emergence-paper}"
git bundle verify "$BUNDLE" >/dev/null
git fetch --quiet "$BUNDLE" master --tags
git reset --hard FETCH_HEAD
echo "HEAD $(git rev-parse HEAD)"
tag=$(git tag --list exp5b-preregistered)
echo "preregistration tag: ${tag:-MISSING}"
[ -n "$tag" ] || { echo "REFUSING: exp5b-preregistered is not in the bundle"; exit 2; }
pc=$(git log --diff-filter=A --format=%H -- experiments/exp5b/projection.md | tail -1)
echo "projection adding commit: ${pc:-MISSING}"
[ -n "$pc" ] || { echo "REFUSING: experiments/exp5b/projection.md was never added"; exit 2; }
if git merge-base --is-ancestor "$pc" HEAD; then
  echo "projection ${pc} is an ancestor of HEAD"
else
  echo "REFUSING: the projection is not an ancestor of HEAD"; exit 2
fi
git tag --list 'exp5-*' 'exp5b-*'
