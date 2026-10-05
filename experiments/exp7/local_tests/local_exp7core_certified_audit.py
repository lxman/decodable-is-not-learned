# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Audit(unittest.TestCase):

    def test_contract(self):
        from exp7core.certified.audit import expected_schedule
        a = expected_schedule('words')
        self.assertEqual(a, expected_schedule('words'))
        self.assertEqual(tuple(map(len, a)), (500, 500, 500))
        self.assertEqual(sum(a[0]), 250)
        self.assertTrue(all((set(row) == {'q0', 'q1', 'q0s', 'q1s'} for row in a[2])))
