from __future__ import annotations

import unittest

from models.transport_problem import TransportProblem
from utils.balance_helper import BalanceHelper


def _make_problem(supply: list[float], demand: list[float]) -> TransportProblem:
    m, n = len(supply), len(demand)
    return TransportProblem(
        supply=supply,
        demand=demand,
        costs=[[float(i + j + 1) for j in range(n)] for i in range(m)],
        source_labels=[f"F{i+1}" for i in range(m)],
        destination_labels=[f"D{j+1}" for j in range(n)],
    )


class TestBalanceHelperBalanced(unittest.TestCase):

    def setUp(self) -> None:
        self.problem = _make_problem([30.0, 40.0], [20.0, 50.0])
        self.balanced, self.dummy = BalanceHelper.balance(self.problem)

    def test_dummy_is_none(self) -> None:
        self.assertIsNone(self.dummy)

    def test_dimensions_unchanged(self) -> None:
        self.assertEqual(self.balanced.num_sources, 2)
        self.assertEqual(self.balanced.num_destinations, 2)

    def test_supply_unchanged(self) -> None:
        self.assertEqual(self.balanced.supply, [30.0, 40.0])

    def test_demand_unchanged(self) -> None:
        self.assertEqual(self.balanced.demand, [20.0, 50.0])


class TestBalanceHelperSupplyExceedsDemand(unittest.TestCase):

    def setUp(self) -> None:
        self.problem = _make_problem([50.0, 40.0], [30.0, 20.0])
        self.balanced, self.dummy = BalanceHelper.balance(self.problem)

    def test_dummy_is_column(self) -> None:
        self.assertEqual(self.dummy, "column")

    def test_dummy_column_appended_to_demand(self) -> None:
        self.assertEqual(len(self.balanced.demand), 3)
        self.assertAlmostEqual(self.balanced.demand[-1], 40.0)

    def test_dummy_column_label(self) -> None:
        self.assertEqual(self.balanced.destination_labels[-1], "D*")

    def test_dummy_column_costs_are_zero(self) -> None:
        for row in self.balanced.costs:
            self.assertAlmostEqual(row[-1], 0.0)

    def test_result_is_balanced(self) -> None:
        self.assertTrue(self.balanced.is_balanced)

    def test_original_not_mutated(self) -> None:
        self.assertEqual(len(self.problem.demand), 2)
        self.assertEqual(len(self.problem.destination_labels), 2)


class TestBalanceHelperDemandExceedsSupply(unittest.TestCase):

    def setUp(self) -> None:
        self.problem = _make_problem([30.0, 20.0], [50.0, 40.0])
        self.balanced, self.dummy = BalanceHelper.balance(self.problem)

    def test_dummy_is_row(self) -> None:
        self.assertEqual(self.dummy, "row")

    def test_dummy_row_appended_to_supply(self) -> None:
        self.assertEqual(len(self.balanced.supply), 3)
        self.assertAlmostEqual(self.balanced.supply[-1], 40.0)

    def test_dummy_row_label(self) -> None:
        self.assertEqual(self.balanced.source_labels[-1], "F*")

    def test_dummy_row_costs_are_zero(self) -> None:
        for cost in self.balanced.costs[-1]:
            self.assertAlmostEqual(cost, 0.0)

    def test_result_is_balanced(self) -> None:
        self.assertTrue(self.balanced.is_balanced)

    def test_original_not_mutated(self) -> None:
        self.assertEqual(len(self.problem.supply), 2)
        self.assertEqual(len(self.problem.source_labels), 2)


if __name__ == "__main__":
    unittest.main()
