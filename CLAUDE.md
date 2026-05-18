# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ejecutar la aplicación

```powershell
.venv\Scripts\python main.py
```

> **Importante:** usar siempre el Python del venv (`.venv\Scripts\python`), no el Python del sistema. tkinter viene incluido con CPython; las demás dependencias están en el venv.

## Arquitectura general

Aplicación de escritorio para resolver el **Problema de Transporte** (Programación Lineal) usando tres métodos de solución básica factible inicial. El diseño aplica principios SOLID con inyección de dependencias.

### Flujo de datos

```
InputPanel → TransportProblem → SolverService → [balance] → BalanceHelper
                                                           → NorthwestCornerAlgorithm
                                                           → MinimumCostAlgorithm
                                                           → VogelAlgorithm
                                     ↓
                              list[SolutionResult]
                                     ↓
                    ResultsPanel + StepsPanel (×3)
```

### Capas y responsabilidades

| Capa | Módulo | Responsabilidad |
|---|---|---|
| Modelo | `models/transport_problem.py` | `TransportProblem`, `AllocationStep`, `SolutionResult` — solo datos |
| Utilidad | `utils/balance_helper.py` | Balancear el problema añadiendo fila o columna ficticia (costo 0) |
| Algoritmos | `algorithms/` | Cada clase implementa `TransportAlgorithm` (ABC). Reciben el problema **ya balanceado** |
| Servicio | `services/solver_service.py` | Balancea una vez, ejecuta todos los algoritmos. Solo depende del ABC (DIP) |
| UI | `ui/` | Entrada dinámica, comparación tabular y trazabilidad por método |
| Entrada | `main.py` | Crea instancias concretas e inyecta en `SolverService` |

### Extensión del sistema (OCP)

Para añadir un 4° algoritmo: crear clase en `algorithms/` que herede `TransportAlgorithm`, implementar `name` y `solve()`, e inyectar la instancia en `main.py`. Sin tocar el resto del código.

## Contratos clave

- `TransportAlgorithm.solve(problem)` recibe el problema **ya balanceado** (garantizado por `SolverService`).
- `SolutionResult.is_balanced` y `dummy_added` los asigna `SolverService` tras ejecutar el algoritmo, no el algoritmo mismo.
- La degeneracy se maneja en todos los algoritmos marcando solo la fila como agotada cuando `supply_rem[i] == demand_rem[j]` en una iteración no final.

## Dependencias

Definidas en `requirements.txt`: `numpy`, `scipy`, `pulp`, `matplotlib`, `pandas`.  
Solo `numpy` se usa actualmente en los algoritmos de transporte (operaciones matriciales con `np.ndarray`).
