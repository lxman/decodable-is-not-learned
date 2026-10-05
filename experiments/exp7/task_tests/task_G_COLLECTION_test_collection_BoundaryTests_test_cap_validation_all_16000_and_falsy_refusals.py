# Exact test method/fixtures extracted; imports pruned by referenced names.
from pathlib import Path
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7core.preflight import validate_caps
from collection_fixtures import fixture
from testing_paths import WORK as SCRATCH
SCRATCH.mkdir(exist_ok=True)


class BoundaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.f = fixture(self.repo)

    def test_cap_validation_all_16000_and_falsy_refusals(self):

        class Tok:
            all_special_ids = [0]

            def encode(self, text, add_special_tokens=True):
                return [ord(x) for x in text]

            def decode(self, tokens, skip_special_tokens=True):
                return ''.join((chr(i) for i in tokens))
        result = validate_caps(self.f.battery, Tok())
        self.assertEqual(result['comparisons'], 16000)
        for empty in (None, {}, False):
            with self.assertRaises(Refusal):
                validate_caps(self.f.battery, empty)

        class BOS(Tok):

            def encode(self, text, add_special_tokens=True):
                return ([0] if add_special_tokens else []) + super().encode(text, False)
        with self.assertRaises(Refusal):
            validate_caps(self.f.battery, BOS())

        class Long(Tok):

            def encode(self, text, add_special_tokens=True):
                return super().encode(text, add_special_tokens) * 10
        with self.assertRaises(Refusal):
            validate_caps(self.f.battery, Long())
