# Respuesta Real de los Endpoints Satelitales (STAC)

Ejemplos reales capturados de las APIs satelitales en vivo para la Tierra y Marte.

---

## 1. 🌍 Tierra (Copernicus CDSE - Sentinel-2 L2A)
**Endpoint:** `POST https://stac.dataspace.copernicus.eu/v1/search`  
**Query:** Bbox Salar de Uyuni `[-68.0, -21.0, -67.0, -20.0]`

```json
{
  "type": "Feature",
  "id": "S2B_MSIL2A_20261113T143649_N0513_R096_T19KGT_20261113T181914",
  "collection": "sentinel-2-l2a",
  "bbox": [-68.0, -21.0, -67.0, -20.0],
  "properties": {
    "datetime": "2026-11-13T14:36:49.024000Z",
    "platform": "sentinel-2b",
    "constellation": "sentinel-2",
    "instruments": ["msi"],
    "eo:cloud_cover": 54.38
  },
  "assets": {
    "thumbnail": {
      "href": "https://zipper.dataspace.copernicus.eu/.../thumbnail.png",
      "type": "image/png"
    },
    "B02_10m": {
      "href": "https://zipper.dataspace.copernicus.eu/.../B02.jp2",
      "title": "Banda Azul (10m)"
    },
    "B04_10m": {
      "href": "https://zipper.dataspace.copernicus.eu/.../B04.jp2",
      "title": "Banda Roja (10m)"
    },
    "B08_10m": {
      "href": "https://zipper.dataspace.copernicus.eu/.../B08.jp2",
      "title": "Infrarrojo Cercano (NIR 10m)"
    },
    "SCL_20m": {
      "href": "https://zipper.dataspace.copernicus.eu/.../SCL.jp2",
      "title": "Scene Classification (Máscara de nubes, suelo y agua)"
    }
  }
}
```

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

