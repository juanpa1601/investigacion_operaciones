# Documentación: Solucionador del Problema de Transporte

## Descripción general

Esta aplicación de escritorio resuelve el **Problema de Transporte** de la Programación Lineal. Dado un conjunto de fuentes con oferta conocida y destinos con demanda conocida, encuentra una distribución de recursos que satisfaga toda la demanda al menor costo total posible.

La herramienta implementa tres métodos de **Solución Básica Factible Inicial (SBFI)**: Esquina Noroeste, Costo Mínimo y Aproximación de Vogel. Los tres se ejecutan en paralelo sobre el mismo problema, permitiendo comparar sus costos y trazabilidades lado a lado.

---

## El Problema de Transporte

### Formulación

Dados:
- **m fuentes** F₁, F₂, …, Fₘ, cada una con oferta `sᵢ`
- **n destinos** D₁, D₂, …, Dₙ, cada uno con demanda `dⱼ`
- **Costo unitario** `cᵢⱼ`: costo de transportar una unidad de Fᵢ a Dⱼ

Se busca determinar las cantidades `xᵢⱼ` (unidades transportadas de Fᵢ a Dⱼ) que:

```
Minimizar   Z = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ

sujeto a:   Σⱼ xᵢⱼ = sᵢ   para toda fuente i    (se agota toda la oferta)
            Σᵢ xᵢⱼ = dⱼ   para todo destino j   (se satisface toda la demanda)
                xᵢⱼ ≥ 0
```

### Problema balanceado vs desbalanceado

Un problema está **balanceado** cuando `Σ sᵢ = Σ dⱼ`. Si no lo está:

| Situación | Acción automática |
|---|---|
| Oferta total > Demanda total | Se añade destino ficticio **D\*** con demanda = excedente y costo 0 |
| Demanda total > Oferta total | Se añade fuente ficticia **F\*** con oferta = déficit y costo 0 |

Las asignaciones a filas o columnas ficticias representan capacidad no utilizada y no generan costo real.

### Degeneración

Una SBFI tiene **m + n − 1 celdas básicas** (con asignación > 0). Si el número de celdas asignadas es menor que eso, la solución es **degenerada**. Ocurre cuando la oferta de una fuente y la demanda de un destino se agotan simultáneamente en la misma iteración. Los tres algoritmos lo detectan y manejan automáticamente.

---

## Algoritmos implementados

### 1. Método de la Esquina Noroeste

**Idea:** Comenzar en la celda (F₁, D₁) —la esquina superior izquierda— e ir avanzando hacia la esquina inferior derecha, sin considerar en ningún momento los costos.

**Procedimiento por iteración:**
1. En la celda actual (i, j), asignar `xᵢⱼ = min(oferta_rem[i], demanda_rem[j])`.
2. Restar la cantidad asignada de ambos remanentes.
3. Si se agota la fila → avanzar `i++`.
4. Si se agota la columna → avanzar `j++`.
5. Si ambos se agotan (degeneración) → avanzar solo `i` para conservar m+n−1 celdas básicas.

**Característica:** Es el método más simple y rápido de aplicar manualmente, pero generalmente produce el costo más alto de los tres.

---

### 2. Método del Costo Mínimo

**Idea:** En cada iteración, elegir la celda activa (no agotada) con el **menor costo unitario** y asignar ahí el máximo posible.

**Procedimiento por iteración:**
1. Buscar en todas las celdas disponibles la de menor `cᵢⱼ`.
2. Asignar `xᵢⱼ = min(oferta_rem[i], demanda_rem[j])`.
3. Marcar como agotada la fila o columna que llegó a cero.
4. Si ambas llegan a cero simultáneamente (degeneración), marcar solo la fila y mantener la columna activa.

**Característica:** Generalmente mejora el costo respecto a la Esquina Noroeste al priorizar celdas baratas, pero no garantiza el óptimo global.

---

### 3. Método de Aproximación de Vogel (VAM)

**Idea:** Antes de cada asignación, calcular la **penalización** de cada fila y columna activa: la diferencia entre el primer y segundo menor costo disponible. Asignar primero donde la penalización es mayor (donde más se "perdería" por no elegir la celda más barata).

