from pydantic import BaseModel, Field

class RoofAnalysisRequest(BaseModel):
    lat: float = Field(ge=-47.5, le=-34.0)
    lon: float = Field(ge=166.0, le=179.0)

