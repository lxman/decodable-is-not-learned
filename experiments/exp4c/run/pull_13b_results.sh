#!/usr/bin/env bash
# exp4c 13B on the rented box (ledger 2026-09-21, ruling 3): pull COMPLETE units into this tree for the
# standing watcher to commit. A unit is complete when its `_load.json` exists (written last by the frozen
# writer); only those directories are pulled, `activations/` excluded (dropped on the box at unit close
# anyway). Also pulls gate1.json and any HALTED marker under the 13B sweep root. Loops until killed.
set -uo pipefail
REPO=/Users/michaeljordan/emergence-paper
KEY=~/.ssh/vastai_ed25519
HOST=${VAST_HOST:-ssh5.vast.ai}
PORT=${VAST_PORT:-36148}
REMOTE=/workspace/emergence-paper/experiments/exp4c/results
LOCAL=$REPO/experiments/exp4c/results
SSH="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 -p $PORT"
cd "$REPO"
while true; do
  units=$($SSH root@$HOST "cd $REMOTE 2>/dev/null && find . -name _load.json -path '*olmo2_13b*' | sed 's|/_load.json||; s|^\./||' ; find . -maxdepth 3 \( -name gate1.json -o -name 'HALTED*' -o -name '*.HALTED*' \) -path '*olmo2_13b*' 2>/dev/null | sed 's|^\./||'" 2>/dev/null | grep -v "Have fun" || true)
  for u in $units; do
    mkdir -p "$LOCAL/$(dirname "$u")"
    if [ "${u##*.}" = "json" ] || [[ "$u" == *HALTED* ]]; then
      rsync -a -e "$SSH" "root@$HOST:$REMOTE/$u" "$LOCAL/$u" 2>/dev/null && echo "[pull $(date +%H:%M:%S)] $u"
    else
      [ -f "$LOCAL/$u/_load.json" ] && continue
      rsync -a --exclude 'activations/' -e "$SSH" "root@$HOST:$REMOTE/$u/" "$LOCAL/$u/" 2>/dev/null && echo "[pull $(date +%H:%M:%S)] unit $u ($(ls "$LOCAL/$u/sets" 2>/dev/null | wc -l | tr -d ' ') sets)"
    fi
  done
  sleep ${PULL_INTERVAL:-180}
done
