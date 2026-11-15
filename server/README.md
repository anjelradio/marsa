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

## 🌍 Copernicus Data Space Ecosystem (CDSE - Datos de la Tierra)

Catálogo oficial de la Agencia Espacial Europea (ESA) para datos de observación terrestre (Sentinel-1, Sentinel-2, Sentinel-3, Landsat, etc.).

### 1. Endpoints Base
- **STAC API (Público para consultas/búsquedas):**  
  `https://stac.dataspace.copernicus.eu/v1`
- **OAuth2 Token Endpoint (Keycloak):**  
  `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`

### 2. Autenticación & Cuotas
- **Consultas anónimas/públicas:** Se pueden consultar las colecciones y buscar items sin autenticación (límite aprox. 60 req/min).
- **Descargas y alta cuota:** Requiere cuenta gratuita en [dataspace.copernicus.eu](https://dataspace.copernicus.eu/) y obtención de token Bearer (límite de 240 req/min y descarga de bandas/assets).

### 3. Endpoints Principales

| Endpoint | Método | Descripción |
| :--- | :---: | :--- |
| `/collections` | `GET` | Lista de colecciones (ej. `sentinel-2-l2a`, `sentinel-1-grd`). |
| `/collections/{collection_id}` | `GET` | Información y detalles de una colección satelital específica. |
| `/collections/{collection_id}/items` | `GET` | Granos/escenas dentro de la colección. |
| `/search` | `GET` / `POST` | Búsqueda global por `bbox`, polígono geoespacial y rangos de fecha (`datetime`). |


---

## 📊 Guía de Datos: Temperatura, Nubosidad y Clima (Tierra vs Marte)

### 1. 🌍 Para la Tierra (Copernicus CDSE STAC)

| Variable | Colección / Instrumento | Atributos y Bandas clave |
| :--- | :--- | :--- |
| **Nubosidad (Cloud Cover)** | `sentinel-2-l2a` | Metadato directo: `eo:cloud_cover` (% de nubes de la escena). Máscara de clasificación: banda `SCL` (Scene Classification Layer) que separa píxeles de nubes altas, cirros y cielo despejado. |
| **Temperatura Superficial** | `sentinel-3-slstr` | Sensor infrarrojo térmico (LST - *Land Surface Temperature*). Mide temperatura superficial terrestre y marina día/noche en Kelvin. |
| **Clima / Atmósfera** | `sentinel-5p-l2` | Aerosoles, monóxido de carbono, ozono y vapor de agua atmosférico. |

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
- **Tierra (Copernicus):** 
  - `datetime`: `"2024-01-01T00:00:00Z/2024-02-01T23:59:59Z"`
  - Permite evaluar variaciones estacionales (verano/invierno) y evolución climática día a día.
- **Marte (USGS STAC):**
  - Misiones históricas y en curso (año de adquisición terrestre o año marciano $L_s$ - longitud solar para estaciones marcianas).
  - Día vs Noche: Permite contrastar la inercia térmica diurna y nocturna (`themis_day` vs `themis_night`).
