# experiments/exp5/collect_5.py
"""The Exp 5 per-unit pipeline (design §3.3, §3.9): the candidate-file
loader generalized to seven sizes (2h's family with `size` threaded),
the unit's records in a fixed order with `_unit.json` LAST, host
attestation, the transport measurement, and a one-slot prefetcher.
Every torch/transformers/huggingface_hub import is inside a function."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
REPO = EXP5.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g.run.sweep_2g import evaluate_items  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402

CKPT_CACHE_5 = Path.home() / "emergence-lab" / "ckpt_cache_5"


# ---------------------------------------------------------------- loaders

def load_tokenizer_5(size: str):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(b5.REPO_OF_5[size], revision=b5.MAIN_SHA_5[size])
    tok.padding_side = "left"                       # 2b's rule, verbatim
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def _rev_dir(size, step, cache_root) -> Path:
    return Path(cache_root) / size / f"step{int(step)}"


def download_entry_5(size: str, entry: dict, cache_root=CKPT_CACHE_5) -> dict:
    from huggingface_hub import hf_hub_download
    rev_dir = _rev_dir(size, b5.FINAL_STEP_5 if entry["revision"] == "main" else int(entry["revision"][4:]),
                       cache_root)
    return {name: Path(hf_hub_download(b5.REPO_OF_5[size], name, revision=entry["commit"],
                                       cache_dir=str(rev_dir))).resolve()
            for name in entry["files"]}


def verify_downloads_5(entry: dict, paths: dict) -> dict:
    shas = {}
    for name, p in paths.items():
        got = bg.sha256_file(p)
        want = entry["lfs_sha256"].get(name)
        if want is not None and got != want:
            raise ValueError(f"{name}: downloaded sha256 {got} against the manifest's {want}")
        shas[name] = got
    return shas


def pinned_config_5(size: str):
    from transformers import AutoConfig
    return AutoConfig.from_pretrained(b5.REPO_OF_5[size], revision=b5.MAIN_SHA_5[size])


def clean_dir_5(size, step, cache_root, paths: dict) -> Path:
    d = _rev_dir(size, step, cache_root) / "clean"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for name, src in paths.items():
        try:
            os.link(src, d / name)
        except OSError:
            shutil.copy2(src, d / name)
    pinned_config_5(size).to_json_file(str(d / "config.json"))
    return d


def load_checkpoint_5(size: str, step: int, entry: dict, *, cache_root=CKPT_CACHE_5,
                      device: str = "cuda"):
    """MODEL CONTACT: the candidate files only, hashed, into the pinned
    config; loading info must be empty; fp16 on `device`."""
    import torch
    from transformers import AutoModelForCausalLM
    t0 = time.time()
    paths = download_entry_5(size, entry, cache_root)
    dl = time.time() - t0
    shas = verify_downloads_5(entry, paths)
    d = clean_dir_5(size, step, cache_root, paths)
    model, li = AutoModelForCausalLM.from_pretrained(str(d), config=pinned_config_5(size),
                                                     dtype=torch.float16, output_loading_info=True)
    bad = {k: list(li.get(k, [])) for k in ("missing_keys", "unexpected_keys", "mismatched_keys")
           if li.get(k)}
    if bad:
        raise ValueError(f"{size} step {step}: the candidate files do not fill the pinned "
                         f"architecture exactly: {bad}")
    model = model.to(device).eval()
    info = {"size": size, "step": int(step), "revision": entry["revision"],
            "commit": entry["commit"], "kind": entry["kind"], "files": list(entry["files"]),
            "sha256": shas, "config_source": f"{b5.REPO_OF_5[size]}@{b5.MAIN_SHA_5[size]}",
            "tokenizer_source": f"{b5.REPO_OF_5[size]}@{b5.MAIN_SHA_5[size]}",
            "loading_info": {k: len(li.get(k, [])) for k in
                             ("missing_keys", "unexpected_keys", "mismatched_keys")},
            "download_seconds": round(dl, 1),
            "transport": "classic" if os.environ.get("HF_HUB_DISABLE_XET") else "xet"}
    return model, info


def free_5(size, step, cache_root=CKPT_CACHE_5) -> None:
    d = _rev_dir(size, step, cache_root)
    if d.exists():
        shutil.rmtree(d)


def release_5(model) -> None:
    if model is None:
        return
    try:
        import torch
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:  # noqa: BLE001 — fakes
        pass


def dtype_5(model) -> str:
    """The loaded weights' dtype, measured (final review M-4): "float16"."""
    return str(next(model.parameters()).dtype).replace("torch.", "")


