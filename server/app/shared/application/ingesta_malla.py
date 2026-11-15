"""Ingesta de la malla global de celdas de 10°.

Para cada cuerpo se recorre la malla, se lee cada fuente y se guardan las celdas como sitios de
clase ``celda`` con sus mediciones (valor, incertidumbre, número de muestras y periodo).

Se valida primero y, si un dato no es válido, se lanza ``InvalidMedicionDataException``. En la
ingesta esa excepción se captura por medición y se anota en el informe: nunca se sustituye el valor
por otro inventado, y un fallo en una celda no detiene las demás.
"""

from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.modules.caracteristica.domain.exceptions import CaracteristicaNotFoundException
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.corrida_analisis.infrastructure.persistence.models.corrida_analisis_model import (
    CorridaAnalisisModel,
)
from app.modules.cuerpo_celeste.domain.exceptions import (
    CuerpoCelesteNotFoundException,
    InvalidCuerpoCelesteDataException,
)
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.dataset.domain.exceptions import DatasetNotFoundException
from app.modules.dataset.infrastructure.persistence.models.dataset_model import DatasetModel
from app.modules.medicion.domain.entities.medicion import Medicion
from app.modules.medicion.domain.exceptions import InvalidMedicionDataException
from app.modules.medicion.infrastructure.persistence.models.medicion_model import MedicionModel
from app.modules.sitio.domain.entities.sitio import Sitio
from app.modules.sitio.domain.services.malla import Celda, generar_malla
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.shared.application.normalizacion import normalizar_valor
from app.shared.infrastructure.external.malla.errores import FuenteError
from app.shared.infrastructure.external.malla.lectura import FuenteCelda, Lectura

VERSION_CORRIDA = "malla-10"
METODO_CORRIDA = "ingesta-malla"


@dataclass
class ErrorIngesta:
    cuerpo: str
    celda: str
    variable: str
    causa: str


@dataclass
class InformeIngesta:
    """Qué se guardó, qué se descartó y qué falló."""

    celdas_guardadas: dict[str, int] = field(default_factory=dict)
    celdas_descartadas: dict[str, dict[str, int]] = field(default_factory=dict)
    celdas_sin_datos: dict[str, int] = field(default_factory=dict)
    mediciones_guardadas: int = 0
    errores: list[ErrorIngesta] = field(default_factory=list)

    def resumen(self) -> str:
        lineas = []
        for cuerpo, n in self.celdas_guardadas.items():
            descartadas = self.celdas_descartadas.get(cuerpo, {})
            extra = ", ".join(f"{motivo}: {c}" for motivo, c in descartadas.items())
            lineas.append(
                f"{cuerpo}: {n} celdas guardadas"
                + (f", descartadas ({extra})" if extra else "")
                + f", sin datos: {self.celdas_sin_datos.get(cuerpo, 0)}"
            )
        lineas.append(
            f"{self.mediciones_guardadas} mediciones guardadas, {len(self.errores)} errores."
        )
        return "\n".join(lineas)

    def como_dict(self) -> dict[str, Any]:
        datos = asdict(self)
        datos["resumen"] = self.resumen()
        return datos


