#!/usr/bin/env bash
# Rented-box setup for Exp 5 (4c ruling 3's recipe): uv-managed Python 3.11, the Mac's pins,
# the repo from a git bundle (no credential on the host), the ckpt cache root. Run from /workspace
# after `emergence-paper.bundle` has been scp'd there.
set -euo pipefail
cd /workspace
curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"
uv python install 3.11
uv venv --python 3.11 /workspace/venv
/workspace/venv/bin/python -m pip install --quiet --upgrade pip
/workspace/venv/bin/python -m pip install --quiet "torch==2.12.1" --index-url https://download.pytorch.org/whl/cu130
/workspace/venv/bin/python -m pip install --quiet "transformers==5.13.0" "numpy==2.4.6" "safetensors==0.8.0" \
  "huggingface_hub[hf_xet]==1.22.0" "tokenizers==0.22.2" "scipy==1.17.1"
git clone /workspace/emergence-paper.bundle /workspace/emergence-paper
cd /workspace/emergence-paper && git checkout master && git tag --list 'exp5-*'
mkdir -p ~/emergence-lab/ckpt_cache_5
/workspace/venv/bin/python - <<'PY'
import torch, transformers, numpy, safetensors, tokenizers, huggingface_hub, scipy
print("torch", torch.__version__, "cuda", torch.version.cuda, torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-")
print("transformers", transformers.__version__, "numpy", numpy.__version__, "safetensors", safetensors.__version__,
      "tokenizers", tokenizers.__version__, "hub", huggingface_hub.__version__, "scipy", scipy.__version__)
import hf_xet; print("hf_xet present")
PY
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader; df -h /workspace | tail -1
