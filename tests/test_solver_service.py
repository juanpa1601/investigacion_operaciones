from __future__ import annotations

import unittest

from algorithms.minimum_cost import MinimumCostAlgorithm
from algorithms.northwest_corner import NorthwestCornerAlgorithm
from algorithms.vogel import VogelAlgorithm
from models.transport_problem import TransportProblem
from services.solver_service import SolverService


def _make_solver() -> SolverService:
    return SolverService(algorithms=[
        NorthwestCornerAlgorithm(),
        MinimumCostAlgorithm(),
        VogelAlgorithm(),
    ])


def _balanced_problem() -> TransportProblem:
    return TransportProblem(
        supply=[30.0, 40.0, 50.0],
        demand=[20.0, 30.0, 40.0, 30.0],
        costs=[[2, 3, 1, 5], [7, 3, 4, 6], [8, 5, 3, 3]],
        source_labels=["F1", "F2", "F3"],
        destination_labels=["D1", "D2", "D3", "D4"],
    )


def _unbalanced_problem() -> TransportProblem:
    return TransportProblem(
        supply=[50.0, 40.0],
        demand=[30.0, 20.0],
        costs=[[1, 2], [3, 4]],
        source_labels=["F1", "F2"],
        destination_labels=["D1", "D2"],
    )


class TestSolverServiceStructure(unittest.TestCase):

    def setUp(self) -> None:
        self.solver = _make_solver()
        self.results = self.solver.solve_all(_balanced_problem())

    def test_returns_one_result_per_algorithm(self) -> None:
        self.assertEqual(len(self.results), 3)

    def test_result_names_in_order(self) -> None:
        names = [r.method_name for r in self.results]
        self.assertEqual(names, ["Esquina Noroeste", "Costo Mínimo", "Aproximación de Vogel"])

    def test_algorithm_names_property(self) -> None:
        self.assertEqual(
            self.solver.algorithm_names,
            ["Esquina Noroeste", "Costo Mínimo", "Aproximación de Vogel"],
        )

    def test_all_total_costs_positive(self) -> None:
        for r in self.results:
            self.assertGreater(r.total_cost, 0)


class TestSolverServiceBalancedMetadata(unittest.TestCase):

    def setUp(self) -> None:
        self.solver = _make_solver()
        self.results = self.solver.solve_all(_balanced_problem())

    def test_is_balanced_true_for_all(self) -> None:
        for r in self.results:
            self.assertTrue(r.is_balanced)

    def test_dummy_added_none_for_all(self) -> None:
        for r in self.results:
            self.assertIsNone(r.dummy_added)


class TestSolverServiceUnbalancedMetadata(unittest.TestCase):

    def setUp(self) -> None:
        self.solver = _make_solver()
        self.results = self.solver.solve_all(_unbalanced_problem())

    def test_is_balanced_false_for_all(self) -> None:
        for r in self.results:
            self.assertFalse(r.is_balanced)

    def test_dummy_added_column_for_all(self) -> None:
        for r in self.results:
            self.assertEqual(r.dummy_added, "column")

    def test_allocation_has_extra_column(self) -> None:
        for r in self.results:
            self.assertEqual(r.allocation_matrix.shape, (2, 3))


class TestSolverServiceWithSingleAlgorithm(unittest.TestCase):

    def test_single_algorithm_returns_one_result(self) -> None:
        solver = SolverService(algorithms=[NorthwestCornerAlgorithm()])
        results = solver.solve_all(_balanced_problem())
        self.assertEqual(len(results), 1)

    def test_empty_algorithm_list_returns_empty(self) -> None:
        solver = SolverService(algorithms=[])
        results = solver.solve_all(_balanced_problem())
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
