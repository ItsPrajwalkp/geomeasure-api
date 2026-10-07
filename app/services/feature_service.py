def extract_features(gdf):
    """
    Extract useful information from a GeoDataFrame.
    """

    features = []

    for index, row in gdf.iterrows():

        geometry = row.geometry

        feature = {
            "feature_id": index,
            "geometry_type": geometry.geom_type,
            "geometry": geometry.__geo_interface__,
            "properties": {}
        }

        # Extract non-geometry attributes
        for column in gdf.columns:
            if column != "geometry":
                value = row[column]

                # Convert NaN values to None
                if value != value:
                    value = None

                feature["properties"][column] = value

        features.append(feature)

    return features