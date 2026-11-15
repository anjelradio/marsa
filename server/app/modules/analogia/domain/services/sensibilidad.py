"""Sensibilidad del ranking a los pesos de grupo.

Los pesos 50 / 20 / 30 son una decisión, no un dato. Para saber cuánto depende de ella un
resultado, se recalcula el ranking con otras combinaciones razonables de pesos y se mira cuántas
veces cada candidato sigue entre los mejores.
"""

from dataclasses import dataclass
from itertools import product

from app.modules.analogia.domain.services.similarity import PESOS_GRUPO, combinar_grupos

# Cada peso se multiplica por estos factores (de la mitad al doble) y se normaliza.
FACTORES = (0.5, 1.0, 2.0)


@dataclass(frozen=True)
class Estabilidad:
    """``estabilidad``: fracción de escenarios en que el candidato queda entre los ``n`` mejores.
    ``similitud_min`` y ``similitud_max``: el rango de su puntuación según los escenarios."""

    estabilidad: float
    similitud_min: float
    similitud_max: float


def escenarios_de_pesos(base: dict[str, float] | None = None) -> list[dict[str, float]]:
    """Todas las combinaciones de multiplicar cada peso por ``FACTORES`` (incluye la base)."""
    base = PESOS_GRUPO if base is None else base
    grupos = list(base)
    escenarios = []
    for factores in product(FACTORES, repeat=len(grupos)):
        pesos = {g: base[g] * f for g, f in zip(grupos, factores)}
        total = sum(pesos.values())
        escenarios.append({g: p / total for g, p in pesos.items()})
    return escenarios


def estabilidad_del_ranking(
    por_grupo: dict[int, dict[str, float]], n: int, base: dict[str, float] | None = None
) -> dict[int, Estabilidad]:
    """Para cada candidato (clave), su estabilidad entre los ``n`` mejores en todos los escenarios."""
    if n < 1:
        raise ValueError("n debe ser al menos 1.")
    escenarios = escenarios_de_pesos(base)
    veces_en_top = {k: 0 for k in por_grupo}
    extremos = {k: [1.0, 0.0] for k in por_grupo}
    for pesos in escenarios:
        puntuacion = {k: combinar_grupos(g, pesos) for k, g in por_grupo.items()}
        for k, valor in puntuacion.items():
            extremos[k][0] = min(extremos[k][0], valor)
            extremos[k][1] = max(extremos[k][1], valor)
        mejores = sorted(puntuacion, key=lambda k: puntuacion[k], reverse=True)[:n]
        for k in mejores:
            veces_en_top[k] += 1
    return {
        k: Estabilidad(
            round(veces_en_top[k] / len(escenarios), 4),
            round(extremos[k][0], 4),
            round(extremos[k][1], 4),
        )
        for k in por_grupo
    }
