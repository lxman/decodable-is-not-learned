#!/bin/sh
# Tier-2 fleet worker (growth battery, staged 2026-08-02): runs the full
# frozen-instrument config (5 seeds x both sizes x 2500 perms) for each
# candidate given as an argument, sequentially. The same script runs on
# the Mac (venv ~/emergence-lab/.venv) and on llmbox (~/emergence-lab-venv);
# pass the python via $TIER2_PYTHON or default per-box below.
#
# Usage:  ./run/tier2_worker.sh <candidate> [<candidate> ...]
# From:   experiments/exp2c
#
# Tier-2 REQUIRES the candidate's untrained-activation npz files to be
# present under results/activations/{410m,1b}_untrained/ (collected at
# tier-1 on the Mac; ship to llmbox by scp, never re-collect off-Mac --
# the two-stage lock and MPS-collection provenance both live on the Mac).
set -eu
PY="${TIER2_PYTHON:-}"
if [ -z "$PY" ]; then
    if [ -x "$HOME/emergence-lab/.venv/bin/python" ]; then
        PY="$HOME/emergence-lab/.venv/bin/python"          # Mac canonical
    else
        PY="$HOME/emergence-lab-venv/bin/python"            # llmbox pinned
    fi
fi
for name in "$@"; do
    for size in 410m 1b; do
        f="results/activations/${size}_untrained/${name}.npz"
        [ -f "$f" ] || { echo "MISSING $f -- ship it first" >&2; exit 1; }
    done
    echo "[tier2-worker] $(hostname) starting $name at $(date -u +%FT%TZ)"
    "$PY" -m run.screen "$name" --tier 2
done
echo "[tier2-worker] $(hostname) done: $* at $(date -u +%FT%TZ)"
