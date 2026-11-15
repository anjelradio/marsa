"""
Deterministic parser for Mars Climate Database (MCD v6.2) ASCII grids (Ls = 105 deg).

Reads the three validated MCD v6.2 ASCII files in `datos-marte/datos-marte/`:
- `marte_ls105_temperatura_presion.txt`: Surface temperature (K) & surface pressure (Pa)
- `marte_ls105_nubes_polvo.txt`: Atmospheric water ice column (kg/m^2) & visible dust optical depth (670 nm)
- `marte_ls105_viento_10m.txt`: Horizontal wind speed at 10 m above surface (m/s)

Outputs:
- `data/processed/mars_mcd_ls105.json`: Global metadata, summary statistics (excluding duplicate +180 meridian),
  extracted cell metrics for Jezero Crater (18.38 N, 77.58 E) and Gale Crater (-4.59 N, 137.44 E),
  and compact grid layers.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_MCD_DIR = ROOT_DIR / "datos-marte" / "datos-marte"
OUTPUT_JSON_PATH = ROOT_DIR / "data" / "processed" / "mars_mcd_ls105.json"


def parse_mcd_ascii_blocks(file_path: Path) -> list[dict[str, Any]]:
    """Parse an MCD v6.2 ASCII file containing one or more `###` header + table blocks."""
    text = file_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    blocks: list[dict[str, Any]] = []
    idx = 0
    n = len(lines)

    while idx < n:
        if not lines[idx].startswith("###"):
            idx += 1
            continue

        header_lines: list[str] = []
        while idx < n and lines[idx].startswith("###"):
            header_lines.append(lines[idx])
            idx += 1

        variable_desc = "Unknown variable"
        for hline in header_lines:
            match = re.search(r"Columns 2\+ are\s+(.+)", hline)
            if match:
                variable_desc = match.group(1).strip()

        if idx >= n or not lines[idx].startswith("---- ||"):
            raise ValueError(f"Expected latitude header '---- ||' in {file_path.name} at line {idx}")

        lat_parts = lines[idx].split("||", 1)[1].split()
        latitudes = [float(val) for val in lat_parts]
        idx += 1

        if idx < n and lines[idx].startswith("---"):
            idx += 1

        longitudes: list[float] = []
        rows: list[list[float]] = []

        while idx < n and not lines[idx].startswith("###"):
            line = lines[idx]
            if "||" in line:
                lon_str, vals_str = line.split("||", 1)
                lon = float(lon_str.strip())
                vals = [float(v) for v in vals_str.split()]
                if len(vals) != len(latitudes):
                    raise ValueError(
                        f"Row longitude {lon} in {file_path.name} has {len(vals)} values, expected {len(latitudes)}"
                    )
                longitudes.append(lon)
                rows.append(vals)
            idx += 1

        blocks.append(
            {
                "variable": variable_desc,
                "latitudes": latitudes,
                "longitudes": longitudes,
                "matrix_lon_lat": rows,
            }
        )

    return blocks


def compute_grid_stats(longitudes: list[float], matrix_lon_lat: list[list[float]]) -> dict[str, float]:
    """
    Compute global min, max, and mean excluding +180 deg if -180 deg is already present,
    following instructions in `datos-marte/README.md`.
    """
    has_neg_180 = any(math.isclose(lon, -180.0) for lon in longitudes)
    values: list[float] = []
    for lon, row in zip(longitudes, matrix_lon_lat):
        if has_neg_180 and math.isclose(lon, 180.0):
            continue
        values.extend(row)

    return {
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(sum(values) / len(values), 6),
        "count_unique_meridians": len(values),
    }


def sample_bilinear(
    latitudes: list[float],
    longitudes: list[float],
    matrix_lon_lat: list[list[float]],
    target_lat: float,
    target_lon: float,
) -> dict[str, float]:
    """
    Interpolate (bilinear) and also return nearest grid cell value for (target_lat, target_lon).
    """
    # Nearest neighbor indices
    nearest_lat_idx = min(range(len(latitudes)), key=lambda i: abs(latitudes[i] - target_lat))
    nearest_lon_idx = min(range(len(longitudes)), key=lambda i: abs(longitudes[i] - target_lon))
    nearest_val = matrix_lon_lat[nearest_lon_idx][nearest_lat_idx]

    # Bilinear bracketing along latitude
    lat_i0 = 0
    for i in range(len(latitudes) - 1):
        if latitudes[i] <= target_lat <= latitudes[i + 1]:
            lat_i0 = i
            break
    lat_i1 = min(lat_i0 + 1, len(latitudes) - 1)

    # Bilinear bracketing along longitude
    lon_j0 = 0
    for j in range(len(longitudes) - 1):
        if longitudes[j] <= target_lon <= longitudes[j + 1]:
            lon_j0 = j
            break
    lon_j1 = min(lon_j0 + 1, len(longitudes) - 1)

    lat0, lat1 = latitudes[lat_i0], latitudes[lat_i1]
    lon0, lon1 = longitudes[lon_j0], longitudes[lon_j1]

    t_lat = 0.0 if math.isclose(lat0, lat1) else (target_lat - lat0) / (lat1 - lat0)
    t_lon = 0.0 if math.isclose(lon0, lon1) else (target_lon - lon0) / (lon1 - lon0)

    q00 = matrix_lon_lat[lon_j0][lat_i0]
    q01 = matrix_lon_lat[lon_j0][lat_i1]
    q10 = matrix_lon_lat[lon_j1][lat_i0]
    q11 = matrix_lon_lat[lon_j1][lat_i1]

    interp_val = (
        (1 - t_lon) * (1 - t_lat) * q00
        + (1 - t_lon) * t_lat * q01
        + t_lon * (1 - t_lat) * q10
        + t_lon * t_lat * q11
    )

    return {
        "bilinear": round(interp_val, 5),
        "nearest": round(nearest_val, 5),
        "nearest_grid_lat": round(latitudes[nearest_lat_idx], 4),
        "nearest_grid_lon": round(longitudes[nearest_lon_idx], 4),
    }


def build_mars_mcd_dataset() -> dict[str, Any]:
    tp_blocks = parse_mcd_ascii_blocks(RAW_MCD_DIR / "marte_ls105_temperatura_presion.txt")
    cd_blocks = parse_mcd_ascii_blocks(RAW_MCD_DIR / "marte_ls105_nubes_polvo.txt")
    wind_blocks = parse_mcd_ascii_blocks(RAW_MCD_DIR / "marte_ls105_viento_10m.txt")

    layer_defs = [
        ("surface_temperature_k", "K", tp_blocks[0]),
        ("surface_pressure_pa", "Pa", tp_blocks[1]),
        ("water_ice_column_kg_m2", "kg/m^2", cd_blocks[0]),
        ("dust_optical_depth_670nm", "dimensionless", cd_blocks[1]),
        ("wind_speed_10m_m_s", "m/s", wind_blocks[0]),
    ]

    latitudes = tp_blocks[0]["latitudes"]
    longitudes = tp_blocks[0]["longitudes"]

    reference_points = {
        "mars-jezero": {"name": "Jezero Crater (Perseverance landing region)", "lat": 18.38, "lon": 77.58},
        "mars-gale": {"name": "Gale Crater (Curiosity landing region)", "lat": -4.59, "lon": 137.44},
    }

    layers_summary: dict[str, Any] = {}
    point_extractions: dict[str, dict[str, Any]] = {
        pid: {"name": info["name"], "lat": info["lat"], "lon": info["lon"], "variables": {}}
        for pid, info in reference_points.items()
    }

    for key, unit, block in layer_defs:
        stats = compute_grid_stats(block["longitudes"], block["matrix_lon_lat"])
        layers_summary[key] = {
            "description": block["variable"],
            "unit": unit,
            "stats": stats,
        }
        for pid, info in reference_points.items():
            sampled = sample_bilinear(
                block["latitudes"],
                block["longitudes"],
                block["matrix_lon_lat"],
                info["lat"],
                info["lon"],
            )
            point_extractions[pid]["variables"][key] = sampled

    # Add derived Celsius and hPa for convenience
    for pid, pdata in point_extractions.items():
        temp_k = pdata["variables"]["surface_temperature_k"]["bilinear"]
        press_pa = pdata["variables"]["surface_pressure_pa"]["bilinear"]
        pdata["derived"] = {
            "mean_temperature_c": round(temp_k - 273.15, 2),
            "surface_pressure_hpa": round(press_pa / 100.0, 3),
        }

    payload = {
        "dataset_id": "mars-mcd-v6.2-ls105",
        "title": "Mars Climate Database (MCD) v6.2 Global Diurnal Mean at Ls=105 deg",
        "citation": "Mars Climate Database v6.2, LMD/OU/IAA/ESA/CNES",
        "url": "https://www-mars.lmd.jussieu.fr/mars/access",
        "scenario": "climatology average solar, diurnal mean over all local times, Ls = 105.0 deg",
        "grid_shape": {"longitudes": len(longitudes), "latitudes": len(latitudes)},
        "latitudes": latitudes,
        "longitudes": longitudes,
        "layers_summary": layers_summary,
        "reference_locations": point_extractions,
    }

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_mars_mcd_dataset()
    print(f"Generated {OUTPUT_JSON_PATH} with {len(result['layers_summary'])} MCD v6.2 layers.")
    print("Jezero Crater extracted MCD v6.2 values:", json.dumps(result["reference_locations"]["mars-jezero"], indent=2))
