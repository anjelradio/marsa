from pathlib import Path
from typing import Iterator

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
import app.shared.infrastructure.db.models  # noqa: F401

SERVER_DIR = Path(__file__).resolve().parents[2]
# Revisión que describe el esquema creado antes con `create_all` (sin tabla de versión).
BASELINE_REVISION = "3bdf6504dd25"

# ── Argumentos condicionales según el motor ───────────────────────────────────
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
pool_pre_ping = not settings.is_sqlite  # ping preventivo solo en PostgreSQL

engine = create_engine(
    settings.database_url_normalized,
    echo=settings.SQL_ECHO,
    connect_args=connect_args,
    pool_pre_ping=pool_pre_ping,
)


def init_db() -> None:
    """
    Crea las tablas definidas en SQLModel.metadata.

    ⚠️  Úsalo SOLO en DEV cuando no quieras gestionar migraciones.
    En PROD (o cuando uses Alembic), este método no se llama —
    las tablas las crea/actualiza `alembic upgrade head`.
    """
    SQLModel.metadata.create_all(engine)


def _alembic_config(url: str | None = None) -> Config:
    """Configuración de Alembic sin archivo .ini, para que env.py no reconfigure el logging."""
    config = Config()
    config.set_main_option("script_location", str(SERVER_DIR / "alembic"))
    if url:
        config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return config


def run_migrations(url: str | None = None) -> None:
    """Deja la base de datos en la última versión del esquema (`alembic upgrade head`).

    Una base creada antes con `create_all` (con tablas pero sin tabla de versión) se marca
    primero en la revisión base, para no intentar crear otra vez sus tablas, y después se
    actualiza con las migraciones que falten.
    """
    target = create_engine(url) if url else engine
    try:
        tables = set(inspect(target).get_table_names())
    finally:
        if url:
            target.dispose()
    config = _alembic_config(url)
    if "alembic_version" not in tables and "sitio" in tables:
        command.stamp(config, BASELINE_REVISION)
    command.upgrade(config, "head")


def get_session() -> Iterator[Session]:
    """Dependencia FastAPI que provee una sesión de BD por request."""
    with Session(engine) as session:
        yield session
