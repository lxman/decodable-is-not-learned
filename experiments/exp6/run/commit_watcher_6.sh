#!/bin/zsh
# Exp 6 commit watcher (Mac) — commits and pushes newly landed OR modified result files every
# cycle, staging by pathspec (the JSON records, the gzipped draws, the HALTED markers) plus
# changes to files already tracked; never `git add -A` (an rsync temp file must never be committed).
# Settle check (2i's watcher-race lesson): two snapshots of the tree 3 s apart; if anything changed
# size between them the cycle defers rather than committing a partial write.
# No hand commit is made over a live watcher (4c's process note 3); the controller pauses it first.
set -uo pipefail
REPO=~/emergence-paper
cd "$REPO"
WATCH_DIR=experiments/exp6/results

_snapshot() {
  find "$WATCH_DIR" -type f \( -name '*.json' -o -name '*.jsonl.gz' -o -name 'HALTED' -o -name '*.HALTED' \) \
    2>/dev/null | sort | while read -r f; do stat -f '%N %z' "$f" 2>/dev/null; done
}

while true; do
  s1=$(_snapshot)
  sleep 3
  s2=$(_snapshot)
  if [[ "$s1" != "$s2" ]]; then
    echo "[watcher] $WATCH_DIR still changing, deferring this cycle"
    sleep 57
    continue
  fi
  git add -- ":(glob)$WATCH_DIR/**/*.json" 2>/dev/null || true
  git add -- ":(glob)$WATCH_DIR/**/*.jsonl.gz" 2>/dev/null || true
  git add -- ":(glob)$WATCH_DIR/**/HALTED" 2>/dev/null || true
  git add -- ":(glob)$WATCH_DIR/**/*.HALTED" 2>/dev/null || true
  git add -u -- "$WATCH_DIR" 2>/dev/null || true
  if ! git diff --cached --quiet; then
    n=$(git diff --cached --name-only | wc -l | tr -d ' ')
    git commit -m "exp6 results: ${n} file(s) landed (watcher)" --quiet
    git push --quiet origin master || echo "[watcher] push failed (will retry next cycle)"
    echo "[watcher] committed+pushed ${n} file(s)"
  fi
  sleep 57
done
