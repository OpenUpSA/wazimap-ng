from django.contrib.gis.geos import Point
from django.db import transaction

from . import models


@transaction.atomic
def loaddata(category, iterable, row_number):

    datarows = []
    logs = []
    for idx, row in enumerate(iterable):
        line_no = row_number+idx+1
        if "longitude" not in row:
            logs.append([line_no, "longitude", "Missing Header Longitude"])

        if "latitude" not in row:
            logs.append([line_no, "latitude", "Missing Header Latitude"])
            continue

        if "name" not in row:
            logs.append([line_no, "name", "Missing Header Name"])
            continue

        location = row.pop("name").strip()
        longitude = row.pop("longitude")
        latitude = row.pop("latitude")

        if not location.strip():
            logs.append([line_no, "Name", "Empty value for Name"])
            continue

        try:
            longitude = float(longitude)
        except Exception as e:
            if not longitude:
                logs.append([line_no, "longitude", "Empty value for longitude"])
            elif isinstance(longitude, str) and not longitude.isdigit():
                logs.append([line_no, "longitude", "Invalid value passed for longitude %s" % longitude])
            else:
                logs.append([line_no, "longitude", e])
            continue

        try:
            latitude = float(latitude)
        except Exception as e:
            if not latitude:
                logs.append([line_no, "latitude", "Empty value for latitude"])
            elif isinstance(latitude, str) and not latitude.isdigit():
                logs.append([line_no, "latitude", "Invalid value passed for latitude %s" % latitude])
            else:
                logs.append([line_no, "latitude", e])
            continue

        try:
            coordinates = Point(longitude, latitude)
        except Exception as e:
            logs.append([line_no, "Coordinates", "Issue while creating coordinates %s " % e])
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
