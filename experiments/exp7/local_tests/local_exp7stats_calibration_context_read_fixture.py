# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from exp7core.contract import Refusal
from exp7stats.common import digest

class FakeColdPort:

    def __init__(self, *, descriptors=(), streams=()):
        self.descriptors, self.streams = (tuple(descriptors), tuple(streams))

    def inherited(self):
        return {'python_threads': 0, 'readable_fds': self.descriptors, 'readable_streams': self.streams}

    def snapshot(self, path, expected):
        with open(path, 'rb') as f:
            raw = f.read()
        if digest(raw) != expected:
            raise Refusal('fabricated snapshot pin mismatch')
        return raw
