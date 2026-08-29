#!/bin/zsh
# Exp 2k commit watcher — the §10 per-rung cadence, executable. Watches
# the 2k results tree and commits+pushes each completed unit (tier
# record, tier draws, halt marker, halted draws) as it lands. Run
# alongside the campaign with Michael's launch authorization; the push
# itself is covered by the standing push policy for this repo. Mirrors
# experiments/exp2d/run/commit_watcher_2d.sh, with the tree swapped and
# 2i's size-stability lesson applied to BOTH gz files this experiment
# writes with `write_draws` — the normal `.draws.jsonl.gz` AND
# `.HALTED.jsonl.gz` (fix round 1: a halt near item 499 writes nearly a
# full rung's rows, and that file is the forensic evidence of a gate-1
# failure — it must not be committed mid-write any more than a normal
# draws file). Neither is complete the second it appears; a 10-second
# poll pair, not a fixed settle, decides when it is safe to commit.
# `.HALTED.jsonl.gz` has no `.json` sibling — its sibling is the
# `<rung>.HALTED` marker, committed together with it once stable.
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
        *.HALTED.jsonl.gz)
          marker="${f%.jsonl.gz}"
          [[ -f "$marker" ]] || continue
          sz1=$(stat -f%z "$f" 2>/dev/null || echo -1)
          sleep 10
          sz2=$(stat -f%z "$f" 2>/dev/null || echo -2)
          if [[ "$sz1" != "$sz2" ]]; then
            echo "[watcher] $f still growing ($sz1 -> $sz2), deferring"
            continue
          fi
          ;;
        *.HALTED)
          # `<rung>.HALTED` sorts BEFORE `<rung>.HALTED.jsonl.gz` (it is
          # a literal prefix of it), so on its own `find` match it would
          # reach this loop ahead of the gz and — via the default branch
          # below — commit alone before the gz's stability check ever
          # runs. The marker never lands without its gz (the runner
          # writes the gz first); defer entirely to the gz's own branch,
          # which stages and commits both together once stable. Never
          # marked `seen`, so this is a cheap no-op every pass until the
          # gz branch handles the pair (harmless — no stat/git calls).
          continue
          ;;
        *)
          sleep 2   # settle
          ;;
      esac
      git add "$f" 2>/dev/null || true
      case "$f" in
        *.draws.jsonl.gz) git add "${f%.draws.jsonl.gz}.json" \
          2>/dev/null || true ;;
        *.HALTED.jsonl.gz) git add "${f%.jsonl.gz}" \
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
