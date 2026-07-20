#!/bin/zsh
# Interim runner (2026-07-20 shuffled-gate crash window): true-label stages
# only, in gate-priority order, while the shuffled-stage fix awaits Michael's
# ruling (see PROGRESS.md). Same frozen runner and unit layout as the
# campaign; skip-if-exists means the relaunched campaign skips all of this.
# NO shuffled units run before the fix is ruled on.
#
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2b && nohup zsh run/interim_true_label.sh \
#     </dev/null >/dev/null 2>&1 & disown

set -u
cd "$(dirname "$0")/.."
mkdir -p logs/m2m3
LOG=logs/m2m3/interim.log
PY=~/emergence-lab/.venv/bin/python

echo "[interim] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) $(date)" >> "$LOG"

for combo in known_present:410m known_present:1b known_absent:1b m3:410m; do
  stage=${combo%%:*}; size=${combo##*:}
  echo "[interim] PROBES START $stage/$size $(date)" >> "$LOG"
  if $PY -u -m run.run_probes_2b "$stage" "$size" >> "$LOG" 2>&1; then
    echo "[interim] PROBES DONE $stage/$size $(date)" >> "$LOG"
  else
    echo "[interim] ABORT: probes $stage/$size failed (rc=$?) $(date)" >> "$LOG"
    exit 1
  fi
done

echo "[interim] ALL DONE $(date)" >> "$LOG"
