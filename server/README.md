# Backend Server - API & External Integrations

Servicio backend para la plataforma de datos geoespaciales y planetarios.

---

## 🛰️ USGS Astrogeology STAC API

Catálogo SpatioTemporal Asset Catalog (STAC) público de la USGS para datos planetarios (Marte, Luna, etc.).  
**Autenticación:** Acceso público (no requiere API Key).

### Base URL
- **Endpoint Principal:** `https://stac.astrogeology.usgs.gov/api`
- **Host Directo (AWS):** `https://g6goyz4w56.execute-api.us-west-2.amazonaws.com/prod`

---

### Endpoints Disponibles

| Endpoint | Método | Formato | Descripción |
| :--- | :---: | :---: | :--- |
| `/` | `GET` | `application/json` | Landing page / Catálogo raíz de STAC. |
| `/conformance` | `GET` | `application/json` | Clases de conformidad STAC y OGC soportadas. |
| `/collections` | `GET` | `application/json` | Lista de todas las colecciones disponibles (ej. `mars_ctx`). |
| `/collections/{collection_id}` | `GET` | `application/json` | Metadatos y detalles de una colección específica. |
| `/collections/{collection_id}/items` | `GET` | `application/geo+json` | Items y escenas pertenecientes a una colección. |
| `/collections/{collection_id}/items/{item_id}` | `GET` | `application/geo+json` | Metadatos y assets de un ítem individual. |
| `/search` | `GET` / `POST` | `application/geo+json` | Búsqueda global por filtros espaciales (bbox, geometría) y temporales. |
| `/aggregate` | `GET` | `application/json` | Agregaciones estadísticas y conteos sobre los datos STAC. |
| `/aggregations` | `GET` | `application/json` | Definiciones y esquemas de agregaciones disponibles. |
| `/queryables` | `GET` | `application/schema+json` | Parámetros y campos filtrables mediante consultas CQL2. |
| `/api` | `GET` | `application/vnd.oai.openapi` | Especificación OpenAPI 3.0 en JSON. |
| `/api.html` | `GET` | `text/html` | Documentación interactiva Swagger / UI web de la API. |

---

## 📊 Guía de Datos: Temperatura, Nubosidad y Clima (Tierra vs Marte)

### 1. 🌍 Para la Tierra (NASA POWER y SRTM, APIs públicas sin clave)

| Variable | Colección / Instrumento | Atributos y Bandas clave |
| :--- | :--- | :--- |
| **Nubosidad (Cloud Cover)** | NASA POWER `CLOUD_AMT` | Fracción de nubes en % (media anual de 25 años, MERRA-2). |
| **Temperatura Superficial** | NASA POWER `TS` | Temperatura de la piel en °C; el proyecto la convierte a Kelvin. |
| **Polvo / Aerosoles** | NASA POWER `AOD_55` | Profundidad óptica de aerosoles a 550 nm. |
| **Elevación** | OpenTopoData SRTM 30 m | Altura en metros del punto (hasta 1 petición por segundo). |

### 2. 🔴 Para Marte (USGS Astrogeology STAC)

| Variable | Colección / Instrumento | Atributos y Bandas clave |
| :--- | :--- | :--- |
| **Temperatura (Infrarrojo)** | `THEMIS` (Mars Odyssey) / `TES` | Mosaicos infrarrojos diurnos y nocturnos (`themis_day_ir`, `themis_night_ir`). Miden temperatura superficial directa e **inercia térmica** del regolito marciano. |
| **Nubosidad / Nubes de Hielo y Polvo** | `mars_ctx` (CTX) / `mars_mroc` (MARCI/MOC) | Detección visible de nubes de hielo de agua ($H_2O$), nieblas matutinas en cañones y tormentas locales/globales de polvo (*dust storms*). |
| **Topografía y Clima** | CTX DTMs / HRSC | Modelos Digitales de Elevación que explican variaciones térmicas y presión atmosférica por altitud (ej. Olympus Mons vs Valles Marineris). |


---

## 🧭 Criterios de Extracción: Posición Espacial y Tiempo (STAC Standard)

Toda consulta a las APIs STAC (Tierra y Marte) se basa en dos dimensiones clave:

### 1. 📍 Dimensión Espacial (Posición Geográfica / Planetaria)
Se define qué área del planeta se va a observar:
- **`bbox` (Bounding Box):** Caja delimitadora en formato `[min_lon, min_lat, max_lon, max_lat]`.
  - Ejemplo Tierra: `[-68.2, -16.6, -68.0, -16.4]` (área de La Paz, Bolivia).
  - Ejemplo Marte: `[-120.0, -10.0, -110.0, 0.0]` (área de Valles Marineris).
- **`intersects` (GeoJSON Polygon / Point):** Para puntos exactos (latitud/longitud) o polígonos complejos dibujados por el usuario en el mapa web.

### 2. ⏱️ Dimensión Temporal (Tiempo y Estaciones)
Define la ventana de tiempo en formato ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`):
- **Tierra (NASA POWER):**
  - Devuelve la climatología de 25 años (`ANN` = media anual, más los 12 meses).
  - No admite rango de fechas: es la media climatológica del punto.
- **Marte (USGS STAC):**
  - Misiones históricas y en curso (año de adquisición terrestre o año marciano $L_s$ - longitud solar para estaciones marcianas).
  - Día vs Noche: Permite contrastar la inercia térmica diurna y nocturna (`themis_day` vs `themis_night`).

---

## 🗄️ Migraciones de la base de datos (Alembic)

El esquema se gestiona con Alembic: las migraciones están en `alembic/versions/` y son la única fuente de verdad.
La base de desarrollo (`dev.db`) no se versiona en Git: se crea sola al arrancar el backend.

| Qué quieres hacer | Comando (desde `server/`) |
| :--- | :--- |
| Aplicar todas las migraciones | `alembic upgrade head` |
| Crear una migración tras cambiar un modelo | `alembic revision --autogenerate -m "descripcion"` |
| Ver en qué versión está la base | `alembic current` |
| Deshacer la última migración | `alembic downgrade -1` |
| Generar el SQL para PostgreSQL sin conectarse | `alembic upgrade head --sql` |

- En DEV con SQLite, el backend ejecuta `alembic upgrade head` al arrancar. Una base creada antes con `create_all`
  se marca automáticamente en la revisión base y luego se actualiza; sus datos se conservan.
- Revisa siempre la migración generada: el autogenerado puede dejar imports sin resolver o no detectar cambios de nombre.
- `tests/test_migrations.py` falla si un modelo cambia sin su migración.

