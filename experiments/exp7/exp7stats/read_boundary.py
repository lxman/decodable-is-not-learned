"""Cold, snapshot-only file inputs; write-only outputs remain ordinary files.

No readable OS descriptor escapes a verified input open. Entry refuses inherited
readable descriptors AND OS-backed buffers (including stale/closed-fd buffers).
Thus prebound C-call aliases need not expose their arguments to the profiler.
This is a controlled CPython I/O contract, not an OS sandbox for native code.
"""
import builtins
import errno
import fcntl
import gc
import io
import _io
import os
import stat
import sys
import _thread
from .common import require, digest

_OPEN = builtins.open
_OS_OPEN, _OS_READ, _OS_CLOSE = os.open, os.read, os.close
_FSTAT, _STAT, _LISTDIR, _FCNTL = os.fstat, os.stat, os.listdir, fcntl.fcntl
_RAW_READS = tuple(getattr(os, n) for n in ('read', 'pread', 'readv', 'preadv', 'sendfile', 'splice', 'copy_file_range') if hasattr(os, n))


def close_cli_stdin(stream, *, close=_OS_CLOSE):
    """Dedicated no-stdin CLI only. Interpreter streams may have closefd=False."""
    require(stream.fileno() == 0, 'cold CLI requires conventional stdin descriptor0')
    stream.close()  # discard any user-space prefetch without consuming it
    try:
        close(0)  # closefd=False must not leave an inherited readable kernel fd
    except OSError as exc:
        require(exc.errno == errno.EBADF, 'could not close cold CLI stdin descriptor')


def os_backed_readable(stream):
    """Memory-only buffers are not inherited file inputs; no buffer is consumed."""
    if not isinstance(stream, io.IOBase) or stream.closed:
        return False
    if not stream.readable():
        return False
    root, seen = stream, set()
    while type(root) in (io.TextIOWrapper, io.BufferedReader, io.BufferedRandom):
        require(id(root) not in seen, 'cyclic inherited stream')
        seen.add(id(root))
        root = root.buffer if type(root) is io.TextIOWrapper else root.raw
    return not isinstance(root, (io.BytesIO, io.StringIO))


class SystemCalls:
    """Actual Darwin/Linux implementation; planning tests inject fake calls."""
    listdir = staticmethod(_LISTDIR)
    stat = staticmethod(_STAT)
    fstat = staticmethod(_FSTAT)
    open = staticmethod(_OS_OPEN)
    read = staticmethod(_OS_READ)
    close = staticmethod(_OS_CLOSE)

    @staticmethod
    def flags(fd):
        return _FCNTL(fd, fcntl.F_GETFL)


def inherited_descriptors(calls, platform):
    require(platform in ('darwin', 'linux'), 'cold descriptor census requires Darwin or Linux')
    names = calls.listdir('/dev/fd' if platform == 'darwin' else '/proc/self/fd')
    require(all(type(n) is str and n.isdecimal() for n in names), 'malformed descriptor census')
    result = []
    for fd in sorted({int(n) for n in names}):
        try:
            flags = calls.flags(fd)
        except OSError as exc:
            # The directory enumeration itself can leave an already-closed fd.
            require(exc.errno == errno.EBADF, 'unobservable inherited descriptor')
            continue
        if flags & os.O_ACCMODE != os.O_WRONLY:
            result.append(fd)
    return tuple(result)


def identity(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


def snapshot_bytes(calls, path, expected):
    """Validate bytes from the actual fd, not the handle's claimed filename.

    fstat/stat identify the regular file on both sides; the independently pinned
    SHA authenticates all bytes before release to the caller. Replacement during
    read refuses even if a later pathname happens to have the expected bytes.
    """
    fd = calls.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = calls.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and identity(before) == identity(calls.stat(path)),
                'snapshot descriptor/path identity mismatch')
        chunks = []
        while True:
            raw = calls.read(fd, 1 << 20)
            require(type(raw) is bytes, 'snapshot byte stream')
            if not raw:
                break
            chunks.append(raw)
        raw = b''.join(chunks)
        require(identity(calls.fstat(fd)) == identity(before) == identity(calls.stat(path)),
                'snapshot descriptor replaced or file changed')
        require(len(raw) == before.st_size and digest(raw) == expected, 'snapshot descriptor bytes not pinned')
        return raw
    finally:
        calls.close(fd)


