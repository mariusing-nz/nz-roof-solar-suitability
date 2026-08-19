"""Read-only probe. Requires LINZ_API_KEY and PDAL; records advertised schemas before queries."""
import asyncio, re
from app.config import settings
from app.linz.wfs import LinzWFS

async def main():
    for layer in (settings.linz_building_layer_id, settings.linz_tile_index_layer_id):
        xml = await LinzWFS(layer).capabilities()
        names = sorted(set(re.findall(r"<Name>([^<]+)</Name>", xml)))
        print(f"layer {layer} advertised feature types: {names}")
    print("Next: use the printed type names in bounded EPSG:2193 queries; no names are guessed.")

if __name__ == "__main__": asyncio.run(main())

