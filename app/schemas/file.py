from pydantic import BaseModel
from typing import Optional


class FileUploadResponse(BaseModel):
    id: str
    filename: str
    status: str


class FileDetailsResponse(BaseModel):
    id: str
    filename: str
    feature_count: Optional[int] = None
    crs: Optional[str] = None
    status: str