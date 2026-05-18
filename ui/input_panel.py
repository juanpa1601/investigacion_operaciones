from __future__ import annotations

import random
import tkinter as tk
from tkinter import (
    messagebox,
    ttk
)
from typing import Callable

from models.transport_problem import TransportProblem

class InputPanel(ttk.Frame):
    """Panel de entrada de datos con grilla dinámica m×n.

    Permite al usuario configurar las dimensiones del problema mediante Spinboxes
    y editar la matriz de costos, los vectores de oferta y demanda en campos de
    texto generados dinámicamente. Ofrece botones para resolver, cargar un ejemplo
    y limpiar todos los campos. Incluye auto-recalculo con debounce de 800 ms.
    """

    _MIN_DIM = 2
    _MAX_DIM = 8

    def __init__(
        self,
        parent: tk.Widget,
        on_solve: Callable[[TransportProblem], None],
        on_clear: Callable[[], None] | None = None
    ) -> None:
        """Inicializa el panel, construye los controles y la grilla inicial.

        on_solve se invoca con el TransportProblem leído cuando el usuario presiona
        Resolver o transcurren 800 ms tras el último cambio. on_clear se invoca al
        presionar Limpiar para notificar a otros paneles que deben vaciarse.
        """
        super().__init__(parent, padding=8)
        self._on_solve = on_solve
        self._on_clear = on_clear
        self._after_id: str | None = None

        self._num_sources_var = tk.IntVar(value=3)
        self._num_destinations_var = tk.IntVar(value=4)

        self._prev_costs: dict[tuple[int, int], str] = {}
        self._prev_supply: dict[int, str] = {}
        self._prev_demand: dict[int, str] = {}

        self._cost_entries: list[list[ttk.Entry]] = []
        self._supply_entries: list[ttk.Entry] = []
        self._demand_entries: list[ttk.Entry] = []

        self._build_controls()
        self._grid_frame = ttk.Frame(self)
        self._grid_frame.pack(fill="x", pady=(8, 0))
        self._rebuild_grid()
        self._build_instructions()

        self._num_sources_var.trace_add("write", self._on_dim_change)
        self._num_destinations_var.trace_add("write", self._on_dim_change)

    def _build_instructions(self) -> None:
        """Construye el panel de instrucciones de uso en el área inferior izquierda."""
        frame = ttk.LabelFrame(self, text="¿Cómo usar este programa?", padding=(10, 6))
        frame.pack(fill="both", expand=True, pady=(12, 0))

        steps = [
            ("1. Dimensiones",
             "Ajuste el número de Fuentes (m) y Destinos (n) con los selectores "
             "en la parte superior (mín. 2, máx. 8)."),
            ("2. Datos del problema",
             "Complete la matriz de costos unitarios (cᵢⱼ), los valores de "
             "Oferta por fila y los valores de Demanda por columna. "
             "Solo se aceptan números positivos; los costos pueden ser cero."),
            ("3. Resolver",
             "Presione 'Resolver' para calcular al instante, o simplemente edite "
             "cualquier celda: el sistema recalcula automáticamente 0.8 s después "
             "del último cambio."),
            ("4. Botones de ejemplo",
             "'Ejemplo' carga un caso 3×4 balanceado de referencia. "
             "'Aleatorio' genera costos y cantidades válidas para el tamaño "
             "actualmente seleccionado."),
            ("5. Resultados",
             "La pestaña 'Comparación' muestra los tres métodos lado a lado y "
             "resalta en verde el de menor costo. Cada pestaña de método presenta "
             "la matriz de asignación final y la trazabilidad paso a paso."),
            ("6. Problemas desbalanceados",
             "Si la oferta total ≠ demanda total, el sistema agrega "
             "automáticamente una fila o columna ficticia (F* / D*) con costo 0 "
             "para balancear; esto se indica en la columna 'Ficticia'."),
        ]

        for title, body in steps:
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill="x", pady=(0, 6))
            ttk.Label(
                row_frame, text=title, font=("", 9, "bold"), foreground="#003399"
            ).pack(anchor="w")
            ttk.Label(
                row_frame, text=body, wraplength=520, justify="left", font=("", 9)
            ).pack(anchor="w", padx=(8, 0))

    def _build_controls(self) -> None:
        """Construye la fila superior con Spinboxes de dimensión y los botones de acción."""
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x")

        ttk.Label(ctrl, text="Fuentes (m):").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(
            ctrl,
            from_=self._MIN_DIM,
            to=self._MAX_DIM,
            textvariable=self._num_sources_var,
            width=4,
            state="readonly",
        ).grid(row=0, column=1, padx=(4, 16))

        ttk.Label(ctrl, text="Destinos (n):").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(
            ctrl,
            from_=self._MIN_DIM,
            to=self._MAX_DIM,
            textvariable=self._num_destinations_var,
            width=4,
            state="readonly",
        ).grid(row=0, column=3, padx=(4, 16))

        ttk.Button(ctrl, text="Resolver", command=self._on_solve_clicked).grid(
            row=0, column=4, padx=8
        )
        ttk.Button(ctrl, text="Ejemplo", command=self._load_example).grid(
            row=0, column=5, padx=(0, 4)
        )
        ttk.Button(ctrl, text="Aleatorio", command=self._load_random_example).grid(
            row=0, column=6, padx=(0, 4)
        )
        ttk.Button(ctrl, text="Limpiar", command=self._clear_all).grid(
            row=0, column=7
        )

    def _on_dim_change(
        self, 
        *_: object
    ) -> None:
        """Guarda los valores actuales en caché y reconstruye la grilla al cambiar m o n."""
        self._save_cache()
        self._rebuild_grid()

    def _save_cache(self) -> None:
        """Almacena los valores actuales de todos los Entry antes de destruirlos."""
        for i, row in enumerate(self._cost_entries):
            for j, entry in enumerate(row):
                self._prev_costs[(i, j)] = entry.get()
        for i, entry in enumerate(self._supply_entries):
            self._prev_supply[i] = entry.get()
        for j, entry in enumerate(self._demand_entries):
            self._prev_demand[j] = entry.get()

    def _rebuild_grid(self) -> None:
        """Destruye y recrea todos los widgets Entry de costos, oferta y demanda.

        Restaura los valores previos de la caché en las celdas que siguen existiendo
        tras un cambio de dimensión.
        """
        for widget in self._grid_frame.winfo_children():
            widget.destroy()
        self._cost_entries = []
        self._supply_entries = []
        self._demand_entries = []

        m = self._num_sources_var.get()
        n = self._num_destinations_var.get()

        ttk.Label(self._grid_frame, text="", width=6).grid(row=0, column=0)
        for j in range(n):
            ttk.Label(
                self._grid_frame, text=f"D{j+1}", width=7, anchor="center",
                font=("", 9, "bold")
            ).grid(row=0, column=j + 1, padx=2)
        ttk.Label(
            self._grid_frame, text="Oferta", width=8, anchor="center",
            font=("", 9, "bold")
        ).grid(row=0, column=n + 1, padx=(8, 0))

        entry_kw = {"width": 7, "justify": "center"}

        for i in range(m):
            ttk.Label(
                self._grid_frame, text=f"F{i+1}", width=6, anchor="center",
                font=("", 9, "bold")
            ).grid(row=i + 1, column=0)

            row_entries: list[ttk.Entry] = []
            for j in range(n):
                e = ttk.Entry(self._grid_frame, **entry_kw)
                e.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                cached = self._prev_costs.get((i, j), "")
                if cached:
                    e.insert(0, cached)
                e.bind("<KeyRelease>", self._schedule_auto_solve)
                row_entries.append(e)
            self._cost_entries.append(row_entries)

            se = ttk.Entry(self._grid_frame, **entry_kw)
            se.grid(row=i + 1, column=n + 1, padx=(8, 0), pady=2)
            cached_s = self._prev_supply.get(i, "")
            if cached_s:
                se.insert(0, cached_s)
            se.bind("<KeyRelease>", self._schedule_auto_solve)
            self._supply_entries.append(se)

        ttk.Label(
            self._grid_frame, text="Demanda", width=6, anchor="center",
            font=("", 9, "bold")
        ).grid(row=m + 1, column=0, pady=(4, 0))
        for j in range(n):
            de = ttk.Entry(self._grid_frame, **entry_kw)
            de.grid(row=m + 1, column=j + 1, padx=2, pady=(4, 0))
            cached_d = self._prev_demand.get(j, "")
            if cached_d:
                de.insert(0, cached_d)
            de.bind("<KeyRelease>", self._schedule_auto_solve)
            self._demand_entries.append(de)

    def _schedule_auto_solve(
        self, 
        _event: object = None
    ) -> None:
        """Programa un auto-recalculo tras 800 ms de inactividad, cancelando el anterior."""
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(800, self._auto_solve)

    def _auto_solve(self) -> None:
        """Ejecuta el recalculo automático en silencio; los errores se ignoran."""
        self._after_id = None
        try:
            problem = self.get_problem()
            self._on_solve(problem)
        except ValueError:
            pass

    def get_problem(self) -> TransportProblem:
        """Lee y valida todos los campos de entrada y retorna un TransportProblem.

        Lanza ValueError con un mensaje descriptivo si algún campo está vacío,
        contiene un valor no numérico, o no cumple las restricciones de signo.
        """
        m = self._num_sources_var.get()
        n = self._num_destinations_var.get()

        costs: list[list[float]] = []
        for i in range(m):
            row: list[float] = []
            for j in range(n):
                val = self._parse_float(
                    self._cost_entries[i][j].get(),
                    f"Costo F{i+1}→D{j+1}",
                    non_negative=True,
                )
                row.append(val)
            costs.append(row)

        supply = [
            self._parse_float(self._supply_entries[i].get(), f"Oferta F{i+1}", positive=True)
            for i in range(m)
        ]
        demand = [
            self._parse_float(self._demand_entries[j].get(), f"Demanda D{j+1}", positive=True)
            for j in range(n)
        ]

        return TransportProblem(
            supply=supply,
            demand=demand,
            costs=costs,
            source_labels=[f"F{i+1}" for i in range(m)],
            destination_labels=[f"D{j+1}" for j in range(n)],
        )

    @staticmethod
    def _parse_float(
        text: str,
        label: str,
        non_negative: bool = False,
        positive: bool = False
    ) -> float:
        """Convierte un texto a float y valida restricciones de signo.

        Lanza ValueError con un mensaje que incluye el nombre del campo (label)
        si el texto está vacío, no es numérico, o viola la restricción indicada.
        """
        text = text.strip()
        if not text:
            raise ValueError(f"{label}: campo vacío.")
        try:
            val = float(text)
        except ValueError:
            raise ValueError(f"{label}: '{text}' no es un número válido.")
        if non_negative and val < 0:
            raise ValueError(f"{label}: debe ser ≥ 0 (obtenido {val}).")
        if positive and val <= 0:
            raise ValueError(f"{label}: debe ser > 0 (obtenido {val}).")
        return val

    def _load_example(self) -> None:
        """Carga un ejemplo predefinido de matriz 3×4 balanceada y lo resuelve."""
        self._num_sources_var.set(3)
        self._num_destinations_var.set(4)
        self._prev_costs.clear()
        self._prev_supply.clear()
        self._prev_demand.clear()
        self._rebuild_grid()

        example_costs = [
            [2, 3, 1, 5],
            [7, 3, 4, 6],
            [8, 5, 3, 3],
        ]
        example_supply = [30, 40, 50]
        example_demand = [20, 30, 40, 30]

        for i, row in enumerate(example_costs):
            for j, val in enumerate(row):
                self._cost_entries[i][j].delete(0, "end")
                self._cost_entries[i][j].insert(0, str(val))
        for i, val in enumerate(example_supply):
            self._supply_entries[i].delete(0, "end")
            self._supply_entries[i].insert(0, str(val))
        for j, val in enumerate(example_demand):
            self._demand_entries[j].delete(0, "end")
            self._demand_entries[j].insert(0, str(val))

        self._on_solve_clicked()

    def _load_random_example(self) -> None:
        """Genera valores aleatorios válidos para el tamaño m×n actualmente seleccionado.

        Los costos son enteros en [1, 20]. La oferta se genera aleatoriamente en [10, 50]
        por fuente; la demanda se distribuye usando puntos de corte aleatorios sobre la
        oferta total, garantizando balance exacto y todos los valores > 0.
        """
        m = self._num_sources_var.get()
        n = self._num_destinations_var.get()

        costs = [[random.randint(1, 20) for _ in range(n)] for _ in range(m)]
        supply = [random.randint(10, 50) for _ in range(m)]
        total = sum(supply)

        breakpoints = sorted(random.sample(range(1, total), n - 1))
        demand: list[int] = []
        prev = 0
        for bp in breakpoints:
            demand.append(bp - prev)
            prev = bp
        demand.append(total - prev)

        self._prev_costs.clear()
        self._prev_supply.clear()
        self._prev_demand.clear()
        self._rebuild_grid()

        for i, row in enumerate(costs):
            for j, val in enumerate(row):
                self._cost_entries[i][j].delete(0, "end")
                self._cost_entries[i][j].insert(0, str(val))
        for i, val in enumerate(supply):
            self._supply_entries[i].delete(0, "end")
            self._supply_entries[i].insert(0, str(val))
        for j, val in enumerate(demand):
            self._demand_entries[j].delete(0, "end")
            self._demand_entries[j].insert(0, str(val))

        self._on_solve_clicked()

    def _clear_all(self) -> None:
        """Vacía todos los campos de entrada y notifica al callback on_clear si está definido."""
        for row in self._cost_entries:
            for entry in row:
                entry.delete(0, "end")
        for entry in self._supply_entries:
            entry.delete(0, "end")
        for entry in self._demand_entries:
            entry.delete(0, "end")
        self._prev_costs.clear()
        self._prev_supply.clear()
        self._prev_demand.clear()
        if self._on_clear:
            self._on_clear()

    def _on_solve_clicked(self) -> None:
        """Valida los campos y llama a on_solve; muestra un diálogo de error si la validación falla."""
        try:
            problem = self.get_problem()
            self._on_solve(problem)
        except ValueError as exc:
            messagebox.showerror("Error de entrada", str(exc))
