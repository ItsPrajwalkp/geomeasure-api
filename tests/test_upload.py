from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_invalid_file_type():

    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test.txt",
                b"this is not a supported file",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Unsupported file format. "
        "Only .zip and .kml files are supported."
    )


def test_get_nonexistent_file():

    response = client.get(
        "/api/files/non-existent-file-id"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "File not found."