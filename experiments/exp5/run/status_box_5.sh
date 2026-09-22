#!/usr/bin/env bash
# One status line every 5 min from the rented box (Exp 5): UTC, campaign process alive?, units
# complete (_unit.json count), GPU memory, last runner log line. Appends to
# experiments/exp5/status_5.log (gitignored — machine-local). Loops until killed.
set -uo pipefail
cd /Users/michaeljordan/emergence-paper
while true; do
  line=$(ssh -i ~/.ssh/vastai_ed25519 -o BatchMode=yes -o ConnectTimeout=30 -p ${VAST_PORT:-36148} root@${VAST_HOST:-ssh5.vast.ai} \
    'printf "%s alive=%s units=%s gpu=%s last=[%s]\n" "$(date -u +%m-%dT%H:%M)" "$(ps -p $(cat /workspace/campaign_5.pid 2>/dev/null) -o pid= >/dev/null 2>&1 && echo y || echo N)" "$(find /workspace/emergence-paper/experiments/exp5/results -name _unit.json 2>/dev/null | wc -l)" "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null)" "$(tr "\r" "\n" < /workspace/campaign_5.log 2>/dev/null | grep -E "\[5 sweep\]|\[5 finals\]|Traceback|HALTED" | tail -1 | cut -c1-90)"' 2>/dev/null | grep -v -E "Welcome|Have fun")
  echo "${line:-$(date -u +%m-%dT%H:%M) SSH-FAILED}" >> experiments/exp5/status_5.log
  sleep 300
done
