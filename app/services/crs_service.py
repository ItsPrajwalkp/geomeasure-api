import geopandas as gpd


def get_projected_gdf(gdf):
    """
    Transform geographic coordinates into a suitable
    projected CRS for accurate distance and area calculations.
    """

    if gdf.crs is None:
        raise ValueError("Input file does not contain a CRS.")

    # Already projected
    if not gdf.crs.is_geographic:
        return gdf

    # Estimate a suitable local projected CRS
    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    return gdf.to_crs(projected_crs)