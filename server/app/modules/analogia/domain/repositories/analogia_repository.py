"""Contrato de repositorio de dominio para analogia."""

from typing import Protocol

from app.modules.analogia.domain.entities.analogia import Analogia


class AnalogiaRepository(Protocol):
    """Puerto secundario para la persistencia de Analogia."""

    def get_by_id(self, id: int) -> Analogia | None:
        """Obtiene la analogía por su identificador entero."""
        ...

    def save(self, entity: Analogia) -> Analogia:
        """Persiste o actualiza la analogía."""
        ...

    def delete(self, id: int) -> None:
        """Elimina la analogía por su identificador."""
        ...
