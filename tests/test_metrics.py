import math
import numpy as np
from app.roof.metrics import azimuth_degrees, compass_direction, fit_plane, surface_area, tilt_degrees

def normal_for(tilt, azimuth):
    t, a = map(math.radians, (tilt, azimuth))
    return np.array([math.sin(t)*math.sin(a), math.sin(t)*math.cos(a), math.cos(t)])

def test_tilt_azimuth_and_direction():
    n = normal_for(20, 30)
    assert tilt_degrees(n) == pytest.approx(20)
    assert azimuth_degrees(n) == pytest.approx(30)
    assert compass_direction(30) == "NE"

def test_plane_fit_and_area():
    xy = np.array([(x,y) for x in range(8) for y in range(8)], float)
    pts = np.c_[xy, 10 + .2*xy[:,0] - .1*xy[:,1]]
    _, _, rmse = fit_plane(pts)
    assert rmse < 1e-10
    assert surface_area(100, 60) == pytest.approx(200)

import pytest

