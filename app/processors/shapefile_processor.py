from pathlib import Path

import geopandas as gpd


def process_shapefile(shapefile_path):
    """
    Read a Shapefile and return its GeoDataFrame.
    """

    try:
        gdf = gpd.read_file(shapefile_path)
    except Exception as exc:
        raise ValueError(
            f"Failed to read Shapefile: {exc}"
        ) from exc

    return gdf