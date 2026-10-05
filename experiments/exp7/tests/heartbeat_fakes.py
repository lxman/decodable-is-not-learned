import guard
from pathlib import Path

class FakeClock:
    def __init__(self):
        self.value, self.scheduled = 0, []
    def advance(self, seconds):
        end = self.value + seconds
        while self.scheduled and min(x[0] for x in self.scheduled) <= end:
            due, callback = min(self.scheduled,key=lambda x:x[0])
            self.scheduled.remove((due,callback)); self.value = due; callback()
        self.value = end
    def every(self, callback, interval):
        def run():
            if callback():
                self.scheduled.append((self.value+interval,run))
        run()

class FakeHeartbeatService:
    """Deterministic independent scheduler; no threads/processes are started."""
    def __init__(self, clock, beats=None):
        self.clock, self.beats = clock, beats if beats is not None else []
    def start(self, config_path):
        from exp7ops.heartbeat import HeartbeatWriter
        writer = HeartbeatWriter.from_config(config_path, now=lambda:self.clock.value)
        writer.start()
        def pulse():
            if writer.finished:
                return False
            writer.tick(); self.beats.append(self.clock.value)
            return not writer.finished
        self.clock.every(pulse,60)
        class Handle:
            def check(self):
                if writer.error:
                    raise RuntimeError("fake heartbeat worker failed")
            def finish(self):
                if not writer.finished:
                    pulse()
                self.check()
        self.writer = writer
        return Handle()
