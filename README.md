# NZ LiDAR Roof Solar Suitability

A roof-geometry prototype for New Zealand. The browser accepts a map click; the planned vertical slice resolves a LINZ roof outline and all intersecting 1:1k tiles, crops Waikato 2021 LiDAR to Classification 6 with PDAL, detects planes, and returns GeoJSON with area, tilt, downslope azimuth, point count, and fit RMSE.

> **Prototype status:** the reusable geometry, mapping, cache, API shell and web map are implemented and unit tested. Live `/api/roof-analysis` deliberately returns `501` until a developer runs the authenticated schema probe and records the actual advertised LINZ feature types. This avoids inventing WFS behaviour.

## Screenshot

_Placeholder: capture after the first authenticated end-to-end roof succeeds._

## Architecture

```text
User → MapLibre → FastAPI → LINZ Building WFS (101290)
                           → LINZ 1:1k Tile Index (104692)
                           → exact Tile Index URL / filename
                           → OpenTopography S3 → atomic LAZ cache
                           → PDAL crop + Classification 6
                           → RANSAC roof planes → metrics → GeoJSON → map
```

CRS boundaries are explicit: browser coordinates are EPSG:4326; all spatial selection and XYZ analysis use EPSG:2193 (metres); heights are NZVD2016.

## Verified tile mapping

The official OpenTopography `NZ21_Waikato_TileIndex.zip` was inspected on 19 August 2026. Its DBF fields include `file_name`, `URL`, bounds, and point metadata. `file_name` values such as `CL2_BB33_2021_1000_2446.laz` follow LINZ's published `[product]_[Topo50 sheet]_[year]_[scale]_[row+column].[ext]` convention. `BB33` is the Topo50 sheet; the four digit suffix is the two-digit row plus two-digit column from an upper-left origin. The exact `URL` is authoritative because updated tiles may be under paths such as `NZ21_Waikato/Addendum5/`.

`backend/app/lidar/tile_mapping.py` is the only module that resolves names. It prefers exact `file_name` + `URL`, validates the name, and fails closed when fields are insufficient. LINZ layer 104692 schema still requires an authenticated `DescribeFeatureType`/feature sample; no field names have been fabricated.

Sources: [OpenTopography Waikato dataset](https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.042023.2193.2), [LINZ national LiDAR specification](https://www.linz.govt.nz/sites/default/files/pgf_version_new_zealand_national_aerial_lidar_base_specification.pdf).

## Data sources

- **LINZ NZ Building Outlines**, layer `101290`: aerial-image-derived roof outlines.
- **LINZ NZ 1:1k Tile Index**, layer `104692`.
- **OpenTopography Waikato 2021**, `OTLAS.042023.2193.2`: endpoint `https://opentopography.s3.sdsc.edu`, bucket `pc-bulk`, prefix `NZ21_Waikato/`, CC BY 4.0 data.

## Install and run (macOS)

PDAL is a native dependency. Homebrew is simplest; Conda-forge is a good alternative.

```bash
brew install pdal python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
# edit .env and set LINZ_API_KEY
PYTHONPATH=backend python scripts/probe_data_chain.py
uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```bash
python3 -m http.server 8080 --directory frontend
# open http://localhost:8080
```

Tests do not use live services:

```bash
pytest -q
```

## Configuration and safety

See `.env.example`. Only `LINZ_API_KEY` is secret and it remains backend-only. Input coordinates are bounded to New Zealand, cache filenames come from validated metadata, downloads use `.partial` files and atomic replacement, and neither arbitrary paths nor PDAL pipelines are accepted from clients.

## Current limitations

- The authenticated LINZ schema probe and complete live orchestration remain to be implemented; the endpoint fails honestly meanwhile.
- Waikato 2021 only; acquisition dates may differ from building outlines.
- Classification errors and complicated roofs, chimneys, skylights and furniture can impair segmentation.
- Current RANSAC segmentation still needs spatial-connectivity enforcement and clipped concave face boundaries.
- Roof polygons are estimates; no annual PV-production estimate exists.

## Roadmap

V1 completes WFS discovery, multi-tile PDAL extraction, connected roof boundaries and real-house validation. V2 adds setbacks, exclusions, panel packing and kWp. V3 adds terrain/vegetation/building shading and irradiance. V4 adds automatic nationwide dataset discovery, background work, persistent analysis cache and 3D/reporting.

