from __future__ import annotations

import copy

from models.transport_problem import TransportProblem


class BalanceHelper:
    """Responsabilidad única: detectar y corregir el desbalance de un problema de transporte.

    Si la oferta total supera a la demanda, añade una columna ficticia con costo cero
    y demanda igual al excedente. Si la demanda supera a la oferta, añade una fila
    ficticia análoga. El problema original nunca se muta.
    """

    @staticmethod
    def balance(problem: TransportProblem) -> tuple[TransportProblem, str | None]:
        """Balancea el problema de transporte si es necesario.

        Retorna una tupla (problema_balanceado, dummy_added) donde dummy_added es
        'row' si se añadió una fila ficticia, 'column' si se añadió una columna
        ficticia, o None si el problema ya estaba balanceado.
        """
        p: TransportProblem = copy.deepcopy(problem)
        diff: float = p.total_supply - p.total_demand

        if abs(diff) < 1e-9:
            return p, None

        if diff > 0:
            for row in p.costs:
                row.append(0.0)
            p.demand.append(diff)
            p.destination_labels.append("D*")
            return p, "column"
        else:
            p.costs.append([0.0] * p.num_destinations)
            p.supply.append(-diff)
            p.source_labels.append("F*")
            return p, "row"
