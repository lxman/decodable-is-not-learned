#!/usr/bin/env bash
# Exp 5 stage 2 on the box: one runner process per large size, largest first (dial i);
# each resumes by its own rule; stops at the first non-zero exit.
set -uo pipefail
# Before this: the box re-bundled to the projection commit by run/rebundle_box_5.sh (final review
# I-3; the old `git fetch <bundle> 'refs/heads/*:refs/heads/*'` recipe silently stays on the old
# commit), and `sweep_5 --size 12b --dry-run` clean.
cd /workspace/emergence-paper
unset HF_HUB_DISABLE_XET        # final review M-13: the xet transport ON (4c lesson 1)
for size in 12b 6.9b 2.8b 1.4b 1b 410m 160m; do
  /workspace/venv/bin/python -m experiments.exp5.run.sweep_5 --size "$size" --device cuda || { echo "[campaign] $size exited $?"; exit 2; }
done
echo "[campaign] complete"
