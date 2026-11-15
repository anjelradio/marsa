"""Modelo de tabla SQLModel para persistencia de sitio."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, Double
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
        AnalogiaModel,
    )
    from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
        CuerpoCelesteModel,
    )
    from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
        MedicionModel,
    )


class SitioModel(SQLModel, table=True):
    """Sitio de estudio terrestre, lunar o marciano."""

    __tablename__ = "sitio"
    __table_args__ = (
        CheckConstraint(
            "clase IN ('referencia', 'celda')", name="ck_sitio_clase_valida"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    cuerpo_id: int = Field(foreign_key="cuerpo_celeste.id", nullable=False)
    nombre: str = Field(max_length=100, nullable=False)
    tipo: str | None = Field(default=None, max_length=50, nullable=True)
    # 'referencia' = sitio con nombre propio; 'celda' = celda de la malla global.
    clase: str = Field(default="referencia", max_length=20, nullable=False)
    # Identificador único: celda (T_S20_W070) o referencia (R_atacama-yungay).
    codigo: str | None = Field(default=None, max_length=60, nullable=True, unique=True)
    lat_min: float | None = Field(default=None, sa_type=Double, nullable=True)
    lat_max: float | None = Field(default=None, sa_type=Double, nullable=True)
    lon_min: float | None = Field(default=None, sa_type=Double, nullable=True)
    lon_max: float | None = Field(default=None, sa_type=Double, nullable=True)
    # Almacena GeoJSON EPSG:4326 en JSONB mientras PostGIS no esté instalado en PostgreSQL 18.
    geom: dict[str, Any] | None = Field(
        default=None,
        sa_type=JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )

    cuerpo: "CuerpoCelesteModel" = Relationship(back_populates="sitios")
    mediciones: list["MedicionModel"] = Relationship(back_populates="sitio")
    analogias_como_tierra: list["AnalogiaModel"] = Relationship(
        back_populates="sitio_tierra",
        sa_relationship_kwargs={"foreign_keys": "AnalogiaModel.sitio_tierra_id"},
    )
    analogias_como_destino: list["AnalogiaModel"] = Relationship(
        back_populates="sitio_destino",
        sa_relationship_kwargs={"foreign_keys": "AnalogiaModel.sitio_destino_id"},
    )
