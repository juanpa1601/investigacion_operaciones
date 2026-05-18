from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from models.transport_problem import (
    SolutionResult, 
    TransportProblem
)
from services.solver_service import SolverService
from ui.input_panel import InputPanel
from ui.results_panel import ResultsPanel
from ui.steps_panel import StepsPanel

class TransportApp:
    """Ventana principal de la aplicación de Problema de Transporte.

    Coordina el panel de entrada (InputPanel), el panel de comparación (ResultsPanel)
    y un panel de pasos por cada algoritmo (StepsPanel), organizados en un
    PanedWindow redimensionable con pestañas en el lado derecho. Recibe un
    SolverService ya configurado con los algoritmos a ejecutar.
    """

    def __init__(
        self, 
        root: tk.Tk, 
        solver: SolverService
    ) -> None:
        """Configura la ventana raíz y construye todos los paneles de la interfaz."""
        self._root = root
        self._solver = solver
        self._results: list[SolutionResult] = []

        root.title("Problema de Transporte — Métodos de Solución Básica Factible")
        root.minsize(900, 600)

        try:
            style = ttk.Style()
            style.theme_use("vista")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self) -> None:
        """Construye la estructura visual: PanedWindow, InputPanel, Notebook y barra de estado."""
        paned = ttk.PanedWindow(self._root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=4, pady=4)

        left_frame = ttk.Frame(paned, padding=4)
        paned.add(left_frame, weight=1)

        ttk.Label(
            left_frame,
            text="Datos del Problema",
            font=("", 12, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        self._input_panel = InputPanel(
            left_frame, on_solve=self._on_solve, on_clear=self._on_clear
        )
        self._input_panel.pack(fill="both", expand=True)

        right_frame = ttk.Frame(paned, padding=4)
        paned.add(right_frame, weight=3)

        self._notebook = ttk.Notebook(right_frame)
        self._notebook.pack(fill="both", expand=True)

        self._results_panel = ResultsPanel(self._notebook)
        self._notebook.add(self._results_panel, text="  Comparación  ")

        self._steps_panels: list[StepsPanel] = []
        for name in self._solver.algorithm_names:
            sp = StepsPanel(self._notebook, name)
            self._notebook.add(sp, text=f"  {name}  ")
            self._steps_panels.append(sp)

        self._status_var = tk.StringVar(value="Ingrese los datos y presione 'Resolver'.")
        ttk.Label(
            self._root,
            textvariable=self._status_var,
            relief="sunken",
            anchor="w",
            padding=(4, 2),
        ).pack(side="bottom", fill="x")

    def _on_clear(self) -> None:
        """Limpia todos los paneles de resultados y restablece la barra de estado."""
        self._results_panel.clear()
        for sp in self._steps_panels:
            sp.clear()
        self._status_var.set("Ingrese los datos y presione 'Resolver'.")

    def _on_solve(
        self, 
        problem: TransportProblem
    ) -> None:
        """Resuelve el problema con todos los algoritmos y actualiza los paneles de resultados.

        Invoca SolverService.solve_all, distribuye los resultados a cada panel y
        muestra en la barra de estado el método con menor costo total.
        """
        try:
            results = self._solver.solve_all(problem)
            self._results = results
            self._results_panel.update_results(results)
            for sp, result in zip(self._steps_panels, results):
                from utils.balance_helper import BalanceHelper
                balanced, _ = BalanceHelper.balance(problem)
                sp.update(result, balanced)
            min_cost = min(r.total_cost for r in results)
            best = next(r.method_name for r in results if abs(r.total_cost - min_cost) < 1e-6)
            self._status_var.set(
                f"Resuelto correctamente.  Mejor método: {best}  (costo = {min_cost:,.2f})"
            )
        except Exception as exc:
            self._status_var.set(f"Error al resolver: {exc}")

    def mainloop(self) -> None:
        """Inicia el bucle principal de eventos de tkinter."""
        self._root.mainloop()
