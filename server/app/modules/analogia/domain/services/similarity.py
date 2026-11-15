"""Servicio de dominio puro para calcular la similitud entre dos sitios.

Método ``ponderado-v1``: por cada característica se calcula
``1 - |a - b| / rango`` (acotado a [0, 1]) y se combinan con los pesos
de cada característica. Solo cuentan las características con dato en ambos
sitios; ``cobertura`` indica qué fracción del peso total quedó cubierta.
"""

from dataclasses import dataclass

METODO = "ponderado-v1"
UMBRAL_COINCIDE = 0.8
UMBRAL_DIFIERE = 0.5


@dataclass(frozen=True)
class CaracteristicaSpec:
    id: int
    nombre: str
    unidad: str | None
    rango: float
    peso: float


@dataclass(frozen=True)
class DetalleCaracteristica:
    caracteristica: str
    unidad: str | None
    valor_tierra: float
    valor_destino: float
    similitud: float


@dataclass(frozen=True)
class ResultadoSimilitud:
    similitud: float
    cobertura: float
    metodo: str
    coincide: str
    difiere: str
    detalle: list[DetalleCaracteristica]


def similitud_caracteristica(a: float, b: float, rango: float) -> float:
    """Similitud en [0, 1] de dos valores respecto al rango de la característica."""
    if rango <= 0:
        raise ValueError("rango debe ser positivo")
    return max(0.0, min(1.0, 1.0 - abs(a - b) / rango))


def calcular_similitud(
    caracteristicas: list[CaracteristicaSpec],
    valores_tierra: dict[int, float],
    valores_destino: dict[int, float],
) -> ResultadoSimilitud:
    """Compara dos sitios y devuelve similitud, cobertura y explicación."""
    peso_total = sum(c.peso for c in caracteristicas)
    peso_cubierto = 0.0
    acumulado = 0.0
    detalle: list[DetalleCaracteristica] = []

    for c in caracteristicas:
        if c.id not in valores_tierra or c.id not in valores_destino:
            continue
        s = similitud_caracteristica(
            valores_tierra[c.id], valores_destino[c.id], c.rango
        )
        peso_cubierto += c.peso
        acumulado += c.peso * s
        detalle.append(
            DetalleCaracteristica(
                caracteristica=c.nombre,
                unidad=c.unidad,
                valor_tierra=valores_tierra[c.id],
                valor_destino=valores_destino[c.id],
                similitud=round(s, 4),
            )
        )

    similitud = acumulado / peso_cubierto if peso_cubierto > 0 else 0.0
    cobertura = peso_cubierto / peso_total if peso_total > 0 else 0.0

    coincide = ", ".join(d.caracteristica for d in detalle if d.similitud >= UMBRAL_COINCIDE)
    difiere = ", ".join(d.caracteristica for d in detalle if d.similitud < UMBRAL_DIFIERE)

    return ResultadoSimilitud(
        similitud=round(similitud, 4),
        cobertura=round(cobertura, 4),
        metodo=METODO,
        coincide=coincide,
        difiere=difiere,
        detalle=detalle,
    )
