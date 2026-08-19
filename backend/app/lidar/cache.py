import logging, os
from pathlib import Path
import httpx

log = logging.getLogger(__name__)

async def cached_download(endpoint: str, bucket: str, object_key: str, cache_dir: Path) -> Path:
    filename = Path(object_key).name
    target = cache_dir / filename
    cache_dir.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size > 0:
        log.info("LiDAR cache hit: %s", filename); return target
    log.info("LiDAR cache miss: %s", filename)
    partial = target.with_suffix(target.suffix + ".partial")
    try:
        async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
            async with client.stream("GET", f"{endpoint.rstrip('/')}/{bucket}/{object_key}") as response:
                response.raise_for_status()
                with partial.open("wb") as out:
                    async for chunk in response.aiter_bytes(): out.write(chunk)
        if partial.stat().st_size == 0: raise IOError("Downloaded tile is empty")
        os.replace(partial, target)
        return target
    finally:
        partial.unlink(missing_ok=True)

