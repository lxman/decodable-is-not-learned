#!/usr/bin/env bash
# Exp 6 sweeps on the box: one runner per family, the smallest first, so a battery that is flat at
# 3 B is found at the least cost. Each runs gate 1 on THIS host first and resumes by its own rule;
# the campaign stops at the first non-zero exit (a gate that fired has written HALTED).
set -uo pipefail
cd /workspace/emergence-paper
unset HF_HUB_DISABLE_XET
for family in smollm3_3b olmo7b comma_7b olmo13b; do
  /workspace/venv/bin/python -m experiments.exp6.run.sweep_6 --family "$family" --device cuda \
    || { echo "[sweep] $family exited $?"; exit 2; }
done
echo "[sweep] complete"
