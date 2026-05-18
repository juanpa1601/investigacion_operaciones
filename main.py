from __future__ import annotations

import tkinter as tk

from algorithms.minimum_cost import MinimumCostAlgorithm
from algorithms.northwest_corner import NorthwestCornerAlgorithm
from algorithms.vogel import VogelAlgorithm
from services.solver_service import SolverService
from ui.app import TransportApp


def build_solver() -> SolverService:
    """Crea y retorna un SolverService con los tres algoritmos de transporte configurados.

    Aplica inyección de dependencias: las clases concretas de algoritmos se instancian
    aquí y se pasan al servicio, que solo conoce la abstracción TransportAlgorithm.
    """
    return SolverService(algorithms=[
        NorthwestCornerAlgorithm(),
        MinimumCostAlgorithm(),
        VogelAlgorithm(),
    ])


def main() -> None:
    """Punto de entrada de la aplicación: crea el solver, la ventana raíz e inicia el bucle."""
    solver = build_solver()
    root = tk.Tk()
    app = TransportApp(root, solver)
    app.mainloop()


if __name__ == "__main__":
    main()
