"""Modelo de tabla SQLModel para persistencia de dataset."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Double, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
        MedicionModel,
    )


class DatasetModel(SQLModel, table=True):
    """Fuente de datos científica o satelital con metadatos de resolución y descarga."""

    __tablename__ = "dataset"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150, nullable=False)
    agencia: str | None = Field(default=None, max_length=100, nullable=True)
    url: str | None = Field(default=None, sa_type=Text, nullable=True)
    resolucion: float | None = Field(default=None, sa_type=Double, nullable=True)
    fecha_descarga: date | None = Field(default=None, nullable=True)

    mediciones: list["MedicionModel"] = Relationship(back_populates="dataset")
