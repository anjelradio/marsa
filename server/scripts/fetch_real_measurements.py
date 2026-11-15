"""Descarga mediciones reales para los sitios sembrados y las guarda en JSON.

Fuentes (todas públicas y sin clave):
  - NASA POWER (climatología MERRA-2, media de 25 años): temperatura de la piel
    (TS, K), nubosidad (CLOUD_AMT, %) y profundidad óptica de aerosoles (AOD_55).
  - OpenTopoData SRTM 30 m: elevación (m) de los sitios terrestres.
  - Mars Climate Database v6.2 vía el backend local: temperatura superficial
    y profundidad óptica de polvo de los sitios marcianos.
  - NASA PDS (LRO): elevación de LOLA (LDEM_16) y temperatura media diurna de
    Diviner (GCP) de los sitios lunares, leídas por rango de bytes (sin bajar
    los ficheros completos).

Uso (desde server/):
    venv/Scripts/python.exe scripts/fetch_real_measurements.py [--backend http://localhost:8000]
    venv/Scripts/python.exe scripts/fetch_real_measurements.py --cuerpos Luna   # solo la Luna

Genera app/shared/infrastructure/db/real_measurements.json. Las características
sin fuente quedan con el valor de referencia del seed.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.modules.cuerpo_celeste.infrastructure.moon_lro import (  # noqa: E402
    get_moon_elevation,
    get_moon_temperature,
)
from app.shared.infrastructure.db.seed import SITIOS  # noqa: E402

SALIDA = ROOT / "app" / "shared" / "infrastructure" / "db" / "real_measurements.json"
FILL = -999.0

DS_POWER = "NASA POWER (MERRA-2)"
DS_SRTM = "OpenTopoData SRTM 30 m"
DS_MCD = "LMD Mars Climate Database"
DS_LRO = "NASA LRO LOLA / Diviner"


def get_json(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": "naseando-seed/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def power(lon: float, lat: float) -> dict[str, float]:
    query = urllib.parse.urlencode(
        {
            "parameters": "TS,CLOUD_AMT,AOD_55",
            "community": "SB",
            "longitude": lon,
            "latitude": lat,
            "format": "JSON",
        }
    )
    data = get_json(f"https://power.larc.nasa.gov/api/temporal/climatology/point?{query}")
    params = data["properties"]["parameter"]
    return {k: v["ANN"] for k, v in params.items() if v.get("ANN", FILL) != FILL}


def elevacion(lon: float, lat: float) -> float | None:
    data = get_json(f"https://api.opentopodata.org/v1/srtm30m?locations={lat},{lon}")
    return data["results"][0]["elevation"]


def clima_marte(backend: str, lon: float, lat: float) -> dict[str, float]:
    data = get_json(
        f"{backend.rstrip('/')}/api/cuerpo-celeste/marte/clima?lat={lat}&lon={lon}"
    )
    return data["values"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="http://localhost:8000")
    parser.add_argument(
        "--cuerpos",
        default="Tierra,Marte,Luna",
        help="Cuerpos a descargar, separados por comas; el resto se conserva del JSON actual.",
    )
    args = parser.parse_args()
    seleccion = {c.strip() for c in args.cuerpos.split(",")}

    resultado: dict = {"generado": date.today().isoformat(), "sitios": {}}
    if SALIDA.exists():
        resultado["sitios"] = json.loads(SALIDA.read_text(encoding="utf-8")).get("sitios", {})
    for cuerpo, nombre, _tipo, lon, lat, _vals in SITIOS:
        if cuerpo not in seleccion:
            continue
        medidas: dict[str, dict] = {}
        try:
            if cuerpo == "Tierra":
                p = power(lon, lat)
                if "TS" in p:
                    medidas["Temperatura Superficial"] = {"valor": round(p["TS"] + 273.15, 2), "dataset": DS_POWER}
                if "CLOUD_AMT" in p:
                    medidas["Nubosidad"] = {"valor": round(p["CLOUD_AMT"], 2), "dataset": DS_POWER}
                if "AOD_55" in p:
                    medidas["Profundidad Óptica de Polvo"] = {"valor": round(p["AOD_55"], 3), "dataset": DS_POWER}
                time.sleep(1)  # cortesía con la API pública
                z = elevacion(lon, lat)
                if z is not None:
                    medidas["Elevación"] = {"valor": float(z), "dataset": DS_SRTM}
                time.sleep(1.1)
            elif cuerpo == "Marte":
                v = clima_marte(args.backend, lon, lat)
                medidas["Temperatura Superficial"] = {"valor": round(v["surface_temperature_k"], 2), "dataset": DS_MCD}
                medidas["Profundidad Óptica de Polvo"] = {"valor": round(v["dust_optical_depth"], 3), "dataset": DS_MCD}
            elif cuerpo == "Luna":
                z = get_moon_elevation(lat, lon)
                medidas["Elevación"] = {"valor": round(z, 1), "dataset": DS_LRO}
                t = get_moon_temperature(lat, lon)
                medidas["Temperatura Superficial"] = {
                    "valor": round(t["mean_k"], 2),
                    "dataset": DS_LRO,
                    "max_k": round(t["max_k"], 1),
                    "min_k": round(t["min_k"], 1),
                    "bins_con_dato": int(t["valid_bins"]),
                }
        except Exception as exc:  # una fuente caída no debe tumbar el resto
            print(f"[aviso] {nombre}: {exc}", file=sys.stderr)
        resultado["sitios"][nombre] = medidas
        print(f"{nombre}: {', '.join(medidas) or 'sin datos reales'}")

    SALIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Escrito {SALIDA}")


if __name__ == "__main__":
    main()
