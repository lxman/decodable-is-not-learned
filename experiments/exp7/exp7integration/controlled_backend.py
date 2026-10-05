"""Stage-bound progress/STOP checks; live model leaves remain lazy and G2 gated."""
from pathlib import Path
from exp7core.contract import require
from exp7core.provenance import LIVE


class ControlledBackend:
    def __init__(self, heartbeat, stop_path, *, backend=LIVE):
        require(callable(heartbeat) and callable(getattr(heartbeat, "check", None)), "started heartbeat callback object")
        require(backend is LIVE or backend and callable(getattr(backend, "open", None)), "explicit backend injection")
        self.heartbeat, self.stop_path, self.backend = heartbeat, Path(stop_path), backend

    def bind(self, campaign, scope):
        campaign._ready()
        campaign.trust.grant(scope)
        if self.backend is LIVE:
            from exp7core.live import LiveBackend
            backend = LiveBackend(campaign, scope)
        else:
            backend = self.backend
        owner = self
        class Bound:
            def open(self, load):
                owner.check_new_unit()
                session = backend.open(load)
                return ControlledSession(session, owner)
        return Bound()

    def check_new_unit(self):
        self.heartbeat.check()
        require(not self.stop_path.exists() and not self.stop_path.is_symlink(), "STOP_NEW_WORK before next unit")


class ControlledSession:
    def __init__(self, session, owner):
        self.session, self.owner, self.unit = session, owner, None

    def __getattr__(self, name):
        return getattr(self.session, name)

    def sample(self, prompt, **kwargs):
        rung = kwargs["rung"]
        unit = "/".join(rung.split("/")[:2]) if rung.startswith("exp7/") else rung
        if unit != self.unit:
            self.owner.check_new_unit()
            self.owner.heartbeat({"phase": "sampling-unit"})
            self.unit = unit
        return self.session.sample(prompt, **kwargs)

    def greedy(self, prompts, cap):
        # A whole8,000-prompt checkpoint is one unit; load boundary handles STOP.
        self.owner.heartbeat.check()
        return self.session.greedy(prompts, cap)

    def close(self):
        return self.session.close()
