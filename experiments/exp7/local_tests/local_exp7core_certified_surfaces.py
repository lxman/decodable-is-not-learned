# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Surfaces(unittest.TestCase):

    def test_contract(self):
        from exp7core.certified.surfaces import shape_path, bb_surfaces
        self.assertEqual(shape_path([(0, 0), (1, 0), (0, 1)]), 'M 0,0 L 1,0 L 0,1 L 0,0')
        self.assertEqual(bb_surfaces('words', [{'scrambled': 'tac'}]), ['The word tac is a scrambled version of the English word '])
