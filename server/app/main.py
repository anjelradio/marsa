# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, init_db
from app.core.dependencies import get_event_bus
from app.core.errors.handlers import setup_exception_handlers
from app.core.events.subscriptions import configure_event_subscriptions

# Configuración de logging estándar
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ==============================================================================
# IMPORTACIONES DE ROUTERS
# ==============================================================================
from app.modules.cuerpo_celeste.infrastructure.api.routers.cuerpo_celeste_router import (
    router as cuerpo_celeste_router,
)
from app.modules.sitio.infrastructure.api.routers.sitio_router import (
    router as sitio_router,
)
from app.modules.dataset.infrastructure.api.routers.dataset_router import (
    router as dataset_router,
)
from app.modules.caracteristica.infrastructure.api.routers.caracteristica_router import (
    router as caracteristica_router,
)
from app.modules.medicion.infrastructure.api.routers.medicion_router import (
    router as medicion_router,
)
from app.modules.analogia.infrastructure.api.routers.analogia_router import (
    router as analogia_router,
)


# ==============================================================================
# LIFESPAN
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.

    - DEV  + SQLite   → crea tablas automáticamente (rápido para prototipar).
    - DEV  + Postgres → se asume que Alembic ya corrió (`alembic upgrade head`).
    - PROD            → Alembic siempre. init_db() nunca se llama.
    """
    if settings.ENVIRONMENT == "DEV" and settings.is_sqlite:
        logger.info("DEV + SQLite — inicializando tablas con SQLModel...")
        init_db()
        # Sembrar datos iniciales (Tierra, Marte, datasets y características)
        from sqlmodel import Session
        from app.shared.infrastructure.db.seed import seed_initial_data
        with Session(engine) as session:
            seed_initial_data(session)
    else:
        logger.info(
            "Modo %s con %s — las migraciones deben ejecutarse con Alembic.",
            settings.ENVIRONMENT,
            "SQLite" if settings.is_sqlite else "PostgreSQL",
        )

    # ── Event Bus — registrar suscripciones de handlers ────────────────────
    configure_event_subscriptions(get_event_bus())
    logger.info("Event Bus configurado con suscripciones del sistema.")

    yield


# ==============================================================================
# APP FASTAPI
# ==============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

setup_exception_handlers(app)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# RUTAS GENÉRICAS / HEALTHCHECK
# ==============================================================================
@app.get("/health", tags=["System"], summary="Verificar estado del sistema y BD")
def health_check():
    """
    Comprueba el estado de la API y la conectividad real con la base de datos.
    Devuelve 200 si todo está saludable, o 503 si la BD no responde.
    """
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Healthcheck: fallo al conectar con la base de datos: %s", exc)
        db_status = "unreachable"

    payload = {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": {
            "engine": "SQLite" if settings.is_sqlite else "PostgreSQL",
            "status": db_status,
        },
        "environment": settings.ENVIRONMENT,
    }

    if db_status != "connected":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload,
        )

    return payload


# ==============================================================================
# REGISTRO DE ROUTERS
# ==============================================================================
app.include_router(
    cuerpo_celeste_router, prefix="/api/cuerpo-celeste", tags=["CuerpoCeleste"]
)
app.include_router(sitio_router, prefix="/api/sitio", tags=["Sitio"])
app.include_router(dataset_router, prefix="/api/dataset", tags=["Dataset"])
app.include_router(
    caracteristica_router, prefix="/api/caracteristica", tags=["Caracteristica"]
)
app.include_router(medicion_router, prefix="/api/medicion", tags=["Medicion"])
app.include_router(analogia_router, prefix="/api/analogia", tags=["Analogia"])

# Rutas de compatibilidad directa para API v1 de análogos geológicos
from app.modules.analogia.infrastructure.api.schemas.geology_schemas import (
    RespuestaComparacion,
    RespuestaMacrostratPuntual,
)
from app.modules.analogia.infrastructure.geology_service import (
    comparar_analogo_tierra,
    consultar_macrostrat,
)
from app.modules.analogia.infrastructure.api.schemas.geology_schemas import MetadatosFuente
from fastapi import Query
from typing import Optional


@app.get(
    "/api/v1/tierra/macrostrat",
    response_model=RespuestaMacrostratPuntual,
    tags=["Geologia v1"],
    summary="API v1: Macrostrat en tiempo real",
)
async def api_v1_macrostrat(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lng: float = Query(..., ge=-180.0, le=180.0),
    scale: Optional[str] = Query(None),
):
    unidades = await consultar_macrostrat(lat, lng, scale)
    return RespuestaMacrostratPuntual(
        coordenadas={"lat": lat, "lng": lng},
        total_unidades=len(unidades),
        unidades=unidades,
        atribucion=MetadatosFuente(
            fuente="Macrostrat API (macrostrat.org)",
            licencia="CC BY 4.0",
            resolucion_o_escala="Continental a Local (1:250k - 1:5M)",
            nota_metodologica="Consulta en tiempo real al punto geográfico seleccionado en el mapa.",
        ),
    )


@app.get(
    "/api/v1/comparar-analogo",
    response_model=RespuestaComparacion,
    tags=["Geologia v1"],
    summary="API v1: Comparar análogo Tierra-Marte/Luna",
)
async def api_v1_comparar_analogo(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lng: float = Query(..., ge=-180.0, le=180.0),
    destino: str = Query("marte"),
):
    return await comparar_analogo_tierra(lat, lng, destino)

