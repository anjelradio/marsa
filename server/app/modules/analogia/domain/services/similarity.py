"""Servicio de dominio puro para calcular la similitud entre dos sitios.

Método ``grupos-v1``. Cada característica pertenece a un grupo (físico, terreno...):

1. Por característica: ``1 - |a - b| / rango`` (acotado a [0, 1]).
2. Por grupo: media ponderada con el peso de cada característica dentro de su grupo,
   solo con las que tienen dato en ambos sitios.
3. Puntuación única: media de los grupos con dato, ponderada con ``PESOS_GRUPO``. Si un grupo
   no tiene datos su peso se reparte entre los demás, y la cobertura baja.

``cobertura`` es la fracción de la información esperada que se pudo usar: promedia, con los
pesos de grupo, qué parte del peso de cada grupo tenía dato.
"""

from dataclasses import dataclass, field

METODO = "grupos-v1"
UMBRAL_COINCIDE = 0.8
UMBRAL_DIFIERE = 0.5

# Peso de cada grupo en la puntuación única. El grupo de geología (30 %) se añade con su propio
# cálculo; mientras tanto estos pesos se reparten entre los grupos presentes.
PESOS_GRUPO: dict[str, float] = {"fisico": 0.5, "terreno": 0.2}


@dataclass(frozen=True)
class CaracteristicaSpec:
    id: int
    nombre: str
    unidad: str | None
    rango: float
    peso: float
    grupo: str = "fisico"


@dataclass(frozen=True)
class DetalleCaracteristica:
    caracteristica: str
    unidad: str | None
    valor_tierra: float
    valor_destino: float
    similitud: float
    grupo: str = "fisico"


@dataclass(frozen=True)
class ResultadoSimilitud:
    similitud: float
    cobertura: float
    metodo: str
    coincide: str
    difiere: str
    detalle: list[DetalleCaracteristica]
    por_grupo: dict[str, float] = field(default_factory=dict)


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
    """Compara dos sitios y devuelve la puntuación única, la de cada grupo y la explicación."""
    peso_total: dict[str, float] = {}
    peso_cubierto: dict[str, float] = {}
    acumulado: dict[str, float] = {}
    detalle: list[DetalleCaracteristica] = []

    for c in caracteristicas:
        peso_total[c.grupo] = peso_total.get(c.grupo, 0.0) + c.peso
        if c.id not in valores_tierra or c.id not in valores_destino:
            continue
        s = similitud_caracteristica(
            valores_tierra[c.id], valores_destino[c.id], c.rango
        )
        peso_cubierto[c.grupo] = peso_cubierto.get(c.grupo, 0.0) + c.peso
        acumulado[c.grupo] = acumulado.get(c.grupo, 0.0) + c.peso * s
        detalle.append(
            DetalleCaracteristica(
                caracteristica=c.nombre,
                unidad=c.unidad,
                valor_tierra=valores_tierra[c.id],
                valor_destino=valores_destino[c.id],
                similitud=round(s, 4),
                grupo=c.grupo,
            )
        )

    por_grupo = {
        g: acumulado[g] / peso_cubierto[g] for g in peso_cubierto if peso_cubierto[g] > 0
    }

    peso_con_dato = sum(PESOS_GRUPO.get(g, 0.0) for g in por_grupo)
    similitud = (
        sum(PESOS_GRUPO.get(g, 0.0) * s for g, s in por_grupo.items()) / peso_con_dato
        if peso_con_dato > 0
        else 0.0
    )

    peso_esperado = sum(PESOS_GRUPO.get(g, 0.0) for g in peso_total if peso_total[g] > 0)
    cobertura = (
        sum(
            PESOS_GRUPO.get(g, 0.0) * (peso_cubierto.get(g, 0.0) / peso_total[g])
            for g in peso_total
            if peso_total[g] > 0
        )
        / peso_esperado
        if peso_esperado > 0
        else 0.0
    )

    coincide = ", ".join(d.caracteristica for d in detalle if d.similitud >= UMBRAL_COINCIDE)
    difiere = ", ".join(d.caracteristica for d in detalle if d.similitud < UMBRAL_DIFIERE)

    return ResultadoSimilitud(
        similitud=round(similitud, 4),
        cobertura=round(cobertura, 4),
        metodo=METODO,
        coincide=coincide,
        difiere=difiere,
        detalle=detalle,
        por_grupo={g: round(s, 4) for g, s in por_grupo.items()},
    )
