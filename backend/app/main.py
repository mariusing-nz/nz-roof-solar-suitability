import logging
import time
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import RoofAnalysisRequest
from app.linz.buildings import building_at, geometry_wgs84
from app.linz.tile_index import intersecting_tiles
from app.lidar.opentopography import locate_object
from app.linz.wfs import LinzError
from app.lidar.tile_mapping import TileMappingError

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
app = FastAPI(title="NZ Roof Solar Suitability", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8000", "http://localhost:8080"], allow_methods=["GET","POST"], allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"ok", "linz_configured": bool(settings.linz_api_key)}

@app.get("/api/basemap/{z}/{x}/{y}.png")
async def aerial_basemap(z: int, x: int, y: int):
    """Backend proxy keeps the LINZ key out of browser JavaScript and network URLs."""
    if not settings.linz_api_key:
        raise HTTPException(503, "LINZ_API_KEY is not configured.")
    if not 0 <= z <= 22 or x < 0 or y < 0:
        raise HTTPException(400, "Invalid map tile coordinates.")
    url = f"https://basemaps.linz.govt.nz/v1/tiles/aerial/3857/{z}/{x}/{y}.png"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            upstream = await client.get(url, params={"api": settings.linz_api_key})
        if upstream.status_code == 404:
            raise HTTPException(404, "Aerial tile unavailable.")
        upstream.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(502, "LINZ aerial basemap request failed.") from exc
    return Response(upstream.content, media_type="image/png", headers={"Cache-Control":"public, max-age=86400"})

@app.post("/api/roof-analysis")
async def roof_analysis(request: RoofAnalysisRequest):
    if not settings.linz_api_key:
        raise HTTPException(503, "LINZ_API_KEY is not configured.")
    started = time.perf_counter()
    try:
        building = await building_at(request.lon, request.lat)
        tile_properties = await intersecting_tiles(building["geometry_nztm"])
        if not tile_properties: raise LookupError("No intersecting LINZ 1:1k tile found.")
        objects = [await locate_object(p) for p in tile_properties]
    except LookupError as exc: raise HTTPException(404, str(exc)) from exc
    except (LinzError, TileMappingError) as exc: raise HTTPException(502, str(exc)) from exc
    return {
        "building":{"id":str(building["id"]), "geometry":geometry_wgs84(building["geometry_nztm"])},
        "lidar":{"tiles":[o.filename for o in objects], "object_keys":[o.object_key for o in objects], "point_count":0},
        "roof_faces":[],
        "processing":{"duration_seconds":round(time.perf_counter()-started,3), "warnings":["Tile chain verified; PDAL extraction and roof-face polygonization are not yet connected to this endpoint."]},
    }
