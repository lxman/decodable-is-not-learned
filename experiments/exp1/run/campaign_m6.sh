#!/bin/zsh
# M6 size sweep, two stages (process rules: confirmation gates BEFORE scored runs).
#
# Stage 1 — one-seed confirmations for every NEW (system, model-size) cell:
#   grokking 10M/100M must grok (mem->gen certification);
#   lubana above 1M/100M must transition AND hold; below 1M/100M must stay flat.
#   A PASS drops a marker in logs/m6/confirm/; a FAIL aborts the campaign (adjust
#   the recipe, never thresholds, then relaunch — markers make this resumable).
# Stage 2 — scored runs, 5 seeds per new cell, skip-if-result-exists:
#   grokking {10M,100M} x5; lubana {above,below} x {1M,100M} x5.
#   (grokking/1M and lubana/10M rows are complete from M4/M5.)
#
# Disk: a 100M lubana below seed writes ~107 GB of checkpoints (main + 4 graph-axis
# sub-runs); checkpoints of SUCCESSFUL 100M runs are deleted after the RunRecord is
# saved (regenerable from config+seed; the record is the durable artifact).
#
# Launch DETACHED (survives session restarts; see M5 lesson in experiments.md rule 7):
#   nohup zsh run/campaign_m6.sh </dev/null >/dev/null 2>&1 & disown
# Progress: tail -f logs/m6/campaign.log
set -u
cd "$(dirname "$0")/.."
source ~/emergence-lab/.venv/bin/activate
export PYTHONUNBUFFERED=1

LOGDIR=logs/m6
mkdir -p "$LOGDIR/confirm"
note() { echo "[m6] $1 $(date)" | tee -a "$LOGDIR/campaign.log"; }
note "begin git=$(/opt/homebrew/bin/git rev-parse --short HEAD)"

confirm_gate() {  # name, pass-pattern, cmd...
  local name=$1 pat=$2; shift 2
  local marker="$LOGDIR/confirm/${name}.pass"
  if [ -f "$marker" ]; then note "confirm $name already passed (marker)"; return 0; fi
  note "CONFIRM $name start"
  "$@" >> "$LOGDIR/confirm/${name}.log" 2>&1
  local rc=$?
  if [ $rc -eq 0 ] && grep -q "$pat" "$LOGDIR/confirm/${name}.log"; then
    touch "$marker"; note "CONFIRM $name PASS"
  else
    note "CONFIRM $name FAIL (rc=$rc) — see $LOGDIR/confirm/${name}.log; ABORT"
    exit 1
  fi
}

# ---- Stage 1: confirmation gates -------------------------------------------------
confirm_gate grok_10M      "grokking certified: True"      python -m run.confirm_grokking "" "" 0 10M
confirm_gate lub_above_1M  "transitioned AND held: True"   python -m run.confirm_lubana above "" 0 paper 1M
confirm_gate lub_below_1M  "BELOW stayed flat: True"       python -m run.confirm_lubana below "" 0 paper 1M
confirm_gate grok_100M     "grokking certified: True"      python -m run.confirm_grokking "" "" 0 100M
confirm_gate lub_above_100M "transitioned AND held: True"  python -m run.confirm_lubana above "" 0 paper 100M
confirm_gate lub_below_100M "BELOW stayed flat: True"      python -m run.confirm_lubana below "" 0 paper 100M
rm -rf checkpoints/grokking_confirm_100M checkpoints/lubana_confirm_above_m100M checkpoints/lubana_confirm_below_m100M
note "all confirmation gates passed"

# ---- Stage 2: scored runs ---------------------------------------------------------
scored() {  # out-json, cleanup-dirs (comma-sep, empty ok), cmd...
  local out=$1 cleanup=$2; shift 2
  local tag="${out#results/}"
  if [ -f "$out" ]; then note "skip $tag (result exists)"; return 0; fi
  note "START $tag"
  "$@" >> "$LOGDIR/$(echo "$tag" | tr '/' '_').log" 2>&1
  local rc=$?
  note "DONE  $tag rc=$rc"
  if [ $rc -ne 0 ]; then note "ABORT: $tag failed"; exit $rc; fi
  if [ -n "$cleanup" ]; then
    for d in ${(s:,:)cleanup}; do rm -rf "checkpoints/$d"; done
    note "cleaned checkpoints for $tag"
  fi
}

for seed in 0 1 2 3 4; do
  scored "results/grokking/10M/seed${seed}.json" "" \
    python -m run.run_grokking "$seed" 10M
  scored "results/lubana_above/1M/seed${seed}.json" "" \
    python -m run.run_lubana above "$seed" paper 1M
  scored "results/lubana_below/1M/seed${seed}.json" "" \
    python -m run.run_lubana below "$seed" paper 1M
done
for seed in 0 1 2 3 4; do
  scored "results/grokking/100M/seed${seed}.json" "grokking_100M/seed${seed}" \
    python -m run.run_grokking "$seed" 100M
  scored "results/lubana_above/100M/seed${seed}.json" "lubana_above_m100M/seed${seed}" \
    python -m run.run_lubana above "$seed" paper 100M
  scored "results/lubana_below/100M/seed${seed}.json" \
    "lubana_below_m100M/seed${seed},lubana_s3graph_0.25_m100M/seed${seed},lubana_s3graph_0.45_m100M/seed${seed},lubana_s3graph_0.65_m100M/seed${seed},lubana_s3graph_0.85_m100M/seed${seed}" \
    python -m run.run_lubana below "$seed" paper 100M
done
note "ALL DONE"
