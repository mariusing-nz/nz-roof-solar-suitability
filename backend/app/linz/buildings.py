from pyproj import Transformer
from shapely.geometry import Point, mapping, shape
from app.config import settings
from app.linz.wfs import LinzWFS

TO_NZTM = Transformer.from_crs(4326, 2193, always_xy=True)
TO_WGS84 = Transformer.from_crs(2193, 4326, always_xy=True)

async def building_at(lon: float, lat: float) -> dict:
    x, y = TO_NZTM.transform(lon, lat)
    data = await LinzWFS(settings.linz_building_layer_id).features(
        type_name=f"data.linz.govt.nz:layer-{settings.linz_building_layer_id}",
        bbox=(x-3, y-3, x+3, y+3),
    )
    point = Point(x, y)
    candidates = [(f, shape(f["geometry"])) for f in data.get("features", [])]
    containing = [(f, g) for f, g in candidates if g.covers(point)]
    if not containing:
        raise LookupError("No LINZ building outline found at this location.")
    feature, geometry = min(containing, key=lambda item: item[1].area)
    return {"id": feature["properties"]["building_id"], "properties": feature["properties"], "geometry_nztm": geometry}

def geometry_wgs84(geometry):
    from shapely.ops import transform
    return mapping(transform(TO_WGS84.transform, geometry))

