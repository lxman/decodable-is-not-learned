#!/bin/zsh
# Exp 2c M2: trained-side campaign — collection (MPS, fast), then the
# starved-probe stages (CPU, LONG — days on the Mac alone), then the
# calibrated gate report. Resumable at every level (skip-if-exists).
#
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2c && nohup zsh run/campaign_m2.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f logs/m2/campaign.log
#
# PAUSE procedure (the exp2 lesson — spawn workers escape name-based pkill):
#   1) pkill -f campaign_m2.sh; pgrep -f "run.campaign_m2" -> runner PID
#   2) pgrep -P <runner-pid> -> worker PIDs; kill runner THEN workers by PID
#   3) verify: ps aux | awk '$3>50'

set -u
cd "$(dirname "$0")/.."
mkdir -p logs/m2
LOG=logs/m2/campaign.log
PY=~/emergence-lab/.venv/bin/python

echo "[m2] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) $(date)" >> "$LOG"

for size in 410m 1b; do
  echo "[m2] COLLECT START $size/trained $(date)" >> "$LOG"
  if $PY -u -m run.campaign_m2 collect "$size" >> "$LOG" 2>&1; then
    echo "[m2] COLLECT DONE $size/trained $(date)" >> "$LOG"
  else
    echo "[m2] ABORT: collection $size failed (rc=$?) $(date)" >> "$LOG"
    exit 1
  fi
done

# 410m stages first (2x faster per unit): gate-relevant results front-load.
for size in 410m 1b; do
  for stage in shuffled known_present m3; do
    echo "[m2] PROBES START $stage/$size $(date)" >> "$LOG"
    if $PY -u -m run.campaign_m2 probes "$stage" "$size" >> "$LOG" 2>&1; then
      echo "[m2] PROBES DONE $stage/$size $(date)" >> "$LOG"
    else
      echo "[m2] ABORT: probes $stage/$size failed (rc=$?) $(date)" >> "$LOG"
      exit 1
    fi
  done
done

echo "[m2] GATE REPORT $(date)" >> "$LOG"
if $PY -u -m run.m2_report >> "$LOG" 2>&1; then
  echo "[m2] GATES CLEAN $(date)" >> "$LOG"
else
  echo "[m2] GATE ATTENTION REQUIRED $(date)" >> "$LOG"
  exit 1
fi

echo "[m2] ALL DONE — review report; M3 Stage 1 assembly + commit + TAG is manual $(date)" >> "$LOG"
