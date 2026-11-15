"""Datos reales de la Luna por coordenadas, leídos del archivo público del PDS.

No se descargan los ficheros completos: ambos tienen registros de tamaño fijo,
así que se leen solo los bytes del punto con peticiones HTTP por rango.

- Elevación: LOLA GDR ``LDEM_16`` (16 píxeles/grado, enteros de 16 bits little-endian,
  altura = DN x 0.5 m sobre la esfera de referencia de 1737.4 km).
- Temperatura: Diviner GCP (Williams et al. 2017), temperatura de brillo bolométrica
  promediada en bins de 0.5° y 0.25 h de hora local (96 bins por punto).
"""

import urllib.request

LDEM_URL = (
    "https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/"
    "data/lola_gdr/cylindrical/img/ldem_16.img"
)
GCP_URL = (
    "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/"
    "data_derived_gcp/global_cumul_avg_cyl_{band}_002.tab"
)

LDEM_PPD = 16
LDEM_COLUMNS = 360 * LDEM_PPD
LDEM_ROWS = 180 * LDEM_PPD
LDEM_SCALE_M = 0.5

GCP_RECORD_BYTES = 113
GCP_TIME_BINS = 96
GCP_LAT_BINS = 20  # 10° de banda / 0.5°
GCP_BIN_DEG = 0.5
GCP_MISSING = -9999.0


def ldem_offset(latitude: float, longitude: float) -> int:
    """Byte del píxel de LDEM_16 para la coordenada (lon 0..360 este, lat 90 arriba)."""
    row = min(int((90.0 - latitude) * LDEM_PPD), LDEM_ROWS - 1)
    column = min(int((longitude % 360.0) * LDEM_PPD), LDEM_COLUMNS - 1)
    return (max(row, 0) * LDEM_COLUMNS + column) * 2


def decode_ldem(raw: bytes) -> float:
    """Altura en metros sobre la esfera de referencia a partir de los 2 bytes del píxel."""
    return int.from_bytes(raw[:2], "little", signed=True) * LDEM_SCALE_M


def gcp_band(latitude: float) -> tuple[str, float]:
    """Nombre de banda del fichero GCP y su latitud mínima (p. ej. ``00N10N``, ``90S80S``)."""
    if latitude >= 0:
        low = min(int(latitude // 10) * 10, 80)
        return f"{low:02d}N{low + 10:02d}N", float(low)
    k = min(int(-latitude // 10), 8)
    return f"{10 * (k + 1):02d}S{10 * k:02d}S", float(-10 * (k + 1))


def gcp_offset(latitude: float, longitude: float) -> tuple[str, int, float, float]:
    """(banda, byte inicial, clon, clat) del primer bin de hora local del punto."""
    band, min_lat = gcp_band(latitude)
    lon = (longitude + 180.0) % 360.0 - 180.0
    lon_index = min(int((lon + 180.0) / GCP_BIN_DEG), 719)
    lat_index = min(int((latitude - min_lat) / GCP_BIN_DEG), GCP_LAT_BINS - 1)
    first_record = 1 + (lon_index * GCP_LAT_BINS + lat_index) * GCP_TIME_BINS  # 1 = cabecera
    clon = -180.0 + (lon_index + 0.5) * GCP_BIN_DEG
    clat = min_lat + (lat_index + 0.5) * GCP_BIN_DEG
    return band, first_record * GCP_RECORD_BYTES, clon, clat


def parse_gcp_rows(text: str) -> list[dict[str, float]]:
    """Filas ``clon, clat, ltim, t3..t9, tbol`` como diccionarios."""
    names = ("clon", "clat", "ltim", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "tbol")
    rows = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != len(names):
            continue
        try:
            rows.append(dict(zip(names, map(float, parts))))
        except ValueError:  # línea de cabecera con los nombres de columna
            continue
    return rows


MIN_VALID_BINS = 12  # al menos 3 h de cobertura para interpolar el resto del día


def _fill_circular(values: list[float | None]) -> list[float]:
    """Rellena los huecos con interpolación lineal sobre el ciclo de 24 h (circular)."""
    size = len(values)
    valid = [i for i, v in enumerate(values) if v is not None]
    filled: list[float] = []
    for i, v in enumerate(values):
        if v is not None:
            filled.append(v)
            continue
        before = next(j for j in (((i - s) % size) for s in range(1, size)) if values[j] is not None)
        after = next(j for j in (((i + s) % size) for s in range(1, size)) if values[j] is not None)
        gap_before = (i - before) % size
        gap_after = (after - i) % size
        weight = gap_before / (gap_before + gap_after)
        filled.append(values[before] * (1 - weight) + values[after] * weight)  # type: ignore[operator]
    if not valid:
        raise ValueError("sin datos")
    return filled


def summarize_diurnal(rows: list[dict[str, float]]) -> dict[str, float]:
    """Media diurna, máxima y mínima de la temperatura bolométrica del punto.

    Máxima y mínima salen solo de bins con dato; la media se calcula sobre el ciclo de
    24 h completo, interpolando las horas locales sin observaciones.
    """
    series: list[float | None] = [None] * GCP_TIME_BINS
    for row in rows:
        if row["tbol"] != GCP_MISSING and row["tbol"] > 0:
            series[min(int(row["ltim"] / 0.25), GCP_TIME_BINS - 1)] = row["tbol"]
    observed = [v for v in series if v is not None]
    if len(observed) < MIN_VALID_BINS:
        raise ValueError("Diviner no tiene observaciones suficientes en este punto")
    full_day = _fill_circular(series)
    return {
        "mean_k": sum(full_day) / len(full_day),
        "max_k": max(observed),
        "min_k": min(observed),
        "valid_bins": float(len(observed)),
    }


def _read_range(url: str, start: int, length: int, timeout: int = 60) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"Range": f"bytes={start}-{start + length - 1}", "User-Agent": "naseando/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 206:
            raise RuntimeError(f"El servidor ignoró la petición por rango ({response.status})")
        return response.read()


def get_moon_elevation(latitude: float, longitude: float) -> float:
    """Elevación LOLA en metros del punto, leyendo solo 2 bytes."""
    return decode_ldem(_read_range(LDEM_URL, ldem_offset(latitude, longitude), 2))


def get_moon_temperature(latitude: float, longitude: float) -> dict[str, float]:
    """Resumen diurno de Diviner del punto, leyendo solo los 96 registros de su bin."""
    band, offset, clon, clat = gcp_offset(latitude, longitude)
    raw = _read_range(
        GCP_URL.format(band=band.lower()), offset, GCP_TIME_BINS * GCP_RECORD_BYTES
    )
    rows = parse_gcp_rows(raw.decode("ascii"))
    if len(rows) != GCP_TIME_BINS:
        raise ValueError(f"Se esperaban {GCP_TIME_BINS} filas y llegaron {len(rows)}")
    if abs(rows[0]["clon"] - clon) > 1e-6 or abs(rows[0]["clat"] - clat) > 1e-6:
        raise ValueError(
            f"El fichero no tiene el orden esperado: bin {rows[0]['clon']},{rows[0]['clat']} "
            f"en lugar de {clon},{clat}"
        )
    return summarize_diurnal(rows)
