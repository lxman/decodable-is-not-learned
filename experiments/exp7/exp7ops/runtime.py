"""Live leaf adapters, imported only after authenticated deployment gates.

Source is inspected and fake-tested at plan time; these methods are never run
by miniature tests. No payment, rental creation or service-management API.
"""
from pathlib import Path
import re
from contextlib import contextmanager
from .evidence import require, strict, identifier

class SystemProcess:
    def __init__(self):
        self.children = {}

    @contextmanager
    def index_lock(self, repo):
        import fcntl
        directory = Path(self.run(["/opt/homebrew/bin/git", "-C", str(repo), "rev-parse", "--absolute-git-dir"],
                                  cwd=repo, shell=False, timeout=30).strip())
        require(directory.is_absolute() and directory.is_dir(), "git directory")
        path = directory / "exp7-publication.lock"
        require(not path.is_symlink(), "publication lock symlink")
        with path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def run(self, argv, *, cwd, shell, timeout):
        require(shell is False and type(argv) is list and argv, "argv-only process")
        import subprocess
        run = subprocess.run(argv, cwd=cwd, shell=False, capture_output=True,
                             text=True, timeout=timeout)
        require(run.returncode == 0, "bound command failed (inspect private log)")
        return run.stdout

    def spawn(self, argv, *, cwd, shell, start_new_session, stdin, stdout, stderr):
        require(shell is False and start_new_session is True and stdin == "DEVNULL"
                and stderr == "STDOUT", "detached process invariants")
        import subprocess
        child = subprocess.Popen(argv, cwd=cwd, shell=False, start_new_session=True,
            stdin=subprocess.DEVNULL, stdout=stdout, stderr=subprocess.STDOUT)
        self.children[child.pid] = child  # retain the child handle, not only a reusable PID
        return child.pid

    def session_id(self, pid):
        import os
        child = self.children.get(pid)
        require(child is not None, "unknown child identity")
        if child.poll() is not None:
            raise ProcessLookupError("bound child already exited")
        return os.getsid(pid)

    def own_session_id(self):
        import os
        return os.getsid(0)

    def terminate(self, pid):
        require(type(pid) is int and pid > 1, "specific PID required")
        child = self.children.get(pid)
        require(child is not None, "unknown child identity")
        if child.poll() is None:
            child.terminate()

REMOTE_COMMANDS = {
    "snapshot": "/venv/main/bin/python -I -B /workspace/exp7_ops/remote_7.py snapshot",
    "final-evidence": "/venv/main/bin/python -I -B /workspace/exp7_ops/remote_7.py final-evidence",
    "stop-new-work": "/venv/main/bin/python -I -B /workspace/exp7_ops/remote_7.py stop-new-work",
    "unit": "/venv/main/bin/python -I -B /workspace/exp7_ops/remote_7.py unit",
}

def remote_argv(route, operation, unit=None):
    require(type(route) is dict and set(route) == {"host", "port", "key", "known_hosts"}, "route schema")
    require(type(route["host"]) is str and re.fullmatch(r"ssh[0-9]+\.vast\.ai", route["host"]), "provider SSH host")
    require(type(route["port"]) is int and 1 <= route["port"] <= 65535, "SSH port")
    require(all(type(route[k]) is str and Path(route[k]).is_absolute() and "\x00" not in route[k]
                for k in ("key", "known_hosts")), "explicit SSH credential/host-key paths")
    require(operation in REMOTE_COMMANDS, "unapproved remote operation")
    command = REMOTE_COMMANDS[operation]
    if operation == "unit":
        from .wire import unit_name
        command += " " + unit_name(unit)  # fixed grammar excludes shell metacharacters
    else:
        require(unit is None, "unexpected remote argument")
    return ["/usr/bin/ssh", "-i", route["key"], "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=" + route["known_hosts"], "-o", "ConnectTimeout=30",
        "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=3", "-p", str(route["port"]),
        "root@" + route["host"], command]

class BoundSSH:
    def __init__(self, process, route, cwd, decode):
        require(callable(decode), "bound wire decoder")
        self.process, self.route, self.cwd, self.decode = process, route, cwd, decode

    def call(self, operation, unit=None):
        data = self.process.run(remote_argv(self.route, operation, unit), cwd=self.cwd,
                                shell=False, timeout=300)
        return self.decode(operation, strict(data))

    def snapshot(self):
        return self.call("snapshot")

    def unit(self, unit_id):
        return self.call("unit", unit_id)

    def final_evidence(self):
        return self.call("final-evidence")

    def stop_new_work(self):
        return self.call("stop-new-work")
