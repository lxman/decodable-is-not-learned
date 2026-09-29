#!/usr/bin/env bash
# Exp 6 endpoint stage on the box: the four families' stage-1 endpoints and init referents, the
# smallest family first; gate 1(b) is written at the end of each invocation. Stops at the first
# non-zero exit. Resumable: a load whose records are complete is skipped.
set -uo pipefail
echo $$ > /workspace/campaign_6.pid      # status_box_6.sh reads it (final review M-5)
cd /workspace/emergence-paper
unset HF_HUB_DISABLE_XET        # the xet transport ON (4c's lesson: the classic path throttles)
for family in smollm3_3b olmo7b comma_7b olmo13b; do
  /workspace/venv/bin/python -m experiments.exp6.run.endpoint_6 --family "$family" --device cuda \
    || { echo "[endpoint] $family exited $?"; exit 2; }
done
/workspace/venv/bin/python -m experiments.exp6.run.endpoint_6 --device cuda \
  || { echo "[endpoint] the closing gate exited $?"; exit 2; }
echo "[endpoint] complete"
