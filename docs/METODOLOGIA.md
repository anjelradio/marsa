# Scientific & Mathematical Methodology (`baseline-v1`)

## 1. Purpose and Scope
**Planetary Analog Explorer** is an interpretable multi-criteria Decision Support System (DSS) designed to identify, rank, and justify terrestrial analog sites for lunar and Martian mission testing. It **does not** claim planetary habitability or exact geological identity; it proposes ranked candidate locations with transparent feature breakdowns and explicit limitations.

---

## 2. Cross-Planetary Scale & Datum Harmonization

1. **Common Spatial Scale (`analysis_scale_m = 100 m`)**:
   - Slope and Terrain Ruggedness Index (TRI) are scale-dependent. Comparing a `1 m` HiRISE raster directly against a `500 m` global DEM produces scientifically invalid ratios.
   - All topographic indicators (`median_slope_deg`, `slope_p90_deg`, `ruggedness_tri`, `local_relief_m`) are evaluated at a documented common scale of **`100 m`**. If a candidate and target have incompatible spatial scales (`>5%` difference), topographic indicators are automatically excluded with status `incompatible_scale`.
2. **Local Relief (`p95 - p5`) Instead of Absolute Elevation**:
   - Earth uses orthometric/ellipsoidal heights relative to WGS84/EGM96 sea level, whereas Mars (`IAU_2015:49900` areoid) and the Moon (`IAU_2000:30100` mean radius) use distinct planetary reference surfaces.
   - Absolute elevations are **never** compared across bodies. Instead, we compare **local relief** (`p95 - p5` elevation difference in meters within the AOI).

---

## 3. Feature Similarity Formulation

### 3.1 Numeric Indicators
For each numeric indicator $i \in \{\text{median\_slope\_deg}, \text{slope\_p90\_deg}, \text{ruggedness\_tri}, \text{local\_relief\_m}, \text{ndvi}, \text{precipitation\_mm\_year}, \text{mean\_temperature\_c}\}$:

$$\text{sim}_i = \max\left(0,\; 1 - \frac{|x_i - y_i|}{\text{tolerance}_i}\right) \in [0, 1]$$

where:
- $x_i$ is the terrestrial candidate value,
- $y_i$ is the planetary reference value,
- $\text{tolerance}_i$ is the maximum admissible domain difference:

| Indicator | Unit | Default Tolerance ($\text{tolerance}_i$) | Scientific Rationale |
| :--- | :---: | :---: | :--- |
| `median_slope_deg` | `deg` | `12.0°` | Distinguishes gentle basin floors (`<5°`) from steep crater rims (`>14°`). |
| `slope_p90_deg` | `deg` | `20.0°` | Captures 90th-percentile hazard slopes critical for rover wheel slip and tip-over margins. |
| `ruggedness_tri` | `TRI` | `6.5` | Separates smooth alluvial/playa flats from rough lava flows and impact ejecta. |
| `local_relief_m` | `m` | `450.0 m` | Differentiates low-relief delta plains (`~180 m`) from deep polar craters (`>600 m`). |
| `ndvi` | `[0..1]` | `0.35` | Penalizes vegetated surfaces (`>0.20`) that obscure bare regolith/outcrop optics. |
| `precipitation_mm_year` | `mm/yr` | `500.0 mm` | Prioritizes hyper-arid (`<20 mm/yr`) and arid (`<200 mm/yr`) desert regimes. |
| `mean_temperature_c` | `°C` | `65.0 °C` | Rewards cold polar/high-altitude deserts (`McMurdo -19.8°C`, `Haughton -16.2°C`) when testing thermal stress. |

### 3.2 Categorical Lithology Compatibility
Lithology is evaluated via a versioned compatibility matrix (`data/manifest.json` -> `lithology_compatibility_matrix`) mapping planetary lithological classes (`fluvio_lacustrine_volcaniclastic`, `anorthositic_highland_impact_regolith`) to terrestrial classes in `[0, 1]`.

---

## 4. Aggregation, Coverage & Classification

Given requested weights $w_i > 0$ and the subset of valid (non-null, scale-compatible) indicators $V$:

$$\text{raw\_score} = 100 \times \frac{\sum_{i \in V} w_i \cdot \text{sim}_i}{\sum_{i \in V} w_i}, \qquad \text{coverage} = \frac{\sum_{i \in V} w_i}{\sum_{\text{all requested } j} w_j}$$

- **Missing Data Policy**: `null` values are **never** coerced to `0`. They are excluded from the numerator and denominator of `raw_score` and reduce `coverage`.
- **Classification & Ranking Order**:
  - `suitable` (`apto`): $\text{coverage} \ge 0.70$. Ranked first by `(raw_score, coverage)` descending.
  - `insufficient_coverage`: $0 < \text{coverage} < 0.70$. Ranked below all `suitable` sites by `(coverage, raw_score)` so a site with a single matching metric never leads the ranking.
  - `not_evaluated`: $\text{coverage} = 0$.

---

## 5. Mission Profiles (`rover_mobility`, `surface_geology`, `environmental_testing`)

| Indicator | `rover_mobility` | `surface_geology` | `environmental_testing` |
| :--- | :---: | :---: | :---: |
| `median_slope_deg` | `0.35` | `0.15` | `0.20` |
| `slope_p90_deg` | `0.25` | `—` | `—` |
| `ruggedness_tri` | `0.25` | `0.25` | `—` |
| `local_relief_m` | `0.15` | `0.20` | `—` |
| `lithology` | `—` | `0.40` | `—` |
| `precipitation_mm_year` | `—` | `—` | `0.35` |
| `ndvi` | `—` | `—` | `0.25` |
| `mean_temperature_c` | `—` | `—` | `0.20` |
