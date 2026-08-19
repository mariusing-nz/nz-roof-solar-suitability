from shapely.geometry import MultiPoint, mapping
from shapely.ops import transform
from app.linz.buildings import TO_WGS84
from app.roof.metrics import azimuth_degrees, compass_direction, surface_area, tilt_degrees

def roof_face(segment: dict, building, face_id: int) -> dict | None:
    horizontal = MultiPoint(segment["points"][:, :2]).convex_hull.intersection(building)
    if horizontal.is_empty or horizontal.geom_type not in ("Polygon", "MultiPolygon"):
        return None
    horizontal_area = horizontal.area
    tilt = tilt_degrees(segment["normal"])
    azimuth = azimuth_degrees(segment["normal"])
    return {
        "id": face_id,
        "area_m2": round(surface_area(horizontal_area, tilt), 2),
        "horizontal_area_m2": round(horizontal_area, 2),
        "tilt_deg": round(tilt, 1),
        "azimuth_deg": round(azimuth, 1),
        "direction": compass_direction(azimuth),
        "point_count": len(segment["points"]),
        "fit_rmse": round(segment["fit_rmse"], 3),
        "geometry": mapping(transform(TO_WGS84.transform, horizontal)),
    }

