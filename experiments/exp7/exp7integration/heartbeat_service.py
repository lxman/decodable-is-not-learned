"""Fixed separate-process heartbeat service; native leaves are lazy/injectable."""
from pathlib import Path
from datetime import datetime, timezone
import os
import time
from exp7ops.evidence import require, once, strict, digest, canonical, verify_files, pin
from exp7ops.heartbeat import HeartbeatWriter, heartbeat_worker


def utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class NativeHeartbeatOS:
    def identity(self, pid):
        """PID plus kernel start identity. No kill(pid,0)-only liveness test."""
        require(type(pid) is int and pid > 1, "specific parent PID")
        if os.uname().sysname == "Linux":
            try:
                data = Path(f"/proc/{pid}/stat").read_text()
                tail = data[data.rindex(")")+2:].split()
                return {"pid": pid, "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                        "start_ticks": tail[19], "group": int(tail[2]), "session": int(tail[3])}
            except FileNotFoundError:
                return None
        import subprocess
        # macOS ps start time + parent/group + command are captured together.
        # Retained Popen handles additionally bind all child operations.
        result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "lstart=", "-o", "ppid=", "-o", "pgid=", "-o", "command="],
                                capture_output=True, text=True, timeout=10, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
        if result.returncode == 1 and not result.stdout.strip():
            return None
        require(result.returncode == 0 and result.stdout.strip(), "parent identity observation unavailable")
        return {"pid": pid, "ps_start_parent_group_command": result.stdout.strip()}

    def spawn(self, argv, *, cwd, log):
        import subprocess
        return subprocess.Popen(argv, cwd=cwd, shell=False, start_new_session=True,
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C"})

    def clock(self):
        return time.monotonic()

    def heartbeat_age(self, stamp):
        require(type(stamp) is str, "heartbeat UTC stamp")
        then = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        require(then.tzinfo is not None, "heartbeat timezone required")
        return (datetime.now(timezone.utc)-then).total_seconds()

    def wait(self, seconds):
        time.sleep(seconds)


class OSHeartbeatHandle:
    def __init__(self, child, config, parent, os_port, *, timeout):
        self.child, self.config, self.parent, self.os = child, config, parent, os_port
        self.root = Path(config["root"])
        self.timeout, self.acknowledged = timeout, False

    def _status(self):
        path = self.root/"status.json"
        if not path.exists():
            return None
        got = strict(path.read_bytes())
        require(not {"token", "heartbeat_token"} & set(got), "legacy heartbeat status fields")
        if got.get("heartbeat_identity_sha256") != self.config["heartbeat_identity_sha256"]:
            return None
        require(got.get("pid") == self.config["pid"], "heartbeat PID identity")
        return got

    def check(self):
        require(self.os.identity(self.parent["pid"]) == self.parent, "operator identity disappeared/reused")
        code = self.child.poll()
        require(code is None or self.acknowledged and code == 0, "heartbeat process not live")
        value = self._status()
        require(value is not None, "heartbeat first pulse not ready")
        age = self.os.heartbeat_age(value.get("heartbeat_utc"))
        require(type(age) in (int, float) and -5 <= age <= self.timeout, "heartbeat stale or future pulse")
        require(not (self.root/"heartbeat-error.json").exists() and
                not (self.root/"heartbeat-parent-absent.json").exists(), "heartbeat worker diagnostic")
        return value

    def ready(self):
        deadline = self.os.clock()+self.timeout
        while self.os.clock() < deadline:
            require(self.child.poll() is None, "heartbeat worker exited before readiness")
            if self._status() is not None:
                return self.check()
            self.os.wait(.05)
        raise ValueError("heartbeat readiness timeout")

    def finish(self):
        mailbox = strict((self.root/"heartbeat-mailbox.json").read_bytes())
        require(type(mailbox.get("exit_code")) is int, "terminal mailbox required")
        deadline = self.os.clock()+self.timeout
        while self.os.clock() < deadline:
            status = self._status()
            code = self.child.poll()
            if status is not None and all(status.get(k) == mailbox[k] for k in ("sequence", "exit_code", "stage")):
                if code == 0:
                    self.child.wait(timeout=1)
                    self.acknowledged = True
                    return self.check()
                require(code is None, "heartbeat terminal worker failed")
            else:
                require(code is None, "heartbeat exited without terminal acknowledgement")
            self.os.wait(.05)
        raise ValueError("heartbeat final acknowledgement timeout")


class OSHeartbeatService:
    def __init__(self, *, config_path, python, bootstrap, fixed_stage, source_root, source_pins,
                  os_port=None, timeout=75, site_sha256=None):
        require(timeout == 75, "fixed bounded heartbeat timeout")
        self.config_path = Path(config_path).absolute()
        self.python, self.bootstrap, self.stage = str(python), str(bootstrap), fixed_stage
        self.source_root, self.source_pins = Path(source_root), dict(source_pins)
        self.os = NativeHeartbeatOS() if os_port is None else os_port
        require(all(callable(getattr(self.os, n, None)) for n in ("identity", "spawn", "clock", "wait", "heartbeat_age")), "heartbeat OS port")
        self.timeout = timeout
        self.site_sha256 = pin(site_sha256)

    def start(self, config_path):
        require(Path(config_path).absolute() == self.config_path, "fixed heartbeat config path")
        verify_files(self.source_root, self.source_pins)
        config = strict(self.config_path.read_bytes())
        HeartbeatWriter(config, now=utc)  # validate the new schema before any spawn
        require(config["stage"] == self.stage, "heartbeat fixed stage")
        parent = self.os.identity(config["pid"])
        require(type(parent) is dict and parent.get("pid") == config["pid"], "parent start identity required")
        root = Path(config["root"])
        once(root/"heartbeat-parent.json", {"config_sha256": digest(self.config_path.read_bytes()), "parent": parent})
        with (root/"heartbeat-worker.log").open("xb") as log:
            child = self.os.spawn([self.python, "-I", "-B", self.bootstrap, "--site-sha256", self.site_sha256, self.stage], cwd=self.source_root, log=log)
        handle = OSHeartbeatHandle(child, config, parent, self.os, timeout=self.timeout)
        handle.ready()
        verify_files(self.source_root, self.source_pins)
        return handle


def run_bound_heartbeat(config_path, *, source_root, source_pins, os_port=None, now=utc):
    """Called only by the fixed bootstrap, with no free config-path CLI flag."""
    native = NativeHeartbeatOS() if os_port is None else os_port
    verify_files(source_root, source_pins)
    config_path = Path(config_path)
    binding = strict((config_path.parent/"heartbeat-parent.json").read_bytes())
    require(binding["config_sha256"] == digest(config_path.read_bytes()), "heartbeat parent/config binding")
    parent = binding["parent"]
    def alive(pid):
        require(pid == parent["pid"], "heartbeat parent PID changed")
        return native.identity(pid) == parent
    result = heartbeat_worker(config_path, now=now, wait=native.wait, parent_alive=alive)
    verify_files(source_root, source_pins)
    require(result.get("state") == "COMPLETE", "heartbeat parent lost before terminal")
    return result
