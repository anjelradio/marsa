"""Las migraciones de Alembic deben producir el esquema de los modelos y conservar los datos."""

import io

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlmodel import SQLModel

import app.shared.infrastructure.db.models  # noqa: F401
from app.core.database import BASELINE_REVISION, _alembic_config, run_migrations

TABLES = {
    "cuerpo_celeste",
    "sitio",
    "dataset",
    "caracteristica",
    "medicion",
    "analogia",
    "composicion_celda",
    "corrida_analisis",
}
FISICAS = {  # nombre -> peso global del esquema base
    "Temperatura Superficial": 0.25,
    "Nubosidad": 0.10,
    "Inercia Térmica": 0.15,
    "Profundidad Óptica de Polvo": 0.10,
    "Hielo/Agua Superficial": 0.15,
    "Elevación": 0.10,
    "Rugosidad del Terreno": 0.15,
}
MINERALES = {
    "Plagioclasa": 0.15,
    "Piroxeno (Augita/Pigeonita)": 0.15,
    "Olivino (Forsterita)": 0.15,
    "Óxidos Férricos (Hematita/Magnetita)": 0.15,
    "Filosilicatos / Minerales Hidratados": 0.15,
    "Ilmenita": 0.15,
    "Sulfatos (Jarosita/Yeso)": 0.10,
}


def _url(tmp_path) -> str:
    return f"sqlite:///{(tmp_path / 'm.db').as_posix()}"


def _head(url: str) -> str:
    return ScriptDirectory.from_config(_alembic_config(url)).get_current_head()


def _rows(url: str, sql: str) -> list[tuple]:
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            return [tuple(row) for row in connection.execute(text(sql))]
    finally:
        engine.dispose()


def _legacy_database(tmp_path, mineral_value: float = 12.0) -> str:
    """Base de datos en el esquema base (como la dejaba el seed anterior): 14 características."""
    url = _url(tmp_path)
    command.upgrade(_alembic_config(url), BASELINE_REVISION)
    engine = create_engine(url)
    with engine.begin() as c:
        c.execute(text("INSERT INTO cuerpo_celeste (nombre) VALUES ('Tierra'), ('Marte')"))
        c.execute(text("INSERT INTO dataset (nombre) VALUES ('NASA POWER'), ('GLiM')"))
        c.execute(text(
            "INSERT INTO sitio (cuerpo_id, nombre, tipo) VALUES (1, 'Atacama', 'Desierto'), (2, 'Gale', 'Cráter')"
        ))
        for nombre, peso in {**FISICAS, **MINERALES}.items():
            unidad = "% wt" if nombre in MINERALES else "x"
            c.execute(
                text("INSERT INTO caracteristica (nombre, unidad, rango, peso) VALUES (:n, :u, 100.0, :p)"),
                {"n": nombre, "u": unidad, "p": peso},
            )
        # 2 sitios x 14 características; los minerales usan `mineral_value` (% wt)
        for sitio_id in (1, 2):
            for car_id, nombre in enumerate({**FISICAS, **MINERALES}, start=1):
                valor = mineral_value if nombre in MINERALES else 50.0
                c.execute(
                    text(
                        "INSERT INTO medicion (sitio_id, caracteristica_id, dataset_id, valor, valor_normalizado) "
                        "VALUES (:s, :c, :d, :v, 0.5)"
                    ),
                    {"s": sitio_id, "c": car_id, "d": 1 if nombre in FISICAS else 2, "v": valor},
                )
        c.execute(text(
            "INSERT INTO analogia (sitio_tierra_id, sitio_destino_id, similitud, cobertura, metodo) "
            "VALUES (1, 2, 0.8, 1.0, 'ponderado-v1')"
        ))
    engine.dispose()
    return url


# ── el esquema ────────────────────────────────────────────────────────────────────────


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


def test_database_created_before_alembic_is_stamped_and_upgraded(tmp_path) -> None:
    url = _legacy_database(tmp_path)
    engine = create_engine(url)
    with engine.begin() as c:
        c.execute(text("DROP TABLE alembic_version"))  # así quedaba una base creada con create_all
    engine.dispose()

    run_migrations(url)  # no debe fallar con "table already exists"
    run_migrations(url)  # y debe poder repetirse

    assert _rows(url, "SELECT version_num FROM alembic_version") == [(_head(url),)]
    assert _rows(url, "SELECT nombre FROM cuerpo_celeste ORDER BY id") == [("Tierra",), ("Marte",)]
    assert _rows(url, "SELECT COUNT(*) FROM composicion_celda") == [(14,)]  # los datos viajaron


# ── la migración de datos ─────────────────────────────────────────────────────────────


