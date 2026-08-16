#!/bin/zsh
# Exp 3 per-cell committer (§10.3 "commit per cell, push per cell";
# launch authorization + per-cell push reconfirmed by Michael
# 2026-08-16, ledgered). OPERATIONAL ONLY: this script moves files
# into git as they land; it never reads, writes, or interprets a
# number. Post-freeze addition of driver-class tooling — decides what
# gets committed and when, never what anything means.
#
# Mechanism: every 5 minutes, stage result files whose mtime is >2
# minutes old (the warm-file guard: a cell record is a single
# write_text, so anything older than the guard is complete), commit,
# push. Exits after the campaign log prints its terminal line and a
# final full sweep finds nothing new. A re-run cell that REWRITES a
# tracked file is also staged (git add path covers modified files);
# the final sweep is belt-and-braces.

cd "${0:A:h}/../../.."   # repo root
LOG=experiments/exp3/logs/campaign.log
GIT=/opt/homebrew/bin/git

while true; do
  find experiments/exp3/results -type f -mmin +2 -print0 2>/dev/null \
    | xargs -0 -r $GIT add --
  if ! $GIT diff --cached --quiet; then
    n=$($GIT diff --cached --name-only | wc -l | tr -d ' ')
    names=$($GIT diff --cached --name-only | sed 's|experiments/exp3/results/||' | head -24)
    $GIT commit -q -m "exp3 campaign: +${n} result file(s) [watcher]" -m "$names"
    $GIT push -q origin master 2>/dev/null
    echo "[watcher] committed ${n} file(s) $(date '+%F %T')"
  fi
  if grep -qE "^\[3\] (complete|STOPPED)" "$LOG" 2>/dev/null; then
    $GIT add -A experiments/exp3/results 2>/dev/null
    if ! $GIT diff --cached --quiet; then
      $GIT commit -q -m "exp3 campaign: final sweep [watcher]"
      $GIT push -q origin master 2>/dev/null
      echo "[watcher] final sweep committed $(date '+%F %T')"
    fi
    echo "[watcher] campaign terminal line seen; exiting $(date '+%F %T')"
    exit 0
  fi
  sleep 300
done
