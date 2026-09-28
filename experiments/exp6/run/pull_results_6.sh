#!/usr/bin/env bash
# Exp 6 puller (Mac): pull COMPLETE units from the box into this tree for the standing watcher to
# commit. A model load's records are listed once its load record exists on the box — the runners
# write it LAST — and re-pulled until every file of the directory is here. The top-level records
# (hosts, gate records, HALTED markers, failed_steps) are pulled every cycle. rsync partials go to
# a directory OUTSIDE the repository, so the tree never holds a half-written file. Loops until killed.
# The Mac pulls; nothing on the box can reach the Mac or the repository's remote.
set -uo pipefail
REPO=/Users/michaeljordan/emergence-paper
KEY=~/.ssh/vastai_ed25519
HOST=${VAST_HOST:?set VAST_HOST}
PORT=${VAST_PORT:?set VAST_PORT}
REMOTE=/workspace/emergence-paper/experiments/exp6/results
LOCAL=$REPO/experiments/exp6/results
SSH="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 -p $PORT"
TMPD=/tmp/exp6_rsync_tmp
mkdir -p "$TMPD"
cd "$REPO"
while true; do
  # directories whose completeness record exists: endpoint/<family>/_<which>.json names
  # endpoint/<family>/<which>/; sweep/<family>/step<N>/_checkpoint.json names its own directory;
  # sweep/<family>/gate1_<host>/_thin.json and _cand.json name thin/ and cand/
  dirs=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && { \
      find endpoint -maxdepth 2 -name '_*.json' 2>/dev/null | sed -E 's|/_([a-z0-9_]+)\.json$|/\1|'; \
      find sweep -name _checkpoint.json 2>/dev/null | sed 's|/_checkpoint.json$||'; \
      find sweep -maxdepth 3 -name '_thin.json' 2>/dev/null | sed 's|/_thin.json$|/thin|'; \
      find sweep -maxdepth 3 -name '_cand.json' 2>/dev/null | sed 's|/_cand.json$|/cand|'; }" \
    2>/dev/null | grep -v "Have fun" || true)
  for d in $dirs; do
    want=$($SSH root@$HOST "ls -1 $REMOTE/$d 2>/dev/null | wc -l" 2>/dev/null | tr -d ' ')
    have=$(ls -1 "$LOCAL/$d" 2>/dev/null | wc -l | tr -d ' ')
    [ -n "$want" ] && [ "$have" -eq "$want" ] && continue
    mkdir -p "$LOCAL/$d"
    rsync -a --temp-dir="$TMPD" -e "$SSH" "root@$HOST:$REMOTE/$d/" "$LOCAL/$d/" 2>/dev/null \
      && echo "[pull $(date +%H:%M:%S)] $d ($have -> $(ls -1 "$LOCAL/$d" | wc -l | tr -d ' ') files)"
  done
  always=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && { \
      find hosts -name '*.json' 2>/dev/null; find endpoint -maxdepth 2 -name '*.json' 2>/dev/null; \
      find endpoint -maxdepth 1 -name HALTED 2>/dev/null; \
      find sweep -maxdepth 2 \( -name 'gate1_*.json' -o -name HALTED \) 2>/dev/null; \
      find sweep -maxdepth 3 \( -name '_thin.json' -o -name '_cand.json' \) 2>/dev/null; \
      find sweep -path '*/failed_steps/*' -type f 2>/dev/null; }" 2>/dev/null | grep -v "Have fun" || true)
  for f in $always; do
    mkdir -p "$LOCAL/$(dirname "$f")"
    rsync -a --temp-dir="$TMPD" -e "$SSH" "root@$HOST:$REMOTE/$f" "$LOCAL/$f" 2>/dev/null
  done
  sleep ${PULL_INTERVAL:-180}
done