**Procedimiento por iteración:**
1. Para cada fila activa: ordenar sus costos disponibles → penalización = `2°_menor − 1°_menor`.
   - Si solo hay un costo activo, la penalización es ese costo.
2. Igual para cada columna activa.
3. Seleccionar la fila o columna con **mayor penalización**.
   - Empate de penalización → elegir la de menor costo mínimo.
   - Empate aún → preferir fila (menor índice).
4. Asignar en la celda de menor costo de esa fila/columna: `xᵢⱼ = min(oferta_rem[i], demanda_rem[j])`.
5. Manejar degeneración igual que el Costo Mínimo.

**Característica:** Es el método más sofisticado y produce habitualmente la solución inicial de menor costo entre los tres.

---

## Arquitectura del proyecto

El proyecto aplica los principios **SOLID** con tipado nativo de Python 3.10+.

```
investigacion_operaciones/
├── main.py                       ← Punto de entrada; inyección de dependencias
├── models/
│   └── transport_problem.py      ← Estructuras de datos puras (dataclasses)
├── algorithms/
│   ├── base.py                   ← Contrato abstracto (ABC) TransportAlgorithm
│   ├── northwest_corner.py       ← NorthwestCornerAlgorithm
│   ├── minimum_cost.py           ← MinimumCostAlgorithm
│   └── vogel.py                  ← VogelAlgorithm
├── utils/
│   └── balance_helper.py         ← BalanceHelper (solo balancea, no resuelve)
├── services/
│   └── solver_service.py         ← SolverService (orquesta sin conocer concreciones)
└── ui/
    ├── app.py                    ← TransportApp (ventana principal)
    ├── input_panel.py            ← InputPanel (grilla de entrada dinámica)
    ├── results_panel.py          ← ResultsPanel (comparación tabular)
    └── steps_panel.py            ← StepsPanel (trazabilidad por método)
```

### Flujo de ejecución

```
Usuario ingresa datos
        │
        ▼
  InputPanel.get_problem()
  → valida campos y construye TransportProblem
        │
        ▼
  SolverService.solve_all(problem)
  ├── BalanceHelper.balance(problem)   ← añade fila/columna ficticia si es necesario
  ├── NorthwestCornerAlgorithm.solve(balanced)  ┐
  ├── MinimumCostAlgorithm.solve(balanced)      ├─ cada uno retorna SolutionResult
  └── VogelAlgorithm.solve(balanced)            ┘
        │
        ▼
  TransportApp distribuye resultados:
  ├── ResultsPanel.update_results()   ← tabla comparativa con mejor en verde
  └── StepsPanel.update() × 3        ← matriz de asignación + pasos por método
```

### Principios SOLID aplicados

| Principio | Aplicación concreta |
|---|---|
| **SRP** — Responsabilidad única | `TransportProblem` solo modela datos. `BalanceHelper` solo balancea. Cada algoritmo solo resuelve su método. Cada panel UI solo renderiza su sección. |
| **OCP** — Abierto/cerrado | Para agregar un 4° algoritmo basta crear la clase en `algorithms/` e inyectarla en `main.py`. El resto del código no se toca. |
| **LSP** — Sustitución de Liskov | Los tres algoritmos son intercambiables en `SolverService`; ninguno rompe el contrato de `TransportAlgorithm`. |
| **ISP** — Segregación de interfaces | `TransportAlgorithm` solo expone `name` y `solve`. |
| **DIP** — Inversión de dependencias | `SolverService` depende de `TransportAlgorithm` (ABC), nunca de las clases concretas. Las instancias concretas se inyectan desde `main.py`. |

---

## Modelos de datos

### `TransportProblem`
Representa el enunciado del problema. Solo almacena datos, sin lógica de resolución.

| Campo | Tipo | Descripción |
|---|---|---|
| `supply` | `list[float]` | Oferta disponible en cada fuente |
| `demand` | `list[float]` | Demanda requerida en cada destino |
| `costs` | `list[list[float]]` | Matriz de costos unitarios m×n |
| `source_labels` | `list[str]` | Etiquetas de filas (F1, F2, …) |
| `destination_labels` | `list[str]` | Etiquetas de columnas (D1, D2, …) |

Propiedades calculadas: `num_sources`, `num_destinations`, `total_supply`, `total_demand`, `is_balanced`, `cost_matrix()`.

