import json
from pathlib import Path
import shutil
from uuid import uuid4

from app.schemas.file import (
    FileUploadResponse,
    FileDetailsResponse,
)

from app.schemas.measurement import MeasurementsResponse
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.database import save_file_record, get_file_record
from app.processors.kml_processor import process_kml
from app.processors.shapefile_processor import process_shapefile
from app.services.feature_service import extract_features
from app.services.measurement_service import calculate_measurements
from app.services.zip_service import extract_zip_safely, find_shapefile


router = APIRouter(prefix="/api/files", tags=["Files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".zip", ".kml"}


@router.post(
    "/",
    response_model=FileUploadResponse
)
async def upload_file(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only .zip and .kml files are supported."
        )

    file_id = str(uuid4())

    safe_filename = Path(file.filename).name
    saved_filename = f"{file_id}_{safe_filename}"
    file_path = UPLOAD_DIR / saved_filename

    # Save uploaded file
    try:
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file."
        ) from exc

    # --------------------------------------------------
    # KML PROCESSING
    # --------------------------------------------------

    if extension == ".kml":

        try:
            gdf = process_kml(file_path)

            features = extract_features(gdf)

            measurements = calculate_measurements(gdf)

        except Exception as exc:

            save_file_record({
                "id": file_id,
                "filename": safe_filename,
                "status": "FAILED",
                "error": str(exc),
                "features": None,
                "measurements": None
            })

            raise HTTPException(
                status_code=400,
                detail=f"Failed to process geospatial file: {exc}"
            ) from exc

            save_file_record({
            "id": file_id,
            "filename": safe_filename,
            "feature_count": len(gdf),
            "crs": str(gdf.crs),
            "status": "COMPLETED",
            "features": json.dumps(features, default=str),
            "measurements": json.dumps(measurements, default=str)
        })

        # Remove temporary extracted files
        shutil.rmtree(extract_dir, ignore_errors=True)

        return {
            "id": file_id,
            "filename": safe_filename,
            "status": "COMPLETED"
        }

    # --------------------------------------------------
    # ZIP / SHAPEFILE PROCESSING
    # --------------------------------------------------

    if extension == ".zip":

        extract_dir = UPLOAD_DIR / file_id

        try:
            # Extract ZIP safely
            extract_zip_safely(file_path, extract_dir)

            # Find Shapefile
            shapefile_path = find_shapefile(extract_dir)

            # Read Shapefile
            gdf = process_shapefile(shapefile_path)

            # Extract features
            features = extract_features(gdf)

            # Calculate measurements
            measurements = calculate_measurements(gdf)

        except Exception as exc:

            shutil.rmtree(extract_dir, ignore_errors=True)

            save_file_record({
                "id": file_id,
                "filename": safe_filename,
                "status": "FAILED",
                "error": str(exc),
                "features": None,
                "measurements": None
            })

            raise HTTPException(
                status_code=400,
                detail=f"Failed to process ZIP file: {exc}"
            ) from exc

        save_file_record({
            "id": file_id,
            "filename": safe_filename,
            "feature_count": len(gdf),
            "crs": str(gdf.crs),
            "status": "COMPLETED",
            "features": json.dumps(features, default=str),
            "measurements": json.dumps(measurements, default=str)
        })

        return {
            "id": file_id,
            "filename": safe_filename,
            "status": "COMPLETED"
        }


# --------------------------------------------------
# GET FILE DETAILS
# --------------------------------------------------

@router.get(
    "/{file_id}",
    response_model=FileDetailsResponse
)
def get_file(file_id: str):

    record = get_file_record(file_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return {
        "id": record["id"],
        "filename": record["filename"],
        "feature_count": record.get("feature_count"),
        "crs": record.get("crs"),
        "status": record["status"]
    }


# --------------------------------------------------
# GET MEASUREMENTS
# --------------------------------------------------

@router.get(
    "/{file_id}/measurements/",
    response_model=MeasurementsResponse
)
def get_measurements(file_id: str):

    record = get_file_record(file_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    if record["status"] != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Measurements are not available for this file."
        )

    measurements = json.loads(
        record["measurements"]
    )

    return {
        "id": record["id"],
        "filename": record["filename"],
        "measurements": measurements
    }