def n_params_5(model) -> int:
    return int(sum(p.numel() for p in model.parameters()))


def real_loaders_5() -> dict:
    from models import load_pythia
    h = bt.harness_2c()

    def checkpoint(size, step, entry, *, cache_root, device):
        return load_checkpoint_5(size, step, entry, cache_root=cache_root, device=device)

    def pythia_2c(size, device):
        tok, model = load_pythia(size, device=device)
        return model, {"size": size, "step": b5.FINAL_STEP_5, "path": "a"}

    def prefetch(size, entry, cache_root):
        download_entry_5(size, entry, cache_root)

    return {"checkpoint": checkpoint, "pythia_2c": pythia_2c, "tokenizer": load_tokenizer_5,
            "runner": lambda tok, model: h.HFRunner(tok, model, batch_size=b5.BATCH_ARGMAX_5),
            "digest": ck.tensor_digest, "free": free_5, "loss": sl5.slice_loss_5,
            "release": release_5, "n_params": n_params_5, "prefetch": prefetch, "dtype": dtype_5}


# ---------------------------------------------------------- attestation

def stack_5() -> dict:
    out = {}
    for name in b5.STACK_KEYS_5:
        try:
            out[name] = __import__(name).__version__
        except Exception:  # noqa: BLE001
            out[name] = None
    try:
        import hf_xet  # noqa: F401
        out["hf_xet"] = True
    except ImportError:
        out["hf_xet"] = False
    return out


def _gpu_name(device: str) -> str:
    try:
        import torch
        if device.startswith("cuda") and torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
        if device == "mps":
            return "Apple MPS"
    except Exception:  # noqa: BLE001
        pass
    return "unknown"


def _cuda_version() -> object:
    try:
        import torch
        return torch.version.cuda
    except Exception:  # noqa: BLE001
        return None


def host_record_5(device: str, transports: dict, *, stack=None, gpu=None, python=None) -> dict:
    rec = {"stack": stack if stack is not None else stack_5(), "device": device,
           "cuda": _cuda_version(),        # final review M-9: recorded, not required (the Mac: None)
           "gpu": gpu if gpu is not None else _gpu_name(device),
           "python": python if python is not None else platform.python_version(),
           "platform": platform.platform(), "transports": dict(transports),
           "hf_hub_disable_xet": os.environ.get("HF_HUB_DISABLE_XET"),
           "thread_pin": _threads_5.thread_pin_record_5()}
    try:
        rec["nvidia_smi"] = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:  # noqa: BLE001
        rec["nvidia_smi"] = None
    canonical = json.dumps(rec, sort_keys=True).encode()
    rec["sha256"] = hashlib.sha256(canonical).hexdigest()
    rec["written_utc"] = datetime.now(timezone.utc).isoformat()
    return rec


def measure_transports_5(size: str = "160m", cache_root=CKPT_CACHE_5) -> dict:
    """Gate 0: the same file (the size's `main` single safetensors) through
    the classic path and the xet path, each in its own subprocess (the
    huggingface_hub env switch is read at import), MB/s each. Scratch
    caches, deleted afterwards."""
    script = ("import time,sys;from huggingface_hub import hf_hub_download;t=time.time();"
              f"p=hf_hub_download({b5.REPO_OF_5[size]!r},'model.safetensors',"
              f"revision={b5.MAIN_SHA_5[size]!r},cache_dir=sys.argv[1]);"
              "import os;print(os.path.getsize(p)/1e6/(time.time()-t))")
    out = {}
    for name, env_extra in (("classic", {"HF_HUB_DISABLE_XET": "1"}), ("xet", {})):
        d = Path(cache_root) / f"_transport_{name}"
        if d.exists():
            shutil.rmtree(d)
        env = {k: v for k, v in os.environ.items() if k != "HF_HUB_DISABLE_XET"}
        env.update(env_extra)
        r = subprocess.run([sys.executable, "-c", script, str(d)], capture_output=True, text=True,
                           env=env, timeout=1800)
        out[f"{name}_mbps"] = round(float(r.stdout.strip().splitlines()[-1]), 1) if r.returncode == 0 else None
        shutil.rmtree(d, ignore_errors=True)
    out["used"] = "classic" if os.environ.get("HF_HUB_DISABLE_XET") else "xet"
    out["file"] = f"{b5.REPO_OF_5[size]}/model.safetensors@{b5.MAIN_SHA_5[size]}"
    return out


