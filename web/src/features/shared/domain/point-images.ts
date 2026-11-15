import type { GeoPoint } from "./geographic-coordinates";

export type PointImagePlanet = "earth" | "moon";
export type PointImageView = "regional" | "detail";

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

/** Recuadro de lado `size` grados centrado en el punto, desplazado para no salir del globo. */
function boundingBox({ latitude, longitude }: GeoPoint, size: number) {
  const south = clamp(latitude - size / 2, -90, 90 - size);
  const west = clamp(longitude - size / 2, -180, 180 - size);
  return [west, south, west + size, south + size];
}

const EARTH_WMS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi";
const MOON_TILES =
  "https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm";

export const POINT_IMAGE_SOURCES = {
  earth: "https://worldview.earthdata.nasa.gov/",
  moon: "https://trek.nasa.gov/moon/",
} as const;

/** URL de la imagen orbital pública (sin clave) para el punto y la escala elegidos. */
export function pointImageUrl(planet: PointImagePlanet, view: PointImageView, point: GeoPoint) {
  if (planet === "earth") {
    // Escala regional (12°) o detalle (3°)
    const bbox = boundingBox(point, view === "regional" ? 12 : 3);
    const params = new URLSearchParams({
      SERVICE: "WMS",
      VERSION: "1.1.1",
      REQUEST: "GetMap",
      LAYERS: "BlueMarble_NextGeneration",
      SRS: "EPSG:4326",
      BBOX: bbox.join(","),
      WIDTH: "512",
      HEIGHT: "512",
      FORMAT: "image/jpeg",
    });
    return `${EARTH_WMS}?${params}`;
  }

  // Mosaico lunar WAC en teselas equirrectangulares: 2^(z+1) columnas x 2^z filas.
  const zoom = view === "regional" ? 3 : 6;
  const columns = 2 ** (zoom + 1);
  const rows = 2 ** zoom;
  const x = clamp(Math.floor(((point.longitude + 180) / 360) * columns), 0, columns - 1);
  const y = clamp(Math.floor(((90 - point.latitude) / 180) * rows), 0, rows - 1);
  return `${MOON_TILES}/${zoom}/${y}/${x}.jpg`;
}
