# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Anchors(unittest.TestCase):

    def test_contract(self):
        from exp7core.anchors import committed, anchor_record, validate_anchor, anchor_spec
        from exp7core.contract import canonical, Refusal
        import gzip
        rows = [{'item': i, 'draws': {'0': ['raw same'] * 64}} for i in range(500)]
        raw = b''.join((canonical(r) for r in rows))
        read = lambda name: gzip.compress(raw) if name.endswith('.gz') else canonical({'max_new_tokens': 8})
        record = anchor_record(raw, read=read, model='olmo2_1b', rung='add_base8', context_json='{}')
        self.assertEqual(record['draws'], 32000)
        changed = raw.replace(b'raw same', b'raw other', 1)
        with self.assertRaises(Refusal):
            validate_anchor(changed, record, read=read, model='olmo2_1b', rung='add_base8', context_json='{}')
