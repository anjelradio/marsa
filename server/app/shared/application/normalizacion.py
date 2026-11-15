"""Normalización de valores al intervalo [0, 1] según el rango físico de la característica."""

from typing import Protocol


class _ConRango(Protocol):
    rango: float
    valor_min: float | None
    valor_max: float | None


def normalizar_valor(valor: float, caracteristica: _ConRango) -> float:
    """``(valor - valor_min) / (valor_max - valor_min)`` acotado a [0, 1].

    Si la característica no tiene rango físico se usa ``0`` a ``rango``.
    """
    minimo, maximo = caracteristica.valor_min, caracteristica.valor_max
    if minimo is None or maximo is None:
        minimo, maximo = 0.0, caracteristica.rango
    return max(0.0, min(1.0, (valor - minimo) / (maximo - minimo)))
