#!/usr/bin/env bash
# Rented-box setup for Exp 6 (Experiment 5's recipe): uv-managed Python 3.11, the Mac's pins, the
# repo from a git bundle (no credential on the host), the checkpoint cache root. Run from
# /workspace after `exp6.bundle` has been scp'd there (made on the Mac by run/make_bundle_6.sh).
# Before ANY of this: the thermal screen (experiments/exp5/run/thermal_screen_5.py) on the bare
# instance — a throttled host is destroyed, not installed on (Experiment 5's German box).
set -euo pipefail
cd /workspace
# Disk (ratified O-1): request 250 GB; require 230 GB free on BOTH filesystems.
# Retained endpoints ~104 GB + retained 13 B step 0 ~55 GB + one checkpoint/candidate
# ~55 GB + software. The candidate and the next checkpoint are never resident together.
# Both caches live under HOME. GB means decimal 10^9 bytes, as on the provider;
# df -Pk reports 1024-byte blocks, NOT GB. Shared filesystems are checked, not summed.
for disk_path in "$HOME" /workspace; do
  free_kb=$(df -Pk "$disk_path" | awk 'NR==2 {print $4}')
  free_gb=$(( free_kb * 1024 / 1000000000 ))
  echo "[setup] $disk_path free: ${free_gb} GB (need 230 GB; request 250 GB)"
  if [ "$free_gb" -lt 230 ] && [ "${EXP6_DISK_OK:-0}" != "1" ]; then
    echo "[setup] REFUSING: ${free_gb} GB free on $disk_path, below 230 GB (set EXP6_DISK_OK=1 to proceed)"; exit 2
  fi
done
curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"
uv python install 3.11
uv venv --seed --python 3.11 /workspace/venv       # --seed: a uv venv has no pip without it
/workspace/venv/bin/python -m pip install --quiet --upgrade pip
/workspace/venv/bin/python -m pip install --quiet "torch==2.12.1" --index-url https://download.pytorch.org/whl/cu130
/workspace/venv/bin/python -m pip install --quiet "transformers==5.13.0" "numpy==2.4.6" "safetensors==0.8.0" \
  "huggingface_hub[hf_xet]==1.22.0" "tokenizers==0.22.2" "scipy==1.17.1"
git clone /workspace/exp6.bundle /workspace/emergence-paper
cd /workspace/emergence-paper && git checkout master && git tag --list 'exp6-*'
mkdir -p ~/emergence-lab/ckpt_cache_6
/workspace/venv/bin/python - <<'PY'
import torch, transformers, numpy, safetensors, tokenizers, huggingface_hub, scipy
print("torch", torch.__version__, "cuda", torch.version.cuda, torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-")
print("transformers", transformers.__version__, "numpy", numpy.__version__, "safetensors", safetensors.__version__,
      "tokenizers", tokenizers.__version__, "hub", huggingface_hub.__version__, "scipy", scipy.__version__)
import hf_xet; print("hf_xet present")
PY
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader; df -h /workspace | tail -1
