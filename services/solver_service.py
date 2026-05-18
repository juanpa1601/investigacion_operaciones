from __future__ import annotations

from algorithms.base import TransportAlgorithm
from models.transport_problem import (
    SolutionResult,
    TransportProblem
)
from utils.balance_helper import BalanceHelper


class SolverService:
    """Orquestador que aplica todos los algoritmos configurados a un problema de transporte.

    Depende únicamente de la abstracción TransportAlgorithm (principio DIP). Las
    implementaciones concretas se inyectan en el constructor desde main.py, por lo
    que este servicio no importa ninguna clase de algoritmo directamente. Antes de
    resolver, delega el balanceo del problema a BalanceHelper.
    """

    def __init__(
        self,
        algorithms: list[TransportAlgorithm]
    ) -> None:
        """Inicializa el servicio con la lista de algoritmos a aplicar.

        Los algoritmos se ejecutarán en el mismo orden en que se proporcionen,
        y los resultados se retornarán en ese mismo orden.
        """
        self._algorithms = algorithms

    def solve_all(
        self,
        problem: TransportProblem
    ) -> list[SolutionResult]:
        """Balancea el problema y aplica todos los algoritmos configurados.

        Retorna una lista de SolutionResult en el mismo orden que la lista de
        algoritmos. Cada resultado incluye metadatos sobre si el problema original
        estaba balanceado y qué tipo de fila o columna ficticia se añadió.
        """
        balanced, dummy = BalanceHelper.balance(problem)
        results: list[SolutionResult] = []
        for algo in self._algorithms:
            result = algo.solve(balanced)
            result.is_balanced = problem.is_balanced
            result.dummy_added = dummy
            results.append(result)
        return results

    @property
    def algorithm_names(self) -> list[str]:
        """Retorna la lista de nombres de los algoritmos configurados, en orden."""
        return [a.name for a in self._algorithms]
