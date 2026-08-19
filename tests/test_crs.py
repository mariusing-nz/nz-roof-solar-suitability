from pyproj import Transformer

def test_crs_round_trip():
    forward = Transformer.from_crs(4326, 2193, always_xy=True)
    reverse = Transformer.from_crs(2193, 4326, always_xy=True)
    lon, lat = 175.46931, -37.89122
    x, y = forward.transform(lon, lat)
    assert (x, y) == pytest.approx((1817135.34, 5803379.55), abs=.05)
    assert reverse.transform(x, y) == pytest.approx((lon, lat), abs=1e-8)

import pytest
