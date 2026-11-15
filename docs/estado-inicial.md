# Initial Repository & Environment Assessment

## 1. Existing Architecture & Assets

### 1.1 Backend (`server/`)
- **Framework & Architecture**: FastAPI (`0.137.2`), SQLModel (`0.0.38`), SQLAlchemy (`2.0.51`), Pydantic v2 (`2.13.4`), structured following **Hexagonal Architecture & DDD** (`app/modules/<module>/{domain,application,infrastructure}`).
- **Tooling**: Includes `server/scripts/create_module.py` for rapid module scaffolding and `pytest` configuration (`server/pytest.ini`).
- **Health Check**: `/health` endpoint already implemented in `server/app/main.py` (we will also alias `/api/health` to satisfy the spec contract).
- **Documented Data Sources (`server/README.md` & `server/.env.template`)**:
  - **USGS Astrogeology STAC API** (`https://stac.astrogeology.usgs.gov/api`): Public STAC catalog for Mars and Moon collections/items without API key requirements.
  - **OpenTopography API**: Configured via `OPENTOPOGRAPHY_API_KEY` in `server/.env` for Earth Digital Elevation Models (DEMs).

### 1.2 Frontend (`web/`)
- **Framework & Stack**: **Next.js 16.2.9** (App Router), **React 19.2.4**, **TypeScript 5**, **Tailwind CSS v4**, **shadcn/ui** (`radix-ui`), and **Three.js (`0.187.0`)**.
- **Architecture**: Clean/Hexagonal feature structure (`src/features/{feature,shared}/{domain,infrastructure,presentation}`) documented in `web/AGENTS.md`.
- **HTTP & Error Handling**: Pre-built `api-client.ts` with FastAPI error adapter (`NEXT_PUBLIC_BACKEND_ADAPTER=fastapi`).
- **Existing Planetary Assets**:
  - `web/src/app/home/page.tsx` and `mars-mission-panels.tsx`: Space dashboard layout with orbital mechanics calculations (vis-viva equation) and NASA NSSDC reference metrics.
  - `web/src/features/mars/presentation/components/mars-planet.tsx`: Interactive WebGL2 / Three.js 3D Mars globe with custom day/night atmospheric scattering shaders, bump mapping, and surface mesh overlay (`mars-surface-overlay.ts`).

### 1.3 Local Scientific Datasets (`datos-marte.zip` -> `datos-marte/datos-marte/`)
- **Source**: **Mars Climate Database (MCD) v6.2** (LMD/OU/IAA/ESA/CNES), `climatology ave solar` scenario, diurnal mean at `Ls = 105°` (northern hemisphere summer).
- **Spatial Resolution**: Global `64 × 48` grid (`-180°` to `+180°` East longitude, `-90°` to `+90°` North latitude; 3,072 finite values per block).
- **Variables Included**:
  1. `marte_ls105_temperatura_presion.txt`: Surface temperature (`K`, range `142.16–235.65 K`) and surface pressure (`Pa`, range `199.89–1295.68 Pa`).
  2. `marte_ls105_nubes_polvo.txt`: Atmospheric water ice column (`kg/m²`) and visible dust optical depth at `670 nm` (dimensionless, range `0.0099–0.3346`).
  3. `marte_ls105_viento_10m.txt`: Horizontal wind speed at `10 m` above surface (`m/s`, range `0.52–17.45 m/s`).

---

## 2. Gaps Against Specification

1. **Missing Geospatial & Scientific Dependencies (`server/requirements.txt`)**:
   - Currently lacks `numpy` (and optionally `rasterio`/`shapely`/`pyproj` for DEM raster processing). Standard Python + `numpy` is sufficient to parse MCD grids, compute DEM morphological metrics (`median_slope_deg`, `slope_p90_deg`, `ruggedness_tri`, `local_relief_m`), and run the deterministic similarity engine.
2. **Missing Domain Catalog & Manifest (`data/manifest.json`, `data/catalog/`)**:
   - Need offline ETL scripts (`pipelines/`) to parse MCD v6.2 data, integrate topographic/environmental metrics for planetary targets (`mars-jezero`, `moon-shackleton-rim`) and Earth analog candidates, and produce a versioned, traceable catalog.
3. **Missing Similarity & Catalog API Endpoints (`server/app/modules/`)**:
   - Need `/api/health`, `/api/targets`, `/api/sites`, `/api/regions/{id}`, `/api/compare`, and `/api/sources`.
4. **Frontend Integration (`web/`)**:
   - Need interactive 2D map (MapLibre GL JS or interactive SVG/Canvas projection with GeoJSON polygons) alongside the 3D Mars view, mission profile selector (`rover_mobility`, `surface_geology`, `environmental_testing`), customizable weight sliders, side-by-side scientific comparison cards, and coordinate search.

---

## 3. Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Stack mismatch (Plan suggested Angular; repo uses Next.js 16 + React 19) | Rebuilding from scratch would waste existing 3D Mars globe and HTTP infrastructure | **Resolved**: Adapt to existing Next.js 16 + FastAPI Hexagonal stack per Section 17 clause. |
| External API rate limits or missing credentials during live evaluation | Demo failure if NASA POWER / OpenTopography is unreachable | Pre-compute and version the real catalog in `data/catalog/` with full provenance in `data/manifest.json` so P0 runs 100% offline. |
| Scale mismatch between planetary grids and local DEMs | Scientifically invalid direct comparisons | Explicitly record `native_resolution_m` and `analysis_scale_m` per feature; separate regional climate context (MCD / NASA POWER) from local topographic metrics. |

---

## 4. Next Steps (Phase 0 -> Phase 1 Vertical Slice)

1. Complete Phase 0 documentation (`docs/DECISIONES.md`, `docs/PROGRESO.md`, `AGENTS.md`, `.gitignore`) and verify backend `/api/health` with automated `pytest` tests.
2. Build the offline ETL pipeline (`pipelines/parse_mcd_mars.py` and `pipelines/build_catalog.py`) to extract exact Mars MCD v6.2 parameters for Jezero Crater and global heatmaps, combined with traced topographic/climatic profiles for `mars-jezero`, `moon-shackleton-rim`, and initial Earth analog sites.
3. Implement the pure similarity engine and FastAPI module (`analog_explorer`) with unit and HTTP tests.
