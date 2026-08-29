#!/bin/zsh
# Exp 2k commit watcher — the §10 per-rung cadence, executable. Watches
# the 2k results tree and commits+pushes each completed unit (tier
# record, tier draws, halt marker, halted draws) as it lands. Run
# alongside the campaign with Michael's launch authorization; the push
# itself is covered by the standing push policy for this repo. Mirrors
# experiments/exp2d/run/commit_watcher_2d.sh, with the tree swapped and
# 2i's size-stability lesson applied to the draws file (a ~MB
# `.draws.jsonl.gz` is not complete the second it appears — a 10-second
# poll pair, not a fixed settle, decides when it is safe to commit).
set -euo pipefail
REPO=~/emergence-paper
cd "$REPO"
seen=""
while true; do
  units=$(find experiments/exp2k/results \
          -type f \( -name '*.json' -o -name '*.draws.jsonl.gz' \
          -o -name '*.HALTED' -o -name '*.HALTED.jsonl.gz' \) 2>/dev/null | sort || true)
  for f in ${(f)units}; do
    if [[ "$seen" != *"|$f|"* ]]; then
      case "$f" in
        *.draws.jsonl.gz)
          rec="${f%.draws.jsonl.gz}.json"
          [[ -f "$rec" ]] || continue
          sz1=$(stat -f%z "$f" 2>/dev/null || echo -1)
          sleep 10
          sz2=$(stat -f%z "$f" 2>/dev/null || echo -2)
          if [[ "$sz1" != "$sz2" ]]; then
            echo "[watcher] $f still growing ($sz1 -> $sz2), deferring"
            continue
          fi
          ;;
        *)
          sleep 2   # settle
          ;;
      esac
      git add "$f" 2>/dev/null || true
      case "$f" in
        *.draws.jsonl.gz) git add "${f%.draws.jsonl.gz}.json" \
          2>/dev/null || true ;;
      esac
      if ! git diff --cached --quiet; then
        unit=$(basename "$f")
        size=$(echo "$f" | sed -E 's#experiments/exp2k/results/k256/([^/]+)/.*#\1#')
        git commit -m "exp2k campaign: ${size} ${unit} landed (watcher)" \
          --quiet
        git push --quiet origin master
        echo "[watcher] committed+pushed ${size} ${unit}"
      fi
      seen="${seen}|$f|"
    fi
  done
  sleep 30
done
