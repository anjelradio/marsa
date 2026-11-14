"""Entidad principal de dominio para medicion."""

from app.modules.medicion.domain.exceptions import InvalidMedicionDataException
from app.shared.domain.validators import (
    require_positive_id,
    require_unit_interval,
)


class Medicion:
    """Entidad de dominio que vincula un sitio, una característica y un dataset."""

    def __init__(
        self,
        id: int | None,
        sitio_id: int,
        caracteristica_id: int,
        dataset_id: int,
        valor: float,
        resolucion: float | None = None,
        valor_normalizado: float | None = None,
    ) -> None:
        self.id = id
        self.sitio_id = sitio_id
        self.caracteristica_id = caracteristica_id
        self.dataset_id = dataset_id
        self.valor = valor
        self.resolucion = resolucion
        self.valor_normalizado = valor_normalizado

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
    ) -> "Medicion":
        """Crea una medición validando referencias positivas y valor_normalizado en [0, 1]."""
        valid_sitio_id = require_positive_id(
            sitio_id, "sitio_id", InvalidMedicionDataException
        )
        valid_caract_id = require_positive_id(
            caracteristica_id, "caracteristica_id", InvalidMedicionDataException
        )
        valid_dataset_id = require_positive_id(
            dataset_id, "dataset_id", InvalidMedicionDataException
        )
        valid_norm = (
            require_unit_interval(
                valor_normalizado, "valor_normalizado", InvalidMedicionDataException
            )
            if valor_normalizado is not None
            else None
        )
        return cls(
            id=None,
            sitio_id=valid_sitio_id,
            caracteristica_id=valid_caract_id,
            dataset_id=valid_dataset_id,
            valor=float(valor),
            resolucion=float(resolucion) if resolucion is not None else None,
            valor_normalizado=valid_norm,
        )
