from __future__ import annotations

import unittest

import numpy as np

from algorithms.minimum_cost import MinimumCostAlgorithm
from algorithms.northwest_corner import NorthwestCornerAlgorithm
from algorithms.vogel import VogelAlgorithm
from models.transport_problem import TransportProblem
from utils.balance_helper import BalanceHelper

# Ejemplo de referencia 3×4 balanceado.
# Costos, oferta y demanda conocidos; resultados verificados contra ejecución real.
_COSTS_3X4 = [[2, 3, 1, 5], [7, 3, 4, 6], [8, 5, 3, 3]]
_SUPPLY_3X4 = [30.0, 40.0, 50.0]
_DEMAND_3X4 = [20.0, 30.0, 40.0, 30.0]


def _problem_3x4() -> TransportProblem:
    return TransportProblem(
        supply=list(_SUPPLY_3X4),
        demand=list(_DEMAND_3X4),
        costs=[list(r) for r in _COSTS_3X4],
        source_labels=["F1", "F2", "F3"],
        destination_labels=["D1", "D2", "D3", "D4"],
    )


def _problem_2x2_degenerate() -> TransportProblem:
    """Problema 2×2 donde NW agota oferta y demanda simultáneamente en el paso 1."""
    return TransportProblem(
        supply=[10.0, 20.0],
        demand=[10.0, 20.0],
        costs=[[1, 2], [3, 4]],
        source_labels=["F1", "F2"],
        destination_labels=["D1", "D2"],
    )


def _balanced(problem: TransportProblem) -> TransportProblem:
    balanced, _ = BalanceHelper.balance(problem)
    return balanced


class _AlgorithmTestBase:
    """Mixin con comprobaciones estructurales válidas para cualquier algoritmo.

    No hereda de TestCase para que unittest no lo recoja como suite independiente.
    Las subclases heredan de (_AlgorithmTestBase, unittest.TestCase) en ese orden.
    """

    algo_class = None  # subclases lo asignan

    def setUp(self) -> None:
        self.algo = self.algo_class()
        self.problem = _problem_3x4()
        self.result = self.algo.solve(_balanced(self.problem))

    def test_allocation_shape(self) -> None:
        self.assertEqual(self.result.allocation_matrix.shape, (3, 4))

    def test_allocation_non_negative(self) -> None:
        self.assertTrue((self.result.allocation_matrix >= 0).all())

    def test_supply_constraints_satisfied(self) -> None:
        row_sums = self.result.allocation_matrix.sum(axis=1)
        np.testing.assert_allclose(row_sums, _SUPPLY_3X4, atol=1e-9)

    def test_demand_constraints_satisfied(self) -> None:
        col_sums = self.result.allocation_matrix.sum(axis=0)
        np.testing.assert_allclose(col_sums, _DEMAND_3X4, atol=1e-9)

    def test_total_cost_positive(self) -> None:
        self.assertGreater(self.result.total_cost, 0)

    def test_steps_count_equals_basic_cells(self) -> None:
        # En un problema no degenerado m+n-1 = 3+4-1 = 6 pasos
        self.assertEqual(len(self.result.steps), 6)

    def test_steps_numbered_sequentially(self) -> None:
        numbers = [s.step_number for s in self.result.steps]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_step_amounts_non_negative(self) -> None:
        for step in self.result.steps:
            self.assertGreaterEqual(step.amount, 0)

    def test_step_reason_non_empty(self) -> None:
        for step in self.result.steps:
            self.assertTrue(step.reason.strip())

    def test_not_degenerate_on_standard_case(self) -> None:
        self.assertFalse(self.result.is_degenerate)


class TestNorthwestCorner(_AlgorithmTestBase, unittest.TestCase):

    algo_class = NorthwestCornerAlgorithm

    def test_method_name(self) -> None:
        self.assertEqual(self.algo.name, "Esquina Noroeste")

    def test_total_cost(self) -> None:
        self.assertAlmostEqual(self.result.total_cost, 360.0)

    def test_allocation_matrix(self) -> None:
        expected = np.array([
            [20, 10,  0,  0],
            [ 0, 20, 20,  0],
            [ 0,  0, 20, 30],
        ], dtype=float)
        np.testing.assert_array_almost_equal(self.result.allocation_matrix, expected)

    def test_degenerate_on_simultaneous_exhaustion(self) -> None:
        result = self.algo.solve(_balanced(_problem_2x2_degenerate()))
        self.assertTrue(result.is_degenerate)

    def test_degenerate_cost(self) -> None:
        result = self.algo.solve(_balanced(_problem_2x2_degenerate()))
        self.assertAlmostEqual(result.total_cost, 90.0)


class TestMinimumCost(_AlgorithmTestBase, unittest.TestCase):

    algo_class = MinimumCostAlgorithm

    def test_method_name(self) -> None:
        self.assertEqual(self.algo.name, "Costo Mínimo")

    def test_total_cost(self) -> None:
        self.assertAlmostEqual(self.result.total_cost, 390.0)

    def test_allocation_matrix(self) -> None:
        expected = np.array([
            [ 0,  0, 30,  0],
            [10, 30,  0,  0],
            [10,  0, 10, 30],
        ], dtype=float)
        np.testing.assert_array_almost_equal(self.result.allocation_matrix, expected)

    def test_degenerate_on_simultaneous_exhaustion(self) -> None:
        result = self.algo.solve(_balanced(_problem_2x2_degenerate()))
        self.assertTrue(result.is_degenerate)


class TestVogel(_AlgorithmTestBase, unittest.TestCase):

    algo_class = VogelAlgorithm

    def test_method_name(self) -> None:
        self.assertEqual(self.algo.name, "Aproximación de Vogel")

    def test_total_cost(self) -> None:
        self.assertAlmostEqual(self.result.total_cost, 330.0)

    def test_allocation_matrix(self) -> None:
        expected = np.array([
            [20,  0, 10,  0],
            [ 0, 30, 10,  0],
            [ 0,  0, 20, 30],
        ], dtype=float)
        np.testing.assert_array_almost_equal(self.result.allocation_matrix, expected)

    def test_vogel_best_or_tied_vs_northwest(self) -> None:
        nw_cost = NorthwestCornerAlgorithm().solve(_balanced(self.problem)).total_cost
        self.assertLessEqual(self.result.total_cost, nw_cost)

    def test_vogel_best_or_tied_vs_minimum_cost(self) -> None:
        mc_cost = MinimumCostAlgorithm().solve(_balanced(self.problem)).total_cost
        self.assertLessEqual(self.result.total_cost, mc_cost)

    def test_degenerate_on_simultaneous_exhaustion(self) -> None:
        result = self.algo.solve(_balanced(_problem_2x2_degenerate()))
        self.assertTrue(result.is_degenerate)


if __name__ == "__main__":
    unittest.main()
