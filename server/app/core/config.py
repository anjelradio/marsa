from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ruta absoluta al directorio 'server' y ubicación esperada de .env
SERVER_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = SERVER_DIR / ".env"
ROOT_ENV_FILE_PATH = SERVER_DIR.parent / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="API", env="PROJECT_NAME")
    ENVIRONMENT: str = Field(default="DEV", env="ENVIRONMENT")

    # ── Base de datos ─────────────────────────────────────────────────────────
    # Valor por defecto: SQLite local para poder arrancar sin configurar nada.
    # En producción (Render / Railway / Fly.io) o en local contra Neon,
    # define DATABASE_URL en tu .env con la URL completa de PostgreSQL.
    DATABASE_URL: str = Field(default="sqlite:///./dev.db", env="DATABASE_URL")
    SQL_ECHO: bool = Field(default=False, env="SQL_ECHO")

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str | list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS",
    )

    # ── Servicios Satelitales & Topográficos ─────────────────────────────────
    USGS_STAC_API_URL: str = Field(
        default="https://stac.astrogeology.usgs.gov/api",
        env="USGS_STAC_API_URL",
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    @property
    def database_url_normalized(self) -> str:
        """
        Devuelve la DATABASE_URL lista para SQLAlchemy con el driver correcto.

        Reglas:
        - SQLite  → se mantiene tal cual (usado en DEV por defecto).
        - postgres:// o postgresql:// sin driver explícito
          → se convierte a postgresql+psycopg://  (psycopg v3, el que
            tenemos instalado vía psycopg / psycopg-binary).
        """
        url = self.DATABASE_URL.strip()

        if url.startswith("sqlite"):
            return url

        # Normalizar a psycopg v3
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return "postgresql+psycopg://" + url[len("postgresql://"):]

        return url

    @property
    def is_sqlite(self) -> bool:
        return self.database_url_normalized.startswith("sqlite")

    model_config = SettingsConfigDict(
        env_file=[str(ENV_FILE_PATH), str(ROOT_ENV_FILE_PATH), ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
