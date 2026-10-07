from pydantic import BaseModel
from typing import Optional


class Measurement(BaseModel):
    feature_id: int
    geometry_type: str
    measurement: Optional[float] = None
    unit: Optional[str] = None


class MeasurementsResponse(BaseModel):
    id: str
    filename: str
    measurements: list[Measurement]