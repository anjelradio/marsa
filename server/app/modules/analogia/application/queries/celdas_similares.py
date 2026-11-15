"""Búsqueda de las celdas de Marte o la Luna más parecidas a un lugar de la Tierra.

Valida primero (origen, destino y datos) y lanza una excepción si algo no es válido. Cada celda
candidata lleva su puntuación única, la de cada grupo, la cobertura de datos y su estabilidad ante
otros pesos de grupo. Las celdas con muy poca cobertura no se ordenan: se cuentan aparte.
"""

from sqlmodel import Session, select

from app.modules.analogia.application.queries.ranking_query import (
    DestinoNoEncontrado,
    _especificaciones,
    _sitios_de,
    _valores_por_sitio,
    limites_de,
)
from app.modules.analogia.domain.services.sensibilidad import estabilidad_del_ranking
from app.modules.analogia.domain.services.similarity import (
    METODO,
    PESOS_GRUPO,
    calcular_similitud,
)
from app.modules.sitio.domain.services.malla import celda_de
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel

COBERTURA_MINIMA = 0.6  # por debajo, la celda no se ordena: faltan demasiados datos


class OrigenNoEncontrado(Exception):
    """El sitio o la celda terrestre de partida no existe en la base."""


class OrigenInvalido(Exception):
    """El origen no es un lugar de la Tierra, o no se indicó."""


class OrigenSinDatos(Exception):
    """El origen no tiene ninguna medición con la que comparar."""


def _origen(
    session: Session, sitio_id: int | None, lat: float | None, lng: float | None
) -> SitioModel:
    if sitio_id is not None:
        sitio = session.get(SitioModel, sitio_id)
        if sitio is None:
            raise OrigenNoEncontrado(f"No existe el sitio {sitio_id}.")
        if sitio.id not in {s.id for s in _sitios_de(session, "Tierra")}:
            raise OrigenInvalido("El origen debe ser un sitio de la Tierra.")
        return sitio
    if lat is None or lng is None:
        raise OrigenInvalido("Indica sitio_id, o lat y lng.")
    codigo = celda_de("Tierra", lat, lng).codigo
    sitio = session.exec(select(SitioModel).where(SitioModel.codigo == codigo)).first()
    if sitio is None:
        raise OrigenNoEncontrado(f"La celda {codigo} no está en la base (o es océano).")
    return sitio


def celdas_similares(
    session: Session,
    destino: str,
    *,
    sitio_id: int | None = None,
    lat: float | None = None,
    lng: float | None = None,
    limite: int = 10,
) -> dict:
    """Las ``limite`` celdas del destino más parecidas al origen, con su estabilidad."""
    if limite < 1:
        raise ValueError("limite debe ser al menos 1.")
    origen = _origen(session, sitio_id, lat, lng)
    celdas = _sitios_de(session, destino, "celda")  # lanza DestinoNoEncontrado
    specs = _especificaciones(session)
    valores = _valores_por_sitio(session)
    valores_origen = valores.get(origen.id, {})
    if not valores_origen:
        raise OrigenSinDatos(f"'{origen.nombre}' no tiene mediciones.")

    resultados = {
        c.id: (c, calcular_similitud(specs, valores_origen, valores.get(c.id, {})))
        for c in celdas
    }
    validas = {
        i: par
        for i, par in resultados.items()
        if par[1].cobertura >= COBERTURA_MINIMA and par[1].por_grupo
    }
    estabilidad = estabilidad_del_ranking(
        {i: r.por_grupo for i, (_, r) in validas.items()}, limite
    )

    ordenadas = sorted(validas.values(), key=lambda par: par[1].similitud, reverse=True)
    filas = []
    for posicion, (celda, r) in enumerate(ordenadas[:limite], start=1):
        e = estabilidad[celda.id]
        filas.append(
            {
                "posicion": posicion,
                "sitio_id": celda.id,
                "codigo": celda.codigo,
                "nombre": celda.nombre,
                "geom": celda.geom,
                "limites": limites_de(celda),
                "similitud": r.similitud,
                "por_grupo": r.por_grupo,
                "cobertura": r.cobertura,
                "estabilidad": e.estabilidad,
                "similitud_min": e.similitud_min,
                "similitud_max": e.similitud_max,
                "coincide": r.coincide,
                "difiere": r.difiere,
                "detalle": [d.__dict__ for d in r.detalle],
            }
        )
    return {
        "origen": {
            "sitio_id": origen.id,
            "nombre": origen.nombre,
            "codigo": origen.codigo,
            "tipo": origen.tipo,
        },
        "destino": destino,
        "metodo": METODO,
        "pesos_grupo": PESOS_GRUPO,
        "cobertura_minima": COBERTURA_MINIMA,
        "evaluadas": len(celdas),
        "validas": len(validas),
        "descartadas_por_cobertura": len(celdas) - len(validas),
        "resultados": filas,
    }


__all__ = [
    "DestinoNoEncontrado",
    "OrigenInvalido",
    "OrigenNoEncontrado",
    "OrigenSinDatos",
    "celdas_similares",
]
