#!/bin/zsh
# Exp 4c commit watcher — commits+pushes each completed unit as it
# lands. Unlike exp4's own two-stage watcher, exp4c has no separate
# reference stage to scope with --stage: it watches the whole results
# tree (results/reference/, just the 13B thin endpoint, and
# results/sweep/, together) as one stage. Committed file types:
# *.json, *.npz, HALTED — EXCLUDING any path containing /activations/
# (gitignored, sha-attested-not-committed). Task 5 controller ruling
# B-5: /attested/ is NOT excluded here — design §3.9 counts it among
# the committed set tables (question-end + pooled sets, sha-bound by
# the record), and `.gitignore`'s own exp4c/attested/ line was removed
# to match. Run alongside the sweep with Michael's launch
# authorization; the push is covered by the standing push policy for
# this repo. Mirrors experiments/exp4/run/commit_watcher_4.sh, minus
# the --stage split.
set -euo pipefail
REPO=~/emergence-paper
cd "$REPO"

WATCH_DIR=experiments/exp4c/results

seen=""
while true; do
  units=$(find "$WATCH_DIR" -type f \( -name '*.json' -o -name '*.npz' -o -name 'HALTED' \) 2>/dev/null \
    | grep -v '/activations/' | sort || true)
  for f in ${(f)units}; do
    if [[ "$seen" != *"|$f|"* ]]; then
      # 2i FREEZE attack item 25 (the watcher race): a fixed 2-second
      # settle is not enough for a still-growing file — a partial blob
      # committed here is the blob a seal tag would bind, and the file
      # is never revisited (the `seen` list is append-only). Wait for
      # the size to stop changing instead of guessing; skip this pass
      # entirely if it is still growing, so the next 30-second sweep
      # retries.
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
        git commit -m "exp4c sweep: ${where:-$unit} landed (watcher)" --quiet
        git push --quiet origin master || echo "[watcher] push failed (will retry with the next unit)"
        echo "[watcher] committed+pushed ${where:-$unit}"
      fi
      seen="${seen}|$f|"
    fi
  done
  sleep 30
done
