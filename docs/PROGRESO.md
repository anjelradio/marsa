# Implementation Progress Log

## Current Status: Phase 0 (Audit & Project Foundation) — In Progress

### Completed Tasks
- [x] **Repository & Branch Setup**: Updated `main` from `origin/main` (`141060c`) and created/switched to branch `dev`.
- [x] **Dataset Extraction**: Extracted `datos-marte.zip` into `datos-marte/datos-marte/` and inspected the 3 Mars Climate Database (MCD v6.2, `Ls=105°`) ASCII files and documentation.
- [x] **Initial Assessment (`docs/estado-inicial.md`)**: Documented existing `server/` (FastAPI Hexagonal) and `web/` (Next.js 16 + Three.js 3D Mars globe) architecture, MCD v6.2 data assets, USGS STAC / OpenTopography integrations, gaps, and risk mitigations.
- [x] **Architecture Decision Records (`docs/DECISIONES.md`)**: Recorded ADR-001 (Retain Next.js 16 + FastAPI stack), ADR-002 (Integrate MCD v6.2 data), and ADR-003 (USGS STAC & OpenTopography offline-first integration).

### In Progress
- [ ] Configure root `AGENTS.md`, `README.md`, and `.gitignore` updates.
- [ ] Add `/api/health` route alias in `server/app/main.py` and verify backend healthcheck with `pytest`.

### Next Task
- **Phase 1 (Scientific Ingestion & Vertical Slice)**: Create `pipelines/parse_mcd_mars.py` and `pipelines/build_catalog.py` to generate `data/manifest.json`, `data/processed/mars_mcd_ls105.json`, and `data/catalog/regions.json` with real, traceable data for `mars-jezero`, `moon-shackleton-rim`, and the terrestrial analog candidates.
