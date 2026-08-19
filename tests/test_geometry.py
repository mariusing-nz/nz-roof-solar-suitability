import numpy as np
from shapely.geometry import box
from app.roof.geometry import roof_faces

def test_disconnected_coplanar_patches_become_separate_faces():
    a = np.array([(x, y, 5 + .1*x) for x in np.linspace(0, 3, 8) for y in np.linspace(0, 3, 8)])
    b = np.array([(x, y, 5 + .1*x) for x in np.linspace(8, 11, 8) for y in np.linspace(0, 3, 8)])
    segment = {"points":np.vstack([a,b]), "normal":np.array([-.1,0,1]), "fit_rmse":.02}
    faces = roof_faces(segment, box(-1,-1,12,4), 1)
    assert len(faces) == 2
    assert [f["id"] for f in faces] == [1,2]
    assert all(f["horizontal_area_m2"] == pytest.approx(9, abs=.1) for f in faces)

import pytest
