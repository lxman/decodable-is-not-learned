"""Independent single-writer heartbeat protocol; fake-clock tested, no implicit spawn.

The foreground stage owns only mailbox.json. A separate bound service owns
status.json for the entire stage, including its terminal acknowledgement.
HeartbeatService.start must start an independent OS process and wait for its
first bound pulse. O8 supplies that fixed-program live port; tests supply fakes.
"""
from pathlib import Path
from threading import RLock
from typing import Protocol
from .evidence import require, once, state, strict, digest, canonical, identifier

class HeartbeatHandle(Protocol):
    def check(self): ...
    def finish(self): ...

class HeartbeatService(Protocol):
    def start(self, config_path): ...

class HeartbeatWriter:
    def __init__(self, config, *, now):
        require(type(config) is dict and set(config) == {"root", "pid", "stage", "heartbeat_identity_sha256"}, "heartbeat config")
        self.root = Path(config["root"]).resolve(strict=True)
        require(type(config["pid"]) is int and config["pid"] > 1, "operator PID")
        identifier(config["stage"])
        require(config["heartbeat_identity_sha256"] == digest(canonical({k:config[k] for k in ("root", "pid", "stage")})), "heartbeat identity")
        self.config, self.now = config, now
        self.finished, self.started, self.error = False, False, None
        self.sequence, self.previous = -1, None

    @classmethod
    def from_config(cls, path, *, now):
        return cls(strict(Path(path).read_bytes()), now=now)

    def start(self):
        require(not self.started, "heartbeat already started")
        once(self.root / "heartbeat-writer.CLAIM", self.config)
        self.started = True

    def tick(self):
        require(self.started, "heartbeat not started")
        if self.finished:
            return False
        try:
            value = strict((self.root / "heartbeat-mailbox.json").read_bytes())
            require(type(value) is dict and set(value) == {"heartbeat_identity_sha256", "pid", "stage", "sequence", "exit_code", "detail", "ended_utc"}, "heartbeat mailbox")
            require(value["heartbeat_identity_sha256"] == self.config["heartbeat_identity_sha256"] and type(value["pid"]) is int
                    and value["pid"] == self.config["pid"], "heartbeat mailbox identity")
            require(type(value["sequence"]) is int and value["sequence"] >= self.sequence, "heartbeat sequence regressed")
            require(value["sequence"] != self.sequence or canonical(value) == self.previous, "heartbeat sequence reused")
            check_detail(value["detail"])
            code = value["exit_code"]
            require(code is None or type(code) is int, "heartbeat exit code")
            require(value["stage"] == self.config["stage"] if code is None
                    else value["stage"] in ("complete", "error"), "heartbeat stage")
            status = {"pid": value["pid"], "stage": value["stage"], "exit_code": code,
                      "heartbeat_utc": self.now(), "heartbeat_identity_sha256": value["heartbeat_identity_sha256"],
                      "sequence": value["sequence"], **value["detail"]}
            if code is not None:
                status["ended_utc"] = value["ended_utc"]
            state(self.root / "status.json", status)
            self.sequence, self.previous = value["sequence"], canonical(value)
            self.finished = code is not None
            return not self.finished
        except Exception as exc:
            self.error = type(exc).__name__
            # Preserve last status. No heartbeat failure fabricates a worker exit.
            once(self.root / "heartbeat-error.json", {"error_type": self.error})
            raise

def check_detail(detail):
    require(type(detail) is dict and set(detail) <= {"completed", "total", "phase"}, "heartbeat detail fields")
    if "phase" in detail:
        identifier(detail["phase"])
    for name in ("completed", "total"):
        if name in detail:
            require(type(detail[name]) is int and detail[name] >= 0, "heartbeat count")

class HeartbeatSession:
    def __init__(self, root, *, pid, stage, now, service):
        require(callable(getattr(service, "start", None)), "independent heartbeat service required")
        self.root, self.now, self.service = Path(root).resolve(strict=True), now, service
        config = {"root": str(self.root), "pid": pid, "stage": stage}
        self.config = {**config, "heartbeat_identity_sha256": digest(canonical(config))}
        # Validate identities before creating any claim/output.
        HeartbeatWriter(self.config, now=now)
        self.lock, self.handle = RLock(), None
        self.terminal_requested, self.sequence = False, 0
        self.detail = {"phase": "starting"}

    def _mailbox(self, *, stage, exit_code=None):
        return {"heartbeat_identity_sha256": self.config["heartbeat_identity_sha256"], "pid": self.config["pid"], "stage": stage,
                "sequence": self.sequence, "exit_code": exit_code, "detail": self.detail,
                "ended_utc": self.now() if exit_code is not None else None}

    def start(self):
        with self.lock:
            require(self.handle is None, "heartbeat session already started")
            once(self.root / "heartbeat-config.json", self.config)
            state(self.root / "heartbeat-mailbox.json", self._mailbox(stage=self.config["stage"]))
            self.handle = self.service.start(self.root / "heartbeat-config.json")
            self.check()

    def check(self):
        require(self.handle is not None, "heartbeat service not started")
        self.handle.check()
        observed = strict((self.root / "status.json").read_bytes())
        require(not {"token", "heartbeat_token"} & set(observed), "legacy heartbeat status fields")
        require(observed.get("heartbeat_identity_sha256") == self.config["heartbeat_identity_sha256"]
                and observed.get("pid") == self.config["pid"], "heartbeat ready identity")
        return observed

    def update(self, detail):
        with self.lock:
            require(not self.terminal_requested, "heartbeat update after terminal")
            self.check()
            check_detail(detail)
            self.detail = {**self.detail, **detail}
            self.sequence += 1
            state(self.root / "heartbeat-mailbox.json", self._mailbox(stage=self.config["stage"]))

    def __call__(self, detail):
        """The bound callback also exposes check() to the watcher scheduler."""
        self.update(detail)

    def finish(self, *, exit_code, stage):
        with self.lock:
            require(type(exit_code) is int and stage in ("complete", "error"), "heartbeat terminal")
            require(not self.terminal_requested, "heartbeat terminal already requested")
            self.terminal_requested = True
            self.sequence += 1
            state(self.root / "heartbeat-mailbox.json", self._mailbox(stage=stage, exit_code=exit_code))
            require(self.handle is not None, "heartbeat worker never started")
            self.handle.finish()  # bounded wait for independent final consumption
            observed = self.check()
            require(observed.get("exit_code") == exit_code and observed.get("stage") == stage
                    and observed.get("sequence") == self.sequence, "heartbeat terminal not acknowledged")

def heartbeat_worker(config_path, *, now, wait, parent_alive):
    """Complete worker body for O8's fixed, pinned bootstrap; independent of work."""
    writer = HeartbeatWriter.from_config(config_path, now=now)
    writer.start()
    while True:
        alive = parent_alive(writer.config["pid"])
        require(type(alive) is bool, "bound operator identity observation required")
        if not alive:
            once(writer.root / "heartbeat-parent-absent.json", {"pid":writer.config["pid"], "child_exit":"UNKNOWN"})
            return {"state":"INSUFFICIENT_DATA", "reason":"operator identity absent"}
        if not writer.tick():
            break
        wait(60)
    return {"state": "COMPLETE", "operator_terminal_acknowledged": True}
