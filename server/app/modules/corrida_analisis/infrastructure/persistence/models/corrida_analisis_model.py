"""Modelo de tabla SQLModel para las corridas del análisis de analogías."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class CorridaAnalisisModel(SQLModel, table=True):
    """Una ejecución del cálculo, identificada por versión y método."""

    __tablename__ = "corrida_analisis"
    __table_args__ = (
        UniqueConstraint("version", "metodo", name="uq_corrida_analisis_version_metodo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    version: str = Field(max_length=30, nullable=False)
    metodo: str = Field(max_length=60, nullable=False)
    fecha: datetime = Field(
        default_factory=_ahora, sa_type=DateTime(timezone=True), nullable=False
    )
    parametros: dict[str, Any] | None = Field(
        default=None,
        sa_type=JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )
