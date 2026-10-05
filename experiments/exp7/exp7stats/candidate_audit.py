"""Explicit candidate/runtime closure, including external/aliased/generated execution.

Runtime allowances are independent pinned data, never discovered and trusted by
this guard. Cold missing cache probes raise ENOENT themselves (no racy open).
"""
from pathlib import Path
import errno
import os
import sys
import types
import importlib.util
import _imp
import _thread
from .common import require, pin, digest
from .read_boundary import ReadBoundary


def code_hash(code):
    def constant(v):
        if isinstance(v, types.CodeType):
            return structural(v)
        if isinstance(v, tuple):
            return [constant(x) for x in v]
        if isinstance(v, frozenset):
            return sorted((constant(x) for x in v), key=repr)
        return {"type": type(v).__name__, "value": repr(v)}
    def structural(c):
        filename = c.co_filename if c.co_filename.startswith("<") else str(Path(c.co_filename).resolve())
        return {"filename": filename, "name": c.co_name, "qualname": c.co_qualname,
                "firstline": c.co_firstlineno, "code": c.co_code.hex(), "constants": [constant(x) for x in c.co_consts],
                "names": c.co_names, "varnames": c.co_varnames, "freevars": c.co_freevars, "cellvars": c.co_cellvars,
                "args": (c.co_argcount, c.co_posonlyargcount, c.co_kwonlyargcount), "flags": c.co_flags,
                "stack": c.co_stacksize, "lines": c.co_linetable.hex(), "exceptions": c.co_exceptiontable.hex()}
    return digest(structural(code))


def code_tree(code):
    yield code
    for value in code.co_consts:
        if isinstance(value, types.CodeType):
            yield from code_tree(value)


