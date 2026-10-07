import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon

from app.services.measurement_service import calculate_measurements


def test_polygon_area():

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

    result = calculate_measurements(gdf)

    assert len(result) == 1
    assert result[0]["geometry_type"] == "Polygon"
    assert result[0]["unit"] == "square_meters"
    assert result[0]["measurement"] > 0


def test_linestring_length():

    line = LineString([
        (77.5900, 12.9700),
        (77.6000, 12.9800)
    ])

    gdf = gpd.GeoDataFrame(
        {"name": ["Test Line"]},
        geometry=[line],
        crs="EPSG:4326"
    )

    result = calculate_measurements(gdf)

    assert len(result) == 1
    assert result[0]["geometry_type"] == "LineString"
    assert result[0]["unit"] == "meters"
    assert result[0]["measurement"] > 0


def test_point_has_no_measurement():

    point = Point(77.5950, 12.9750)

    gdf = gpd.GeoDataFrame(
        {"name": ["Test Point"]},
        geometry=[point],
        crs="EPSG:4326"
    )

    result = calculate_measurements(gdf)

    assert len(result) == 1
    assert result[0]["geometry_type"] == "Point"
    assert result[0]["measurement"] is None
    assert result[0]["unit"] is None
    