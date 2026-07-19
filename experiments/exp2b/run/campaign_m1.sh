#!/bin/zsh
# Exp 2b M1 campaign: inclusion pass at the probe sizes (410m, 1b), trained +
# untrained (empirical chance floors), all capabilities. Resumable: per-(size,
# mode, capability) result JSONs are skipped if present.
#
# DO NOT start while Exp 1's M6 campaign holds the MPS device — one GPU.
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2b && nohup zsh run/campaign_m1.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f logs/m1/campaign.log

set -u
cd "$(dirname "$0")/.."
mkdir -p logs/m1
LOG=logs/m1/campaign.log
PY=~/emergence-lab/.venv/bin/python

echo "[m1] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) $(date)" >> "$LOG"

if pgrep -f 'exp2/run/campaign' > /dev/null; then
  echo "[m1] ABORT: an exp2 campaign is running — one MPS device $(date)" >> "$LOG"
  exit 1
fi

for size in 410m 1b; do
  for mode in untrained trained; do
    echo "[m1] START $size/$mode $(date)" >> "$LOG"
    if $PY -u -m run.run_inclusion "$size" "$mode" >> "$LOG" 2>&1; then
      echo "[m1] DONE $size/$mode $(date)" >> "$LOG"
    else
      echo "[m1] ABORT: $size/$mode failed (rc=$?) $(date)" >> "$LOG"
      exit 1
    fi
  done
done

echo "[m1] inclusion table (dry run) $(date)" >> "$LOG"
$PY -u -m run.fix_battery --dry-run >> "$LOG" 2>&1
echo "[m1] ALL DONE — review table, then run fix_battery and commit $(date)" >> "$LOG"
