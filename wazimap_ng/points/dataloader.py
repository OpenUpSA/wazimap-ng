from django.contrib.gis.geos import Point
from django.db import transaction

from . import models


@transaction.atomic
def loaddata(category, iterable, row_number):

    datarows = []
    logs = []
    for idx, row in enumerate(iterable):

        if "longitude" not in row:
            logs.append([row_number+idx+1, "longitude", "Missing Header Longitude"])

        if "latitude" not in row:
            logs.append([row_number+idx+1, "latitude", "Missing Header Latitude"])
            continue

        if "name" not in row:
            logs.append([row_number+idx+1, "name", "Missing Header Name"])
            continue

        location = row.pop("name").strip()
        longitude = row.pop("longitude")
        latitude = row.pop("latitude")

        if not location.strip():
            logs.append([row_number+idx+1, "Name", "Empty value for Name"])
            continue

        try:
            longitude = float(longitude)
        except Exception as e:
            if not longitude:
                logs.append([row_number+idx+1, "longitude", "Empty value for longitude"])
            elif isinstance(longitude, str) and not longitude.isdigit():
                logs.append([row_number+idx+1, "longitude", "Invalid value passed for longitude %s" % longitude])
            else:
                logs.append([row_number+idx+1, "longitude", e])
            continue

        try:
            latitude = float(latitude)
        except Exception as e:
            if not latitude:
                logs.append([row_number+idx+1, "latitude", "Empty value for latitude"])
            elif isinstance(latitude, str) and not latitude.isdigit():
                logs.append([row_number+idx+1, "latitude", "Invalid value passed for latitude %s" % latitude])
            else:
                logs.append([row_number+idx+1, "latitude", e])
            continue

        try:
            coordinates = Point(longitude, latitude)
        except Exception as e:
            logs.append([row_number+idx+1, "Coordinates", "Issue while creating coordinates %s " % e])
            continue

        dd = models.Location(
            name=location, category=category,
            coordinates=coordinates, data=row
        )

        datarows.append(dd)

        if len(datarows) >= 10000:
            models.Location.objects.bulk_create(datarows, 1000)
            datarows = []


    models.Location.objects.bulk_create(datarows, 1000)
    return logs
