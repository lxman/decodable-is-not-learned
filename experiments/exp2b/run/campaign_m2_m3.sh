#!/bin/zsh
# Exp 2b M2 gates + M3 Stage 1: activation collection (GPU, fast), then the
# starved-probe program (CPU, LONG — days on the Mac alone; distributed
# workers join by syncing results/probes/, idempotent skip-if-exists), then
# the calibrated gate report. Resumable at every level.
#
# Stage order interleaves sizes so the 410m stages (2x faster per unit)
# front-load gate-relevant results.
#
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2b && nohup zsh run/campaign_m2_m3.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f logs/m2m3/campaign.log
#
# PAUSE procedure (the exp2 lesson — spawn workers escape name-based pkill):
#   1) pkill -f campaign_m2_m3.sh; pgrep -f run_probes_2b -> runner PID
#   2) pgrep -P <runner-pid> -> worker PIDs; kill runner THEN workers by PID
#   3) verify: ps aux | awk '$3>50'

set -u
cd "$(dirname "$0")/.."
mkdir -p logs/m2m3
LOG=logs/m2m3/campaign.log
PY=~/emergence-lab/.venv/bin/python

echo "[m2m3] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) $(date)" >> "$LOG"

for size in 410m 1b; do
  for mode in untrained trained; do
    echo "[m2m3] COLLECT START $size/$mode $(date)" >> "$LOG"
    if $PY -u -m run.collect_activations "$size" "$mode" >> "$LOG" 2>&1; then
      echo "[m2m3] COLLECT DONE $size/$mode $(date)" >> "$LOG"
    else
      echo "[m2m3] ABORT: collection $size/$mode failed (rc=$?) $(date)" >> "$LOG"
      exit 1
    fi
  done
done

for size in 410m 1b; do
  for stage in known_absent shuffled known_present m3; do
    echo "[m2m3] PROBES START $stage/$size $(date)" >> "$LOG"
    if $PY -u -m run.run_probes_2b "$stage" "$size" >> "$LOG" 2>&1; then
      echo "[m2m3] PROBES DONE $stage/$size $(date)" >> "$LOG"
    else
      echo "[m2m3] ABORT: probes $stage/$size failed (rc=$?) $(date)" >> "$LOG"
      exit 1
    fi
  done
done

echo "[m2m3] M2 REPORT $(date)" >> "$LOG"
if $PY -u -m run.m2_report_2b >> "$LOG" 2>&1; then
  echo "[m2m3] M2 GATES CLEAN $(date)" >> "$LOG"
else
  echo "[m2m3] M2 GATE ATTENTION REQUIRED $(date)" >> "$LOG"
  exit 1
fi

echo "[m2m3] ALL DONE — review report; Stage 1 assembly + commit + TAG is manual $(date)" >> "$LOG"
