from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from models.transport_problem import SolutionResult

class ResultsPanel(ttk.Frame):
    """Panel de comparación tabular de los resultados de los tres métodos.

    Muestra un Treeview con una fila por algoritmo, incluyendo el costo total,
    el número de celdas básicas asignadas, si la solución es degenerada y si se
    añadió una fila o columna ficticia. Resalta en verde el método con menor costo.
    """

    _COLUMNS = ("method", "cost", "allocations", "degenerate", "dummy")
    _HEADERS = ("Método", "Costo Total", "Asignaciones", "Degenerado", "Ficticia")
    _WIDTHS = (180, 110, 110, 90, 90)

    def __init__(
        self, 
        parent: tk.Widget
    ) -> None:
        """Construye el Treeview de comparación y la etiqueta de resumen inferior."""
        super().__init__(parent, padding=8)

        ttk.Label(self, text="Comparación de Métodos", font=("", 11, "bold")).pack(anchor="w")

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, pady=(6, 0))

        self._tree = ttk.Treeview(
            frame,
            columns=self._COLUMNS,
            show="headings",
            height=6,
        )
        for col, header, width in zip(self._COLUMNS, self._HEADERS, self._WIDTHS):
            self._tree.heading(col, text=header)
            self._tree.column(col, width=width, anchor="center")

        self._tree.tag_configure("best", foreground="#007700", font=("", 9, "bold"))
        self._tree.tag_configure("normal", foreground="#000000")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._summary_var = tk.StringVar()
        ttk.Label(self, textvariable=self._summary_var, font=("", 9), foreground="#555").pack(
            anchor="w", pady=(6, 0)
        )

    def clear(self) -> None:
        """Elimina todas las filas del Treeview y limpia el texto de resumen."""
        self._tree.delete(*self._tree.get_children())
        self._summary_var.set("")

    def update_results(
        self, 
        results: list[SolutionResult]
    ) -> None:
        """Repuebla la tabla con los resultados proporcionados y resalta el mejor método.

        Identifica el resultado de menor costo total y le aplica el tag 'best',
        que lo muestra en verde y negrita. Actualiza también el texto de resumen
        con información sobre balanceo y filas o columnas ficticias añadidas.
        """
        self._tree.delete(*self._tree.get_children())
        if not results:
            return

        min_cost = min(r.total_cost for r in results)

        for r in results:
            tag = "best" if abs(r.total_cost - min_cost) < 1e-6 else "normal"
            basic_cells = int((r.allocation_matrix > 0).sum())
            dummy_text = {"row": "Fila F*", "column": "Col D*"}.get(r.dummy_added or "", "No")
            self._tree.insert(
                "",
                "end",
                values=(
                    r.method_name,
                    f"{r.total_cost:,.2f}",
                    str(basic_cells),
                    "Sí" if r.is_degenerate else "No",
                    dummy_text,
                ),
                tags=(tag,),
            )

        balanced = results[0].is_balanced
        dummy = results[0].dummy_added
        status_parts = ["Problema balanceado" if balanced else "Problema desbalanceado"]
        if dummy == "column":
            status_parts.append("se añadió columna ficticia D*")
        elif dummy == "row":
            status_parts.append("se añadió fila ficticia F*")
        self._summary_var.set(" · ".join(status_parts))