class IngestaMalla:
    """Orquesta las fuentes de cada cuerpo y guarda las celdas con sus mediciones."""

    def __init__(
        self,
        session: Session,
        planes: dict[str, list[FuenteCelda]],
        *,
        ahora: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.session = session
        self.planes = planes
        self._ahora = ahora

    # ── validación previa ─────────────────────────────────────────────────────────────

    def _validar_catalogo(self, cuerpos: list[str]) -> None:
        """Comprueba, antes de pedir nada a la red, que existen los cuerpos, las características
        y los datasets que van a usarse."""
        for cuerpo in cuerpos:
            if cuerpo not in self.planes:
                raise InvalidCuerpoCelesteDataException(f"No hay plan de ingesta para '{cuerpo}'.")
            if self._cuerpo(cuerpo) is None:
                raise CuerpoCelesteNotFoundException(f"El cuerpo '{cuerpo}' no existe en la base.")
            for fuente in self.planes[cuerpo]:
                if self._dataset(fuente.dataset) is None:
                    raise DatasetNotFoundException(f"Falta el dataset '{fuente.dataset}'.")
                for variable in fuente.variables:
                    if self._caracteristica(variable) is None:
                        raise CaracteristicaNotFoundException(
                            f"Falta la característica '{variable}'."
                        )

    def _cuerpo(self, nombre: str) -> CuerpoCelesteModel | None:
        return self.session.exec(
            select(CuerpoCelesteModel).where(CuerpoCelesteModel.nombre == nombre)
        ).first()

    def _dataset(self, nombre: str) -> DatasetModel | None:
        return self.session.exec(select(DatasetModel).where(DatasetModel.nombre == nombre)).first()

    def _caracteristica(self, nombre: str) -> CaracteristicaModel | None:
        return self.session.exec(
            select(CaracteristicaModel).where(CaracteristicaModel.nombre == nombre)
        ).first()

    # ── ejecución ─────────────────────────────────────────────────────────────────────

    def ejecutar(
        self, cuerpos: Iterable[str] | None = None, limite: int | None = None
    ) -> InformeIngesta:
        lista = list(cuerpos) if cuerpos is not None else list(self.planes)
        self._validar_catalogo(lista)
        informe = InformeIngesta()
        for cuerpo in lista:
            self._ingerir_cuerpo(cuerpo, limite, informe)
        self._registrar_corrida(informe)
        return informe

    def _ingerir_cuerpo(self, cuerpo: str, limite: int | None, informe: InformeIngesta) -> None:
        cuerpo_id = self._cuerpo(cuerpo).id  # type: ignore[union-attr]
        celdas = generar_malla(cuerpo)
        if limite is not None:
            celdas = celdas[:limite]
        fuentes = self.planes[cuerpo]
        informe.celdas_guardadas[cuerpo] = 0
        informe.celdas_sin_datos[cuerpo] = 0

        for fuente in fuentes:  # agrupar peticiones, si la fuente sabe hacerlo
            precargar = getattr(fuente, "precargar", None)
            if precargar:
                try:
                    precargar(celdas)
                except FuenteError as exc:
                    informe.errores.append(ErrorIngesta(cuerpo, "*", "precarga", str(exc)))

        for celda in celdas:
            motivo = self._motivo_de_descarte(fuentes, celda, cuerpo, informe)
            if motivo:
                por_motivo = informe.celdas_descartadas.setdefault(cuerpo, {})
                por_motivo[motivo] = por_motivo.get(motivo, 0) + 1
                continue
            lecturas = self._leer_celda(fuentes, celda, cuerpo, informe)
            if not lecturas:
                informe.celdas_sin_datos[cuerpo] += 1
                continue
            sitio, es_nueva = self._asegurar_celda(cuerpo_id, celda)
            guardadas = self._guardar_mediciones(sitio, celda, lecturas, cuerpo, informe)
            if guardadas:
                informe.celdas_guardadas[cuerpo] += 1
                informe.mediciones_guardadas += guardadas
            else:
                informe.celdas_sin_datos[cuerpo] += 1
                if es_nueva:  # ninguna medición fue válida: no se deja una celda vacía
                    self.session.delete(sitio)
                    self.session.flush()
        self.session.commit()

    @staticmethod
    def _motivo_de_descarte(
        fuentes: list[FuenteCelda], celda: Celda, cuerpo: str, informe: InformeIngesta
    ) -> str | None:
        for fuente in fuentes:
            descartar = getattr(fuente, "descartar", None)
            if descartar:
                try:
                    motivo = descartar(celda)
                except FuenteError as exc:
                    informe.errores.append(ErrorIngesta(cuerpo, celda.codigo, "descarte", str(exc)))
                    return "sin elevación"
                if motivo:
                    return motivo
        return None

    @staticmethod
    def _leer_celda(
        fuentes: list[FuenteCelda], celda: Celda, cuerpo: str, informe: InformeIngesta
    ) -> list[tuple[str, str, Lectura]]:
        """(dataset, característica, lectura) de todas las fuentes que respondieron."""
        lecturas: list[tuple[str, str, Lectura]] = []
        for fuente in fuentes:
            try:
                for variable, lectura in fuente.leer(celda).items():
                    lecturas.append((fuente.dataset, variable, lectura))
            except FuenteError as exc:
                informe.errores.append(
                    ErrorIngesta(cuerpo, celda.codigo, "+".join(fuente.variables), str(exc))
                )
        return lecturas

    def _asegurar_celda(self, cuerpo_id: int, celda: Celda) -> tuple[SitioModel, bool]:
        existente = self.session.exec(
            select(SitioModel).where(SitioModel.codigo == celda.codigo)
        ).first()
        if existente:
            return existente, False
        valido = Sitio.create(
            cuerpo_id=cuerpo_id,
            nombre=f"Celda {celda.codigo}",
            tipo="Celda de 10°",
            geom=celda.poligono(),
            clase="celda",
            codigo=celda.codigo,
            lat_min=celda.lat_min,
            lat_max=celda.lat_max,
            lon_min=celda.lon_min,
            lon_max=celda.lon_max,
        )
        sitio = SitioModel(
            cuerpo_id=valido.cuerpo_id,
            nombre=valido.nombre,
            tipo=valido.tipo,
            geom=valido.geom,
            clase=valido.clase,
            codigo=valido.codigo,
            lat_min=valido.lat_min,
            lat_max=valido.lat_max,
            lon_min=valido.lon_min,
            lon_max=valido.lon_max,
        )
        self.session.add(sitio)
        self.session.flush()
        return sitio, True

    def _guardar_mediciones(
        self,
        sitio: SitioModel,
        celda: Celda,
        lecturas: list[tuple[str, str, Lectura]],
        cuerpo: str,
        informe: InformeIngesta,
    ) -> int:
        guardadas = 0
        for dataset_nombre, variable, lectura in lecturas:
            car = self._caracteristica(variable)
            dataset = self._dataset(dataset_nombre)
            try:
                valida = Medicion.create(
                    sitio_id=sitio.id,
                    caracteristica_id=car.id,
                    dataset_id=dataset.id,
                    valor=lectura.valor,
                    valor_normalizado=normalizar_valor(lectura.valor, car)
                    if _es_finito(lectura.valor)
                    else None,
                    incertidumbre=lectura.incertidumbre,
                    n_muestras=lectura.n_muestras,
                    periodo_inicio=lectura.periodo_inicio,
                    periodo_fin=lectura.periodo_fin,
                    rango_fisico=(car.valor_min, car.valor_max),
                )
            except InvalidMedicionDataException as exc:
                informe.errores.append(ErrorIngesta(cuerpo, celda.codigo, variable, str(exc)))
                continue
            self._guardar_medicion(sitio.id, car.id, dataset.id, valida)
            guardadas += 1
        return guardadas

    def _guardar_medicion(
        self, sitio_id: int, caracteristica_id: int, dataset_id: int, valida: Medicion
    ) -> None:
        existente = self.session.exec(
            select(MedicionModel).where(
                MedicionModel.sitio_id == sitio_id,
                MedicionModel.caracteristica_id == caracteristica_id,
            )
        ).first()
        campos = dict(
            dataset_id=dataset_id,
            valor=valida.valor,
            valor_normalizado=valida.valor_normalizado,
            incertidumbre=valida.incertidumbre,
            n_muestras=valida.n_muestras,
            periodo_inicio=valida.periodo_inicio,
            periodo_fin=valida.periodo_fin,
        )
        if existente:
            for nombre, valor in campos.items():
                setattr(existente, nombre, valor)
            self.session.add(existente)
        else:
            self.session.add(
                MedicionModel(sitio_id=sitio_id, caracteristica_id=caracteristica_id, **campos)
            )

    def _registrar_corrida(self, informe: InformeIngesta) -> None:
        """Deja constancia de la ingesta: una corrida por versión y método, con el resumen."""
        corrida = self.session.exec(
            select(CorridaAnalisisModel).where(
                CorridaAnalisisModel.version == VERSION_CORRIDA,
                CorridaAnalisisModel.metodo == METODO_CORRIDA,
            )
        ).first()
        parametros = {
            "celdas_guardadas": informe.celdas_guardadas,
            "mediciones_guardadas": informe.mediciones_guardadas,
            "errores": len(informe.errores),
        }
        if corrida is None:
            corrida = CorridaAnalisisModel(
                version=VERSION_CORRIDA, metodo=METODO_CORRIDA, parametros=parametros
            )
        else:
            corrida.fecha = self._ahora()
            corrida.parametros = parametros
        self.session.add(corrida)
        self.session.commit()


def _es_finito(valor: float) -> bool:
    return valor == valor and valor not in (float("inf"), float("-inf"))
