import guard  # FIRST: direct imports require guarded launcher
import unittest,tempfile,json
from pathlib import Path
from exp7core.contract import Refusal,digest
from exp7core.guardio import Pins,safe_path,write_once,publish_unit,load_unit,run_stage
SCRATCH = Path(tempfile.gettempdir())

class IOTests(unittest.TestCase):
    def test_completion_hash_not_replaceable_by_count_only_check(self):
        publish_unit(self.root, 'digest_only', b'{"draw":"a"}\n', {'count': 1})
        (self.root / 'digest_only' / 'raw.jsonl').write_bytes(b'{ "draw":"a"}\n')
        with self.assertRaises(Refusal):
            load_unit(self.root, 'digest_only', validator=lambda raw, record: None)


    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'input.txt').write_bytes(b'frozen')
        self.pins = Pins(self.root, {'input.txt': digest(b'frozen')})

    def test_entry_exit_pin_refuses_mutation(self):

        def bad():
            self.assertEqual(self.pins.read('input.txt'), b'frozen')
            (self.root / 'input.txt').write_bytes(b'changed')
            return {'would_be': 'success'}
        r = run_stage(self.root, 'analyze', pins=self.pins, body=bad)
        self.assertEqual(r['state'], 'INSUFFICIENT_DATA')
        self.assertTrue((self.root / 'HALTED.json').exists())
        self.assertFalse((self.root / 'analyze.COMPLETE.json').exists())
        self.assertIn('exit', ' '.join(r['failures']))

    def test_once_only_and_no_body_after_halt(self):
        r = run_stage(self.root, 'power', pins=self.pins, body=lambda: {'miniature': True})
        self.assertEqual(r['state'], 'COMPLETE')
        calls = []
        r = run_stage(self.root, 'power', pins=self.pins, body=lambda: calls.append(1))
        self.assertEqual(r['state'], 'INSUFFICIENT_DATA')
        self.assertEqual(calls, [])

    def test_empty_pin_and_path_injections_refuse(self):
        with self.assertRaises(Refusal):
            Pins(self.root, {})
        for p in ('../a', '/a', 'a/../b', 'a//b'):
            with self.subTest(path=p), self.assertRaises(Refusal):
                safe_path(self.root, p)
        with self.assertRaises(Refusal):
            self.pins.read('not_pinned')

    def test_complete_unit_resume_and_rederive(self):
        raw, record = (b'{"draw":"a"}\n', {'count': 1})
        publish_unit(self.root, 'unit', raw, record)

        def check(data, rec):
            if rec['count'] != len(data.splitlines()):
                raise Refusal('count does not rederive')
        self.assertEqual(load_unit(self.root, 'unit', validator=check), (raw, record))
        with self.assertRaises(FileExistsError):
            publish_unit(self.root, 'unit', raw, record)
        (self.root / 'unit' / 'record.json').write_text('{"count":2}')
        with self.assertRaises(Refusal):
            load_unit(self.root, 'unit', validator=check)

    def test_torn_and_attested_pass_refuse(self):
        (self.root / 'torn').mkdir()
        (self.root / 'torn' / 'raw.jsonl').write_bytes(b'partial')
        with self.assertRaises(Refusal):
            load_unit(self.root, 'torn', validator=lambda a, b: None)
        publish_unit(self.root, 'attested', b'{}\n', {'pass': True})
        with self.assertRaises(Refusal):
            load_unit(self.root, 'attested', validator=lambda a, b: None)

    def test_write_once_no_overwrite_and_exception_terminal(self):
        write_once(self.root / 'value', b'one')
        with self.assertRaises(FileExistsError):
            write_once(self.root / 'value', b'two')

        def crash():
            raise RuntimeError('fixture failure')
        r = run_stage(self.root, 'seal', pins=self.pins, body=crash)
        self.assertEqual(r['state'], 'INSUFFICIENT_DATA')
        self.assertIn('fixture failure', r['failures'][0])
        self.assertTrue((self.root / 'seal.REFUSED.json').exists())

    def test_invalid_root_is_also_a_terminal(self):
        r = run_stage(None, 'analyze', pins=self.pins, body=lambda: {})
        self.assertEqual(r['state'], 'INSUFFICIENT_DATA')
        self.assertIn('TypeError', r['failures'][0])
