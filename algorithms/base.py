from __future__ import annotations

from abc import (
    ABC,
    abstractmethod
)

import numpy as np

from models.transport_problem import (
    TransportProblem,
    SolutionResult
)


class TransportAlgorithm(ABC):
    """Contrato abstracto para todos los algoritmos de solución básica factible inicial.

    Define la interfaz que SolverService utiliza para invocar cualquier método de
    transporte sin depender de implementaciones concretas (principio DIP). Incluye
    métodos auxiliares compartidos por todas las subclases.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna el nombre legible del método de resolución."""
        ...

    @abstractmethod
    def solve(
        self,
        problem: TransportProblem
    ) -> SolutionResult:
        """Resuelve el problema de transporte y retorna la solución básica factible inicial.

        El problema recibido debe estar previamente balanceado. Retorna un
        SolutionResult con la matriz de asignación, los pasos de trazabilidad
        y el costo total calculado.
        """
        ...

    @staticmethod
    def _compute_total_cost(
        allocation: np.ndarray,
        costs: np.ndarray
    ) -> float:
        """Calcula el costo total multiplicando elemento a elemento asignación y costos."""
        return float(np.sum(allocation * costs))

    @staticmethod
    def _is_degenerate(allocation: np.ndarray) -> bool:
        """Determina si la solución es degenerada.

        Una solución es degenerada cuando el número de celdas básicas con asignación
        positiva es menor que m + n - 1, donde m y n son las dimensiones de la matriz.
        """
        m, n = allocation.shape
        return int(np.count_nonzero(allocation)) < m + n - 1
