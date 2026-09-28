# experiments/exp6/run/_common_6.py
"""What every Exp 6 runner shares: the stack, the host record, the
finiteness probe, the gates every runner passes before a model loads."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import pins_6 as p6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402

STACK_KEYS_6 = ("torch", "transformers", "numpy", "safetensors", "tokenizers",
                "huggingface_hub")
# Exp 5's frozen stack pin (`battery_5.STACK_PIN_5`), as literals: that
# module imports torch at its top and the analyzer, which checks every
# host record, loads none. A test holds the two equal.
STACK_PIN_6 = {"torch": "2.12.1", "transformers": "5.13.0", "numpy": "2.4.6",
               "safetensors": "0.8.0", "tokenizers": "0.22.2",
               "huggingface_hub": "1.22.0"}
PYTHON_PIN_6 = "3.11"
# the fields that IDENTIFY a host; transports and the clock are recorded
# beside them and do not enter the key
HOST_KEY_FIELDS = ("stack", "device", "cuda", "gpu", "python", "platform",
                   "nvidia_smi", "node")


def stack() -> dict:
    out = {}
    for name in STACK_KEYS_6:
        try:
            out[name] = __import__(name).__version__
        except Exception:  # noqa: BLE001
            out[name] = None
    return out


def short_stack() -> dict:
    s = stack()
    return {"torch": s["torch"], "transformers": s["transformers"]}


def host_key(rec: dict) -> str:
    core = {k: rec.get(k) for k in HOST_KEY_FIELDS}
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()


def host_record(device: str, *, stack_=None, gpu=None, cuda=None, node=None,
                nvidia_smi=None, python=None, platform_=None) -> dict:
    """The host this process runs on. Every argument is an injection
    for tests; a runner passes `device` alone."""
    if gpu is None or cuda is None:
        try:
            import torch
            cuda = torch.version.cuda if cuda is None else cuda
            if gpu is None:
                gpu = (torch.cuda.get_device_name(0)
                       if device.startswith("cuda") and torch.cuda.is_available()
                       else ("Apple MPS" if device == "mps" else "unknown"))
        except Exception:  # noqa: BLE001
            gpu = gpu or "unknown"
    if nvidia_smi is None:
        try:
            nvidia_smi = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                 "--format=csv,noheader"], capture_output=True, text=True,
                timeout=20).stdout.strip()
        except Exception:  # noqa: BLE001
            nvidia_smi = ""
    rec = {"stack": stack_ if stack_ is not None else stack(), "device": device,
           "cuda": cuda, "gpu": gpu,
           "python": python if python is not None else platform.python_version(),
           "platform": platform_ if platform_ is not None else platform.platform(),
           "nvidia_smi": nvidia_smi,
           "node": node if node is not None else platform.node(),
           "hf_hub_disable_xet": os.environ.get("HF_HUB_DISABLE_XET")}
    rec["sha256"] = host_key(rec)
    rec["written_utc"] = datetime.now(timezone.utc).isoformat()
    return rec


def hosts_dir(root) -> Path:
    return r6.results(root) / "hosts"


def ensure_host(root, device: str, **inject) -> dict:
    """This host's record, written once under results/hosts/<sha12>.json
    and re-read on every later call from the same host."""
    rec = host_record(device, **inject)
    p = hosts_dir(root) / f"{rec['sha256'][:12]}.json"
    if p.exists():
        old = r6.read_json(p)
        if host_key(old) != rec["sha256"]:
            raise RuntimeError(f"{p} does not hash to its own name")
        return old
    r6.write_json(p, rec)
    return rec


def stack_pin_failures(rec: dict) -> list:
    """Exp 5's rule: each pinned package at its pinned version (a local
    build suffix after `+` is not part of the version), Python 3.11."""
    bad = []
    stack = rec.get("stack") or {}
    for k, want in STACK_PIN_6.items():
        got = str(stack.get(k) or "").split("+")[0]
        if got != want:
            bad.append(f"host record: {k} {stack.get(k)!r} is not the pinned "
                       f"{want!r}")
    py = str(rec.get("python") or "")
    if py.split(".")[:2] != PYTHON_PIN_6.split("."):
        bad.append(f"host record: python {py!r} is not {PYTHON_PIN_6}.x")
    return bad


def host_failures(rec: dict) -> list:
    """The stack pin and the record's own consistency."""
    bad = stack_pin_failures(rec)
    for k in ("device", "gpu", "python", "node"):
        if not rec.get(k):
            bad.append(f"host record: {k} missing")
    if rec.get("sha256") != host_key(rec):
        bad.append("host record: sha256 is not the key of its own fields")
    return bad


def n_nonfinite(model, tok, prompts, *, n: int = 8) -> int:
    """Non-finite logits at the last position of the first `n` prompts:
    finiteness MEASURED, never attested (Exp 5 slip 9)."""
    import torch
    enc = tok(list(prompts[:n]), return_tensors="pt", padding=True).to(model.device)
    with torch.no_grad():
        logits = model(**enc).logits[:, -1].float()
    return int((~torch.isfinite(logits)).sum().item())


class GateFired(RuntimeError):
    """A gate fired inside a runner, before the model was handed a
    prompt. `load` is what the loader measured: the evidence."""

    def __init__(self, gate: str, failures: list, load=None):
        self.gate, self.failures, self.load = gate, list(failures), load
        super().__init__(f"GATE {gate} FIRED: {self.failures[:3]}")


def require_the_macs_weights(info: dict, family, key, entry, *, label) -> None:
    """Gate 1(d) at the runner: the digest the loader MEASURED against
    the Mac's committed one, before a runner is built or a prompt is
    rendered for the model."""
    from experiments.exp6 import referents_6 as rf
    seen = {"family": family, "key": key, "digest": info.get("tensor_digest"),
            "commit": entry.get("commit"), "revision": entry.get("revision")}
    bad = rf.digest_failures(seen, family, key, label=label)
    if bad:
        raise GateFired("1(d)", bad, seen)


def gates(*, tag_exists=None, blob_sha=None, frozen_check=None) -> dict:
    """What every runner requires before a model loads: the
    preregistration tag binding the instrument, the frozen modules, the
    runner's own import surface (4c F-1)."""
    prereg = p6.require_prereg_6(tag_exists=tag_exists, blob_sha=blob_sha)
    (frozen_check or p6.check_frozen_6)()
    if frozen_check is None:
        p6.check_imports_6()
    return prereg


def exit_gate(marker, *, frozen_check=None) -> None:
    """The frozen modules and the import surface AGAIN, when a runner has
    done its work: the loaders and the sampler are imported lazily, after
    the entry gate has passed, and a module that arrived during the run
    is seen here (the analyzer checks at entry and at exit for the same
    reason). A failure writes the stage's halt marker at `marker` — the
    records are on disk and nothing may read them as clean — and raises."""
    try:
        (frozen_check or p6.check_frozen_6)()
        if frozen_check is None:
            p6.check_imports_6()
    except Exception as e:  # noqa: BLE001 — whatever it is, the stage is not clean
        marker = Path(marker)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(f"exit gate: {type(e).__name__}: {e}\n")
        raise RuntimeError(f"EXIT GATE FIRED: {e}") from e


def refuse_if_halted(root) -> None:
    marks = r6.halt_markers(root)
    if marks:
        raise RuntimeError(f"halt marker(s) present: {[str(m) for m in marks[:3]]} — "
                           f"the analyzer reads this tree as INSUFFICIENT_DATA")