class SystemReadPort:
    def inherited(self):
        # Cold serial launch is mandatory; no concurrent fd-table changes from
        # existing Python workers. No inherited descriptor is auto-enrolled.
        return {'python_threads': _thread._count(),
                'readable_fds': inherited_descriptors(SystemCalls(), sys.platform),
                'readable_streams': tuple(v for v in gc.get_objects() if os_backed_readable(v))}

    def snapshot(self, path, expected):
        return snapshot_bytes(SystemCalls(), path, expected)


class ReadOnlySnapshot(io.BytesIO):
    def writable(self):
        return False

    def write(self, *args):
        raise io.UnsupportedOperation('read-only input snapshot')

    writelines = truncate = write

    def getbuffer(self):
        return memoryview(self.getvalue())


class ReadBoundary:
    def __init__(self, owner, port=None):
        self.owner = owner
        self.port = SystemReadPort() if port is None else port
        require(callable(getattr(self.port, 'inherited', None)) and callable(getattr(self.port, 'snapshot', None)),
                'cold read observation/snapshot port')
        self.opening = False
        self.bindings = []

    def cold(self):
        observed = self.port.inherited()
        require(type(observed) is dict and set(observed) == {'python_threads', 'readable_fds', 'readable_streams'},
                'complete cold input observation required')
        require(type(observed['python_threads']) is int and observed['python_threads'] == 0,
                'cold input boundary requires no existing Python workers')
        require(type(observed['readable_fds']) in (list, tuple) and not observed['readable_fds'],
                'inherited readable descriptors refused; reopen pinned inputs through snapshot open')
        require(type(observed['readable_streams']) in (list, tuple) and not observed['readable_streams'],
                'inherited OS-backed readable/buffered streams refused')

    def install(self):
        self.cold()
        for module, name, replacement in ((builtins, 'open', self.open), (io, 'open', self.open),
                (_io, 'open', self.open), (io, 'open_code', self.open_code), (_io, 'open_code', self.open_code)):
            self.bindings.append((module, name, getattr(module, name), replacement))
            setattr(module, name, replacement)

    def restore(self):
        intact = all(getattr(module, name) is replacement for module, name, old, replacement in self.bindings)
        for module, name, old, replacement in reversed(self.bindings):
            setattr(module, name, old)
        self.bindings.clear()
        require(intact, 'snapshot input wrappers changed during operation')
        self.cold()

    def native_call(self, function):
        # Defense in depth. This observes identity, NOT arguments. The cold-fd
        # refusal + no exposed input fd is what also covers partial/C aliases.
        require(not any(function is f for f in _RAW_READS), 'unattributed raw descriptor consumption refused')
        numpy = sys.modules.get('numpy')
        require(numpy is None or function is not getattr(numpy, 'fromfile', None),
                'native file input must use a verified snapshot')

    def open_code(self, path):
        return self.open(path, 'rb')

    def open(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        if self.owner.busy or not self.owner.active:
            return _OPEN(file, mode, buffering, encoding, errors, newline, closefd, opener)
        require(type(mode) is str and mode, 'input open mode')
        reading = 'r' in mode or '+' in mode
        if not reading:
            return _OPEN(file, mode, buffering, encoding, errors, newline, closefd, opener)
        require(mode in ('r', 'rt', 'rb', 'tr', 'br') and closefd is True and opener is None,
                'snapshot inputs require read-only path open without custom opener')
        require(isinstance(file, (str, bytes, os.PathLike)), 'inherited/unattributed descriptor open refused')
        # Run the original path/cache rule before any temporary fd is opened.
        self.opening = True
        try:
            self.owner.audit('open', (file, mode, os.O_RDONLY))
        finally:
            self.opening = False
        self.owner.busy = True
        try:
            path = self.owner.locate(file)
            raw = self.port.snapshot(path, self.owner.expected[path])
            require(type(raw) is bytes and digest(raw) == self.owner.expected[path], 'snapshot port byte binding')
            memory = ReadOnlySnapshot(raw)
            memory.name = path
            if 'b' in mode:
                require(encoding is None and errors is None and newline is None, 'binary snapshot text arguments')
                return memory if buffering == 0 else io.BufferedReader(memory)
            require(buffering != 0, 'unbuffered text input')
            return io.TextIOWrapper(io.BufferedReader(memory), encoding=encoding, errors=errors, newline=newline)
        finally:
            self.owner.busy = False
