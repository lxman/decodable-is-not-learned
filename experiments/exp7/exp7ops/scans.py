"""Audited synthetic read/exec discovery, including transient/aliased imports."""
from pathlib import Path
import ast
import os
import sys
import marshal
import importlib.util
import errno
from .evidence import require, digest, pin, verify_files

class ReadImportScan:
    def __init__(self, roots, allowed_external=None, generated_producers=None):
        require(type(roots) is dict and roots, "scan roots")
        self.roots = {Path(root).resolve(): dict(pins) for root, pins in roots.items()}
        require(allowed_external is None or type(allowed_external) is dict, "external hash manifest")
        self.external = {str(Path(p).resolve()): pin(want) for p, want in (allowed_external or {}).items()}
        require(generated_producers is None or type(generated_producers) is dict, "generated-code producers")
        self.producers = {str(Path(p).resolve()): frozenset(names)
                          for p, names in (generated_producers or {}).items()}
        self.generated = set()
        self.missing_cache_probes = set()
        self.reads, self.execs, self.violations = set(), set(), []
        self.active, self.busy = False, False
        for root, pins in self.roots.items():
            verify_files(root, pins)
        self.check_external()
        sys.addaudithook(self.audit)

    def check_external(self):
        for name, want in self.external.items():
            require(digest(Path(name).read_bytes()) == want, "external source/read drift")

    def locate(self, filename):
        require(isinstance(filename, (str, bytes, os.PathLike)), "unattributed file-descriptor read")
        path = Path(os.fsdecode(filename)).resolve()
        for root, pins in self.roots.items():
            if path.is_relative_to(root):
                rel = path.relative_to(root).as_posix()
                require(rel in pins, "unpinned read/exec: " + rel)
                require(digest(path.read_bytes()) == pin(pins[rel]), "source/read drift: " + rel)
                return str(path)
        require(str(path) in self.external, "external unpinned read/exec: " + str(path))
        require(digest(path.read_bytes()) == self.external[str(path)], "external source/read drift")
        return str(path)

    def audit(self, event, args):
        if not self.active or self.busy:
            return
        if event == "exec":
            filename, collection = args[0].co_filename, self.execs
        elif event == "import" and len(args) > 1 and isinstance(args[1], str):
            filename, collection = args[1], self.execs
        elif event == "open":
            filename, mode, flags = args
            # Audit reads and read/write opens; exclusive write-only outputs are
            # evidence, not scientific inputs. io.open and cached direct reads hit this.
            if isinstance(mode, str) and not ("r" in mode or "+" in mode):
                return
            if mode is None and flags & os.O_ACCMODE == os.O_WRONLY:
                return
            collection = self.reads
        else:
            return
        self.busy = True
        try:
            if event == "open" and isinstance(filename, (str, bytes, os.PathLike)):
                candidate = Path(os.fsdecode(filename))
                if candidate.suffix == ".pyc":
                    try:
                        source = Path(importlib.util.source_from_cache(str(candidate)))
                    except ValueError:
                        source = None
                    if source is not None:
                        try:
                            candidate.lstat()  # existing/broken-symlink bytecode is never a missing probe
                        except FileNotFoundError:
                            self.locate(source)
                            self.missing_cache_probes.add(str(candidate.resolve()))
                            # Do NOT permit a racy open after testing absence.
                            # Deny it with its normal ENOENT so SourceFileLoader
                            # falls back to the pinned source. No input was read.
                            raise FileNotFoundError(errno.ENOENT, "missing cold bytecode probe", str(candidate))
            if event == "exec" and filename.startswith("<"):
                frame = sys._getframe(1)
                producer = str(Path(frame.f_code.co_filename).resolve())
                require(frame.f_code.co_name in self.producers.get(producer, ()), "unattributed generated exec")
                self.locate(producer)
                self.generated.add((producer, frame.f_code.co_name, digest(marshal.dumps(args[0]))))
            else:
                collection.add(self.locate(filename))
        except FileNotFoundError as exc:
            if event == "open" and str(Path(os.fsdecode(filename)).resolve()) in self.missing_cache_probes:
                raise
            self.violations.append(str(exc))
            raise
        except BaseException as exc:
            self.violations.append(str(exc))
            raise
        finally:
            self.busy = False

    def __enter__(self):
        self.active = True
        return self

    def __exit__(self, kind, error, trace):
        self.active = False
        for root, pins in self.roots.items():
            verify_files(root, pins)
        self.check_external()
        require(not self.violations, "audit violations: " + "; ".join(self.violations))
        return False

    def receipt(self):
        return {"reads": sorted(self.reads), "execs": sorted(self.execs),
                "generated_exec": sorted(self.generated), "missing_cache_probes": sorted(self.missing_cache_probes),
                "violations": list(self.violations),
                "scope": "synthetic fixture execution only"}

def static_imports(root, sources):
    """Cold source-only inventory supplements (never substitutes for) audit trace."""
    report = {}
    for name in sorted(sources):
        path = Path(root) / name
        tree = ast.parse(path.read_text(), filename=str(path))
        rows = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                rows.extend({"line": node.lineno, "name": a.name, "level": 0} for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                rows.append({"line": node.lineno, "name": node.module or "", "level": node.level})
            elif isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute)):
                symbol = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
                if symbol in ("import_module", "__import__", "exec", "eval", "open", "read_bytes", "read_text", "load"):
                    rows.append({"line": node.lineno, "dynamic_surface": symbol})
        report[name] = {"sha256": digest(path.read_bytes()), "imports_and_reads": rows}
    return report
