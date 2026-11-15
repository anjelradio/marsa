"""Modelo de tabla SQLModel para persistencia de cuerpo_celeste."""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Double
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.sitio.infrastructure.persistence.models.sitio_model import (
        SitioModel,
    )


class CuerpoCelesteModel(SQLModel, table=True):
    """Cuerpo planetario de referencia o destino (Tierra, Luna, Marte)."""

    __tablename__ = "cuerpo_celeste"
    __table_args__ = (
        CheckConstraint(
            "radio_km IS NULL OR radio_km > 0", name="ck_cuerpo_celeste_radio_positivo"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50, nullable=False, unique=True)
    radio_km: float | None = Field(default=None, sa_type=Double, nullable=True)

    sitios: list["SitioModel"] = Relationship(back_populates="cuerpo")
