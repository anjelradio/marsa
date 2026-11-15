"""Consulta de ranking: sitios terrestres ordenados por similitud con un destino."""

from sqlmodel import Session, select

from app.modules.analogia.domain.services.similarity import (
    CaracteristicaSpec,
    ResultadoSimilitud,
    calcular_similitud,
)
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
    MedicionModel,
)
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel


class DestinoNoEncontrado(Exception):
    """El cuerpo destino pedido no existe en la base de datos."""


def _especificaciones(session: Session) -> list[CaracteristicaSpec]:
    return [
        CaracteristicaSpec(c.id, c.nombre, c.unidad, c.rango, c.peso, c.grupo)
        for c in session.exec(select(CaracteristicaModel)).all()
        if c.id is not None
    ]


def _valores_por_sitio(session: Session) -> dict[int, dict[int, float]]:
    valores: dict[int, dict[int, float]] = {}
    for m in session.exec(select(MedicionModel)).all():
        valores.setdefault(m.sitio_id, {})[m.caracteristica_id] = m.valor
    return valores


def _sitios_de(session: Session, nombre_cuerpo: str) -> list[SitioModel]:
    cuerpo = session.exec(
        select(CuerpoCelesteModel).where(CuerpoCelesteModel.nombre == nombre_cuerpo)
    ).first()
    if cuerpo is None:
        raise DestinoNoEncontrado(nombre_cuerpo)
    return list(session.exec(select(SitioModel).where(SitioModel.cuerpo_id == cuerpo.id)).all())


def mejor_coincidencia(
    specs: list[CaracteristicaSpec],
    valores: dict[int, dict[int, float]],
    sitio_tierra: SitioModel,
    sitios_destino: list[SitioModel],
) -> tuple[SitioModel, ResultadoSimilitud] | None:
    """Devuelve el sitio destino más parecido al sitio terrestre dado."""
    mejor: tuple[SitioModel, ResultadoSimilitud] | None = None
    for destino in sitios_destino:
        resultado = calcular_similitud(
            specs, valores.get(sitio_tierra.id, {}), valores.get(destino.id, {})
        )
        if mejor is None or resultado.similitud > mejor[1].similitud:
            mejor = (destino, resultado)
    return mejor


def ranking_analogos(session: Session, destino: str) -> list[dict]:
    """Ordena los sitios terrestres por similitud con el mejor sitio del destino.

    ``destino`` es el nombre del cuerpo celeste (p. ej. ``Marte`` o ``Luna``).
    """
    sitios_destino = _sitios_de(session, destino)
    sitios_tierra = _sitios_de(session, "Tierra")
    specs = _especificaciones(session)
    valores = _valores_por_sitio(session)

    filas: list[dict] = []
    for tierra in sitios_tierra:
        par = mejor_coincidencia(specs, valores, tierra, sitios_destino)
        if par is None:
            continue
        sitio_destino, r = par
        filas.append(
            {
                "sitio_tierra_id": tierra.id,
                "sitio_tierra": tierra.nombre,
                "tipo": tierra.tipo,
                "geom": tierra.geom,
                "sitio_destino_id": sitio_destino.id,
                "sitio_destino": sitio_destino.nombre,
                "geom_destino": sitio_destino.geom,
                "similitud": r.similitud,
                "cobertura": r.cobertura,
                "por_grupo": r.por_grupo,
                "metodo": r.metodo,
                "coincide": r.coincide,
                "difiere": r.difiere,
                "detalle": [d.__dict__ for d in r.detalle],
            }
        )
    filas.sort(key=lambda f: f["similitud"], reverse=True)
    for posicion, fila in enumerate(filas, start=1):
        fila["posicion"] = posicion
    return filas
