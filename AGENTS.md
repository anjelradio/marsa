# Planetary Analog Explorer — Agent Guidelines

## Overview
**Planetary Analog Explorer** is a scientific Decision Support System (DSS) built for the **NASA Space Apps Challenge 2026** (*Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*).

## Architecture & Stack
- **Backend (`server/`)**: Python 3.12 + FastAPI + SQLModel + Pydantic v2 following **Hexagonal Architecture & DDD** (`server/app/modules/<module>/{domain,application,infrastructure}`).
- **Frontend (`web/`)**: Next.js 16 (App Router) + React 19 + TypeScript 5 + Tailwind CSS v4 + shadcn/ui + Three.js (`web/src/features/<feature>/{domain,infrastructure,presentation}`).
- **Scientific Pipelines (`pipelines/` & `data/`)**: Deterministic offline ETL scripts generating versioned datasets and provenance manifests (`data/manifest.json`, `data/catalog/`, `data/processed/`).

## Core Engineering & Scientific Rules
1. **Traceability First**: Every terrestrial and planetary region metric must carry provenance metadata (`source_id`, `dataset_version`, `native_resolution_m`, `analysis_scale_m`, `method`, `quality`, `null_reason`).
2. **Never Invent Scientific Values**: Never replace `null` with `0` or fabricate similarity scores. Any synthetic test fixture must live in `data/demo/` or `server/tests/` and be explicitly tagged `DEMO` or `SCHEMA_EXAMPLE_NOT_DATA`.
3. **Separate Scientific Scoring from Visual/ML Exploration**: The deterministic multi-criteria engine (`similarity`) computes geoscientific compatibility (`raw_score` and `coverage`), never an LLM.
4. **Offline-First P0 Reliability**: All P0 endpoints (`/api/health`, `/api/targets`, `/api/sites`, `/api/regions/{id}`, `/api/compare`, `/api/sources`) must work without live internet dependencies using the versioned catalog in `data/catalog/`.
5. **Artifact Language**: Keep code identifiers, comments, commit messages, and technical documentation in English unless Spanish UI copy is required for the user-facing product.