# --------------------------------------------------------------- records

def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def rung_record_5(*, size, step, rung, cap, ev, ckpt, host, git_sha, t_s) -> dict:
    return {"rung": rung, "size": size, "step": int(step), "revision": ckpt["revision"],
            "commit": ckpt["commit"], "kind": ckpt["kind"], "files": list(ckpt["files"]),
            "weight_sha256": dict(ckpt.get("sha256", {})),
            "config_source": ckpt.get("config_source"), "tokenizer_source": ckpt.get("tokenizer_source"),
            "items_sha256": cap["items_sha256"], "n": len(ev["bits"]), "correct": ev["correct"],
            "bits": ev["bits"], "continuations": ev["continuations"],
            "max_new_tokens": bt.max_new_tokens(rung), "n_shots": bt.N_SHOTS, "dtype": b5.DTYPE_5,
            "batch_size": b5.BATCH_ARGMAX_5, "answer_type": cap["answer_type"],
            "verify": "2c normalize + exact match under 3c's total wrapper",
            "prereg_tag": b5.PREREG_TAG_5, "stack": host["stack"], "device": host["device"],
            "gpu": host["gpu"], "host_sha256": host["sha256"], "git_sha": git_sha,
            "written_utc": datetime.now(timezone.utc).isoformat(), "seconds": round(t_s, 2)}


# Ratification slip 9: the unit kinds whose slice loss the search READS (design
# §3.7 gate 3 as ratified) — a non-finite loss on one of these halts the size.
HALT_ON_NONFINITE_WHY_5 = ("spine", "bisect", "final")


def run_unit_5(size, step, *, root, manifest, cache_root, device, battery, verify_fn, sl, host,
               loaders, git_sha, why, prefetcher=None) -> dict:
    """One unit end to end; `_unit.json` LAST; the checkpoint freed in
    `finally`. Returns {"action": "loaded"|"reused", "loss": ℓ}."""
    if b5.unit_complete_5(root, size, step):
        rec = json.loads(b5.loss_record_path_5(root, size, step).read_text())
        return {"action": "reused", "loss": rec["loss"], "finite": b5.loss_is_finite_5(rec),
                "size": size, "step": int(step)}
    entry = b5.entry_5(manifest, size, step)
    d = b5.unit_dir_5(root, size, step)
    if d.exists():
        shutil.rmtree(d)                                   # a torn unit is never resumed
    if prefetcher is not None:
        # Freeze F-8 (ruling): join the in-flight download ONLY if it is this
        # very unit's; a download of a DIFFERENT step (the next one) keeps
        # running while this unit loads and scores — different cache dirs, no
        # race; the same step cannot race because wait_for joins first.
        prefetcher.wait_for(size, step)
    t0 = time.time()
    model = None
    try:
        model, info = loaders["checkpoint"](size, step, entry, cache_root=cache_root, device=device)
        digest = loaders["digest"](model)
        n_params = loaders["n_params"](model)
        _write(b5.checkpoint_record_path_5(root, size, step),
               {**info, "digest": digest, "n_params": n_params, "dtype": b5.DTYPE_5,
                "dtype_measured": loaders["dtype"](model),      # final review M-4: measured
                "stack": host["stack"], "device": host["device"], "host_sha256": host["sha256"],
                "git_sha": git_sha, "why": why})
        loss = loaders["loss"](model, sl, batch_size=b5.LOSS_BATCH_5, device=device)
        _write(b5.loss_record_path_5(root, size, step),
               {**loss, "size": size, "step": int(step), "stack": host["stack"],
                "device": host["device"], "host_sha256": host["sha256"], "git_sha": git_sha})
        # Freeze F-7 (ruling B-3(b)) as NARROWED by ratification slip 9 (2026-09-23):
        # gate 3 requires a finite loss on every spine, bisection and final unit —
        # the losses the search reads — so a non-finite one on such a unit halts
        # the size HERE (the unit left incomplete, no _unit.json; the checkpoint
        # freed in `finally`; exit 2). Any OTHER unit (a window member, S11, the
        # preflight's or S9's) is written whole and MARKED: `_unit.json` carries
        # `finite` false, the runner's search log lists it, and the analyzer
        # treats a window member as ABSENT (its side shorter, the edge rule) and
        # never reads its counts — the argmax reads come from the same
        # overflowed forward. The MEASURED value decides, never the attestation.
        finite = b5.loss_is_finite_5(loss)
        if not finite and why in HALT_ON_NONFINITE_WHY_5:
            hp = b5.halt_marker_path_5(root, size)
            hp.parent.mkdir(parents=True, exist_ok=True)
            msg = (f"non-finite slice loss at {size}/step{int(step)} ({why}): "
                   f"n_nonfinite {loss.get('n_nonfinite')} — gate 3 (finite loss on every spine, "
                   f"bisection and final unit)")
            hp.write_text(msg + "\n")
            print(f"[5] HALTED: {msg}", flush=True)
            raise SystemExit(2)
        if not finite:
            print(f"[5] NONFINITE ({why}): {size}/step{int(step)} slice loss not finite "
                  f"(n_nonfinite {loss.get('n_nonfinite')}) — unit written and marked; treated as "
                  f"ABSENT, its counts never read (slip 9)", flush=True)
        runner = loaders["runner"](loaders["tokenizer"](size), model)
        ckpt = {**info, "revision": entry["revision"], "commit": entry["commit"],
                "kind": entry["kind"], "files": list(entry["files"]), "sha256": info["sha256"]}
        for rung in b5.RUNGS:
            t = time.time()
            ev = evaluate_items(runner, battery[rung], verify_fn)
            _write(b5.rung_record_path_5(root, size, step, rung),
                   rung_record_5(size=size, step=step, rung=rung, cap=battery[rung], ev=ev,
                                 ckpt=ckpt, host=host, git_sha=git_sha, t_s=time.time() - t))
        files = {name: bg.sha256_file(d / name) for name in b5.unit_files_5()}
        _write(b5.unit_record_path_5(root, size, step),
               {"size": size, "step": int(step), "why": why, "files": files, "digest": digest,
                "loss": loss["loss"], "finite": finite, "n_nonfinite": loss.get("n_nonfinite"),
                "git_sha": git_sha, "host_sha256": host["sha256"],
                "prereg_tag": b5.PREREG_TAG_5, "seconds": round(time.time() - t0, 1),
                "written_utc": datetime.now(timezone.utc).isoformat()})
        print(f"[5] {size}/step{step} ({why}): loss {loss['loss']:.5f}, "
              f"{time.time() - t0:.0f} s", flush=True)
        return {"action": "loaded", "loss": loss["loss"], "finite": finite, "size": size,
                "step": int(step)}
    finally:
        loaders["release"](model)
        model = None
        loaders["free"](size, step, cache_root)


