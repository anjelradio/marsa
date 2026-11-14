"""Modelo de tabla SQLModel para persistencia de medicion."""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Double, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
        CaracteristicaModel,
    )
    from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
        DatasetModel,
    )
    from app.modules.sitio.infrastructure.persistence.models.sitio_model import (
        SitioModel,
    )


class MedicionModel(SQLModel, table=True):
    """Medición observada de una característica sobre un sitio y dataset dado."""

    __tablename__ = "medicion"
    __table_args__ = (
        CheckConstraint(
            "valor_normalizado BETWEEN 0 AND 1",
            name="ck_medicion_valor_normalizado_rango",
        ),
        UniqueConstraint(
            "sitio_id",
            "caracteristica_id",
            "dataset_id",
            name="uq_medicion_sitio_caracteristica_dataset",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    sitio_id: int = Field(foreign_key="sitio.id", nullable=False)
    caracteristica_id: int = Field(foreign_key="caracteristica.id", nullable=False)
    dataset_id: int = Field(foreign_key="dataset.id", nullable=False)
    valor: float = Field(sa_type=Double, nullable=False)
    resolucion: float | None = Field(default=None, sa_type=Double, nullable=True)
    valor_normalizado: float | None = Field(
        default=None,
        sa_type=Double,
        nullable=True,
    )

    sitio: "SitioModel" = Relationship(back_populates="mediciones")
    caracteristica: "CaracteristicaModel" = Relationship(back_populates="mediciones")
    dataset: "DatasetModel" = Relationship(back_populates="mediciones")
