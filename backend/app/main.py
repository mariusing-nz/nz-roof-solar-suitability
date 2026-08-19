import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import RoofAnalysisRequest

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="NZ Roof Solar Suitability", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8000", "http://localhost:8080"], allow_methods=["GET","POST"], allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"ok", "linz_configured": bool(settings.linz_api_key)}

@app.post("/api/roof-analysis")
async def roof_analysis(request: RoofAnalysisRequest):
    if not settings.linz_api_key:
        raise HTTPException(503, "LINZ_API_KEY is not configured.")
    raise HTTPException(501, "Live analysis requires advertised LINZ feature types to be recorded by the integration probe; run scripts/probe_data_chain.py first.")

