#!/usr/bin/env bash
# Exp 5b puller (Mac; Experiment 5's puller reshaped): pull COMPLETE units into this tree for the
# standing watcher to commit. A unit is listed once its `_unit_5b.json` exists on the box (written
# LAST by 5b's attestation, after Experiment 5's own writer); it is re-pulled until all 38 of its
# files are here. Also pulls the top-level `results/*.json` files (host_5b.json, gate1_5b.json,
# power_5b.json — they change over the campaign) and, per size, `HALTED` (no search logs, no
# gate1c — 5b has neither). Loops until killed.
set -uo pipefail
REPO=/Users/michaeljordan/emergence-paper
KEY=~/.ssh/vastai_ed25519
HOST=${VAST_HOST:-ssh5.vast.ai}
PORT=${VAST_PORT:-36148}
REMOTE=/workspace/emergence-paper/experiments/exp5b/results
LOCAL=$REPO/experiments/exp5b/results
SSH="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 -p $PORT"
TMPD=/tmp/exp5b_rsync_tmp          # rsync partials, outside the repo (I-4, exp5)
mkdir -p "$TMPD"
cd "$REPO"
while true; do
  units=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && find . -name _unit_5b.json | sed 's|/_unit_5b.json||; s|^\./||'" 2>/dev/null | grep -v "Have fun" || true)
  for u in $units; do
    mkdir -p "$LOCAL/$(dirname "$u")"
    # final review I-4 (exp5): skip only when ALL 38 files are here (`_unit_5b.json` sorts LAST, so
    # an interrupted rsync can leave the other 37 with the attestation still missing); partials go
    # to a temp dir OUTSIDE the repo, so the tree never holds a half-written file
    n=$(ls -1 "$LOCAL/$u" 2>/dev/null | wc -l | tr -d ' ')
    [ "$n" -eq 38 ] && continue
    rsync -a --temp-dir="$TMPD" -e "$SSH" "root@$HOST:$REMOTE/$u/" "$LOCAL/$u/" 2>/dev/null && echo "[pull $(date +%H:%M:%S)] unit $u ($n -> $(ls -1 "$LOCAL/$u" | wc -l | tr -d ' ') files)"
  done
  always=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && find . -maxdepth 1 -name '*.json'; find . -mindepth 3 -maxdepth 3 -path './units/*' -name HALTED" 2>/dev/null | sed 's|^\./||' | grep -v "Have fun" || true)
  for f in $always; do
    mkdir -p "$LOCAL/$(dirname "$f")"
    rsync -a --temp-dir="$TMPD" -e "$SSH" "root@$HOST:$REMOTE/$f" "$LOCAL/$f" 2>/dev/null && echo "[pull $(date +%H:%M:%S)] $f"
  done
  sleep ${PULL_INTERVAL:-180}
done
