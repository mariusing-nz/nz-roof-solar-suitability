import math
import numpy as np
from app.roof.metrics import azimuth_degrees, tilt_degrees
from app.roof.segmentation import segment_planes

def test_synthetic_gable():
    rng = np.random.default_rng(7); y = np.repeat(np.linspace(0,10,16),16); x = np.tile(np.linspace(-5,5,16),16)
    z = 5 - np.tan(math.radians(20))*np.abs(x) + rng.normal(0,.015,len(x))
    planes = segment_planes(np.c_[x,y,z], .06, 70, 2)
    assert len(planes) == 2
    assert sorted(tilt_degrees(p["normal"]) for p in planes) == pytest.approx([20,20], abs=1)
    assert sorted(round(azimuth_degrees(p["normal"])) for p in planes) == [90,270]

import pytest

