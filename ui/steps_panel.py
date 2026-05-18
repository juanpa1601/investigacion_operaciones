from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from models.transport_problem import (
    SolutionResult,
    TransportProblem
)


class StepsPanel(ttk.Frame):
    """Panel de trazabilidad de un método de transporte específico.

    Muestra dos secciones: la matriz de asignación final con las celdas asignadas
    resaltadas en verde y tooltips con el costo unitario al pasar el cursor, y
    una tabla de pasos enumerados que describen el criterio de selección de cada
    celda durante la ejecución del algoritmo.
    """

    def __init__(
        self,
        parent: tk.Widget,
        method_name: str
    ) -> None:
        """Inicializa el panel con el nombre del método y construye la estructura visual."""
        super().__init__(parent, padding=8)
        self._method_name = method_name

        ttk.Label(self, text="Matriz de Asignación", font=("", 10, "bold")).pack(anchor="w")
        self._alloc_frame = ttk.Frame(self)
        self._alloc_frame.pack(fill="x", pady=(4, 8))

        ttk.Label(self, text="Trazabilidad Paso a Paso", font=("", 10, "bold")).pack(anchor="w")
        steps_frame = ttk.Frame(self)
        steps_frame.pack(fill="both", expand=True, pady=(4, 0))

        self._steps_tree = ttk.Treeview(
            steps_frame,
            columns=("step", "cell", "amount", "reason"),
            show="headings",
        )
        self._steps_tree.heading("step", text="#")
        self._steps_tree.heading("cell", text="Celda")
        self._steps_tree.heading("amount", text="Cantidad")
        self._steps_tree.heading("reason", text="Razón")
        self._steps_tree.column("step", width=40, anchor="center")
        self._steps_tree.column("cell", width=80, anchor="center")
        self._steps_tree.column("amount", width=90, anchor="center")
        self._steps_tree.column("reason", width=500, anchor="w")

        vsb = ttk.Scrollbar(steps_frame, orient="vertical", command=self._steps_tree.yview)
        self._steps_tree.configure(yscrollcommand=vsb.set)
        self._steps_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._cost_var = tk.StringVar()
        ttk.Label(self, textvariable=self._cost_var, font=("", 10, "bold"), foreground="#003399").pack(
            anchor="e", pady=(6, 0)
        )

    def clear(self) -> None:
        """Elimina la matriz de asignación, limpia la tabla de pasos y borra el costo total."""
        for widget in self._alloc_frame.winfo_children():
            widget.destroy()
        self._steps_tree.delete(*self._steps_tree.get_children())
        self._cost_var.set("")

    def update(
        self,
        result: SolutionResult,
        problem: TransportProblem
    ) -> None:
        """Actualiza ambas secciones con el resultado del algoritmo y el problema balanceado."""
        self._render_allocation(result, problem)
        self._render_steps(result)
        self._cost_var.set(f"Costo Total: {result.total_cost:,.2f}")

    def _render_allocation(
        self,
        result: SolutionResult,
        problem: TransportProblem
    ) -> None:
        """Reconstruye la tabla de asignación con etiquetas de fila y columna.

        Las celdas con asignación positiva se muestran en verde con el valor en negrita.
        Al pasar el cursor sobre una celda se muestra también el costo unitario (tooltip).
        La última columna muestra la oferta de cada fuente y la última fila la demanda
        de cada destino; la celda inferior derecha contiene el costo total.
        """
        for widget in self._alloc_frame.winfo_children():
            widget.destroy()

        alloc = result.allocation_matrix
        m, n = alloc.shape
        src_labels = problem.source_labels
        dst_labels = problem.destination_labels
        costs = problem.cost_matrix()

        header_kw = {"font": ("", 9, "bold"), "width": 9, "anchor": "center", "relief": "groove", "padding": 2}
        cell_kw = {"width": 9, "anchor": "center", "relief": "sunken", "padding": 2}

        ttk.Label(self._alloc_frame, text="", **header_kw).grid(row=0, column=0, padx=1, pady=1)
        for j, lbl in enumerate(dst_labels):
            ttk.Label(self._alloc_frame, text=lbl, **header_kw).grid(row=0, column=j+1, padx=1, pady=1)
        ttk.Label(self._alloc_frame, text="Oferta", **header_kw).grid(row=0, column=n+1, padx=(4, 1), pady=1)

        for i in range(m):
            ttk.Label(self._alloc_frame, text=src_labels[i], **header_kw).grid(
                row=i+1, column=0, padx=1, pady=1
            )
            for j in range(n):
                val = alloc[i][j]
                cost_val = costs[i][j]
                text = f"{val:.4g}" if val > 0 else "—"
                bg = "#d4edda" if val > 0 else "#f8f9fa"
                lbl_widget = tk.Label(
                    self._alloc_frame,
                    text=text,
                    width=9,
                    anchor="center",
                    relief="sunken",
                    bg=bg,
                    font=("", 9, "bold") if val > 0 else ("", 9),
                )
                lbl_widget.grid(row=i+1, column=j+1, padx=1, pady=1, sticky="nsew")
                lbl_widget.bind(
                    "<Enter>",
                    lambda e, c=cost_val, a=val: e.widget.config(
                        text=f"c={c:.4g}" if a == 0 else f"{a:.4g}\nc={c:.4g}"
                    ),
                )
                lbl_widget.bind(
                    "<Leave>",
                    lambda e, a=val: e.widget.config(text=f"{a:.4g}" if a > 0 else "—"),
                )
            supply_val = problem.supply[i]
            ttk.Label(self._alloc_frame, text=f"{supply_val:.4g}", **cell_kw).grid(
                row=i+1, column=n+1, padx=(4, 1), pady=1
            )

        ttk.Label(self._alloc_frame, text="Demanda", **header_kw).grid(
            row=m+1, column=0, padx=1, pady=(4, 1)
        )
        for j in range(n):
            ttk.Label(self._alloc_frame, text=f"{problem.demand[j]:.4g}", **cell_kw).grid(
                row=m+1, column=j+1, padx=1, pady=(4, 1)
            )
        ttk.Label(
            self._alloc_frame,
            text=f"{result.total_cost:.2f}",
            font=("", 9, "bold"),
            width=9, anchor="center", relief="groove", padding=2
        ).grid(row=m+1, column=n+1, padx=(4, 1), pady=(4, 1))

    def _render_steps(
        self,
        result: SolutionResult
    ) -> None:
        """Repuebla el Treeview de pasos con la trazabilidad del resultado."""
        self._steps_tree.delete(*self._steps_tree.get_children())
        for step in result.steps:
            self._steps_tree.insert(
                "",
                "end",
                values=(
                    step.step_number,
                    f"({step.source+1},{step.destination+1})",
                    f"{step.amount:.4g}",
                    step.reason,
                ),
            )
