#!/bin/zsh
# Exp 2 M2 gates + M3 Stage 1: activation collection (GPU), then probe fitting
# (CPU-heavy: 1000-permutation nulls x 2 positions x all layers), then gate
# adjudication and Stage 1 assembly. Resumable at every level (per-(size,mode,
# cap) npz; per-(stage,size,cap,seed) probe JSONs).
#
# STOPS after the m2 report if attrition or a gate failure needs human review:
# Stage 1 only assembles when gates are clean AND any attrition has been
# reviewed/re-committed (m3_stage1.py enforces the ordering itself).
#
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2 && nohup zsh run/campaign_m2_m3.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f logs/m2m3/campaign.log

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
  for stage in m2_untrained m2_shuffled m2_controls m3; do
    echo "[m2m3] PROBES START $stage/$size $(date)" >> "$LOG"
    if $PY -u -m run.run_probes "$stage" "$size" >> "$LOG" 2>&1; then
      echo "[m2m3] PROBES DONE $stage/$size $(date)" >> "$LOG"
    else
      echo "[m2m3] ABORT: probes $stage/$size failed (rc=$?) $(date)" >> "$LOG"
      exit 1
    fi
  done
done

echo "[m2m3] M2 REPORT $(date)" >> "$LOG"
if $PY -u -m run.m2_report >> "$LOG" 2>&1; then
  echo "[m2m3] M2 GATES CLEAN $(date)" >> "$LOG"
else
  echo "[m2m3] M2 GATE ATTENTION REQUIRED (see report above) $(date)" >> "$LOG"
  exit 1
fi

echo "[m2m3] ALL DONE — review m2 report; if clean and no attrition, run m3_stage1, commit + tag $(date)" >> "$LOG"
