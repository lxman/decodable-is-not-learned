"""No test of Experiment 6 loads a weight or reaches the Hub, under any
mutant. The process is put offline and its model cache is pointed at an
empty directory BEFORE anything imports `huggingface_hub`, so a test that
falls through to a real loader fails at once, with nothing fetched and
nothing read. (A mutation run on 2026-09-28 reached the real SmolLM3-3B
loader through a loader table that was empty and therefore falsy; see
the ledger.)"""
import atexit
import os
import shutil
import tempfile

_EMPTY = tempfile.mkdtemp(prefix="exp6-no-models-")
atexit.register(shutil.rmtree, _EMPTY, ignore_errors=True)
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HOME"] = _EMPTY
os.environ["HF_HUB_CACHE"] = os.path.join(_EMPTY, "hub")
os.environ["HUGGINGFACE_HUB_CACHE"] = os.environ["HF_HUB_CACHE"]
os.environ["TRANSFORMERS_CACHE"] = os.environ["HF_HUB_CACHE"]


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "slow: regenerates item files or exercises real git (slow)")
