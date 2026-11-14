"""Contrato de repositorio de dominio para cuerpo_celeste."""

from typing import Protocol

from app.modules.cuerpo_celeste.domain.entities.cuerpo_celeste import CuerpoCeleste


class CuerpoCelesteRepository(Protocol):
    """Puerto secundario para la persistencia de CuerpoCeleste."""

    def get_by_id(self, id: int) -> CuerpoCeleste | None:
        """Obtiene el cuerpo celeste por su identificador entero."""
        ...

    def save(self, entity: CuerpoCeleste) -> CuerpoCeleste:
        """Persiste o actualiza el cuerpo celeste."""
        ...

    def delete(self, id: int) -> None:
        """Elimina el cuerpo celeste por su identificador."""
        ...
