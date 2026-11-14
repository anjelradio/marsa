# app/shared/infrastructure/db/models.py
#
# ============================================================
# REGISTRY CENTRAL DE MODELOS  ─  ALEMBIC LO IMPORTA AQUÍ
# ============================================================
# Cada vez que agregues un nuevo módulo con tablas SQLModel,
# importa su modelo en este archivo.  Eso es todo lo que
# necesitas para que `alembic revision --autogenerate` lo detecte.
#
# Ejemplo:
#   from app.modules.users.infrastructure.persistence.models.profile_model import ProfileModel
#   from app.modules.orders.infrastructure.persistence.models.order_model import OrderModel
#
# ⚠️  No importes aquí lógica de negocio ni servicios;
#     solo los modelos que heredan de SQLModel con table=True.
# ============================================================

# ruff: noqa: F401
from app.modules.cuerpo_celeste.infrastructure.persistence.models.cuerpo_celeste_model import (
    CuerpoCelesteModel,
)
from app.modules.sitio.infrastructure.persistence.models.sitio_model import SitioModel
from app.modules.dataset.infrastructure.persistence.models.dataset_model import (
    DatasetModel,
)
from app.modules.caracteristica.infrastructure.persistence.models.caracteristica_model import (
    CaracteristicaModel,
)
from app.modules.medicion.infrastructure.persistence.models.medicion_model import (
    MedicionModel,
)
from app.modules.analogia.infrastructure.persistence.models.analogia_model import (
    AnalogiaModel,
)
