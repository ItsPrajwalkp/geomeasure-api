import sqlite3
from pathlib import Path


DATABASE_PATH = Path("geomeasure.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            feature_count INTEGER,
            crs TEXT,
            status TEXT NOT NULL,
            error TEXT,
            features TEXT,
            measurements TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_file_record(record):
    connection = get_connection()

    connection.execute(
        """
        INSERT OR REPLACE INTO files (
            id,
            filename,
            feature_count,
            crs,
            status,
            error,
            features,
            measurements
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["id"],
            record["filename"],
            record.get("feature_count"),
            record.get("crs"),
            record["status"],
            record.get("error"),
            record.get("features"),
            record.get("measurements"),
        )
    )

    connection.commit()
    connection.close()


def get_file_record(file_id):
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM files WHERE id = ?",
        (file_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)