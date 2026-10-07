import geopandas as gpd


def process_kml(file_path):
    """
    Read a KML file and return its geospatial features.
    """

    try:
        gdf = gpd.read_file(file_path, driver="KML")
    except Exception as exc:
        raise ValueError(f"Failed to read KML file: {exc}") from exc

    return gdf