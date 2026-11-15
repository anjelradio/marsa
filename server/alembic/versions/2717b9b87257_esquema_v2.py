"""esquema v2: grupos, periodo e incertidumbre, composición, corridas y puntuación por grupo

Cambios de esquema
  - cuerpo_celeste: radio_km.
  - sitio: clase (referencia o celda), codigo único y límites de latitud y longitud.
  - caracteristica: grupo (fisico o terreno), rango físico (valor_min y valor_max); el peso pasa
    a ser el peso dentro del grupo.
  - medicion: periodo, incertidumbre y número de muestras.
  - composicion_celda (nueva): porcentaje de cada roca o mineral de un sitio o celda.
  - corrida_analisis (nueva): historial de ejecuciones del análisis.
  - analogia: corrida_id, puntuaciones por grupo y estabilidad; la clave única incluye la corrida.

Migración de datos
  - Las 7 variables físicas reciben su grupo, su peso dentro del grupo y su rango físico.
  - Las características minerales y sus mediciones pasan a composicion_celda (tipo mineral).
    Si algún porcentaje queda fuera de 0 a 100 la migración se detiene sin cambiar nada.
  - Las analogías existentes se asignan a una corrida inicial.

Revision ID: 2717b9b87257
Revises: 3bdf6504dd25
Create Date: 2026-11-15 11:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2717b9b87257"
down_revision: Union[str, Sequence[str], None] = "3bdf6504dd25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# nombre -> (grupo, peso global anterior, valor_min, valor_max)
VARIABLES: dict[str, tuple[str, float, float, float]] = {
    "Temperatura Superficial": ("fisico", 0.25, 0.0, 500.0),
    "Nubosidad": ("fisico", 0.10, 0.0, 100.0),
    "Inercia Térmica": ("fisico", 0.15, 0.0, 2500.0),
    "Profundidad Óptica de Polvo": ("fisico", 0.10, 0.0, 10.0),
    "Hielo/Agua Superficial": ("fisico", 0.15, 0.0, 100.0),
    "Elevación": ("terreno", 0.10, -12000.0, 22000.0),
    "Rugosidad del Terreno": ("terreno", 0.15, 0.0, 1000.0),
}
# Características minerales que antes vivían como variables físicas: nombre -> peso global anterior.
MINERALES: dict[str, float] = {
    "Plagioclasa": 0.15,
    "Piroxeno (Augita/Pigeonita)": 0.15,
    "Olivino (Forsterita)": 0.15,
    "Óxidos Férricos (Hematita/Magnetita)": 0.15,
    "Filosilicatos / Minerales Hidratados": 0.15,
    "Ilmenita": 0.15,
    "Sulfatos (Jarosita/Yeso)": 0.10,
}


def _peso_en_grupo(nombre: str) -> float:
    grupo, peso, _, _ = VARIABLES[nombre]
    total = sum(p for g, p, _, _ in VARIABLES.values() if g == grupo)
    return peso / total


def _q(text: str) -> str:
    """Literal SQL entre comillas simples (todos los valores salen de constantes de este archivo)."""
    return "'" + text.replace("'", "''") + "'"


MINERALES_SQL = ", ".join(_q(nombre) for nombre in MINERALES)


def _comprobar_minerales() -> None:
    """Detiene la migración, sin cambiar nada, si hay porcentajes minerales fuera de 0 a 100.

    En modo SQL no hay conexión para consultar; allí protege la restricción CHECK de la tabla nueva.
    """
    if op.get_context().as_sql:
        return
    fuera = op.get_bind().execute(
        sa.text(
            "SELECT COUNT(*) FROM medicion m JOIN caracteristica c ON c.id = m.caracteristica_id "
            f"WHERE c.nombre IN ({MINERALES_SQL}) AND (m.valor < 0 OR m.valor > 100)"
        )
    ).scalar_one()
    if fuera:
        raise RuntimeError(
            f"{fuera} medición(es) mineral(es) tienen un porcentaje fuera de 0 a 100; "
            "corrígelas antes de migrar."
        )


def upgrade() -> None:
    _comprobar_minerales()  # antes de cualquier cambio de esquema

    # ── cuerpo_celeste ──────────────────────────────────────────────────────────────
    with op.batch_alter_table("cuerpo_celeste") as batch:
        batch.add_column(sa.Column("radio_km", sa.Double(), nullable=True))
        batch.create_check_constraint(
            "ck_cuerpo_celeste_radio_positivo", "radio_km IS NULL OR radio_km > 0"
        )

    # ── sitio ───────────────────────────────────────────────────────────────────────
    with op.batch_alter_table("sitio") as batch:
        batch.add_column(
            sa.Column("clase", sa.String(length=20), nullable=False, server_default="referencia")
        )
        batch.add_column(sa.Column("codigo", sa.String(length=60), nullable=True))
        for nombre in ("lat_min", "lat_max", "lon_min", "lon_max"):
            batch.add_column(sa.Column(nombre, sa.Double(), nullable=True))
        batch.create_unique_constraint("uq_sitio_codigo", ["codigo"])
        batch.create_check_constraint(
            "ck_sitio_clase_valida", "clase IN ('referencia', 'celda')"
        )

    # ── caracteristica ──────────────────────────────────────────────────────────────
    with op.batch_alter_table("caracteristica") as batch:
        batch.add_column(
            sa.Column("grupo", sa.String(length=20), nullable=False, server_default="fisico")
        )
        batch.add_column(sa.Column("valor_min", sa.Double(), nullable=True))
        batch.add_column(sa.Column("valor_max", sa.Double(), nullable=True))
        batch.create_check_constraint(
            "ck_caracteristica_grupo_valido", "grupo IN ('fisico', 'terreno')"
        )
        batch.create_check_constraint(
            "ck_caracteristica_rango_fisico_orden",
            "valor_min IS NULL OR valor_max IS NULL OR valor_min < valor_max",
        )

    # ── medicion ────────────────────────────────────────────────────────────────────
    with op.batch_alter_table("medicion") as batch:
        batch.add_column(sa.Column("periodo_inicio", sa.Date(), nullable=True))
        batch.add_column(sa.Column("periodo_fin", sa.Date(), nullable=True))
        batch.add_column(sa.Column("incertidumbre", sa.Double(), nullable=True))
        batch.add_column(sa.Column("n_muestras", sa.Integer(), nullable=True))
        batch.create_check_constraint(
            "ck_medicion_incertidumbre_no_negativa", "incertidumbre IS NULL OR incertidumbre >= 0"
        )
        batch.create_check_constraint(
            "ck_medicion_n_muestras_positivo", "n_muestras IS NULL OR n_muestras >= 1"
        )
        batch.create_check_constraint(
            "ck_medicion_periodo_orden",
            "periodo_inicio IS NULL OR periodo_fin IS NULL OR periodo_inicio <= periodo_fin",
        )

    # ── tablas nuevas ───────────────────────────────────────────────────────────────
    op.create_table(
        "composicion_celda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sitio_id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("porcentaje", sa.Double(), nullable=False),
        sa.CheckConstraint("porcentaje BETWEEN 0 AND 100", name="ck_composicion_celda_porcentaje_rango"),
        sa.CheckConstraint("tipo IN ('litologia', 'mineral')", name="ck_composicion_celda_tipo_valido"),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.ForeignKeyConstraint(["sitio_id"], ["sitio.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "sitio_id", "dataset_id", "tipo", "nombre",
            name="uq_composicion_celda_sitio_dataset_tipo_nombre",
        ),
    )
    op.create_table(
        "corrida_analisis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=30), nullable=False),
        sa.Column("metodo", sa.String(length=60), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "parametros",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version", "metodo", name="uq_corrida_analisis_version_metodo"),
    )

    # ── analogia (corrida_id queda sin NOT NULL hasta asignar la corrida inicial) ─────
    with op.batch_alter_table("analogia") as batch:
        batch.add_column(sa.Column("corrida_id", sa.Integer(), nullable=True))
        for nombre in ("sim_fisica", "sim_terreno", "sim_geologica", "estabilidad"):
            batch.add_column(sa.Column(nombre, sa.Double(), nullable=True))
            batch.create_check_constraint(
                f"ck_analogia_{nombre}_rango", f"{nombre} IS NULL OR {nombre} BETWEEN 0 AND 1"
            )
        batch.drop_constraint("uq_analogia_sitio_tierra_destino", type_="unique")

    # ── migración de datos (SQL puro: funciona también en modo `--sql`) ───────────────
    # (a) grupo, peso dentro del grupo y rango físico de las 7 variables físicas
    for nombre, (grupo, _, vmin, vmax) in VARIABLES.items():
        op.execute(
            sa.text(
                f"UPDATE caracteristica SET grupo = {_q(grupo)}, peso = {_peso_en_grupo(nombre)!r}, "
                f"valor_min = {vmin!r}, valor_max = {vmax!r} WHERE nombre = {_q(nombre)}"
            )
        )

    # (b) minerales: de variable física a composición de la celda
    op.execute(
        sa.text(
            "INSERT INTO composicion_celda (sitio_id, dataset_id, tipo, nombre, porcentaje) "
            "SELECT m.sitio_id, m.dataset_id, 'mineral', c.nombre, m.valor "
            "FROM medicion m JOIN caracteristica c ON c.id = m.caracteristica_id "
            f"WHERE c.nombre IN ({MINERALES_SQL})"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM medicion WHERE caracteristica_id IN "
            f"(SELECT id FROM caracteristica WHERE nombre IN ({MINERALES_SQL}))"
        )
    )
    op.execute(sa.text(f"DELETE FROM caracteristica WHERE nombre IN ({MINERALES_SQL})"))

    # (c) las analogías existentes pertenecen a una corrida inicial (solo si hay analogías)
    op.execute(
        sa.text(
            "INSERT INTO corrida_analisis (version, metodo, fecha) "
            "SELECT 'v1-inicial', 'ponderado-v1', CURRENT_TIMESTAMP "
            "WHERE EXISTS (SELECT 1 FROM analogia)"
        )
    )
    op.execute(
        sa.text(
            "UPDATE analogia SET corrida_id = (SELECT id FROM corrida_analisis "
            "WHERE version = 'v1-inicial' AND metodo = 'ponderado-v1')"
        )
    )

    # ── restricciones finales y limpieza de valores por defecto ───────────────────────
    with op.batch_alter_table("analogia") as batch:
        batch.alter_column("corrida_id", existing_type=sa.Integer(), nullable=False)
        batch.create_foreign_key(
            "fk_analogia_corrida_id_corrida_analisis", "corrida_analisis", ["corrida_id"], ["id"]
        )
        batch.create_unique_constraint(
            "uq_analogia_corrida_tierra_destino",
            ["corrida_id", "sitio_tierra_id", "sitio_destino_id"],
        )
    with op.batch_alter_table("sitio") as batch:
        batch.alter_column(
            "clase", existing_type=sa.String(length=20), existing_nullable=False, server_default=None
        )
    with op.batch_alter_table("caracteristica") as batch:
        batch.alter_column(
            "grupo", existing_type=sa.String(length=20), existing_nullable=False, server_default=None
        )


def downgrade() -> None:
    # ── analogia: se conserva solo la última corrida para poder volver a la clave anterior ──
    op.execute(
        sa.text("DELETE FROM analogia WHERE corrida_id <> (SELECT MAX(id) FROM corrida_analisis)")
    )
    with op.batch_alter_table("analogia") as batch:
        batch.drop_constraint("uq_analogia_corrida_tierra_destino", type_="unique")
        batch.drop_constraint("fk_analogia_corrida_id_corrida_analisis", type_="foreignkey")
        for nombre in ("sim_fisica", "sim_terreno", "sim_geologica", "estabilidad"):
            batch.drop_constraint(f"ck_analogia_{nombre}_rango", type_="check")
        for nombre in ("corrida_id", "sim_fisica", "sim_terreno", "sim_geologica", "estabilidad"):
            batch.drop_column(nombre)
        batch.create_unique_constraint(
            "uq_analogia_sitio_tierra_destino", ["sitio_tierra_id", "sitio_destino_id"]
        )

    # ── medicion y caracteristica: se quitan las columnas nuevas antes de restaurar minerales ──
    with op.batch_alter_table("medicion") as batch:
        for nombre in (
            "ck_medicion_incertidumbre_no_negativa",
            "ck_medicion_n_muestras_positivo",
            "ck_medicion_periodo_orden",
        ):
            batch.drop_constraint(nombre, type_="check")
        for nombre in ("periodo_inicio", "periodo_fin", "incertidumbre", "n_muestras"):
            batch.drop_column(nombre)

    with op.batch_alter_table("caracteristica") as batch:
        batch.drop_constraint("ck_caracteristica_grupo_valido", type_="check")
        batch.drop_constraint("ck_caracteristica_rango_fisico_orden", type_="check")
        for nombre in ("grupo", "valor_min", "valor_max"):
            batch.drop_column(nombre)

    # ── pesos globales anteriores de las variables físicas ────────────────────────────
    for nombre, (_, peso, _, _) in VARIABLES.items():
        op.execute(
            sa.text(f"UPDATE caracteristica SET peso = {peso!r} WHERE nombre = {_q(nombre)}")
        )

    # ── minerales: vuelven a ser características con sus mediciones ───────────────────
    for nombre, peso in MINERALES.items():
        op.execute(
            sa.text(
                "INSERT INTO caracteristica (nombre, unidad, rango, peso) "
                f"SELECT {_q(nombre)}, '% wt', 100.0, {peso!r} "
                "WHERE EXISTS (SELECT 1 FROM composicion_celda "
                f"WHERE tipo = 'mineral' AND nombre = {_q(nombre)})"
            )
        )
    op.execute(
        sa.text(
            "INSERT INTO medicion (sitio_id, caracteristica_id, dataset_id, valor, valor_normalizado) "
            "SELECT cc.sitio_id, c.id, cc.dataset_id, cc.porcentaje, cc.porcentaje / 100.0 "
            "FROM composicion_celda cc JOIN caracteristica c ON c.nombre = cc.nombre "
            "WHERE cc.tipo = 'mineral'"
        )
    )
    op.drop_table("composicion_celda")
    op.drop_table("corrida_analisis")

    with op.batch_alter_table("sitio") as batch:
        batch.drop_constraint("uq_sitio_codigo", type_="unique")
        batch.drop_constraint("ck_sitio_clase_valida", type_="check")
        for nombre in ("clase", "codigo", "lat_min", "lat_max", "lon_min", "lon_max"):
            batch.drop_column(nombre)

    with op.batch_alter_table("cuerpo_celeste") as batch:
        batch.drop_constraint("ck_cuerpo_celeste_radio_positivo", type_="check")
        batch.drop_column("radio_km")
