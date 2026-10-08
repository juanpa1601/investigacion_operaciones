# Solucionador del Problema de Transporte

Aplicación de escritorio en Python que resuelve el problema de transporte de la programación lineal y compara tres métodos de solución básica factible inicial.

## Tecnologías

- Python 3.10 o superior
- Tkinter (interfaz gráfica)
- NumPy
- unittest / pytest

## Qué hace

- Ejecuta **Esquina Noroeste**, **Costo Mínimo** y **Aproximación de Vogel** sobre el mismo problema y compara el costo total de cada uno. El de menor costo se resalta.
- Balancea automáticamente los problemas desbalanceados agregando una fuente o un destino ficticio, y detecta soluciones degeneradas.
- Muestra para cada método la matriz de asignación y la trazabilidad paso a paso (celda, cantidad y razón de cada asignación).
- Permite matrices de 2×2 a 8×8, cargar un ejemplo, generar datos aleatorios balanceados y recalcular automáticamente al editar.

La explicación detallada de los algoritmos y de la arquitectura está en [`DOCUMENTACION.md`](DOCUMENTACION.md).

## Estructura

```
algorithms/   Esquina Noroeste, Costo Mínimo y Vogel (heredan de una clase base)
models/       TransportProblem y resultados
services/     SolverService: ejecuta los algoritmos inyectados
utils/        Balanceo de oferta y demanda
ui/           Paneles de Tkinter
tests/        Pruebas de algoritmos, modelo, balanceo y servicio
```

## Cómo ejecutarlo

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Pruebas:

```bash
python -m pytest
```

Las 82 pruebas pasan localmente con Python 3.14.

## Contexto

Proyecto académico de la materia Investigación de Operaciones.