class Prefetcher:
    """One background download at a time (design §7: the runner overlaps
    the next candidate's download with the current unit's scoring)."""

    def __init__(self, loaders, *, cache_root):
        self.loaders, self.cache_root, self._t, self._err = loaders, cache_root, None, None
        self.target = None          # (size, step) in flight, None when idle (freeze F-8)

    def start(self, size, entry) -> None:
        self.wait()
        self._err = None
        rev = entry["revision"]
        self.target = (size, b5.FINAL_STEP_5 if rev == "main" else int(rev[4:]))

        def go():
            try:
                self.loaders["prefetch"](size, entry, self.cache_root)
            except Exception as e:  # noqa: BLE001 — surfaced by wait(); the real load retries
                self._err = e
        self._t = threading.Thread(target=go, daemon=True)
        self._t.start()

    def wait_for(self, size, step) -> None:
        """Join only if the in-flight download is (size, step) (freeze F-8)."""
        if self.target == (size, int(step)):
            self.wait()

    def wait(self) -> None:
        if self._t is not None:
            self._t.join()
            self._t = None
            self.target = None
            if self._err is not None:
                print(f"[5 prefetch] failed ({self._err}); the unit's own download will retry",
                      flush=True)


def rebuild_loss_table_5(root) -> dict:
    table = {}
    units = b5.units_root_5(root)
    if units.exists():
        for size_dir in sorted(units.iterdir()):
            if not size_dir.is_dir():
                continue
            for step_dir in sorted(size_dir.iterdir()):
                if not step_dir.name.startswith("step"):
                    continue
                step = int(step_dir.name[4:])
                if not b5.unit_complete_5(root, size_dir.name, step):
                    continue
                rec = json.loads(b5.loss_record_path_5(root, size_dir.name, step).read_text())
                table.setdefault(size_dir.name, {})[str(step)] = b5.loss_table_entry_5(rec)
    table = {s: dict(sorted(v.items(), key=lambda kv: int(kv[0]))) for s, v in table.items()}
    _write(b5.loss_table_path_5(root), table)
    return table
