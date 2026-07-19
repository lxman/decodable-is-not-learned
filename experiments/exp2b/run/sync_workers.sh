#!/bin/zsh
# Mac-side worker sync loop (two-way): push newly collected activations and
# the merged result set out to each worker; pull each worker's results back.
# fit_one's execution-time existence check turns synced results into skips on
# every box, so queue collisions cost at most one duplicated unit.
# llmbox: rsync. devbox: scp (Windows, no rsync; JSONs are small enough that
# full re-copies per cycle are fine). Log: logs/m2m3/sync.log
#
# Launch detached:
#   cd ~/emergence-paper/experiments/exp2b && nohup zsh run/sync_workers.sh \
#     </dev/null >/dev/null 2>&1 & disown

set -u
cd "$(dirname "$0")/.."
LOG=logs/m2m3/sync.log
LLMBOX="<user>@<llmbox-lan-ip>"
DEVBOX="<user>@<devbox-lan-ip>"
LLMBOX_DIR="exp2b-worker/experiments/exp2b/results"
DEVBOX_DIR="exp2b-worker/experiments/exp2b/results"

echo "[sync] loop start $(date)" >> "$LOG"
while true; do
  # llmbox: activations out, results both ways
  rsync -a results/activations/ "$LLMBOX:$LLMBOX_DIR/activations/" >> "$LOG" 2>&1
  rsync -a "$LLMBOX:$LLMBOX_DIR/probes/" results/probes/ >> "$LOG" 2>&1
  rsync -a results/probes/ "$LLMBOX:$LLMBOX_DIR/probes/" >> "$LOG" 2>&1
  # devbox: results both ways (activations pushed one-shot at collection time)
  scp -q -r "$DEVBOX:$DEVBOX_DIR/probes" results/ 2>> "$LOG" || true
  scp -q -r results/probes "$DEVBOX:$DEVBOX_DIR/" 2>> "$LOG" || true
  echo "[sync] cycle $(date): $(find results/probes -name '*.json' 2>/dev/null | wc -l | tr -d ' ') results local" >> "$LOG"
  sleep 240
done
