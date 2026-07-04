#!/bin/zsh
# M5 scored campaign: 5 seeds x {above, below} at paper scale, sequential (one MPS).
#
# Resumable by design (power-failure lesson from the confirmation run): a run whose
# RunRecord JSON already exists is skipped, so re-invoking this script after any
# interruption picks up where it left off. Per-run stdout goes to a durable log file,
# not the session's terminal. Interleaved above/below per seed so both truth-table
# rows accumulate evidence at the same rate.
#
# Usage: zsh run/campaign_m5.sh   (from experiments/exp1, venv active or not)
set -u
cd "$(dirname "$0")/.."
source ~/emergence-lab/.venv/bin/activate

LOGDIR=logs/m5_scored
mkdir -p "$LOGDIR"
echo "[campaign] begin $(date) git=$(/opt/homebrew/bin/git rev-parse --short HEAD)" | tee -a "$LOGDIR/campaign.log"

for seed in 0 1 2 3 4; do
  for setting in above below; do
    out="results/lubana_${setting}/10M/seed${seed}.json"
    if [ -f "$out" ]; then
      echo "[campaign] skip ${setting} seed${seed} (result exists)" | tee -a "$LOGDIR/campaign.log"
      continue
    fi
    echo "[campaign] START ${setting} seed${seed} $(date)" | tee -a "$LOGDIR/campaign.log"
    python -m run.run_lubana "$setting" "$seed" paper >> "$LOGDIR/${setting}_seed${seed}.log" 2>&1
    rc=$?
    echo "[campaign] DONE  ${setting} seed${seed} rc=${rc} $(date)" | tee -a "$LOGDIR/campaign.log"
    if [ $rc -ne 0 ]; then
      echo "[campaign] ABORT: ${setting} seed${seed} failed; see $LOGDIR/${setting}_seed${seed}.log" | tee -a "$LOGDIR/campaign.log"
      exit $rc
    fi
  done
done
echo "[campaign] ALL DONE $(date)" | tee -a "$LOGDIR/campaign.log"
