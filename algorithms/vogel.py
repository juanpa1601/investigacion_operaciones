from __future__ import annotations

import numpy as np

from algorithms.base import TransportAlgorithm
from models.transport_problem import (
    AllocationStep,
    SolutionResult,
    TransportProblem
)


class VogelAlgorithm(TransportAlgorithm):
    """Implementación del Método de Aproximación de Vogel (VAM).

    Construye la solución básica factible inicial usando penalizaciones para
    seleccionar en qué fila o columna asignar primero. La penalización de una
    fila o columna es la diferencia entre el primer y segundo menor costo activo,
    lo que refleja el costo de oportunidad de no usar la celda más barata.
    Produce habitualmente la solución inicial de menor costo entre los tres métodos.
    """

    @property
    def name(self) -> str:
        """Retorna el nombre del método."""
        return "Aproximación de Vogel"

    def _row_penalty(
        self,
        costs: np.ndarray,
        row: int,
        col_done: list[bool]
    ) -> tuple[float, int]:
        """Calcula la penalización de una fila activa.

        Ordena los costos disponibles en la fila y retorna la diferencia entre el
        segundo y el primer menor costo, junto con el índice de la columna del mínimo.
        Si solo hay un costo activo, la penalización es ese costo. Retorna (-1, -1)
        si la fila no tiene columnas activas disponibles.
        """
        active_costs: list[tuple[float, int]] = [
            (costs[row][j], j) for j in range(costs.shape[1]) if not col_done[j]
        ]
        if not active_costs:
            return -1.0, -1
        active_costs.sort()
        best_j = active_costs[0][1]
        if len(active_costs) == 1:
            return active_costs[0][0], best_j
        return active_costs[1][0] - active_costs[0][0], best_j

    def _col_penalty(
        self,
        costs: np.ndarray,
        col: int,
        row_done: list[bool]
    ) -> tuple[float, int]:
        """Calcula la penalización de una columna activa.

        Ordena los costos disponibles en la columna y retorna la diferencia entre el
        segundo y el primer menor costo, junto con el índice de la fila del mínimo.
        Si solo hay un costo activo, la penalización es ese costo. Retorna (-1, -1)
        si la columna no tiene filas activas disponibles.
        """
        active_costs: list[tuple[float, int]] = [
            (costs[i][col], i) for i in range(costs.shape[0]) if not row_done[i]
        ]
        if not active_costs:
            return -1.0, -1
        active_costs.sort()
        best_i = active_costs[0][1]
        if len(active_costs) == 1:
            return active_costs[0][0], best_i
        return active_costs[1][0] - active_costs[0][0], best_i

    def solve(
        self,
        problem: TransportProblem
    ) -> SolutionResult:
        """Aplica el Método de Aproximación de Vogel al problema recibido.

        En cada iteración calcula las penalizaciones de todas las filas y columnas
        activas, selecciona la de mayor penalización (con desempate por menor costo
        mínimo y luego por menor índice), y asigna el máximo posible en la celda de
        menor costo de esa fila o columna. Maneja degeneración conservando m+n-1
        celdas básicas cuando oferta y demanda se agotan simultáneamente.
        """
        m, n = problem.num_sources, problem.num_destinations
        costs: np.ndarray = problem.cost_matrix()
        allocation: np.ndarray = np.zeros((m, n), dtype=float)
        supply_rem: list[float] = list(problem.supply)
        demand_rem: list[float] = list(problem.demand)
        row_done: list[bool] = [False] * m
        col_done: list[bool] = [False] * n
        steps: list[AllocationStep] = []
        step_num: int = 1

        while not all(row_done) and not all(col_done):
            row_pens: list[tuple[float, int, int]] = []
            for i in range(m):
                if row_done[i]:
                    continue
                pen, best_j = self._row_penalty(costs, i, col_done)
                if best_j != -1:
                    row_pens.append((pen, best_j, i))

            col_pens: list[tuple[float, int, int]] = []
            for j in range(n):
                if col_done[j]:
                    continue
                pen, best_i = self._col_penalty(costs, j, row_done)
                if best_i != -1:
                    col_pens.append((pen, best_i, j))

            if not row_pens and not col_pens:
                break

            best_row_pen = max(row_pens, key=lambda x: x[0]) if row_pens else None
            best_col_pen = max(col_pens, key=lambda x: x[0]) if col_pens else None

            use_row: bool
            if best_row_pen is None:
                use_row = False
            elif best_col_pen is None:
                use_row = True
            elif best_row_pen[0] > best_col_pen[0]:
                use_row = True
            elif best_col_pen[0] > best_row_pen[0]:
                use_row = False
            else:
                row_min_cost = costs[best_row_pen[2]][best_row_pen[1]]
                col_min_cost = costs[best_col_pen[1]][best_col_pen[2]]
                use_row = row_min_cost <= col_min_cost

            if use_row:
                pen_val, j, i = best_row_pen  # type: ignore[misc]
                label = f"fila {i+1}"
            else:
                pen_val, i, j = best_col_pen  # type: ignore[misc]
                label = f"col {j+1}"

            amount = min(supply_rem[i], demand_rem[j])
            allocation[i][j] += amount
            steps.append(AllocationStep(
                step_num, i, j, amount,
                f"Máx. penalización {label}={pen_val:.4g}: "
                f"c({i+1},{j+1})={costs[i][j]:.4g}, "
                f"asignar min({supply_rem[i]:.4g},{demand_rem[j]:.4g})={amount:.4g}"
            ))
            step_num += 1
            supply_rem[i] -= amount
            demand_rem[j] -= amount

            both_zero = supply_rem[i] < 1e-9 and demand_rem[j] < 1e-9
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
