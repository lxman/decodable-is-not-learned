"""Standalone PRE-TAG calibration CLI. Never run in plan-authoring tests."""
import sys
import builtins

_blocked = {"torch", "transformers", "mlx", "mlx_lm", "huggingface_hub", "tokenizers", "safetensors",
            "datasets", "accelerate", "socket", "_socket", "ssl", "_ssl", "http", "requests", "httpx", "aiohttp",
            "sentencepiece", "hf_xet", "ftplib", "smtplib", "websockets", "boto3", "botocore", "paramiko", "experiments"}
_original_import = builtins.__import__


def _forbidden(name):
    return name.split(".")[0] in _blocked or name.startswith("urllib.") and name != "urllib.parse"


if any(_forbidden(name) for name in sys.modules):
    raise RuntimeError("forbidden import before cold calibration guard")


def _deny(name, globals=None, locals=None, fromlist=(), level=0):
    if _forbidden(name):
        raise ImportError(f"calibration is model/network-free: {name}")
    return _original_import(name, globals, locals, fromlist, level)


builtins.__import__ = _deny
class _Finder:
    def find_spec(self, fullname, path=None, target=None):
        if _forbidden(fullname):
            raise ImportError(f"calibration is model/network-free: {fullname}")
        return None


def _audit(event, args):
    if event == "import" and _forbidden(args[0]):
        raise ImportError(f"calibration is model/network-free: {args[0]}")
    if event.startswith("socket.") or event in ("os.system", "os.posix_spawn"):
        raise RuntimeError(f"calibration refused {event}")
    if event == "subprocess.Popen":
        executable, argv = args[:2]
        if executable != "/opt/homebrew/bin/git" or not isinstance(argv, (tuple, list)) or len(argv) < 5 or argv[3] not in ("show", "rev-parse"):
            raise RuntimeError("calibration permits read-only pinned git subprocesses only")


sys.meta_path.insert(0, _Finder())
sys.addaudithook(_audit)
sys.dont_write_bytecode = True

from pathlib import Path
import argparse
from .calibration_context import CalibrationContext
from .common import encode
from .read_boundary import close_cli_stdin


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pre-tag frozen synthetic calibration; no Campaign/model contact")
    parser.add_argument("--root", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--manifest", required=True, help="repo-relative committed candidate manifest")
    parser.add_argument("--manifest-sha256", required=True, help="independent frozen candidate manifest SHA256")
    args = parser.parse_args(argv)
    # This dedicated cold CLI has no stdin input. Close its interpreter-owned
    # stream before the candidate boundary; never discard buffered input by
    # pretending that the underlying descriptor proves its provenance.
    close_cli_stdin(sys.stdin)
    context = CalibrationContext(args.root, args.repo, candidate_commit=args.candidate_commit,
                                 manifest_path=args.manifest, manifest_sha256=args.manifest_sha256)
    # Bind the candidate before importing the generator/kernel source. The
    # actual stage repeats checks and consumes its exclusive once-only claim.
    manifest = context._manifest()
    context._check(manifest)
    from .calibration import run
    result = run(context)
    print(result["state"], flush=True)
    return 0 if result["state"] == "NO-DETECTED-CALIBRATION-DEFECT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
