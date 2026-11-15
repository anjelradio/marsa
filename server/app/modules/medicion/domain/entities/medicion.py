"""Entidad principal de dominio para medicion."""

from datetime import date

from app.modules.medicion.domain.exceptions import InvalidMedicionDataException
from app.shared.domain.validators import (
    require_in_range,
    require_non_negative,
    require_positive_id,
    require_unit_interval,
)


class Medicion:
    """Entidad de dominio que vincula un sitio, una característica y un dataset.

    Además del valor guarda de cuándo es (``periodo_inicio`` a ``periodo_fin``), cuánta
    incertidumbre tiene y con cuántas muestras se obtuvo.
    """

    def __init__(
        self,
        id: int | None,
        sitio_id: int,
        caracteristica_id: int,
        dataset_id: int,
        valor: float,
        resolucion: float | None = None,
        valor_normalizado: float | None = None,
        periodo_inicio: date | None = None,
        periodo_fin: date | None = None,
        incertidumbre: float | None = None,
        n_muestras: int | None = None,
    ) -> None:
        self.id = id
        self.sitio_id = sitio_id
        self.caracteristica_id = caracteristica_id
        self.dataset_id = dataset_id
        self.valor = valor
        self.resolucion = resolucion
        self.valor_normalizado = valor_normalizado
        self.periodo_inicio = periodo_inicio
        self.periodo_fin = periodo_fin
        self.incertidumbre = incertidumbre
        self.n_muestras = n_muestras

    @classmethod
    def create(
        cls,
        *,
        sitio_id: int,
        caracteristica_id: int,
        dataset_id: int,
        valor: float,
        resolucion: float | None = None,
        valor_normalizado: float | None = None,
        periodo_inicio: date | None = None,
        periodo_fin: date | None = None,
        incertidumbre: float | None = None,
        n_muestras: int | None = None,
        rango_fisico: tuple[float | None, float | None] | None = None,
    ) -> "Medicion":
        """Crea una medición validando referencias, el valor y los metadatos.

        Si se pasa ``rango_fisico`` (``valor_min``, ``valor_max`` de la característica), un
        valor fuera de ese rango lanza ``InvalidMedicionDataException``: se valida antes de
        guardar y nunca se sustituye por otro valor.
        """
        valid_sitio_id = require_positive_id(
            sitio_id, "sitio_id", InvalidMedicionDataException
        )
        valid_caract_id = require_positive_id(
            caracteristica_id, "caracteristica_id", InvalidMedicionDataException
        )
        valid_dataset_id = require_positive_id(
            dataset_id, "dataset_id", InvalidMedicionDataException
        )
        minimo, maximo = rango_fisico if rango_fisico is not None else (None, None)
        valid_valor = require_in_range(
            valor,
            "valor",
            minimo if minimo is not None else float("-inf"),
            maximo if maximo is not None else float("inf"),
            InvalidMedicionDataException,
        )
        valid_norm = (
            require_unit_interval(
                valor_normalizado, "valor_normalizado", InvalidMedicionDataException
            )
            if valor_normalizado is not None
            else None
        )
        valid_incertidumbre = (
            require_non_negative(
                incertidumbre, "incertidumbre", InvalidMedicionDataException
            )
            if incertidumbre is not None
            else None
        )
        if n_muestras is not None and (isinstance(n_muestras, bool) or n_muestras < 1):
            raise InvalidMedicionDataException(
                "El campo 'n_muestras' debe ser un entero mayor o igual que 1."
            )
        if periodo_inicio and periodo_fin and periodo_inicio > periodo_fin:
            raise InvalidMedicionDataException(
                "'periodo_inicio' no puede ser posterior a 'periodo_fin'."
            )
        return cls(
            id=None,
            sitio_id=valid_sitio_id,
            caracteristica_id=valid_caract_id,
            dataset_id=valid_dataset_id,
            valor=valid_valor,
            resolucion=float(resolucion) if resolucion is not None else None,
            valor_normalizado=valid_norm,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            incertidumbre=valid_incertidumbre,
            n_muestras=n_muestras,
        )
