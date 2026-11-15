# Planetary Analog Explorer

**NASA Space Apps Challenge 2026** — *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*

Planetary Analog Explorer is an interpretable geospatial Decision Support System (DSS) that combines topography, geology, and environmental datasets from **Mars, the Moon, and Earth** to identify, rank, and justify terrestrial analog sites for planetary exploration testing (`rover_mobility`, `surface_geology`, and `environmental_testing`).

---

## Repository Structure

```text
naseando/
├── PLAN_PLANETARY_ANALOG_EXPLORER_NASA_2026.md  # Functional & scientific specification
├── AGENTS.md                                    # Agent & architecture guidelines
├── server/                                      # FastAPI Hexagonal backend (Python 3.12)
├── web/                                         # Next.js 16 + React 19 + Three.js frontend
├── pipelines/                                   # Reproducible offline scientific ETL scripts
├── data/                                        # Versioned catalog, processed MCD grids & manifest
│   ├── manifest.json                            # Dataset provenance, resolutions & licenses
│   ├── processed/                               # Processed Mars Climate Database (MCD v6.2) JSON
│   └── catalog/                                 # Validated RegionProfile catalog
└── docs/                                        # Project audit, ADRs, methodology & progress log
    ├── estado-inicial.md
    ├── DECISIONES.md
    ├── PROGRESO.md
    ├── FUENTES.md
    └── METODOLOGIA.md
```

---

## Quick Start

### 1. Backend (`server/`)
```bash
cd server
cp .env.template .env
python -m uvicorn app.main:app --reload --port 8000
```
Run backend tests:
```bash
cd server
python -m pytest
```

### 2. Frontend (`web/`)
```bash
cd web
cp .env.template .env
pnpm install
pnpm dev
```

---

## Scientific Data Sources & Attribution
- **Mars Climate Database (MCD) v6.2** (LMD/OU/IAA/ESA/CNES): Diurnal mean surface temperature, pressure, dust optical depth (670 nm), water ice column, and 10m wind speed at `Ls = 105°`.
- **USGS Astrogeology STAC API & NASA PDS (MOLA / LOLA)**: Planetary topography and reference coordinates for Jezero Crater (`mars-jezero`) and Shackleton Rim (`moon-shackleton-rim`, LOLA PGDA Site04).
- **OpenTopography / Copernicus DEM GLO-30 & SRTM**: Terrestrial digital elevation metrics (slope, ruggedness TRI, local relief).
- **NASA POWER Climatology & Macrostrat API v2**: Terrestrial temperature, hyper-aridity (annual precipitation), and lithological units.
