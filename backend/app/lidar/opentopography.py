import httpx
from app.config import settings
from app.lidar.tile_mapping import LidarObject, TileMappingError, resolve_tile

async def locate_object(properties: dict) -> LidarObject:
    candidate = resolve_tile(properties, settings.opentopography_prefix)
    roots = [settings.opentopography_prefix] + [f"{settings.opentopography_prefix}/Addendum{i}" for i in range(1, 6)]
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for root in roots:
            key = f"{root}/{candidate.filename}"
            url = f"{settings.opentopography_s3_endpoint.rstrip('/')}/{settings.opentopography_bucket}/{key}"
            response = await client.head(url)
            if response.status_code == 200:
                return LidarObject(candidate.filename, key)
            if response.status_code not in (403, 404): response.raise_for_status()
    raise TileMappingError(f"OpenTopography object unavailable for {candidate.filename}.")

