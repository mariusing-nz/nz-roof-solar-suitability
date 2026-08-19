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
from app.lidar.pdal_processing import PdalError, extract_building_points
from app.roof.segmentation import segment_planes
from app.roof.geometry import roof_face

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
    if not 0 <= z <= 22 or x < 0 or y < 0:
        raise HTTPException(400, "Invalid map tile coordinates.")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if settings.linz_basemap_api_key:
                url = f"https://basemaps.linz.govt.nz/v1/tiles/aerial/3857/{z}/{x}/{y}.png"
                upstream = await client.get(url, params={"api": settings.linz_basemap_api_key})
            else:
                url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                upstream = await client.get(url)
        if upstream.status_code == 404:
            raise HTTPException(404, "Aerial tile unavailable.")
        upstream.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(502, "LINZ aerial basemap request failed.") from exc
    media_type = upstream.headers.get("content-type", "image/jpeg").split(";", 1)[0]
    return Response(upstream.content, media_type=media_type, headers={"Cache-Control":"public, max-age=86400"})

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
        points = await extract_building_points([o.object_key for o in objects], building["geometry_nztm"])
        if len(points) == 0: raise LookupError("No Classification 6 building points found.")
        if len(points) < settings.min_roof_points:
            raise LookupError(f"Insufficient roof points ({len(points)}; minimum {settings.min_roof_points}).")
        segments = segment_planes(points, settings.ransac_distance_threshold, settings.min_plane_points)
        faces = []
        for segment in segments:
            face = roof_face(segment, building["geometry_nztm"], len(faces) + 1)
            if face and face["horizontal_area_m2"] >= settings.min_roof_face_area: faces.append(face)
        if not faces: raise LookupError("Roof-plane segmentation produced no usable faces.")
    except LookupError as exc: raise HTTPException(404, str(exc)) from exc
    except (LinzError, TileMappingError, PdalError) as exc: raise HTTPException(502, str(exc)) from exc
    return {
        "building":{"id":str(building["id"]), "geometry":geometry_wgs84(building["geometry_nztm"])},
        "lidar":{"tiles":[o.filename for o in objects], "point_count":len(points)},
        "roof_faces":faces,
        "processing":{"duration_seconds":round(time.perf_counter()-started,3), "warnings":["Prototype RANSAC boundaries use building-clipped point hulls."]},
    }
