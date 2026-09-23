#!/usr/bin/env bash
# Exp 5 puller (Mac; 4c's `pull_13b_results.sh` reshaped): pull COMPLETE units into this tree for the
# standing watcher to commit. A unit is listed once its `_unit.json` exists on the box (written LAST
# by the frozen writer); it is re-pulled until all 37 of its files are here. Also pulls the top-level `results/*.json` files
# (host_5.json, gate1a.json, gate1b.json, loss_table_5.json, power_5.json — they change over the
# campaign) and, per size, `search_log.json`/`gate1c.json`/`HALTED`, always (they change too). Loops
# until killed.
set -uo pipefail
REPO=/Users/michaeljordan/emergence-paper
KEY=~/.ssh/vastai_ed25519
HOST=${VAST_HOST:-ssh5.vast.ai}
PORT=${VAST_PORT:-36148}
REMOTE=/workspace/emergence-paper/experiments/exp5/results
LOCAL=$REPO/experiments/exp5/results
SSH="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 -p $PORT"
TMPD=/tmp/exp5_rsync_tmp          # rsync partials, outside the repo (I-4)
mkdir -p "$TMPD"
cd "$REPO"
while true; do
  units=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && find . -name _unit.json | sed 's|/_unit.json||; s|^\./||'" 2>/dev/null | grep -v "Have fun" || true)
  for u in $units; do
    mkdir -p "$LOCAL/$(dirname "$u")"
    # final review I-4: skip only when ALL 37 files are here (`_unit.json` sorts FIRST, so an
    # interrupted rsync can leave it beside missing rung files); partials go to a temp dir
    # OUTSIDE the repo, so the tree never holds a half-written file
    n=$(ls -1 "$LOCAL/$u" 2>/dev/null | wc -l | tr -d ' ')
    [ "$n" -eq 37 ] && continue
    rsync -a --temp-dir="$TMPD" -e "$SSH" "root@$HOST:$REMOTE/$u/" "$LOCAL/$u/" 2>/dev/null && echo "[pull $(date +%H:%M:%S)] unit $u ($n -> $(ls -1 "$LOCAL/$u" | wc -l | tr -d ' ') files)"
  done
  always=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && find . -maxdepth 1 -name '*.json'; find . -mindepth 2 -maxdepth 2 -path './units/*' \( -name search_log.json -o -name gate1c.json -o -name HALTED \)" 2>/dev/null | sed 's|^\./||' | grep -v "Have fun" || true)
  for f in $always; do
    mkdir -p "$LOCAL/$(dirname "$f")"
    rsync -a --temp-dir="$TMPD" -e "$SSH" "root@$HOST:$REMOTE/$f" "$LOCAL/$f" 2>/dev/null && echo "[pull $(date +%H:%M:%S)] $f"
  done
  sleep ${PULL_INTERVAL:-180}
done
