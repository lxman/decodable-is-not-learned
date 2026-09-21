#!/usr/bin/env bash
# One status line every 5 min from the rented box (exp4c 13B): UTC, process alive?, units with _load.json,
# rung files so far, GPU memory, last runner line. Appends to experiments/exp4c/status_13b.log. Loops until killed.
set -uo pipefail
cd /Users/michaeljordan/emergence-paper
while true; do
  line=$(ssh -i ~/.ssh/vastai_ed25519 -o BatchMode=yes -o ConnectTimeout=30 -p ${VAST_PORT:-36148} root@${VAST_HOST:-ssh5.vast.ai} \
    'printf "%s alive=%s units=%s sets=%s gpu=%s last=[%s]\n" "$(date -u +%m-%dT%H:%M)" "$(ps -p 1293 -o pid= >/dev/null 2>&1 && echo y || echo N)" "$(find /workspace/emergence-paper/experiments/exp4c/results -name _load.json -path "*olmo2_13b*" 2>/dev/null | wc -l)" "$(find /workspace/emergence-paper/experiments/exp4c/results -name "*.npz" -path "*olmo2_13b*sets*" 2>/dev/null | wc -l)" "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null)" "$(tr "\r" "\n" < /workspace/sweep_olmo2_13b.log | grep -E "\[4c sweep\]|Traceback|HALTED" | tail -1 | cut -c1-90)"' 2>/dev/null | grep -v -E "Welcome|Have fun")
  echo "${line:-$(date -u +%m-%dT%H:%M) SSH-FAILED}" >> experiments/exp4c/status_13b.log
  sleep 300
done
