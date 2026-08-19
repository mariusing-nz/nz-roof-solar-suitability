import httpx
from app.config import settings

class LinzError(RuntimeError): pass

class LinzWFS:
    def __init__(self, layer_id: int):
        if not settings.linz_api_key:
            raise LinzError("LINZ_API_KEY is not configured.")
        self.url = f"{settings.linz_wfs_base_url}/services;key={settings.linz_api_key}/wfs/layer-{layer_id}/"

    async def capabilities(self) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.url, params={"service":"WFS", "request":"GetCapabilities"})
            response.raise_for_status()
            return response.text

    async def features(self, *, type_name: str, bbox: tuple[float,float,float,float], srs: str = "EPSG:2193") -> dict:
        params = {"service":"WFS", "version":"2.0.0", "request":"GetFeature", "typeNames":type_name,
                  "srsName":srs, "bbox":",".join(map(str, (*bbox, srs))), "outputFormat":"application/json"}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.get(self.url, params=params)
            if response.status_code in (401, 403): raise LinzError("LINZ authentication failed.")
            response.raise_for_status()
            return response.json()

