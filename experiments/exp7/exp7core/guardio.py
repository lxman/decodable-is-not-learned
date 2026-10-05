"""Write-once, pins and complete-unit primitives. Not the production seal validator."""
from pathlib import Path
import json
import os
import sys
from .contract import Refusal, canonical, digest, pin, require


def safe_path(root, name):
    root = Path(root).resolve(strict=True)
    require(type(name) is str and name and not Path(name).is_absolute(), "relative path required")
    require(all(p not in ("", ".", "..") for p in name.split("/")), "path traversal")
    path = root
    for part in name.split("/"):
        path = path / part
        require(not path.is_symlink(), "symlink refused")
    require(path.resolve().is_relative_to(root), "path escaped root")
    return path


def write_once(path, data):
    require(type(data) is bytes, "write bytes only")
    path = Path(path)
    require(not path.is_symlink(), "symlink output refused")
    # No replace/rename-overwrite operation exists in this primitive.
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Pins:
    def __init__(self, root, expected):
        self.root = Path(root).resolve(strict=True)
        require(type(expected) is dict and expected, "empty pin injection refused")
        self.expected = {name: pin(sha) for name, sha in expected.items()}
        self.reads = set()

    def check(self):
        for name, sha in self.expected.items():
            require(digest(safe_path(self.root, name).read_bytes()) == sha,
                    f"pin mismatch: {name}")

    def read(self, name):
        require(name in self.expected, f"unpinned read: {name}")
        data = safe_path(self.root, name).read_bytes()
        require(digest(data) == self.expected[name], f"pin mismatch: {name}")
        self.reads.add(name)
        return data

    def imported_sources(self):
        """Entry/exit check of executed repository sources, including __init__.

        Dynamic read/import audit hooks remain an integration requirement;
        this snapshot does not claim to detect an import removed from sys.modules.
        """
        seen = set()
        for mod in tuple(sys.modules.values()):
            name = getattr(mod, "__file__", None)
            if not name:
                continue
            path = Path(name).resolve()
            if path.is_relative_to(self.root):
                rel = path.relative_to(self.root).as_posix()
                require(rel in self.expected, f"unpinned imported source: {rel}")
                seen.add(rel)
        return tuple(sorted(seen))


def publish_unit(root, name, raw, record):
    root = Path(root).resolve(strict=True)
    directory = safe_path(root, name)
    directory.mkdir()  # exclusive unit claim; parent must already exist
    write_once(directory / "raw.jsonl", raw)
    write_once(directory / "record.json", canonical(record))
    bindings = {n: digest((directory / n).read_bytes()) for n in ("raw.jsonl", "record.json")}
    write_once(directory / "DONE.json", canonical(bindings))
    return bindings


def load_unit(root, name, *, validator):
    require(callable(validator), "missing unit validator")
    directory = safe_path(root, name)
    if not directory.exists():
        return None
    require(directory.is_dir() and not directory.is_symlink(), "unit directory")
    want = {"raw.jsonl", "record.json", "DONE.json"}
    require({p.name for p in directory.iterdir()} == want, "torn/extra unit files")
    for n in want:
        require(not (directory / n).is_symlink(), "unit symlink")
    done = json.loads((directory / "DONE.json").read_bytes())
    require(type(done) is dict and set(done) == want - {"DONE.json"}, "completion bindings")
    payload = {}
    for n in ("raw.jsonl", "record.json"):
        payload[n] = (directory / n).read_bytes()
        require(digest(payload[n]) == pin(done[n]), "unit digest mismatch")
    rec = json.loads(payload["record.json"])
    require(type(rec) is dict and "pass" not in rec, "attested pass forbidden")
    # validator must RE-DERIVE all schema/provenance/scoring facts; its return
    # value is ignored, so returning a falsy value cannot mean validation.
    result = validator(payload["raw.jsonl"], rec)
    require(result is None, "unit validator must return None or raise")
    return payload["raw.jsonl"], rec


def run_stage(root, stage, *, pins, body):
    """A terminal-returning boundary; failures set HALTED before a success can exist.

    Claim is consumed even on failure. This is suitable for once-only analysis
    and power; a campaign needs per-unit claims and its own resumable driver.
    """
    failures, value, claimed = [], None, False
    try:
        root = Path(root)
        require(root.is_dir() and not root.is_symlink(), "stage root")
        require(type(stage) is str and stage.isidentifier(), "stage name")
        require(isinstance(pins, Pins) and callable(body), "stage injections")
        require(not (root / "HALTED.json").exists(), "stage already HALTED")
        write_once(root / f"{stage}.CLAIM", canonical({"stage": stage}))
        claimed = True
        pins.check()
        pins.imported_sources()
        value = body()
        canonical(value)  # serialization must succeed before success publication
    except BaseException as e:
        failures.append(f"{type(e).__name__}: {e}")
    if claimed:
        try:
            pins.check()
            pins.imported_sources()
        except BaseException as e:
            failures.append(f"exit {type(e).__name__}: {e}")
    result = {"state": "INSUFFICIENT_DATA" if failures else "COMPLETE",
              "failures": failures, "value": None if failures else value}
    if claimed:
        try:
            if failures:
                if not (root / "HALTED.json").exists():
                    write_once(root / "HALTED.json", canonical(result))
                write_once(root / f"{stage}.REFUSED.json", canonical(result))
            else:
                require(not (root / "HALTED.json").exists(), "HALTED before publication")
                write_once(root / f"{stage}.COMPLETE.json", canonical(result))
        except BaseException as e:
            result = {"state": "INSUFFICIENT_DATA", "value": None,
                      "failures": failures + [f"publication {type(e).__name__}: {e}"]}
            try:
                if not (root / "HALTED.json").exists():
                    write_once(root / "HALTED.json", canonical(result))
            except BaseException:
                # Unwritable disk cannot be promised a durable terminal; caller
                # must emit this returned refusal to stderr and exit nonzero.
                result["failures"].append("HALTED could not be persisted")
    return result
