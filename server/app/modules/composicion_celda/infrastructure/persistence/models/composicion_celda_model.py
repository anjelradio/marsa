"""Modelo de tabla SQLModel para la composición de roca y minerales de un sitio o celda."""

from sqlalchemy import CheckConstraint, Double, UniqueConstraint
from sqlmodel import Field, SQLModel


class ComposicionCeldaModel(SQLModel, table=True):
    """Porcentaje de un tipo de roca (litología) o de un mineral en un sitio o celda."""

    __tablename__ = "composicion_celda"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('litologia', 'mineral')", name="ck_composicion_celda_tipo_valido"
        ),
        CheckConstraint(
            "porcentaje BETWEEN 0 AND 100", name="ck_composicion_celda_porcentaje_rango"
        ),
        UniqueConstraint(
            "sitio_id",
            "dataset_id",
            "tipo",
            "nombre",
            name="uq_composicion_celda_sitio_dataset_tipo_nombre",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    sitio_id: int = Field(foreign_key="sitio.id", nullable=False)
    dataset_id: int = Field(foreign_key="dataset.id", nullable=False)
    tipo: str = Field(max_length=20, nullable=False)
    nombre: str = Field(max_length=100, nullable=False)
    porcentaje: float = Field(sa_type=Double, nullable=False)
