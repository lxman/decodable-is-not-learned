#!/bin/zsh
# Exp 2d commit watcher — the §10 per-rung cadence, executable.
# Watches the 2d results tree and commits+pushes each completed unit
# (pilot/main record+draws pair, gate-1 record, argmax record,
# power_2d.json) as it lands. Run alongside the campaign with
# Michael's launch authorization; the push itself is covered by the
# standing push policy for this repo.
set -euo pipefail
REPO=~/emergence-paper
cd "$REPO"
seen=""
while true; do
  units=$(find experiments/exp2d/results experiments/exp2d/power_2d.json \
          -type f \( -name '*.json' -o -name '*.draws.jsonl.gz' \
          -o -name '*.HALTED.jsonl.gz' \) 2>/dev/null | sort || true)
  for f in ${(f)units}; do
    if [[ "$seen" != *"|$f|"* ]]; then
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
        tier=$(echo "$f" | sed -E 's#experiments/exp2d/results/([^/]+)/([^/]+)/.*#\1/\2#')
        git commit -m "exp2d campaign: ${tier} ${unit} landed (watcher)" \
          --quiet
        git push --quiet origin master
        echo "[watcher] committed+pushed ${tier} ${unit}"
      fi
      seen="${seen}|$f|"
    fi
  done
  sleep 30
done