def test_data_migration_regroups_variables_and_moves_minerals(tmp_path) -> None:
    url = _legacy_database(tmp_path)
    run_migrations(url)

    # las 7 variables físicas: grupo, peso dentro del grupo y rango físico
    caracteristicas = {
        nombre: (grupo, peso, vmin, vmax)
        for nombre, grupo, peso, vmin, vmax in _rows(
            url, "SELECT nombre, grupo, peso, valor_min, valor_max FROM caracteristica"
        )
    }
    assert set(caracteristicas) == set(FISICAS)  # los minerales ya no son características
    assert caracteristicas["Temperatura Superficial"][0] == "fisico"
    assert caracteristicas["Elevación"][0] == "terreno"
    assert caracteristica_range(caracteristicas, "Elevación") == (-12000.0, 22000.0)
    assert caracteristica_range(caracteristicas, "Temperatura Superficial") == (0.0, 500.0)
    for grupo in ("fisico", "terreno"):
        suma = sum(p for g, p, _, _ in caracteristicas.values() if g == grupo)
        assert suma == pytest.approx(1.0)
    assert caracteristicas["Rugosidad del Terreno"][1] == pytest.approx(0.6)
    assert caracteristicas["Temperatura Superficial"][1] == pytest.approx(1 / 3)

    # los minerales pasaron a la composición con su porcentaje y su dataset
    assert _rows(url, "SELECT COUNT(*) FROM medicion") == [(14,)]  # 2 sitios x 7 físicas
    composicion = _rows(url, "SELECT tipo, nombre, porcentaje, dataset_id FROM composicion_celda")
    assert len(composicion) == 14
    assert {fila[0] for fila in composicion} == {"mineral"}
    assert {fila[1] for fila in composicion} == set(MINERALES)
    assert {fila[2] for fila in composicion} == {12.0}
    assert {fila[3] for fila in composicion} == {2}

    # la analogía existente pertenece a la corrida inicial
    assert _rows(url, "SELECT version, metodo FROM corrida_analisis") == [("v1-inicial", "ponderado-v1")]
    assert _rows(url, "SELECT a.corrida_id = c.id FROM analogia a, corrida_analisis c") == [(1,)]


def caracteristica_range(caracteristicas: dict, nombre: str) -> tuple[float, float]:
    _, _, vmin, vmax = caracteristicas[nombre]
    return vmin, vmax


def test_empty_database_gets_no_initial_run(tmp_path) -> None:
    url = _url(tmp_path)
    run_migrations(url)
    assert _rows(url, "SELECT COUNT(*) FROM corrida_analisis") == [(0,)]


def test_downgrade_restores_minerals_and_global_weights(tmp_path) -> None:
    url = _legacy_database(tmp_path)
    run_migrations(url)
    command.downgrade(_alembic_config(url), BASELINE_REVISION)

    pesos = dict(_rows(url, "SELECT nombre, peso FROM caracteristica"))
    assert pesos == pytest.approx({**FISICAS, **MINERALES})
    assert _rows(url, "SELECT COUNT(*) FROM medicion") == [(28,)]  # 2 sitios x 14
    assert _rows(url, "SELECT valor FROM medicion m JOIN caracteristica c ON c.id = m.caracteristica_id "
                      "WHERE c.nombre = 'Ilmenita' ORDER BY m.id") == [(12.0,), (12.0,)]
    assert _rows(url, "SELECT COUNT(*) FROM analogia") == [(1,)]
    assert set(inspect(create_engine(url)).get_table_names()) >= {"alembic_version"}


@pytest.mark.parametrize("valor", [150.0, -1.0])
def test_mineral_percentage_out_of_range_aborts_without_changes(tmp_path, valor: float) -> None:
    url = _legacy_database(tmp_path, mineral_value=valor)

    with pytest.raises(RuntimeError, match="fuera de 0 a 100"):
        run_migrations(url)

    # se validó antes de tocar nada: sigue en la revisión base, sin tablas ni columnas nuevas
    assert _rows(url, "SELECT version_num FROM alembic_version") == [(BASELINE_REVISION,)]
    engine = create_engine(url)
    assert "composicion_celda" not in inspect(engine).get_table_names()
    assert "grupo" not in {c["name"] for c in inspect(engine).get_columns("caracteristica")}
    engine.dispose()
    assert _rows(url, "SELECT COUNT(*) FROM caracteristica") == [(14,)]


# ── PostgreSQL ────────────────────────────────────────────────────────────────────────


def test_postgres_sql_is_generated_without_a_connection_and_with_literal_values() -> None:
    """`alembic upgrade head --sql` sirve para producción: los valores van escritos en el SQL."""
    config = _alembic_config("postgresql+psycopg://u:p@localhost/db")
    config.output_buffer = io.StringIO()
    command.upgrade(config, "head", sql=True)
    sql = config.output_buffer.getvalue()

    assert "JSONB" in sql
    assert "UPDATE caracteristica SET grupo = 'fisico'" in sql
    assert "WHERE nombre = 'Temperatura Superficial'" in sql
    assert "= NULL" not in sql  # un parámetro sin sustituir corrompería los datos
    assert "INSERT INTO composicion_celda" in sql
