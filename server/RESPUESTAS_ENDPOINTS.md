# Respuesta Real de los Endpoints Satelitales (STAC)

Ejemplos reales capturados de las APIs satelitales en vivo para la Tierra y Marte.

---

## 1. 🌍 Tierra (NASA POWER, climatología)
**Endpoint:** `GET https://power.larc.nasa.gov/api/temporal/climatology/point`  
**Query:** `parameters=TS,CLOUD_AMT,AOD_55&community=SB&longitude=-69.9&latitude=-24.1&format=JSON` (Atacama)

Respuesta real, recortada a los valores anuales (`ANN`); cada serie trae también los 12 meses:

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [-69.9, -24.1, 1261.0] },
  "properties": {
    "parameter": {
      "CLOUD_AMT": { "ANN": 20.57 },
      "AOD_55": { "ANN": 0.04 }
    }
  },
  "header": { "api": { "name": "POWER Climatology API" }, "fill_value": -999.0 }
}
```

Los valores `-999.0` indican que no hay dato; el backend responde 404 en ese caso.

---

## 2. 🔴 Marte (USGS Astrogeology STAC)
**Endpoint:** `GET https://stac.astrogeology.usgs.gov/api/search?limit=1`  
*(Se utiliza GET para evitar bloqueos 403 de CloudFront).*

```json
{
  "type": "Feature",
  "id": "ESP_093796_2260_RED",
  "collection": "mro_hirise_uncontrolled_observations",
  "bbox": [-142.3, 45.8, -141.9, 46.2],
  "properties": {
    "title": "ESP_093796_2260_RED",
    "missions": ["Mars Reconnaissance Orbiter (MRO)"],
    "instruments": ["HiRISE"],
    "start_datetime": "2024-03-01T10:15:00Z",
    "end_datetime": "2024-03-01T10:20:00Z"
  },
  "assets": {
    "thumbnail": {
      "href": "https://pilot.wr.usgs.gov/.../thumbnail.jpg",
      "type": "image/jpeg"
    },
    "image": {
      "href": "https://pilot.wr.usgs.gov/.../product.tif",
      "type": "image/tiff; application=geotiff"
    },
    "provenance": {
      "href": "https://pilot.wr.usgs.gov/.../provenance.json"
    },
    "pds_label": {
      "href": "https://pilot.wr.usgs.gov/.../label.xml"
    }
  }
}
```

