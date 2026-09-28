#!/usr/bin/env bash
# One status line every 5 min from the rented box (Exp 6): UTC, campaign process alive?, model
# loads complete, GPU memory, last runner log line. Appends to experiments/exp6/status_6.log
# (gitignored — machine-local). Loops until killed.
set -uo pipefail
cd /Users/michaeljordan/emergence-paper
while true; do
  line=$(ssh -i ~/.ssh/vastai_ed25519 -o BatchMode=yes -o ConnectTimeout=30 -p ${VAST_PORT:?} root@${VAST_HOST:?} \
    'printf "%s alive=%s loads=%s gpu=%s last=[%s]\n" "$(date -u +%m-%dT%H:%M)" "$(ps -p $(cat /workspace/campaign_6.pid 2>/dev/null) -o pid= >/dev/null 2>&1 && echo y || echo N)" "$(find /workspace/emergence-paper/experiments/exp6/results \( -name _checkpoint.json -o -name "_stage1_final.json" -o -name "_init.json" \) 2>/dev/null | wc -l)" "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null)" "$(tr "\r" "\n" < /workspace/campaign_6.log 2>/dev/null | grep -E "\[endpoint\]|\[sweep\]|Traceback|FIRED|HALTED" | tail -1 | cut -c1-90)"' 2>/dev/null | grep -v -E "Welcome|Have fun")
  echo "${line:-$(date -u +%m-%dT%H:%M) SSH-FAILED}" >> experiments/exp6/status_6.log
  sleep 300
done
