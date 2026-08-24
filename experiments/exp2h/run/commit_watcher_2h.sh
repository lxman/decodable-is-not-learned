#!/bin/zsh
# Exp 2h commit watcher — commits+pushes each completed sweep unit as it
# lands (per-rung records, _checkpoint.json, gate1.json, HALTED). Run
# alongside the sweep with Michael's launch authorization; the push is
# covered by the standing push policy for this repo.
set -euo pipefail
REPO=~/emergence-paper
cd "$REPO"
seen=""
while true; do
  units=$(find experiments/exp2h/results/sweep -type f \( -name '*.json' -o -name 'HALTED' \) 2>/dev/null | sort || true)
  for f in ${(f)units}; do
    if [[ "$seen" != *"|$f|"* ]]; then
      sleep 2
      git add "$f" 2>/dev/null || true
      if ! git diff --cached --quiet; then
        unit=$(basename "$f")
        where=$(echo "$f" | sed -E 's#experiments/exp2h/results/sweep/([^/]+)/([^/]+)/?.*#\1/\2#')
        git commit -m "exp2h sweep: ${where} ${unit} landed (watcher)" --quiet
        git push --quiet origin master || echo "[watcher] push failed (will retry with the next unit)"
        echo "[watcher] committed+pushed ${where} ${unit}"
      fi
      seen="${seen}|$f|"
    fi
  done
  sleep 30
done
