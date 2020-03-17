from django.contrib.gis.geos import Point
from django.db import transaction

from . import models
from ..boundaries.models import GeographyBoundary


def get_levels(coordinates):
    levels = {}
    geographies = GeographyBoundary.objects.filter(
        geom__contains=coordinates
    ).values("geography__level", "geography__id", "geography__name", "geography__code")

    for geo in geographies:
        levels[geo["geography__level"]] = {
            "id": geo["geography__id"],
            "name": geo["geography__name"],
            "code": geo["geography__code"]
        }
    return levels

@transaction.atomic
def loaddata(name, category, iterable):

    datarows = []
    for idx, row in enumerate(iterable):

        if "longitude" not in row:
            print(f"Missing Longitude - skipping it.")
            continue

        if "latitude" not in row:
            print(f"Missing Latitude - skipping it.")
            continue

        if "name" not in row:
            print(f"Missing Name - skipping it.")
            continue

        location = row.pop("name")
        coordinates = Point(row.pop("longitude"), row.pop("latitude"))

        row["levels"] = get_levels(coordinates)
        dd = models.Location(
            name=location, category=category,
            coordinates=coordinates, data=row
        )

        datarows.append(dd)

        if len(datarows) >= 10000:
            models.Location.objects.bulk_create(datarows, 1000)
            datarows = []

    models.Location.objects.bulk_create(datarows, 1000)