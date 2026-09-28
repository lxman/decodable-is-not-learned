#!/usr/bin/env bash
# Exp 6, BOX side: move the box's checkout to the Mac's bundle. Refuses (exit 2) unless the tags
# the NEXT stage needs are in the bundle and bind the working tree the stage will read:
#   endpoint stage: exp6-preregistered, exp6-predictor-sealed
#   sweep stage:    the two above, exp6-endpoint-sealed, and the projection's adding commit an
#                   ancestor of HEAD (the projection is sealed BEFORE any intermediate checkpoint).
# NOT `git fetch <bundle> 'refs/heads/*:refs/heads/*'`: git refuses to fetch into the checked-out
# master and the reset that follows silently stays on the OLD commit (Experiment 5, review I-3).
# Usage (on the box): run/rebundle_box_6.sh /workspace/exp6.bundle endpoint|sweep
set -euo pipefail
BUNDLE=${1:?usage: rebundle_box_6.sh <bundle> endpoint|sweep}
STAGE=${2:?usage: rebundle_box_6.sh <bundle> endpoint|sweep}
cd "${REPO_DIR:-/workspace/emergence-paper}"
git bundle verify "$BUNDLE" >/dev/null
git fetch --quiet "$BUNDLE" master --tags --force
git reset --hard FETCH_HEAD
echo "HEAD $(git rev-parse HEAD)"
need="exp6-preregistered exp6-predictor-sealed"
[ "$STAGE" = "sweep" ] && need="$need exp6-endpoint-sealed"
for t in $need; do
  [ -n "$(git tag --list "$t")" ] || { echo "REFUSING: $t is not in the bundle"; exit 2; }
  echo "tag $t at $(git rev-list -n 1 "$t")"
done
if [ "$STAGE" = "sweep" ]; then
  pc=$(git log --diff-filter=A --format=%H -- experiments/exp6/projection.md | tail -1)
  [ -n "$pc" ] || { echo "REFUSING: experiments/exp6/projection.md was never added"; exit 2; }
  git merge-base --is-ancestor "$pc" HEAD || { echo "REFUSING: the projection is not an ancestor of HEAD"; exit 2; }
  echo "projection $pc is an ancestor of HEAD"
fi