### `AllocationStep`
Registra una asignación individual para la trazabilidad.

| Campo | Tipo | Descripción |
|---|---|---|
| `step_number` | `int` | Número de paso en la secuencia |
| `source` | `int` | Índice de la fila asignada (base 0) |
| `destination` | `int` | Índice de la columna asignada (base 0) |
| `amount` | `float` | Cantidad transportada |
| `reason` | `str` | Descripción del criterio de selección |

### `SolutionResult`
Resultado completo de un algoritmo.

| Campo | Tipo | Descripción |
|---|---|---|
| `method_name` | `str` | Nombre del algoritmo |
| `allocation_matrix` | `np.ndarray` | Matriz de asignación final m×n |
| `steps` | `list[AllocationStep]` | Trazabilidad completa paso a paso |
| `total_cost` | `float` | Costo total calculado |
| `is_degenerate` | `bool` | `True` si hay menos de m+n−1 celdas básicas |
| `is_balanced` | `bool` | `True` si el problema original estaba balanceado |
| `dummy_added` | `str \| None` | `"row"`, `"column"` o `None` |

---

## Interfaz de usuario

### Panel izquierdo — Entrada de datos

- **Spinboxes m y n**: configuran las dimensiones de la matriz (mínimo 2×2, máximo 8×8).
- **Grilla dinámica**: al cambiar las dimensiones, la grilla se reconstruye automáticamente preservando los valores que siguen siendo válidos.
- **Campo Oferta**: una columna a la derecha de cada fila con la oferta de esa fuente.
- **Fila Demanda**: una fila inferior con la demanda de cada destino.
- **Botón Resolver**: calcula inmediatamente.
- **Botón Ejemplo**: carga un caso 3×4 balanceado de referencia con solución conocida.
- **Botón Aleatorio**: genera costos en [1, 20] y cantidades balanceadas para el tamaño seleccionado.
- **Botón Limpiar**: vacía todos los campos y limpia los paneles de resultados.
- **Auto-cálculo**: cualquier cambio en un campo activa un temporizador de 800 ms; si no hay más cambios en ese lapso, el sistema resuelve automáticamente (silenciosamente si hay errores de validación).

### Panel derecho — Resultados (pestañas)

#### Pestaña "Comparación"
Tabla con una fila por método:

| Columna | Descripción |
|---|---|
| Método | Nombre del algoritmo |
| Costo Total | Suma ponderada de asignaciones × costos |
| Asignaciones | Número de celdas con asignación positiva |
| Degenerado | Sí / No |
| Ficticia | Fila F\* / Columna D\* / No |

El método de menor costo se resalta en **verde**.

#### Pestañas "Esquina Noroeste", "Costo Mínimo", "Aproximación de Vogel"
Cada pestaña muestra:

1. **Matriz de asignación**: tabla con etiquetas de fila y columna, columna de oferta y fila de demanda. Las celdas con asignación positiva aparecen en verde. Al pasar el cursor sobre una celda se muestra el costo unitario.
2. **Trazabilidad paso a paso**: tabla con columnas Paso | Celda | Cantidad | Razón. Describe el criterio exacto de cada asignación.
3. **Costo total** al pie del panel.

---

## Ejecución

```powershell
# Activar el entorno virtual (Windows)
.venv\Scripts\activate

# Ejecutar la aplicación
python main.py
```

### Dependencias

Definidas en `requirements.txt`. Solo `numpy` se utiliza activamente en los algoritmos de transporte para las operaciones matriciales.

```
numpy
scipy
pulp
matplotlib
pandas
```

---

## Ejemplo de referencia (3×4 balanceado)

|   | D1 | D2 | D3 | D4 | Oferta |
|---|---|---|---|---|---|
| **F1** | 2 | 3 | 1 | 5 | 30 |
| **F2** | 7 | 3 | 4 | 6 | 40 |
| **F3** | 8 | 5 | 3 | 3 | 50 |
| **Demanda** | 20 | 30 | 40 | 30 | **120** |

Resultados esperados con este caso (Vogel produce la mejor solución inicial):

| Método | Costo Total |
|---|---|
| Esquina Noroeste | Mayor |
| Costo Mínimo | Intermedio |
| **Aproximación de Vogel** | **Menor** |
