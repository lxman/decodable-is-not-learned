"""Actual-file, independently classified pre-outcome inventory.

The authority manifest is independently SHA-pinned by the deployment, never
derived from discovered files. Every campaign file must have a classification.
Only the statistics-owned current CLAIM is derived locally, after its exclusive
creation. This does not authorize any collection contact or grant.
"""
from pathlib import Path
import os
import re
import stat
import sys
from exp7core.records import strict_json
from exp7stats.common import (CONTACT_ROOTS, SCHEMA, digest, require, pin,
                              require_preoutcome, require_preoutcome_inventory)


def relative(name):
    require(type(name) is str and name and not Path(name).is_absolute()
            and all(p not in ("", ".", "..") for p in name.split("/")), "unsafe relative path")
    return name


def safe(root, name):
    path = Path(root)
    require(path.is_dir() and not path.is_symlink(), "unsafe root")
    for part in relative(name).split("/"):
        path = path / part
        require(not path.is_symlink(), f"symlink refused: {name}")
    return path


def enumerate_tree(root):
    """All files AND directories, including empty marker dirs; no symlink escape."""
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), "campaign root")
    files, directories = {}, []
    for base, dirs, names in os.walk(root, followlinks=False):
        for name in sorted(dirs + names):
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            mode = path.lstat().st_mode
            require(not stat.S_ISLNK(mode), f"campaign symlink: {rel}")
            require(name not in ("HALTED", "HALTED.json"), f"global HALTED: {rel}")
            if stat.S_ISDIR(mode):
                directories.append(rel)
            else:
                require(stat.S_ISREG(mode), f"nonregular campaign entry: {rel}")
                files[rel] = digest(path.read_bytes())
    return files, tuple(sorted(directories))


def verify_classification(root, row):
    """Independent labels cannot override a receipt's actual stage metadata.

    Unknown stage metadata fails closed. A future deployment must use the
    actual grant schema and carry its source pin; it cannot mark an outcome
    grant 'predictor' just because it has not yet been consumed.
    """
    name = row["path"]
    forbidden = re.compile(r"outcome|endpoint|smollm|sweep", re.I)
    require(not forbidden.search(name), f"outcome-related path before power: {name}")
    if not name.endswith(".json"):
        return
    obj = strict_json(safe(root, name).read_bytes())
    def visit(value):
        if type(value) is dict:
            for key, item in value.items():
                if key in ("stage", "phase", "scope", "stage_name", "authorized_stage", "contact_stage"):
                    require(type(item) is str and not forbidden.search(item), f"outcome/unknown receipt stage: {name}")
                    prefix = item.split("-", 1)[0]
                    require(prefix in ("generation", "predictor", "calibration", "power"), f"unclassified stage metadata: {name}")
                    require(prefix == row["phase"], f"receipt phase classification mismatch: {name}")
                if key in ("subject", "model", "model_id", "model_repo", "endpoint") and type(item) is str:
                    require(not forbidden.search(item), f"outcome grant/contact subject: {name}")
                visit(item)
        elif type(value) is list:
            for item in value:
                visit(item)
    visit(obj)


