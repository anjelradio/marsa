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
from app.modules.analog_explorer.infrastructure.api.routers.explorer_router import (
    router as explorer_router,
)

try:
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

    HAS_SQLMODEL_ROUTERS = True
except ImportError:
    HAS_SQLMODEL_ROUTERS = False


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
        if HAS_SQLMODEL_ROUTERS:
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
@app.get("/api/health", tags=["System"], summary="Verificar estado del sistema y BD (API alias)")
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
app.include_router(explorer_router, prefix="/api", tags=["Planetary Analog Explorer"])

if HAS_SQLMODEL_ROUTERS:
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
