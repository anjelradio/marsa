# Scientific Data Sources & Attribution Catalog

Every dataset integrated into **Planetary Analog Explorer** is documented below with its native spatial resolution, coordinate reference system (CRS), variables derived, and scientific limitations.

---

## 1. Planetary Sources (Mars & Moon)

### 1.1 Mars Climate Database (MCD) v6.2 (`mars-mcd-v6.2`)
- **Provider**: Laboratoire de Météorologie Dynamique (LMD) / Open University / IAA / ESA / CNES
- **URL**: https://www-mars.lmd.jussieu.fr/mars/access
- **Scenario & Version**: `MCD v6.2`, `climatology average solar`, diurnal mean over all local times at solar longitude `Ls = 105°` (northern summer).
- **Spatial Resolution & CRS**: Global `64 × 48` grid (`~330 km` equatorial spacing), `IAU2000 Mars Equirectangular` (`-180°` to `+180°` East, `-90°` to `+90°` North).
- **Variables Derived**:
  - `surface_temperature_k` / `mean_temperature_c` (`K` / `°C`)
  - `surface_pressure_pa` / `surface_pressure_hpa` (`Pa` / `hPa`)
  - `water_ice_column_kg_m2` (`kg/m²`)
  - `dust_optical_depth_670nm` (dimensionless visible optical depth at `670 nm`)
  - `wind_speed_10m_m_s` (`m/s` at `10 m` above local surface)
- **License & Attribution**: Mars Climate Database v6.2, LMD/OU/IAA/ESA/CNES.

### 1.2 USGS Astrogeology STAC API & NASA PDS MOLA/HiRISE (`usgs-stac-mars-mola-hirise`)
- **Provider**: USGS Astrogeology Science Center & NASA Planetary Data System (PDS Geosciences Node)
- **URLs**:
  - STAC API: https://stac.astrogeology.usgs.gov/api
  - MOLA MEGDR: https://pds-geosciences.wustl.edu/missions/mgs/megdr.html
- **Target Covered**: `mars-jezero` (Jezero Crater western delta and floor, `18.38° N, 77.58° E`, `IAU_2015:49900`).
- **Native Resolution & Common Analysis Scale**: `20 m/pixel` DTM resampled to `analysis_scale_m = 100 m` for cross-body comparability with Earth DEMs.
- **License**: Public Domain (NASA / USGS).

### 1.3 NASA PGDA LRO LOLA South Pole Site04 (`nasa-pgda-lola-site04`)
- **Provider**: NASA GSFC Planetary Geodesy Data Archive (PGDA)
- **URL**: https://pgda.gsfc.nasa.gov/products/78
- **Target Covered**: `moon-shackleton-rim` (Shackleton Crater illuminated rim sector, `-89.78° S, 120.0° E`, `IAU_2000:30100` South Polar Stereographic).
- **Native Resolution & Common Analysis Scale**: `5 m–20 m` polar laser altimetry products aggregated to `analysis_scale_m = 100 m`.
- **Limitations**: Includes track interpolation uncertainty at extreme polar latitudes; no atmospheric variables apply.
- **License**: Public Domain (NASA).

---

## 2. Terrestrial Sources (Earth Analog Candidates)

### 2.1 OpenTopography — Copernicus DEM GLO-30 & SRTM (`opentopography-copernicus-glo30`)
- **Provider**: OpenTopography / ESA Copernicus / NASA JPL
- **URL**: https://portal.opentopography.org/apidocs/
- **Native Resolution & Common Analysis Scale**: `30 m` (`GLO-30`) reprojected to local metric UTM zones and aggregated to `analysis_scale_m = 100 m`.
- **Variables Derived**:
  - `median_slope_deg` (degrees)
  - `slope_p90_deg` (90th percentile slope in degrees)
  - `ruggedness_tri` (Terrain Ruggedness Index at 100 m scale)
  - `local_relief_m` (`p95 - p5` elevation range in meters within AOI)
- **Notes**: High-latitude sites (`earth-haughton-crater` at `75.38° N` and `earth-mcmurdo-dry-valleys` at `-77.52° S`) lie outside SRTM coverage (`±60°`) and rely on Copernicus GLO-30 / polar DEM coverage.

### 2.2 NASA POWER Climatology API (`nasa-power-climatology`)
- **Provider**: NASA Langley Research Center (LaRC)
- **URL**: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/
- **Native Resolution**: `0.5° × 0.625°` (`~50 km`), 30-year climatology (`1991–2020`).
- **Variables Derived**: `precipitation_mm_year` (`mm/year`) and `mean_temperature_c` (`°C`).
- **Limitations**: Coarse regional grid; represents macro-climatic aridity and thermal regime rather than micro-topographic shelter.

### 2.3 Macrostrat API v2 (`macrostrat-v2`)
- **Provider**: University of Wisconsin–Madison Macrostrat & regional geological surveys
- **URL**: https://macrostrat.org/api
- **Variable Derived**: `lithology` (harmonized planetary analog lithological classes).
- **License**: CC-BY 4.0.

### 2.4 NASA Harmonized Landsat Sentinel-2 (`nasa-hls-ndvi`)
- **Provider**: NASA LP DAAC
- **URL**: https://hls.gsfc.nasa.gov/data-access-and-tools/
- **Native Resolution**: `30 m`.
- **Variable Derived**: `ndvi` (Normalized Difference Vegetation Index, `[0..1]`, used to verify surface bareness / lack of vegetation mask).
