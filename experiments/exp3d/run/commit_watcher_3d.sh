#!/bin/zsh
# Exp 3d commit watcher — the §10.4 per-block cadence, executable.
# Watches the 3d results tree and commits+pushes each completed unit
# (gate-1 record, scoring record, sampling block shard pair) as it
# lands. Run alongside the campaign with Michael's launch
# authorization; the push itself is covered by that authorization.
set -euo pipefail
REPO=~/emergence-paper
cd "$REPO"
seen=""
while true; do
  units=$(find experiments/exp3d/results -type f \
          \( -name '*.json' -o -name '*.draws.jsonl.gz' \) \
          2>/dev/null | sort || true)
  for f in ${(f)units}; do
    if [[ "$seen" != *"|$f|"* ]]; then
      # a shard is complete only when its record json exists too
      case "$f" in
        *.draws.jsonl.gz)
          rec="${f%.draws.jsonl.gz}.json"
          [[ -f "$rec" ]] || continue ;;
      esac
      sleep 2   # settle
      git add "$f" 2>/dev/null || true
      case "$f" in
        *.draws.jsonl.gz) git add "${f%.draws.jsonl.gz}.json" \
          2>/dev/null || true ;;
      esac
      if ! git diff --cached --quiet; then
        unit=$(basename "$f")
        git commit -m "exp3d campaign: ${unit} landed (watcher)" \
          --quiet
        git push --quiet origin master
        echo "[watcher] committed+pushed ${unit}"
      fi
      seen="${seen}|$f|"
    fi
  done
  sleep 30
done
