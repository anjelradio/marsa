"""Estadística básica sobre las muestras de una celda."""

import math
from collections.abc import Iterable


def resumir(valores: Iterable[float | None]) -> tuple[float, float, int] | None:
    """Media, desviación típica poblacional y número de muestras de los valores finitos.

    Ignora ``None``, NaN e infinitos. Devuelve ``None`` si no queda ningún valor.
    """
    limpios = [
        float(v) for v in valores if v is not None and not isinstance(v, bool) and math.isfinite(v)
    ]
    if not limpios:
        return None
    n = len(limpios)
    media = sum(limpios) / n
    varianza = sum((v - media) ** 2 for v in limpios) / n
    return media, math.sqrt(varianza), n
