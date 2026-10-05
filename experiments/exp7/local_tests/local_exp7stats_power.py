# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from exp7stats.power import grid
from exp7stats.calibration import envelope_grid, prompt_probabilities

class SimulationContractTests(unittest.TestCase):

    def test_finite_grid_exact_counts_without_running_grid(self):
        rows = list(grid())
        self.assertEqual(sum((r[-1] is None for r in rows)), 80)
        self.assertEqual(sum((r[-1] is not None for r in rows)), 240)
        self.assertEqual(len({str(r) for r in rows}), 320)
        cells = list(envelope_grid())
        impossible = sum((any((prompt_probabilities(*row[:2], row[2], d)['status'] == 'UNSUPPORTED' for row in pattern)) for _, pattern, _, d in cells))
        self.assertEqual((len(cells), impossible), (80, 16))
