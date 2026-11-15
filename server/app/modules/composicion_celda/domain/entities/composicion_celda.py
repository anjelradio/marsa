"""Entidad de dominio: composición de roca o mineral de un sitio o celda."""

from app.modules.composicion_celda.domain.exceptions import (
    InvalidComposicionCeldaDataException,
)
from app.shared.domain.validators import (
    require_in_range,
    require_non_empty_text,
    require_one_of,
    require_positive_id,
)

TIPOS_COMPOSICION = ("litologia", "mineral")


class ComposicionCelda:
    """Porcentaje (0 a 100) de un tipo de roca o de un mineral en un sitio o celda."""

    def __init__(
        self,
        id: int | None,
        sitio_id: int,
        dataset_id: int,
        tipo: str,
        nombre: str,
        porcentaje: float,
    ) -> None:
        self.id = id
        self.sitio_id = sitio_id
        self.dataset_id = dataset_id
        self.tipo = tipo
        self.nombre = nombre
        self.porcentaje = porcentaje

    @classmethod
    def create(
        cls,
        *,
        sitio_id: int,
        dataset_id: int,
        tipo: str,
        nombre: str,
        porcentaje: float,
    ) -> "ComposicionCelda":
        """Crea una composición validando referencias, tipo y porcentaje entre 0 y 100."""
        exc = InvalidComposicionCeldaDataException
        return cls(
            id=None,
            sitio_id=require_positive_id(sitio_id, "sitio_id", exc),
            dataset_id=require_positive_id(dataset_id, "dataset_id", exc),
            tipo=require_one_of(tipo, "tipo", TIPOS_COMPOSICION, exc),
            nombre=require_non_empty_text(nombre, "nombre", 100, exc),
            porcentaje=require_in_range(porcentaje, "porcentaje", 0.0, 100.0, exc),
        )
