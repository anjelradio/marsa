"""Contrato de repositorio de dominio para medicion."""

from typing import Protocol

from app.modules.medicion.domain.entities.medicion import Medicion


class MedicionRepository(Protocol):
    """Puerto secundario para la persistencia de Medicion."""

    def get_by_id(self, id: int) -> Medicion | None:
        """Obtiene la medición por su identificador entero."""
        ...

    def save(self, entity: Medicion) -> Medicion:
        """Persiste o actualiza la medición."""
        ...

    def delete(self, id: int) -> None:
        """Elimina la medición por su identificador."""
        ...
