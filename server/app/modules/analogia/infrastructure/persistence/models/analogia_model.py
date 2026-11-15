"""Modelo de tabla SQLModel para persistencia de analogia."""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Double, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.sitio.infrastructure.persistence.models.sitio_model import (
        SitioModel,
    )


class AnalogiaModel(SQLModel, table=True):
    """Relación de analogía calculada entre un sitio en la Tierra y un sitio destino."""

    __tablename__ = "analogia"
    __table_args__ = (
        CheckConstraint(
            "similitud BETWEEN 0 AND 1",
            name="ck_analogia_similitud_rango",
        ),
        CheckConstraint(
            "cobertura BETWEEN 0 AND 1",
            name="ck_analogia_cobertura_rango",
        ),
        UniqueConstraint(
            "sitio_tierra_id",
            "sitio_destino_id",
            name="uq_analogia_sitio_tierra_destino",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    sitio_tierra_id: int = Field(foreign_key="sitio.id", nullable=False)
    sitio_destino_id: int = Field(foreign_key="sitio.id", nullable=False)
    similitud: float | None = Field(default=None, sa_type=Double, nullable=True)
    cobertura: float | None = Field(default=None, sa_type=Double, nullable=True)
    metodo: str | None = Field(default=None, sa_type=Text, nullable=True)
    coincide: str | None = Field(default=None, sa_type=Text, nullable=True)
    difiere: str | None = Field(default=None, sa_type=Text, nullable=True)

    sitio_tierra: "SitioModel" = Relationship(
        back_populates="analogias_como_tierra",
        sa_relationship_kwargs={"foreign_keys": "AnalogiaModel.sitio_tierra_id"},
    )
    sitio_destino: "SitioModel" = Relationship(
        back_populates="analogias_como_destino",
        sa_relationship_kwargs={"foreign_keys": "AnalogiaModel.sitio_destino_id"},
    )
