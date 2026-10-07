from pathlib import Path
from zipfile import ZipFile

import pytest

from app.services.zip_service import (
    extract_zip_safely,
    find_shapefile,
)


def test_zip_without_shapefile(tmp_path):

    zip_path = tmp_path / "invalid.zip"
    extract_dir = tmp_path / "extracted"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "dummy.txt",
            "This ZIP does not contain a shapefile."
        )

    extract_zip_safely(zip_path, extract_dir)

    with pytest.raises(
        ValueError,
        match="does not contain a Shapefile"
    ):
        find_shapefile(extract_dir)


def test_corrupt_zip(tmp_path):

    zip_path = tmp_path / "corrupt.zip"

    zip_path.write_bytes(
        b"This is not a real ZIP file."
    )

    with pytest.raises(Exception):
        extract_zip_safely(
            zip_path,
            tmp_path / "extracted"
        )


def test_zip_path_traversal_is_blocked(tmp_path):

    zip_path = tmp_path / "malicious.zip"
    extract_dir = tmp_path / "extracted"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "../../malicious.txt",
            "malicious content"
        )

    with pytest.raises(
        ValueError,
        match="path traversal detected"
    ):
        extract_zip_safely(zip_path, extract_dir)
        
def test_multiple_shapefiles_are_rejected(tmp_path):

    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()

    # Create two dummy Shapefile files
    (extract_dir / "first.shp").write_bytes(b"dummy")
    (extract_dir / "second.shp").write_bytes(b"dummy")

    with pytest.raises(
        ValueError,
        match="multiple Shapefiles"
    ):
        find_shapefile(extract_dir)

def test_incomplete_shapefile_is_rejected(tmp_path):

    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()

    # Only .shp exists; required .shx and .dbf are missing.
    (extract_dir / "incomplete.shp").write_bytes(b"dummy")

    with pytest.raises(
        ValueError,
        match="Incomplete Shapefile"
    ):
        find_shapefile(extract_dir)