#!/bin/zsh
# Exp 2c M4: the eval campaign — argmax on the LOCKED side (2.8b/6.9b/
# 12b), trained and untrained, over all 34 scored rungs. This is the
# scale-ascent outcome (design §3). 204 cells, one durable JSON each,
# resumable (skip-if-exists).
#
# The runner refuses to start unless the Stage 1 tag exists; that check
# lives in run/campaign_m4.py, not here, so it cannot be bypassed by
# invoking python directly.
#
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2c && nohup zsh run/campaign_m4.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f logs/m4/campaign.log
# Dry run the plan: python -m run.campaign_m4 --plan
#
# PAUSE procedure (the exp2 lesson — name-based pkill catches its own shell):
#   1) pkill -f campaign_m4.sh; pgrep -f "run.campaign_m4" -> runner PID
#   2) kill that PID; a partially written cell is simply absent and reruns
#   3) verify: ps aux | awk '$3>50'
#
# ORDER: sizes ascend, and within a size the UNTRAINED arm runs first.
# The untrained floor is cheap (random init, no download, same shapes)
# and it is what every trained number is normalized against — a size
# whose floor is missing yields no ascent score, so the floor is never
# left as the thing still running when the box is needed back.
#
# 12b is the long pole. Loading it costs ~24GB at fp16 against 48GB of
# unified memory, so it runs LAST and ALONE — do not start another
# heavy job against this box while the 12b rows are open.

set -u
cd "$(dirname "$0")/.."
mkdir -p logs/m4
LOG=logs/m4/campaign.log
PY=~/emergence-lab/.venv/bin/python

echo "[m4] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) tag=$(/opt/homebrew/bin/git describe --tags --abbrev=0 2>/dev/null) $(date)" >> "$LOG"

for size in 2.8b 6.9b 12b; do
  for mode in untrained trained; do
    echo "[m4] START $size/$mode $(date)" >> "$LOG"
    if $PY -u -m run.campaign_m4 "$size" "$mode" >> "$LOG" 2>&1; then
      echo "[m4] DONE $size/$mode $(date)" >> "$LOG"
    else
      echo "[m4] ABORT: $size/$mode failed (rc=$?) $(date)" >> "$LOG"
      exit 1
    fi
  done
done

echo "[m4] ALL DONE — 204 cells; M5 frozen analysis is next, and the" >> "$LOG"
echo "[m4] verdict projection goes in the ledger BEFORE the report runs $(date)" >> "$LOG"
