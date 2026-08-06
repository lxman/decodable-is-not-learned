#!/bin/zsh
# Exp 2c M1 campaign: inclusion pass at the probe sizes (410m, 1b),
# trained + untrained (empirical chance floors), new-pool rungs +
# ctrl_copy. Resumable: per-(size, mode, capability) result JSONs are
# skipped if present. 2b's campaign_m1.sh pattern verbatim.
#
# One MPS device: refuses to start while another exp2* campaign or a
# 2c screen/collection holds it.
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2c && nohup zsh run/campaign_m1.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f logs/m1/campaign.log

set -u
cd "$(dirname "$0")/.."
mkdir -p logs/m1
LOG=logs/m1/campaign.log
PY=~/emergence-lab/.venv/bin/python

echo "[m1] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) $(date)" >> "$LOG"

if pgrep -f 'exp2b?/run/campaign|run\.screen|collect_activations' > /dev/null; then
  echo "[m1] ABORT: another MPS campaign is running $(date)" >> "$LOG"
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

echo "[m1] ALL DONE — transcribe + adjudicate against gate bars, then commit $(date)" >> "$LOG"