class CandidateAudit:
    def __init__(self, expected, source_paths, runtime, *, read_port=None):
        require(type(runtime) is dict and set(runtime) == {"schema", "roots", "files", "frozen", "generated"}
                and runtime["schema"] == "exp7.calibration-runtime.v1", "independent runtime allowance required")
        require(type(runtime["roots"]) is dict and set(runtime["roots"]) == {"stdlib", "numpy"}, "explicit stdlib/NumPy roots")
        self.runtime = runtime
        self.expected = {str(Path(k).resolve()): pin(v) for k, v in expected.items()}
        self.sources = {str(Path(k).resolve()) for k in source_paths}
        self.roots = {k: Path(v).resolve() for k, v in runtime["roots"].items()}
        require(all(p.is_dir() for p in self.roots.values()), "runtime root directories")
        for path, row in runtime["files"].items():
            require(type(row) is dict and set(row) == {"sha256", "role"} and row["role"] in ("stdlib", "numpy", "helper"), "runtime file role")
            p = Path(path)
            require(p.is_absolute() and str(p.resolve()) == path, "canonical runtime path")
            if row["role"] != "helper":
                require(p.is_relative_to(self.roots[row["role"]]), "runtime file outside explicit root")
            require(path not in self.expected or self.expected[path] == row["sha256"], "conflicting runtime/candidate pin")
            self.expected[path] = pin(row["sha256"])
            if p.suffix == ".py":
                self.sources.add(path)
        self.allowed_codes, self.known_code_objects, self.loaded_sources = set(), {}, set()
        self.busy = self.active = False
        self.violations, self.missing_cache_probes, self.reads, self.execs = [], set(), set(), set()
        self.inputs = ReadBoundary(self, read_port)
        for name, expected_hash in runtime["frozen"].items():
            require(_imp.is_frozen(name), "runtime frozen module")
            code = _imp.get_frozen_object(name)
            require(code_hash(code) == pin(expected_hash), "frozen interpreter code changed")
            self.allowed_codes.update(code_hash(c) for c in code_tree(code))
        for fingerprint, row in runtime["generated"].items():
            pin(fingerprint)
            require(type(row) is dict and set(row) == {"producer", "producer_sha256"}, "generated-code authority")
            require(row["producer"] in self.sources and self.expected[row["producer"]] == pin(row["producer_sha256"]), "unbound generated-code producer")
            self.allowed_codes.add(fingerprint)
        self.check_files()
        self.check_modules()
        sys.addaudithook(self.audit)

    def check_files(self):
        for name, want in self.expected.items():
            require(digest(Path(name).read_bytes()) == want, f"candidate/runtime binding changed: {name}")

    def check_modules(self):
        for module in tuple(sys.modules.values()):
            path = getattr(module, "__file__", None)
            if path:
                require(str(Path(path).resolve()) in self.expected, f"unbound loaded external/local module: {path}")

    def locate(self, filename):
        require(isinstance(filename, (str, bytes, os.PathLike)), "unattributed descriptor read")
        path = str(Path(os.fsdecode(filename)).resolve())
        require(path in self.expected, f"unpinned external/candidate read/exec: {path}")
        require(digest(Path(path).read_bytes()) == self.expected[path], f"candidate/runtime read changed: {path}")
        return path

    def allow_code(self, code):
        if self.known_code_objects.get(id(code)) is code:
            return
        filename = code.co_filename
        if not filename.startswith("<"):
            path = self.locate(filename)
            require(path in self.sources, "execution from non-source input")
            if path not in self.loaded_sources:
                compiled = compile(Path(path).read_bytes(), path, "exec", dont_inherit=True, optimize=sys.flags.optimize)
                self.allowed_codes.update(code_hash(c) for c in code_tree(compiled))
                self.loaded_sources.add(path)
        require(code_hash(code) in self.allowed_codes, f"unbound generated/altered code object: {filename}/{code.co_name}")
        self.known_code_objects[id(code)] = code
        self.execs.add(filename)

    def profile(self, frame, event, arg):
        if not self.active or self.busy or event not in ("call", "c_call"):
            return
        self.busy = True
        try:
            if event == "c_call":
                require(arg is not _thread.start_new_thread, "serial calibration cannot start untraced Python threads")
                self.inputs.native_call(arg)
            else:
                self.allow_code(frame.f_code)
        except BaseException as exc:
            self.violations.append(str(exc))
            raise
        finally:
            self.busy = False

    def audit(self, event, args):
        if not self.active or self.busy:
            return
        self.busy = True
        try:
            if event == "sys.setprofile":
                require(False, "candidate cannot replace execution guard")
            elif event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.fork"):
                require(False, "candidate operation cannot spawn untraced execution")
            elif event == "exec":
                self.allow_code(args[0])
            elif event == "import" and len(args) > 1 and isinstance(args[1], str):
                self.locate(args[1])
            elif event == "ctypes.dlopen":
                self.locate(args[0])
            elif event == "mmap.__new__":
                require(False, "file-backed mappings are outside snapshot input API")
            elif event == "open":
                filename, mode, flags = args
                if isinstance(mode, str) and not ("r" in mode or "+" in mode):
                    return
                if mode is None and flags & os.O_ACCMODE == os.O_WRONLY:
                    return
                require(self.inputs.opening, "readable opens must use the controlled snapshot API")
                if isinstance(filename, (str, bytes, os.PathLike)):
                    path = Path(os.fsdecode(filename))
                    if path.suffix == ".pyc":
                        try:
                            source = Path(importlib.util.source_from_cache(str(path)))
                        except ValueError:
                            source = None
                        if source is not None:
                            try:
                                path.lstat()
                            except FileNotFoundError:
                                require(str(source.resolve()) in self.sources, "cache probe has no pinned source")
                                self.locate(source)
                                self.missing_cache_probes.add(str(path.resolve()))
                                raise FileNotFoundError(errno.ENOENT, "missing pinned cold cache probe", str(path))
                        require(False, "existing/unbound bytecode refused")
                self.reads.add(self.locate(filename))
        except FileNotFoundError as exc:
            if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)) and str(Path(os.fsdecode(args[0])).resolve()) in self.missing_cache_probes:
                raise
            self.violations.append(str(exc))
            raise
        except BaseException as exc:
            self.violations.append(str(exc))
            raise
        finally:
            self.busy = False

    def __enter__(self):
        require(sys.getprofile() is None, "cold calibration requires no prior profiler")
        frame = sys._getframe()
        while frame is not None:
            self.allow_code(frame.f_code)
            frame = frame.f_back
        self.inputs.install()
        sys.setprofile(self.profile)
        self.active = True
        return self

    def __exit__(self, *args):
        self.active = False
        sys.setprofile(None)
        self.inputs.restore()
        self.check_files()
        self.check_modules()
        require(not self.violations, "candidate audit violations: " + "; ".join(self.violations))
        return False
