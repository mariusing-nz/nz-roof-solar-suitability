from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    linz_api_key: str = ""
    linz_basemap_api_key: str = ""
    linz_building_layer_id: int = 101290
    linz_tile_index_layer_id: int = 104692
    linz_wfs_base_url: str = "https://data.linz.govt.nz"
    opentopography_s3_endpoint: str = "https://opentopography.s3.sdsc.edu"
    opentopography_bucket: str = "pc-bulk"
    opentopography_prefix: str = "NZ21_Waikato"
    lidar_cache_dir: Path = Path("./data/lidar-cache")
    lidar_extraction_buffer_metres: float = 1.0
    min_roof_points: int = 50
    ransac_distance_threshold: float = 0.12
    min_plane_points: int = 30
    min_roof_face_area: float = 2.0
    spatial_connectivity_radius: float = 0.8
    concave_hull_ratio: float = 0.25

settings = Settings()
