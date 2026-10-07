from pathlib import Path
from zipfile import ZipFile


def extract_zip_safely(zip_path, extract_dir):
    """
    Safely extract a ZIP file.
    """

    extract_dir = Path(extract_dir).resolve()
    extract_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, "r") as zip_ref:

        for member in zip_ref.infolist():

            target_path = (extract_dir / member.filename).resolve()

            if not str(target_path).startswith(str(extract_dir)):
                raise ValueError(
                    "Unsafe ZIP file: path traversal detected."
                )

        zip_ref.extractall(extract_dir)

    return extract_dir


def find_shapefile(extract_dir):
    """
    Find and validate the Shapefile inside an extracted directory.
    """

    extract_dir = Path(extract_dir)

    shp_files = list(extract_dir.rglob("*.shp"))

    if not shp_files:
        raise ValueError(
            "ZIP file does not contain a Shapefile (.shp)."
        )

    if len(shp_files) > 1:
        raise ValueError(
            "ZIP file contains multiple Shapefiles. "
            "Please provide one Shapefile per ZIP."
        )

    shp_file = shp_files[0]

    # A Shapefile normally requires these companion files.
    required_files = [
        shp_file.with_suffix(".shx"),
        shp_file.with_suffix(".dbf"),
    ]

    missing_files = [
        file.name
        for file in required_files
        if not file.exists()
    ]

    if missing_files:
        raise ValueError(
            "Incomplete Shapefile. Missing required file(s): "
            + ", ".join(missing_files)
        )

    return shp_file