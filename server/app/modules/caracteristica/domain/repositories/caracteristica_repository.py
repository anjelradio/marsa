"""Contrato de repositorio de dominio para caracteristica."""

from typing import Protocol

from app.modules.caracteristica.domain.entities.caracteristica import Caracteristica


class CaracteristicaRepository(Protocol):
    """Puerto secundario para la persistencia de Caracteristica."""

    def get_by_id(self, id: int) -> Caracteristica | None:
        """Obtiene la característica por su identificador entero."""
        ...

    def save(self, entity: Caracteristica) -> Caracteristica:
        """Persiste o actualiza la característica."""
        ...

    def delete(self, id: int) -> None:
        """Elimina la característica por su identificador."""
        ...
