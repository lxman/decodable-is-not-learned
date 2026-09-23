#!/bin/zsh
# Exp 5 commit watcher — commits+pushes newly-landed OR modified files every cycle. Unlike 4c's
# watcher (an append-only `seen` list, so a file that is re-written in place — the loss table, a
# search log, a gate record retried after a HALTED tolerance miss — is never re-committed once
# seen), this one re-stages every `*.json` and `HALTED` under the results tree each cycle (by
# pathspec, plus `git add -u` for tracked files) and commits only if something is staged, so a
# modified file is picked up again on its next change; never `git add -A` (final review I-4).
#
# Settle check (2i's watcher-race lesson, carried from 4c): every cycle takes two snapshots of the
# tree 3 s apart; if anything changed size between them, the cycle defers rather than committing a
# partial write. Run alongside a campaign stage with Michael's launch authorization; the push is
# covered by the standing push policy for this repo.
set -uo pipefail
REPO=~/emergence-paper
cd "$REPO"

WATCH_DIR=experiments/exp5/results

_snapshot() {
  find "$WATCH_DIR" -type f \( -name '*.json' -o -name 'HALTED' \) 2>/dev/null | sort \
    | while read -r f; do stat -f '%N %z' "$f" 2>/dev/null; done
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
  # final review I-4: stage by pathspec — the JSON records and HALTED markers only, plus changes
  # to files already tracked — never `git add -A` (an rsync temp file must never be committed)
  git add -- ":(glob)$WATCH_DIR/**/*.json" 2>/dev/null || true
  git add -- ":(glob)$WATCH_DIR/**/HALTED" 2>/dev/null || true
  git add -u -- "$WATCH_DIR" 2>/dev/null || true
  if ! git diff --cached --quiet; then
    n=$(git diff --cached --name-only | wc -l | tr -d ' ')
    git commit -m "exp5 sweep: ${n} file(s) landed (watcher)" --quiet
    git push --quiet origin master || echo "[watcher] push failed (will retry next cycle)"
    echo "[watcher] committed+pushed ${n} file(s)"
  fi
  sleep 57
done
