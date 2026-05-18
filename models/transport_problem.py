from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class AllocationStep:
    """Representa una asignación individual realizada durante la ejecución de un algoritmo.

    Almacena el número de paso, los índices de fila y columna de la celda asignada,
    la cantidad transportada y una descripción textual del criterio de selección.
    """

    step_number: int
    source: int
    destination: int
    amount: float
    reason: str


@dataclass
class SolutionResult:
    """Contiene el resultado completo de aplicar un algoritmo al problema de transporte.

    Incluye la matriz de asignación, la lista de pasos con trazabilidad, el costo total
    calculado y metadatos sobre degeneración y balanceo del problema.
    """

    method_name: str
    allocation_matrix: np.ndarray
    steps: list[AllocationStep]
    total_cost: float
    is_degenerate: bool
    is_balanced: bool = True
    dummy_added: str | None = None


@dataclass
class TransportProblem:
    """Modela un problema de transporte con m fuentes y n destinos.

    Almacena los vectores de oferta y demanda, la matriz de costos unitarios de
    transporte y las etiquetas descriptivas de filas y columnas. No contiene
    lógica de resolución ni de balanceo.
    """

    supply: list[float]
    demand: list[float]
    costs: list[list[float]]
    source_labels: list[str]
    destination_labels: list[str]

    @property
    def num_sources(self) -> int:
        """Retorna el número de fuentes (filas) del problema."""
        return len(self.supply)

    @property
    def num_destinations(self) -> int:
        """Retorna el número de destinos (columnas) del problema."""
        return len(self.demand)

    @property
    def total_supply(self) -> float:
        """Retorna la suma total de la oferta disponible."""
        return sum(self.supply)

    @property
    def total_demand(self) -> float:
        """Retorna la suma total de la demanda requerida."""
        return sum(self.demand)

    @property
    def is_balanced(self) -> bool:
        """Retorna True si la oferta total es igual a la demanda total (tolerancia 1e-9)."""
        return abs(self.total_supply - self.total_demand) < 1e-9

    def cost_matrix(self) -> np.ndarray:
        """Convierte la lista de listas de costos en un arreglo NumPy de tipo float."""
        return np.array(self.costs, dtype=float)
