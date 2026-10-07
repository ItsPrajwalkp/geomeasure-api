# GeoMeasure API

A production-oriented geospatial file measurement service built with **FastAPI**, **GeoPandas**, **Shapely**, **PyProj**, and **SQLite**.

GeoMeasure API accepts geospatial files, extracts their features and attributes, handles coordinate reference systems (CRS), and calculates measurements for supported geometries.

---

## 1. Features

- Upload `.kml` files.
- Upload `.zip` files containing a Shapefile.
- Extract feature information:
  - Feature ID
  - Geometry type
  - Geometry
  - CRS
  - Properties/attributes
- Calculate:
  - Polygon → Area in square meters
  - LineString → Length in meters
  - Point → No measurement required
- Automatically transform geographic CRS such as `EPSG:4326` into a suitable projected CRS before measurement.
- Validate Shapefile ZIP contents.
- Protect against ZIP path-traversal attacks.
- Reject ZIP files containing multiple Shapefiles.
- Store processed file information and results in SQLite.
- Automatically clean temporary extracted ZIP contents.
- Provide Swagger/OpenAPI documentation.
- Automated test suite with 13 passing tests.

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| GeoPandas | Geospatial data processing |
| Shapely | Geometry operations |
| PyProj | CRS transformation |
| Fiona / Pyogrio | Geospatial file I/O |
| Pydantic | API response validation |
| SQLite | Persistent metadata/result storage |
| Pytest | Automated testing |

---

## 3. Project Architecture

```text
geomeasure-api/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │       └── files.py
│   │
│   ├── core/
│   │   └── database.py
│   │
│   ├── schemas/
│   │   ├── file.py
│   │   └── measurement.py
│   │
│   ├── services/
│   │   ├── crs_service.py
│   │   ├── feature_service.py
│   │   ├── measurement_service.py
│   │   └── zip_service.py
│   │
│   └── processors/
│       ├── kml_processor.py
│       └── shapefile_processor.py
│
├── tests/
│   ├── test_health.py
│   ├── test_measurements.py
│   ├── test_upload.py
│   ├── test_crs.py
│   └── test_zip_service.py
│
├── sample_data/
│
├── uploads/
│
├── requirements.txt
├── .gitignore
└── README.md
```

### Architecture responsibilities

**Routes**

Handle HTTP requests and responses.

**Processors**

Read supported geospatial file formats and return GeoDataFrames.

**Services**

Contain business logic such as:

- ZIP validation
- Feature extraction
- CRS transformation
- Measurement calculation

**Schemas**

Define the structure of API responses using Pydantic.

**Database**

Stores processed file metadata, extracted features, and measurements.

---

## 4. Setup

### Prerequisites

- Python 3.12 or compatible Python version
- pip
- Git

### Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd geomeasure-api
```

### Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 5. Run the API

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 6. API Endpoints

### 6.1 Upload File

```http
POST /api/files/
```

Accepts:

- `.kml`
- `.zip` containing one Shapefile

Example response:

```json
{
  "id": "60c31c27-4a67-447f-9627-912c23c76f50",
  "filename": "sample_shapefile.zip",
  "status": "COMPLETED"
}
```

---

### 6.2 Get File Details

```http
GET /api/files/{file_id}
```

Example response:

```json
{
  "id": "60c31c27-4a67-447f-9627-912c23c76f50",
  "filename": "sample_shapefile.zip",
  "feature_count": 1,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

---

### 6.3 Get Measurements

```http
GET /api/files/{file_id}/measurements/
```

Example response:

```json
{
  "id": "60c31c27-4a67-447f-9627-912c23c76f50",
  "filename": "sample_shapefile.zip",
  "measurements": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "measurement": 1201683.9190970361,
      "unit": "square_meters"
    }
  ]
}
```

---

## 7. File Processing Flow

The upload workflow is:

```text
Client
  │
  ▼
POST /api/files/
  │
  ▼
Validate file extension
  │
  ├── KML ───────────────► KML Processor
  │
  └── ZIP
       │
       ▼
   Safe ZIP extraction
       │
       ▼
   Find Shapefile
       │
       ▼
   Validate Shapefile
       │
       ▼
   Shapefile Processor
       │
       ▼
   Feature Extraction
       │
       ▼
   CRS Handling
       │
       ▼
   Measurement Calculation
       │
       ▼
   Store results in SQLite
       │
       ▼
   Remove temporary extraction directory
       │
       ▼
   Return file ID and status
```

---

## 8. Feature Extraction

For every feature, the service extracts:

```text
Feature ID
Geometry Type
Geometry
Properties / Attributes
```

Example:

```json
{
  "feature_id": 0,
  "geometry_type": "Polygon",
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  },
  "properties": {
    "name": "Test Polygon"
  }
}
```

The geometry is represented using the GeoJSON-style geometry interface provided by Shapely.

---

## 9. Measurement Flow

The service supports measurements based on geometry type.

```text
Polygon
   ↓
Area
   ↓
square meters
```

```text
LineString
   ↓
Length
   ↓
meters
```

```text
Point
   ↓
No measurement required
```

Unsupported geometry types are handled gracefully and return:

```json
{
  "measurement": null,
  "unit": null
}
```

---

## 10. CRS Handling

Correct CRS handling is important for geospatial measurements.

Geographic CRS such as:

```text
EPSG:4326
```

uses latitude and longitude coordinates in degrees.

Area and distance should not be calculated directly from these degree-based coordinates.

### GeoMeasure approach

1. Check whether the input GeoDataFrame has a CRS.
2. If no CRS exists, return a validation error.
3. If the CRS is already projected, use it.
4. If the CRS is geographic, estimate a suitable local UTM projected CRS.
5. Transform the geometry into the projected CRS.
6. Calculate area or length.

The implementation uses:

```python
gdf.estimate_utm_crs()
```

followed by:

```python
gdf.to_crs(projected_crs)
```

This provides a more appropriate coordinate system for local distance and area calculations.

---

## 11. ZIP and Shapefile Validation

ZIP uploads are validated before processing.

The service checks for:

### No Shapefile

Rejected with:

```text
ZIP file does not contain a Shapefile (.shp).
```

### Multiple Shapefiles

Rejected because the current API expects one Shapefile per ZIP.

```text
ZIP file contains multiple Shapefiles.
```

### Incomplete Shapefile

The required `.shx` and `.dbf` companion files are checked.

Example:

```text
Incomplete Shapefile. Missing required file(s): file.shx, file.dbf
```

### Path Traversal Protection

ZIP member paths are resolved before extraction.

Potential paths such as:

```text
../../malicious.txt
```

are rejected to prevent files from being extracted outside the intended directory.

### Temporary File Cleanup

After successful or failed processing, the temporary ZIP extraction directory is removed.

---

## 12. Error Handling

The API returns appropriate HTTP errors for common invalid requests.

Examples:

### Unsupported file

```http
400 Bad Request
```

```json
{
  "detail": "Unsupported file format. Only .zip and .kml files are supported."
}
```

### File not found

```http
404 Not Found
```

```json
{
  "detail": "File not found."
}
```

### Invalid geospatial file

```http
400 Bad Request
```

with a descriptive processing error.

---

## 13. Database

SQLite is used to persist processed file information.

The database stores:

```text
File ID
Filename
Feature count
CRS
Processing status
Error information
Extracted features
Measurements
```

This allows file details and measurements to remain available after restarting the FastAPI server.

---

## 14. Testing

The project uses **Pytest**.

Run all tests:

```powershell
pytest
```

Current result:

```text
13 passed
```

The tests cover:

- Health endpoint
- Polygon area
- LineString length
- Point handling
- Geographic CRS transformation
- Missing CRS
- Invalid file type
- Non-existent file
- ZIP without Shapefile
- Corrupt ZIP
- ZIP path traversal
- Multiple Shapefiles
- Incomplete Shapefile

---

## 15. Design Decisions

### FastAPI

FastAPI was selected because it provides:

- Simple REST API development
- Automatic OpenAPI documentation
- Request/response validation
- Good support for asynchronous file uploads

### GeoPandas

GeoPandas provides a convenient abstraction for reading and processing geospatial vector data.

### Shapely

Shapely is used for geometry-level operations such as:

- Geometry type detection
- Area calculation
- Length calculation
- GeoJSON-style geometry representation

### SQLite

SQLite was selected for this implementation because the assignment requires persistence but does not require a separate database server.

It keeps the project simple to run locally while still providing persistent storage.

### One Shapefile per ZIP

The current implementation intentionally rejects ZIP files containing multiple Shapefiles. This keeps the processing contract clear and avoids ambiguity about which dataset should be measured.

---

## 16. Future Improvements

Possible improvements for a larger production deployment include:

- PostgreSQL/PostGIS for scalable geospatial persistence
- Background processing for large files
- File-size and ZIP-bomb protection
- Authentication and authorization
- Rate limiting
- Cloud object storage
- Structured application logging
- More detailed processing status tracking
- Support for additional geospatial formats
- More comprehensive geometry support
- Improved CRS selection for large geographic extents
- Containerized deployment
- CI/CD pipeline
- API versioning

---

## 17. Example Workflow

A typical client workflow is:

```text
1. Upload a KML or Shapefile ZIP
           ↓
2. Receive a unique file ID
           ↓
3. Request file details
           ↓
4. Request measurements
           ↓
5. Use the returned area/length values
```

Example:

```text
POST /api/files/
        ↓
file_id
        ↓
GET /api/files/{file_id}
        ↓
GET /api/files/{file_id}/measurements/
```

---

## 18. Project Status

The current implementation provides the required geospatial file upload, feature extraction, CRS handling, measurement calculation, persistence, validation, and REST APIs.

Automated test status:

```text
13 passed
```

The project is designed as a modular FastAPI service so that additional processors, measurement types, storage backends, and deployment options can be added later.