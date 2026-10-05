# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal, canonical, digest
from exp7core.collectors import persist_receipt, publish, greedy_new, outcome_raw, collect_outcome_anchors
from exp7core.records import build_record
from collection_fixtures import fixture, FakeSession
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_endpoint_raw_identity_not_just_equal_bits(self):
        expected = None
        with self.f.campaign() as c:
            for loader, load in [('thin', 'thin'), ('candidate', 'outcome-3440000')]:
                s = FakeSession(c, load)
                persist_receipt(c, load, s.receipt)
                collect_outcome_anchors(c, s, load, 3440000)
                name = f'units/endpoint/fakehost/{loader}'
                raw = outcome_raw(c, name, greedy_new(c, s))
                e = c.expected(name)
                publish(c, name, raw, build_record(raw, e))
                if loader == 'candidate':
                    expected = e
            c.verify_endpoint('fakehost')
        folder = self.f.root / 'units/endpoint/fakehost/candidate'
        raw = (folder / 'raw.jsonl').read_bytes().replace(b'"red"', b'" red"', 1)
        rec = canonical(build_record(raw, expected))
        (folder / 'raw.jsonl').write_bytes(raw)
        (folder / 'record.json').write_bytes(rec)
        (folder / 'DONE.json').write_bytes(canonical({'raw.jsonl': digest(raw), 'record.json': digest(rec)}))
        with self.f.campaign() as c:
            with self.assertRaisesRegex(Refusal, 'full endpoint raw identity'):
                c.verify_endpoint('fakehost')
