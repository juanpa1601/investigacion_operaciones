from __future__ import annotations

import numpy as np

from algorithms.base import TransportAlgorithm
from models.transport_problem import (
    AllocationStep,
    SolutionResult,
    TransportProblem
)


class NorthwestCornerAlgorithm(TransportAlgorithm):
    """Implementación del Método de la Esquina Noroeste.

    Construye la solución básica factible inicial comenzando siempre en la celda
    superior izquierda (esquina noroeste) y avanzando hacia la esquina inferior
    derecha. En cada paso asigna el máximo posible según oferta y demanda
    restantes, sin considerar los costos unitarios.
    """

    @property
    def name(self) -> str:
        """Retorna el nombre del método."""
        return "Esquina Noroeste"

    def solve(
        self,
        problem: TransportProblem
    ) -> SolutionResult:
        """Aplica el Método de la Esquina Noroeste al problema recibido.

        Recorre la matriz desde la celda (0,0) asignando min(oferta_i, demanda_j)
        en cada iteración. Al agotar una fila avanza i; al agotar una columna avanza j.
        Si ambos se agotan simultáneamente (degeneración), avanza solo i para conservar
        m+n-1 celdas básicas.
        """
        m, n = problem.num_sources, problem.num_destinations
        costs: np.ndarray = problem.cost_matrix()
        allocation: np.ndarray = np.zeros(
            (m, n),
            dtype=float
        )
        supply_rem: list[float] = list(problem.supply)
        demand_rem: list[float] = list(problem.demand)
        steps: list[AllocationStep] = []
        step_num: int = 1
        i, j = 0, 0

        while i < m and j < n:
            amount: float = min(supply_rem[i], demand_rem[j])
            allocation[i][j] = amount
            steps.append(AllocationStep(
                step_num, i, j, amount,
                f"Esquina ({i+1},{j+1}): min({supply_rem[i]:.4g}, {demand_rem[j]:.4g}) = {amount:.4g}"
            ))
            step_num += 1
            supply_rem[i] -= amount
            demand_rem[j] -= amount

            if supply_rem[i] < 1e-9 and demand_rem[j] < 1e-9:
                supply_rem[i] = 0.0
                demand_rem[j] = 0.0
                i += 1
                if i < m and j + 1 < n:
                    j += 1
                    if i < m and j < n and supply_rem[i] < 1e-9:
                        pass
            elif supply_rem[i] < 1e-9:
                supply_rem[i] = 0.0
                i += 1
            else:
                demand_rem[j] = 0.0
                j += 1

        total_cost: float = self._compute_total_cost(allocation, costs)
        degenerate: bool = self._is_degenerate(allocation)

        return SolutionResult(
            method_name=self.name,
            allocation_matrix=allocation,
            steps=steps,
            total_cost=total_cost,
            is_degenerate=degenerate
        )
