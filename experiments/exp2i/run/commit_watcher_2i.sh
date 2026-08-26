#!/bin/zsh
# Exp 2i commit watcher — commits+pushes each completed unit as it
# lands, scoped to one stage's directory via --stage: predictor
# (draws+records under results/predictor), endpoint (records +
# rung_set_2i.json under results/endpoint), sweep (records,
# _checkpoint.json, gate1.json, HALTED under results/sweep — Task 4).
# Run alongside a stage with Michael's launch authorization; the push
# is covered by the standing push policy for this repo. Mirrors
# experiments/exp2h/run/commit_watcher_2h.sh.
set -euo pipefail
REPO=~/emergence-paper
cd "$REPO"

STAGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage) STAGE="$2"; shift 2 ;;
    *) echo "usage: commit_watcher_2i.sh --stage predictor|endpoint|sweep" >&2; exit 1 ;;
  esac
done
case "$STAGE" in
  predictor) WATCH_DIR=experiments/exp2i/results/predictor ;;
  endpoint)  WATCH_DIR=experiments/exp2i/results/endpoint ;;
  sweep)     WATCH_DIR=experiments/exp2i/results/sweep ;;
  *) echo "usage: commit_watcher_2i.sh --stage predictor|endpoint|sweep" >&2; exit 1 ;;
esac

seen=""
while true; do
  units=$(find "$WATCH_DIR" -type f \( -name '*.json' -o -name '*.jsonl.gz' -o -name 'HALTED' \) 2>/dev/null | sort || true)
  for f in ${(f)units}; do
    if [[ "$seen" != *"|$f|"* ]]; then
      # FREEZE attack item 25 (the watcher race): a fixed 2-second
      # settle is not enough for a ~1 GB `.draws.jsonl.gz` still being
      # written — a partial blob committed here is the blob
      # `exp2i-predictor-sealed` would bind, and the file is never
      # revisited (the `seen` list is append-only). Wait for the size
      # to stop changing instead of guessing; skip this pass entirely
      # if it is still growing, so the next 30-second sweep retries.
      sz1=$(stat -f%z "$f" 2>/dev/null || echo -1)
      sleep 3
      sz2=$(stat -f%z "$f" 2>/dev/null || echo -2)
      if [[ "$sz1" != "$sz2" ]]; then
        echo "[watcher] $f still growing ($sz1 -> $sz2), deferring"
        continue
      fi
      git add "$f" 2>/dev/null || true
      if ! git diff --cached --quiet; then
        unit=$(basename "$f")
        where=$(echo "$f" | sed -E "s#${WATCH_DIR}/?##")
        git commit -m "exp2i ${STAGE}: ${where:-$unit} landed (watcher)" --quiet
        git push --quiet origin master || echo "[watcher] push failed (will retry with the next unit)"
        echo "[watcher] committed+pushed ${where:-$unit}"
      fi
      seen="${seen}|$f|"
    fi
  done
  sleep 30
done
