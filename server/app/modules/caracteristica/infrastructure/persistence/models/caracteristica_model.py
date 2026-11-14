"""Modelo de tabla SQLModel para persistencia de caracteristica."""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Double
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
        MedicionModel,
    )


class CaracteristicaModel(SQLModel, table=True):
    """Variable física o química medida con rango de normalización y peso."""

    __tablename__ = "caracteristica"
    __table_args__ = (
        CheckConstraint("rango > 0", name="ck_caracteristica_rango_positivo"),
        CheckConstraint("peso BETWEEN 0 AND 1", name="ck_caracteristica_peso_rango"),
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False, unique=True)
    unidad: str | None = Field(default=None, max_length=20, nullable=True)
    rango: float = Field(sa_type=Double, nullable=False)
    peso: float = Field(sa_type=Double, nullable=False)

    mediciones: list["MedicionModel"] = Relationship(back_populates="caracteristica")
