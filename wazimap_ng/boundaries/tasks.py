from ..points.models import Location

def update_location_geo_levels_data(boundary):
    """
    Run this Task to update geo levels data of locations
    """
    geo_level = boundary.geography.level
    data = {
        "id" : boundary.id,
        "name" : boundary.geography.name,
        "code" : boundary.geography.code,
    }
    for location in Location.objects.filter(coordinates__within=boundary.geom):
        if "levels" in location.data:
            location.data["levels"][geo_level] = data
        else:
            location.data["levels"] = {geo_level : data}
        location.save()