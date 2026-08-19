import pytest
from app.lidar.tile_mapping import TileMappingError, resolve_tile

def test_official_index_url_preserves_addendum():
    obj = resolve_tile({"file_name":"CL2_BE36_2021_1000_5035.laz", "URL":"https://opentopography.s3.sdsc.edu/pc-bulk/NZ21_Waikato/Addendum5/CL2_BE36_2021_1000_5035.laz"})
    assert obj.object_key == "NZ21_Waikato/Addendum5/CL2_BE36_2021_1000_5035.laz"

def test_rejects_unverified_name():
    with pytest.raises(TileMappingError): resolve_tile({"name":"something.laz"})

def test_verified_linz_schema_fields():
    obj = resolve_tile({"index_tile_id":"BD34_1000_4928", "sheet_code_id":"BD34", "scale":1000, "tile":"4928"})
    assert obj.filename == "CL2_BD34_2021_1000_4928.laz"
