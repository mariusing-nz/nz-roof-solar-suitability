import numpy as np
from sklearn.linear_model import RANSACRegressor
from app.roof.metrics import fit_plane

def segment_planes(points, distance_threshold=.12, min_points=30, max_planes=12):
    remaining = np.asarray(points, float); result = []
    for _ in range(max_planes):
        if len(remaining) < min_points: break
        model = RANSACRegressor(residual_threshold=distance_threshold, min_samples=3, random_state=42).fit(remaining[:,:2], remaining[:,2])
        mask = model.inlier_mask_
        if mask.sum() < min_points: break
        cloud = remaining[mask]; normal, d, rmse = fit_plane(cloud)
        result.append({"points":cloud, "normal":normal, "d":d, "fit_rmse":rmse})
        remaining = remaining[~mask]
    return result

