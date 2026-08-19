import math
import numpy as np

def upward_normal(normal):
    n = np.asarray(normal, dtype=float); n /= np.linalg.norm(n)
    return -n if n[2] < 0 else n

def tilt_degrees(normal) -> float:
    n = upward_normal(normal)
    return math.degrees(math.acos(float(np.clip(n[2], -1, 1))))

def azimuth_degrees(normal) -> float:
    """Downslope compass bearing; NZTM x=east, y=north."""
    n = upward_normal(normal)
    return math.degrees(math.atan2(n[0], n[1])) % 360

def compass_direction(azimuth: float) -> str:
    return ("N","NE","E","SE","S","SW","W","NW")[int((azimuth % 360 + 22.5)//45) % 8]

def surface_area(horizontal_area: float, tilt_deg: float) -> float:
    return horizontal_area / math.cos(math.radians(tilt_deg))

def fit_plane(points):
    pts = np.asarray(points, dtype=float); centroid = pts.mean(axis=0)
    _, _, vh = np.linalg.svd(pts - centroid, full_matrices=False)
    normal = upward_normal(vh[-1]); d = -float(normal @ centroid)
    residuals = pts @ normal + d
    return normal, d, float(np.sqrt(np.mean(residuals**2)))

