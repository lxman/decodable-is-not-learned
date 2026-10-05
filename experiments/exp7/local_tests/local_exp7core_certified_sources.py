# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Sources(unittest.TestCase):

    def test_contract(self):
        from exp7core.certified.sources import geometry_key, clue_key, textkey
        a = [(0, 0), (2, 0), (0, 1)]
        self.assertEqual(geometry_key(a), geometry_key([(x + 5, y - 3) for x, y in reversed(a)]))
        self.assertNotEqual(geometry_key(a), geometry_key([(0, 0), (3, 0), (0, 1)]))
        self.assertEqual(clue_key([('b', 'c'), ('a', 'b')]), 'a<b;b<c')
        self.assertEqual(textkey(' q   here\nOptions: a, b'), 'q here')
