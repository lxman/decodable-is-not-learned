# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Oracle(unittest.TestCase):

    def test_contract(self):
        from exp7core.certified.oracle import parse_path, geometry, options
        points = parse_path('M 0,0 L 2,0 L 2,2 L 0,2 L 0,0')
        self.assertEqual(geometry(points), 'square')
        self.assertEqual(options('q\nOptions: a, b, c, d, e'), ('q', ['a', 'b', 'c', 'd', 'e']))
        with self.assertRaises(ValueError):
            parse_path('M 0,0 M 2,0')
        with self.assertRaises(ValueError):
            options('q\nOptions: a, a, c, d, e')
