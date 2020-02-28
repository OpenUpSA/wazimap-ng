from django.contrib.gis.geos import Point
from django.db import transaction

from . import models

@transaction.atomic
def loaddata(name, iterable):

    theme, created  = models.Theme.objects.get_or_create(
        name="unspecified theme"
    )
    category, created  = models.Category.objects.get_or_create(
        name="unspecified category", theme=theme
    )

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
        latitude = row.pop("latitude")
        longitude = row.pop("longitude")

        dd = models.Location(
            name=location, category=category,
            coordinates=Point(longitude, latitude) ,data=row
        )

        datarows.append(dd)

        if len(datarows) >= 10000:
            models.Location.objects.bulk_create(datarows, 1000)
            datarows = []

    models.Location.objects.bulk_create(datarows, 1000)