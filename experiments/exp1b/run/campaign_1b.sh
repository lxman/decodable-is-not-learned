#!/bin/zsh
# Exp 1b campaign: thirty trained cells + thirty untrained twins, in four
# blocks. Resumable at every level — the Python driver derives its worklist
# from records on disk (skip-if-exists), so re-running this script after any
# interruption picks up exactly where it stopped.
#
# Block order is the cheap tier first, untrained last:
#   trained/1M -> trained/10M -> untrained/1M -> untrained/10M
# A broken recipe therefore surfaces in minutes, not after a day of training.
# Any non-zero exit aborts the whole campaign rather than pressing on.
#
# NOTE this script cds to the REPO ROOT, not to experiments/exp1b as exp2c's
# campaign does. exp1b's modules import absolutely from the repo root
# (`experiments.exp1b.*`), so the module path is fully qualified.
#
# NOTE the untrained blocks re-run the thirty cells already measured pre-freeze
# into `results/` (design open item 5). The pre-freeze copies live in
# `diagnostics/pre_freeze_untrained/` and are deliberately not reused: they
# predate the freeze, and `present` is a derived field whose meaning the
# floor-corrected S1 has since changed. ~1 h 46 min.
#
# Launch DETACHED (survives session restarts; M5 lesson, experiments.md rule 7):
#   nohup zsh ~/emergence-paper/experiments/exp1b/run/campaign_1b.sh \
#     </dev/null >/dev/null 2>&1 & disown
# Watch: tail -f ~/emergence-paper/experiments/exp1b/logs/1b/campaign.log
#
# PAUSE procedure. Bracket the regex so the pattern does not match the shell
# running it (a plain `pkill -f campaign_1b.sh` kills your own SSH shell), and
# kill the runner before its workers — spawned children escape name-based
# pkill, which is the exp2 lesson:
#   1) pkill -f '[c]ampaign_1b.sh'
#   2) pgrep -f '[c]ampaign_1b'        -> runner PID
#   3) pgrep -P <runner-pid>           -> worker PIDs
#   4) kill <runner-pid>, THEN the workers, by PID, in separate calls
#   5) verify: ps aux | awk '$3>50'

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"          # experiments/exp1b/run
EXP1B="$(dirname "$HERE")"                     # experiments/exp1b
ROOT="$(dirname "$(dirname "$EXP1B")")"        # repo root
cd "$ROOT"

LOGDIR="$EXP1B/logs/1b"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/campaign.log"
PY=~/emergence-lab/.venv/bin/python
MOD=experiments.exp1b.run.campaign_1b

echo "[1b] begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD) $(date)" >> "$LOG"

block() {  # kind size
  local kind=$1 size=$2
  echo "[1b] START $kind/$size $(date)" >> "$LOG"
  $PY -u -m $MOD --only "$kind" --size "$size" >> "$LOG" 2>&1
  local rc=$?
  if [ $rc -eq 0 ]; then
    echo "[1b] DONE  $kind/$size $(date)" >> "$LOG"
  else
    echo "[1b] ABORT $kind/$size (rc=$rc) $(date)" >> "$LOG"
    exit $rc
  fi
}

for kind in trained untrained; do
  for size in 1M 10M; do
    block "$kind" "$size"
  done
done

echo "[1b] ALL DONE — analysis, close-out and the exp1b-closed tag are manual $(date)" >> "$LOG"
