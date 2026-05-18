from __future__ import annotations

import numpy as np

from algorithms.base import TransportAlgorithm
from models.transport_problem import (
    AllocationStep,
    SolutionResult,
    TransportProblem
)


class MinimumCostAlgorithm(TransportAlgorithm):
    """Implementación del Método del Costo Mínimo.

    Construye la solución básica factible inicial eligiendo en cada iteración la
    celda activa con el menor costo unitario de transporte. Asigna el máximo
    posible en esa celda y marca la fila o columna como agotada. Produce
    generalmente soluciones de menor costo que el Método de la Esquina Noroeste,
    aunque no garantiza el óptimo global.
    """

    @property
    def name(self) -> str:
        """Retorna el nombre del método."""
        return "Costo Mínimo"

    def solve(
        self,
        problem: TransportProblem
    ) -> SolutionResult:
        """Aplica el Método del Costo Mínimo al problema recibido.

        En cada iteración busca la celda (i, j) no agotada con menor costo unitario,
        asigna min(oferta_i, demanda_j) y actualiza los remanentes. Cuando oferta y
        demanda se agotan simultáneamente (degeneración), solo marca la fila como
        agotada para conservar m+n-1 celdas básicas.
        """
        m, n = problem.num_sources, problem.num_destinations
        costs: np.ndarray = problem.cost_matrix()
        allocation: np.ndarray = np.zeros(
            (m, n),
            dtype=float
        )
        supply_rem: list[float] = list(problem.supply)
        demand_rem: list[float] = list(problem.demand)
        row_done: list[bool] = [False] * m
        col_done: list[bool] = [False] * n
        steps: list[AllocationStep] = []
        step_num: int = 1

        while True:
            best_cost: float = float("inf")
            best_i: int = -1
            best_j: int = -1
            for ii in range(m):
                if row_done[ii]:
                    continue
                for jj in range(n):
                    if col_done[jj]:
                        continue
                    if costs[ii][jj] < best_cost:
                        best_cost = costs[ii][jj]
                        best_i, best_j = ii, jj

            if best_i == -1:
                break

            i, j = best_i, best_j
            amount: float = min(supply_rem[i], demand_rem[j])
            allocation[i][j] += amount
            steps.append(AllocationStep(
                step_num, i, j, amount,
                f"Costo mínimo c({i+1},{j+1})={best_cost:.4g}: "
                f"asignar min({supply_rem[i]:.4g},{demand_rem[j]:.4g})={amount:.4g}"
            ))
            step_num += 1
            supply_rem[i] -= amount
            demand_rem[j] -= amount

            both_zero: bool = supply_rem[i] < 1e-9 and demand_rem[j] < 1e-9
            if supply_rem[i] < 1e-9:
                supply_rem[i] = 0.0
                row_done[i] = True
            if demand_rem[j] < 1e-9:
                demand_rem[j] = 0.0
                col_done[j] = True

            if both_zero and not all(row_done) and not all(col_done):
                col_done[j] = False

        total_cost: float = self._compute_total_cost(
            allocation,
            costs
        )
        degenerate: bool = self._is_degenerate(allocation)

        return SolutionResult(
            method_name=self.name,
            allocation_matrix=allocation,
            steps=steps,
            total_cost=total_cost,
            is_degenerate=degenerate
        )
