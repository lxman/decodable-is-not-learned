#!/usr/bin/env bash
# Exp 5b stage 2 on the box: one runner process per small size, largest first (dial n);
# each resumes by its own rule; stops at the first non-zero exit.
set -uo pipefail
# Before this: the box re-bundled to the projection commit by run/rebundle_box_5b.sh, and
# `units_5b --size 6.9b --dry-run` clean.
cd /workspace/emergence-paper
unset HF_HUB_DISABLE_XET        # final review M-13 (exp5): the xet transport ON (4c lesson 1)
for size in 6.9b 2.8b 1.4b 1b 410m 160m; do
  /workspace/venv/bin/python -m experiments.exp5b.run.units_5b --size "$size" --device cuda || { echo "[campaign] $size exited $?"; exit 2; }
done
echo "[campaign] complete"
