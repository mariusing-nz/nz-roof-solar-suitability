from shapely import concave_hull
from shapely.geometry import MultiPoint, mapping
from shapely.ops import transform
from sklearn.cluster import DBSCAN
from app.config import settings
from app.linz.buildings import TO_WGS84
from app.roof.metrics import azimuth_degrees, compass_direction, surface_area, tilt_degrees

def _face_for_points(segment: dict, points, building, face_id: int) -> dict | None:
    cloud = MultiPoint(points[:, :2])
    horizontal = concave_hull(cloud, ratio=settings.concave_hull_ratio, allow_holes=False).intersection(building)
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
        "point_count": len(points),
        "fit_rmse": round(segment["fit_rmse"], 3),
        "geometry": mapping(transform(TO_WGS84.transform, horizontal)),
    }

def roof_faces(segment: dict, building, first_id: int) -> list[dict]:
    """Split coplanar but disconnected roof patches before creating boundaries."""
    points = segment["points"]
    labels = DBSCAN(eps=settings.spatial_connectivity_radius, min_samples=4).fit_predict(points[:, :2])
    faces = []
    for label in sorted(set(labels) - {-1}):
        cluster = points[labels == label]
        if len(cluster) < settings.min_plane_points: continue
        face = _face_for_points(segment, cluster, building, first_id + len(faces))
        if face and face["horizontal_area_m2"] >= settings.min_roof_face_area:
            faces.append(face)
    return faces
