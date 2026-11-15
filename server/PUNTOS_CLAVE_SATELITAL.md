# Puntos Clave de la Integración Satelital (Tierra vs Marte)

Resumen técnico de los aspectos más importantes para el desarrollo del backend y frontend.

---

## 1. Dónde y Cuándo (Filtros Espacio-Temporales)
* **Posición (`bbox`):** Coordenadas `[min_lon, min_lat, max_lon, max_lat]`. Se extraen automáticamente del GeoJSON guardado en `sitio.geom`.
* **Tiempo (`datetime`):** Formato ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).
  * **Tierra:** NASA POWER entrega la media climatológica; no admite rango de fechas.
  * **Marte:** Permite contrastar tomas diurnas y nocturnas para inercia térmica.

---

## 2. Variables de Clima Extraídas
* **Nubosidad (Tierra):** NASA POWER `CLOUD_AMT` (% de nubes, media anual de 25 años).
* **Temperatura (Tierra):** NASA POWER `TS` (temperatura de la piel), convertida a Kelvin.
* **Temperatura e Inercia Térmica (Marte):** Se obtiene de mosaicos `THEMIS IR` diurnos y nocturnos.
* **Topografía:** SRTM 30 m (OpenTopoData, sin clave) en la Tierra, LOLA en la Luna y CTX DTMs en Marte para correlacionar altitud y clima.

---

## 3. Autenticación y Protocolos
* **NASA POWER (Tierra):**
  * API pública sin clave; devuelve la media climatológica de 25 años del punto.
* **USGS Astrogeology (Marte):**
  * Catálogo público sin API Key (`https://stac.astrogeology.usgs.gov/api`).
  * **Importante:** Utilizar peticiones `GET` para `/search` para evitar bloqueos 403 de CloudFront.

---

## 4. Persistencia en Base de Datos
* Las consultas satelitales no se pierden en memoria: se vinculan a la tabla `medicion`.
* Cada medición se asocia a:
  * `sitio_id` (Lugar seleccionado).
  * `caracteristica_id` (Temperatura, Nubosidad, Inercia Térmica, etc.).
  * `dataset_id` (NASA POWER, LOLA, THEMIS, etc.).
* El campo `valor_normalizado` ($0 \le x \le 1$) permite que el módulo de **analogías** compare directamente la similitud entre la Tierra y Marte.

