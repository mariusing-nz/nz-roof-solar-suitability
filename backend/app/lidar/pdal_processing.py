import asyncio
import csv
import json
import tempfile
from pathlib import Path
import numpy as np
from app.config import roof_classes, settings

class PdalError(RuntimeError): pass

def classification_limits() -> str:
    return ",".join(f"Classification[{value}:{value}]" for value in roof_classes())

async def extract_building_points(object_keys: list[str], geometry) -> np.ndarray:
    """Stream remote LAZ through PDAL, spatially crop first, then keep Class 6."""
    with tempfile.TemporaryDirectory(prefix="nz-roof-") as tmp:
        output = Path(tmp) / "points.csv"
        inputs = [
            {"type":"readers.las", "filename":f"{settings.opentopography_s3_endpoint.rstrip('/')}/{settings.opentopography_bucket}/{key}"}
            for key in object_keys
        ]
        pipeline = inputs + [
            {"type":"filters.crop", "polygon":geometry.buffer(settings.lidar_extraction_buffer_metres).wkt},
            {"type":"filters.range", "limits":classification_limits()},
            {"type":"writers.text", "filename":str(output), "format":"csv", "order":"X,Y,Z", "keep_unspecified":"false"},
        ]
        proc = await asyncio.create_subprocess_exec(
            "pdal", "pipeline", "--stdin", stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(json.dumps(pipeline).encode())
        if proc.returncode:
            raise PdalError("PDAL extraction failed: " + stderr.decode(errors="replace")[-500:])
        if not output.exists(): raise PdalError("PDAL did not produce an extracted point file.")
        with output.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        if not rows: return np.empty((0, 3), dtype=float)
        try: return np.array([[float(r["X"]), float(r["Y"]), float(r["Z"])] for r in rows])
        except (KeyError, ValueError) as exc: raise PdalError("PDAL returned invalid XYZ data.") from exc
