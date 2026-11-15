"""Las migraciones de Alembic deben producir exactamente el esquema de los modelos."""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlmodel import SQLModel

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import BASELINE_REVISION, _alembic_config, run_migrations

TABLES = {"cuerpo_celeste", "sitio", "dataset", "caracteristica", "medicion", "analogia"}


def _url(tmp_path) -> str:
    return f"sqlite:///{(tmp_path / 'm.db').as_posix()}"


def test_upgrade_creates_every_table_and_matches_the_models(tmp_path) -> None:
    url = _url(tmp_path)
    run_migrations(url)

    engine = create_engine(url)
    assert TABLES | {"alembic_version"} <= set(inspect(engine).get_table_names())
    with engine.connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), SQLModel.metadata)
    engine.dispose()
    assert diff == []  # si cambias un modelo, falta su migración


def test_downgrade_to_base_leaves_only_the_version_table(tmp_path) -> None:
    url = _url(tmp_path)
    run_migrations(url)
    command.downgrade(_alembic_config(url), "base")

    engine = create_engine(url)
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
    engine.dispose()


def test_database_created_with_create_all_is_stamped_not_recreated(tmp_path) -> None:
    url = _url(tmp_path)
    legacy = create_engine(url)
    SQLModel.metadata.create_all(legacy)  # como se creaba antes de Alembic
    with legacy.begin() as connection:
        connection.execute(text("INSERT INTO cuerpo_celeste (nombre) VALUES ('Tierra')"))

    run_migrations(url)  # no debe fallar con "table already exists"
    run_migrations(url)  # y debe poder repetirse

    with legacy.connect() as connection:
        versions = connection.execute(text("SELECT version_num FROM alembic_version")).all()
        bodies = connection.execute(text("SELECT nombre FROM cuerpo_celeste")).all()
    legacy.dispose()
    assert len(versions) == 1
    assert bodies == [("Tierra",)]  # los datos existentes se conservan
    assert BASELINE_REVISION  # la revisión de partida existe


def test_postgres_baseline_renders_without_a_connection() -> None:
    """El SQL para PostgreSQL se puede generar sin conexión (`alembic upgrade head --sql`)."""
    config = _alembic_config("postgresql+psycopg://u:p@localhost/db")
    command.upgrade(config, "head", sql=True)
