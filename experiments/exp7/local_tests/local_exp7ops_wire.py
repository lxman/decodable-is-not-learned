# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import once, snapshot, Refusal
from exp7ops.wire import remote_main
from local_exp7ops_wire_test_operations import payload
TERMINAL = {'exit_code': 2, 'controller_live': False, 'group_live': False, 'kind': 'error'}

class ReviewFixTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_R2_remote_failed_terminal_survives_extra_done_diagnostic(self):
        unit = self.root / 'unit'
        unit.mkdir()
        for name, data in payload().items():
            once(unit / name, data)
        once(unit / 'error.log', b'diagnostic')
        error, result = (None, None)
        try:
            result = remote_main(['snapshot'], root=self.root, allowed_units=('unit',), inventory=lambda: tuple(snapshot(self.root)), observe_terminal=lambda: TERMINAL, stop_path=self.root / 'STOP', check_bindings=lambda: None)
        except Refusal as exc:
            error = str(exc)
        self.assertIsNone(error)
        self.assertEqual(result['terminal'], TERMINAL)
