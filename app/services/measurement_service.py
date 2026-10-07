from app.services.crs_service import get_projected_gdf


def calculate_measurements(gdf):
    """
    Calculate measurements for supported geometry types.

    Polygon    -> area
    LineString -> length
    Point      -> no measurement
    """

    projected_gdf = get_projected_gdf(gdf)

    measurements = []

    for index, row in projected_gdf.iterrows():

        geometry = row.geometry
        geometry_type = geometry.geom_type

        measurement = {
            "feature_id": index,
            "geometry_type": geometry_type,
            "measurement": None,
            "unit": None
        }

        if geometry_type == "Polygon":
            measurement["measurement"] = geometry.area
            measurement["unit"] = "square_meters"

        elif geometry_type == "LineString":
            measurement["measurement"] = geometry.length
            measurement["unit"] = "meters"

        elif geometry_type == "Point":
            # No measurement required
            pass

        else:
            measurement["measurement"] = None
            measurement["unit"] = None

        measurements.append(measurement)

    return measurements