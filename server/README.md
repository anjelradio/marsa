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

## ⛰️ OpenTopography API

API para descarga y procesamiento de Modelos Digitales de Elevación (DEMs) globales.
- **Documentación:** [https://portal.opentopography.org/apidocs/](https://portal.opentopography.org/apidocs/)
- **Autenticación:** Requiere parámetro de consulta `API_Key` configurado en `server/.env` (`OPENTOPOGRAPHY_API_KEY`).

