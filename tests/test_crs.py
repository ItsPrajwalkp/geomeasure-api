import geopandas as gpd
import pytest
from shapely.geometry import Polygon

from app.services.crs_service import get_projected_gdf


def test_geographic_crs_is_projected():

    polygon = Polygon([
        (77.5900, 12.9700),
        (77.6000, 12.9700),
        (77.6000, 12.9800),
        (77.5900, 12.9800),
        (77.5900, 12.9700)
    ])

    gdf = gpd.GeoDataFrame(
        {"name": ["Test Polygon"]},
        geometry=[polygon],
        crs="EPSG:4326"
    )

    projected_gdf = get_projected_gdf(gdf)

    assert projected_gdf.crs is not None
    assert projected_gdf.crs.is_projected


def test_missing_crs_raises_error():

    polygon = Polygon([
        (77.5900, 12.9700),
        (77.6000, 12.9700),
        (77.6000, 12.9800),
        (77.5900, 12.9800),
        (77.5900, 12.9700)
    ])

    gdf = gpd.GeoDataFrame(
        {"name": ["Test Polygon"]},
        geometry=[polygon]
    )

    with pytest.raises(ValueError, match="does not contain a CRS"):
        get_projected_gdf(gdf)