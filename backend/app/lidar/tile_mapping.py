import re
from dataclasses import dataclass
from urllib.parse import urlparse

PATTERN = re.compile(r"^CL2_([A-Z]{2}\d{2})_(\d{4})_1000_(\d{4})\.laz$")

class TileMappingError(ValueError): pass

@dataclass(frozen=True)
class LidarObject:
    filename: str
    object_key: str

def resolve_tile(properties: dict, prefix: str = "NZ21_Waikato") -> LidarObject:
    """Resolve only observed, validated tile-index fields; never guess from geometry."""
    filename = next((str(properties[k]).strip() for k in ("file_name", "filename", "name") if properties.get(k)), "")
    if not filename:
        sheet = next((str(properties[k]).strip() for k in ("sheet_code_id", "sheet", "topo50") if properties.get(k)), "")
        tile = next((str(properties[k]).strip().zfill(4) for k in ("tile", "tile_id", "tile_num") if properties.get(k) is not None), "")
        if properties.get("scale") not in (None, 1000, "1000"):
            raise TileMappingError("Only LINZ 1:1k tiles are supported.")
        if sheet and tile: filename = f"CL2_{sheet}_2021_1000_{tile}.laz"
    if not PATTERN.fullmatch(filename):
        raise TileMappingError("Tile index does not provide a verified Waikato 2021 CL2 filename.")
    url = next((str(properties[k]).strip() for k in ("URL", "url") if properties.get(k)), "")
    marker = "/pc-bulk/"
    object_key = urlparse(url).path.split(marker, 1)[1] if url and marker in urlparse(url).path else f"{prefix.strip('/')}/{filename}"
    if not object_key.endswith("/" + filename) and object_key != filename:
        raise TileMappingError("Tile URL and filename disagree.")
    return LidarObject(filename, object_key)
