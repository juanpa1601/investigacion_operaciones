from __future__ import annotations

import unittest

import numpy as np

from models.transport_problem import TransportProblem


class TestTransportProblem(unittest.TestCase):

    def setUp(self) -> None:
        self.problem = TransportProblem(
            supply=[30.0, 40.0, 50.0],
            demand=[20.0, 30.0, 40.0, 30.0],
            costs=[[2, 3, 1, 5], [7, 3, 4, 6], [8, 5, 3, 3]],
            source_labels=["F1", "F2", "F3"],
            destination_labels=["D1", "D2", "D3", "D4"],
        )

    def test_num_sources(self) -> None:
        self.assertEqual(self.problem.num_sources, 3)

    def test_num_destinations(self) -> None:
        self.assertEqual(self.problem.num_destinations, 4)

    def test_total_supply(self) -> None:
        self.assertAlmostEqual(self.problem.total_supply, 120.0)

    def test_total_demand(self) -> None:
        self.assertAlmostEqual(self.problem.total_demand, 120.0)

    def test_is_balanced_when_equal(self) -> None:
        self.assertTrue(self.problem.is_balanced)

    def test_is_not_balanced_when_supply_exceeds_demand(self) -> None:
        p = TransportProblem(
            supply=[60.0, 40.0],
            demand=[20.0, 30.0],
            costs=[[1, 2], [3, 4]],
            source_labels=["F1", "F2"],
            destination_labels=["D1", "D2"],
        )
        self.assertFalse(p.is_balanced)

    def test_is_not_balanced_when_demand_exceeds_supply(self) -> None:
        p = TransportProblem(
            supply=[30.0, 20.0],
            demand=[50.0, 40.0],
            costs=[[1, 2], [3, 4]],
            source_labels=["F1", "F2"],
            destination_labels=["D1", "D2"],
        )
        self.assertFalse(p.is_balanced)

    def test_cost_matrix_shape(self) -> None:
        self.assertEqual(self.problem.cost_matrix().shape, (3, 4))

    def test_cost_matrix_values(self) -> None:
        expected = np.array([[2, 3, 1, 5], [7, 3, 4, 6], [8, 5, 3, 3]], dtype=float)
        np.testing.assert_array_equal(self.problem.cost_matrix(), expected)

    def test_cost_matrix_dtype(self) -> None:
        self.assertEqual(self.problem.cost_matrix().dtype, float)


if __name__ == "__main__":
    unittest.main()
