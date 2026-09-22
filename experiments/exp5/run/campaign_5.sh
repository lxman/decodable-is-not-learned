#!/usr/bin/env bash
# Exp 5 stage 2 on the box: one runner process per large size, largest first (dial i);
# each resumes by its own rule; stops at the first non-zero exit.
set -uo pipefail
cd /workspace/emergence-paper
for size in 12b 6.9b 2.8b 1.4b 1b 410m 160m; do
  /workspace/venv/bin/python -m experiments.exp5.run.sweep_5 --size "$size" --device cuda || { echo "[campaign] $size exited $?"; exit 2; }
done
echo "[campaign] complete"
