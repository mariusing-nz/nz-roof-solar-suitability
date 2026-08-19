from shapely.geometry import shape
from app.config import settings
from app.linz.wfs import LinzWFS

async def intersecting_tiles(geometry) -> list[dict]:
    query = geometry.buffer(settings.lidar_extraction_buffer_metres)
    data = await LinzWFS(settings.linz_tile_index_layer_id).features(
        type_name=f"data.linz.govt.nz:layer-{settings.linz_tile_index_layer_id}", bbox=query.bounds
    )
    return [f["properties"] for f in data.get("features", []) if shape(f["geometry"]).intersects(query)]