def power_inventory(root, specification, *, production, repo):
    require_preoutcome(root)
    require_preoutcome(repo)
    require(type(specification) is dict and set(specification) == {"covered_roots", "repository_roots", "entries"},
            "independent inventory specification")
    roots = specification["covered_roots"]
    require(type(roots) is list and len(roots) == len(set(roots))
            and set(CONTACT_ROOTS) <= set(roots), "all known contact roots required")
    for name in roots:
        relative(name)
    repo_roots = specification["repository_roots"]
    require(type(repo_roots) is list and len(repo_roots) == len(set(repo_roots))
            and set(CONTACT_ROOTS) | {"receipts", "preflight"} <= set(repo_roots), "all repository contact roots required")
    for name in repo_roots:
        relative(name)
    require(type(specification["entries"]) is list, "independent receipt entries")
    entries, expected = [], {}
    for row in specification["entries"]:
        require(type(row) is dict and set(row) == {"path", "phase", "kind", "sha256"}, "receipt classification schema")
        name = relative(row["path"])
        require(name not in expected, "duplicate receipt classification")
        expected[name] = pin(row["sha256"])
        entries.append(dict(row))
    claim_name = "statistics/power/CLAIM.json"
    require(claim_name not in expected, "current statistics claim is not preexisting authority")
    claim = safe(root, claim_name).read_bytes()
    require(strict_json(claim) == {"schema": SCHEMA, "stage": "power", "production": production},
            "statistics power CLAIM identity")
    # This claim's meaning follows from the exact independently specified stage
    # schema, not a phase label supplied by an arbitrary outcome receipt.
    expected[claim_name] = digest(claim)
    entries.append({"path": claim_name, "phase": "power", "kind": "phase", "sha256": digest(claim)})
    files, dirs = enumerate_tree(root)
    dirs = list(dirs)
    for name in sorted(repo_roots):
        path = safe(repo, name)
        if path.absolute().is_relative_to(Path(root).absolute()):
            continue  # already fully enumerated; never exclude actual campaign files
        if path.is_dir():
            extra_files, extra_dirs = enumerate_tree(path)
            files.update({f"repository/{name}/{p}": sha for p, sha in extra_files.items()})
            dirs += [f"repository/{name}", *(f"repository/{name}/{p}" for p in extra_dirs)]
        elif path.exists():
            require(path.is_file(), "nonregular repository marker")
            files[f"repository/{name}"] = digest(path.read_bytes())
    dirs = tuple(sorted(set(dirs)))
    require(files == expected, "unclassified, omitted, changed or missing campaign receipt")
    for row in entries:
        if row["path"].startswith("repository/"):
            verify_classification(repo, {**row, "path": row["path"][11:]})
        else:
            verify_classification(root, row)
    # Empty unknown dirs are markers too. Every directory must be a declared
    # root/ancestor or a parent of an independently classified actual file.
    declared = set(roots) | {"statistics", "statistics/power"} | {"repository/"+p for p in repo_roots}
    parents = {p.as_posix() for n in tuple(expected) + tuple(declared)
               for p in Path(n).parents if p.as_posix() != "."}
    require(set(dirs) <= declared | parents, "unclassified empty campaign marker directory")
    covered = sorted(declared | {n.split("/")[0] for n in files})
    inventory = {"schema": "exp7.contact-inventory.v1", "covered_roots": covered,
                 "entries": sorted(entries, key=lambda r: r["path"])}
    require_preoutcome_inventory({"contact_inventory": inventory,
                                 "input_sha256": {"contact_inventory": digest(inventory)}})
    return inventory, (files, dirs)


class ReadOnlyCampaign:
    """Latch transient writes, creates, deletes and renames during power.

    A removed probe still refuses. Audit hooks are scoped by an active flag;
    they do not survive as active guards after context exit. Entry/exit actual
    enumeration remains necessary for changes outside this Python process.
    """
    def __init__(self, root, *, additional_roots=()):
        self.roots = tuple(Path(p).resolve() for p in (root, *additional_roots))
        self.active = False
        self.events = []

    def _inside(self, value):
        # Audit open omits dir_fd; CWD cannot attribute relative mutations.
        # Descriptor/non-path targets likewise have no independently known root.
        if not isinstance(value, (str, bytes, os.PathLike)):
            return True
        path = Path(os.fsdecode(value))
        if not path.is_absolute():
            return True
        path = Path(os.path.abspath(path))
        return any(path.is_relative_to(root) or path.resolve().is_relative_to(root) for root in self.roots)

    def _audit(self, event, args):
        if not self.active:
            return
        candidates = ()
        if event == "open":
            mode, flags = args[1], args[2]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            if writing:
                candidates = args[:1]
        elif event in ("os.rename", "os.link", "os.symlink"):
            candidates = args[:2]
        elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.truncate", "os.chmod", "os.utime"):
            candidates = args[:1]
        if any(self._inside(v) for v in candidates):
            self.events.append((event, tuple(str(v) for v in candidates)))
            # Latch rather than interrupting: tests demonstrate create/remove,
            # and the terminal boundary must retain the genuine operation error.

    def start(self):
        sys.addaudithook(self._audit)
        self.active = True

    def check(self):
        require(not self.events, f"transient campaign mutation during power: {self.events}")

    def stop(self):
        self.active = False
