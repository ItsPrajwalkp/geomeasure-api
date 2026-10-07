from fastapi import FastAPI

from app.api.routes.files import router as files_router
from app.core.database import initialize_database


initialize_database()


app = FastAPI(
    title="GeoMeasure API",
    description="Geospatial File Measurement Service",
    version="1.0.0",
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GeoMeasure API"
    }


app.include_router(files_router)