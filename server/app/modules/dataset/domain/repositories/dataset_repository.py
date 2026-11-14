"""Contrato de repositorio de dominio para dataset."""

from typing import Protocol

from app.modules.dataset.domain.entities.dataset import Dataset


class DatasetRepository(Protocol):
    """Puerto secundario para la persistencia de Dataset."""

    def get_by_id(self, id: int) -> Dataset | None:
        """Obtiene el dataset por su identificador entero."""
        ...

    def save(self, entity: Dataset) -> Dataset:
        """Persiste o actualiza el dataset."""
        ...

    def delete(self, id: int) -> None:
        """Elimina el dataset por su identificador."""
        ...
