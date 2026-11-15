# Architectural & Technical Decisions (ADR)

## ADR-001: Retain Next.js 16 + React 19 + Three.js Frontend Instead of Angular
- **Date**: 2026-11-14
- **Status**: Accepted
- **Context**: Section 7 of `PLAN_PLANETARY_ANALOG_EXPLORER_NASA_2026.md` suggests Angular as a preferred frontend stack, while Section 17 explicitly states *"salvo que el repositorio existente obligue a adaptarnos"*. The existing `web/` directory already contains a production-grade **Next.js 16.2.9 + React 19 + Tailwind CSS v4 + shadcn/ui + Three.js** application with a working 3D Mars globe (`mars-planet.tsx`), custom atmospheric shaders, and a typed FastAPI HTTP client (`api-client.ts`).
- **Decision**: Keep and extend the existing Next.js 16 (`web/`) and FastAPI Hexagonal (`server/`) stack.
- **Consequences**: Preserves the 3D Mars visualization and clean architecture foundation, saving days of boilerplate work and allowing immediate focus on the scientific DSS engine and interactive analog explorer UI.

---

## ADR-002: Incorporate Mars Climate Database (MCD v6.2) into Environmental Testing Profile
- **Date**: 2026-11-14
- **Status**: Accepted
- **Context**: The repository includes `datos-marte.zip` containing validated ASCII grids from **Mars Climate Database (MCD) v6.2** (`Ls = 105°`, diurnal mean, `64 × 48` grid) for surface temperature (`K`), surface pressure (`Pa`), water ice column (`kg/m²`), visible dust optical depth (`670 nm`), and `10 m` horizontal wind speed (`m/s`).
- **Decision**:
  1. Parse the MCD v6.2 ASCII grids via a deterministic Python ETL script into structured JSON layers (`data/processed/mars_mcd_ls105.json`) avoiding double-counting of the `±180°` meridian on global statistics.
  2. Extract bilinear/nearest cell environmental metadata for Martian target AOIs (such as `mars-jezero` at `18.38° N, 77.58° E`) to enrich the scientific profile with traceable Martian atmospheric context alongside topographic metrics.
  3. Keep environmental testing comparisons scientifically honest: Earth temperature and aridity (NASA POWER) evaluate terrestrial equipment stress similarity (e.g., hyper-aridity, cold desert thermal regimes) rather than claiming direct atmospheric equivalence with Mars's ~6–7 hPa CO2 atmosphere.

---

## ADR-003: Integrate USGS Astrogeology STAC API and OpenTopography API
- **Date**: 2026-11-14
- **Status**: Accepted
- **Context**: `server/README.md` and `server/.env.template` define two primary external providers:
  1. **USGS Astrogeology STAC API** (`https://stac.astrogeology.usgs.gov/api`) — public, keyless STAC catalog for planetary datasets (Mars MOLA/HiRISE/CTX, Moon LOLA).
  2. **OpenTopography API** (`https://portal.opentopography.org/apidocs/`) — DEM provider for Earth AOIs using `OPENTOPOGRAPHY_API_KEY`.
- **Decision**: Register USGS STAC, OpenTopography, NASA POWER, Macrostrat, NASA PDS (MOLA/LOLA), and MCD v6.2 in `data/manifest.json` and `docs/FUENTES.md`, and implement offline-first caching so that P0 endpoints never fail if external networks or API keys are unavailable during evaluation.
