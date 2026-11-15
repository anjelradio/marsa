# Puntos Clave de la Integración Satelital (Tierra vs Marte)

Resumen técnico de los aspectos más importantes para el desarrollo del backend y frontend.

---

## 1. Dónde y Cuándo (Filtros Espacio-Temporales)
* **Posición (`bbox`):** Coordenadas `[min_lon, min_lat, max_lon, max_lat]`. Se extraen automáticamente del GeoJSON guardado en `sitio.geom`.
* **Tiempo (`datetime`):** Formato ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).
  * **Tierra:** Permite evaluar estaciones del año y nubosidad semanal.
  * **Marte:** Permite contrastar tomas diurnas y nocturnas para inercia térmica.

---

## 2. Variables de Clima Extraídas
* **Nubosidad (Tierra):** Se extrae directo de `properties.eo:cloud_cover` (% de cobertura) y se clasifica píxel por píxel con la banda `SCL`.
* **Temperatura (Tierra):** Se obtiene de Sentinel-3 SLSTR en Kelvin (LST - Land Surface Temperature).
* **Temperatura e Inercia Térmica (Marte):** Se obtiene de mosaicos `THEMIS IR` diurnos y nocturnos.
* **Topografía:** SRTM 30 m (OpenTopoData, sin clave) en la Tierra, LOLA en la Luna y CTX DTMs en Marte para correlacionar altitud y clima.

---

## 3. Autenticación y Protocolos
* **Copernicus CDSE (Tierra):**
  * Búsquedas públicas anónimas permitidas (`https://stac.dataspace.copernicus.eu/v1`).
  * Para descargas masivas o cuota alta usa OAuth2 Bearer token con `client_id=cdse-public`.
* **USGS Astrogeology (Marte):**
  * Catálogo público sin API Key (`https://stac.astrogeology.usgs.gov/api`).
  * **Importante:** Utilizar peticiones `GET` para `/search` para evitar bloqueos 403 de CloudFront.

---

## 4. Persistencia en Base de Datos
* Las consultas satelitales no se pierden en memoria: se vinculan a la tabla `medicion`.
* Cada medición se asocia a:
  * `sitio_id` (Lugar seleccionado).
  * `caracteristica_id` (Temperatura, Nubosidad, Inercia Térmica, etc.).
  * `dataset_id` (Sentinel-2, THEMIS, etc.).
* El campo `valor_normalizado` ($0 \le x \le 1$) permite que el módulo de **analogías** compare directamente la similitud entre la Tierra y Marte.

