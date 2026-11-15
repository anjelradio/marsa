"""Contrato de repositorio de dominio para sitio."""

from typing import Protocol

from app.modules.sitio.domain.entities.sitio import Sitio


class SitioRepository(Protocol):
    """Puerto secundario para la persistencia de Sitio."""

    def get_by_id(self, id: int) -> Sitio | None:
        """Obtiene el sitio por su identificador entero."""
        ...

    def save(self, entity: Sitio) -> Sitio:
        """Persiste o actualiza el sitio."""
        ...

    def delete(self, id: int) -> None:
        """Elimina el sitio por su identificador."""
        ...
