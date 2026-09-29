#!/usr/bin/env bash
# Exp 6 sweeps on the box: one runner per family, the smallest first, so a battery that is flat at
# 3 B is found at the least cost. Each runs gate 1 on THIS host first and resumes by its own rule;
# the campaign stops at the first non-zero exit (a gate that fired has written HALTED).
set -uo pipefail
echo $$ > /workspace/campaign_6.pid      # status_box_6.sh reads it (final review M-5)
cd /workspace/emergence-paper
# the projection is sealed BEFORE any intermediate checkpoint (final review M-2; the ancestor
# check stays in rebundle_box_6.sh)
[ -f experiments/exp6/projection.md ] || { echo "[sweep] REFUSING: experiments/exp6/projection.md is not in this checkout"; exit 2; }
unset HF_HUB_DISABLE_XET
for family in smollm3_3b olmo7b comma_7b olmo13b; do
  /workspace/venv/bin/python -m experiments.exp6.run.sweep_6 --family "$family" --device cuda \
    || { echo "[sweep] $family exited $?"; exit 2; }
done
echo "[sweep] complete"
