from django.contrib.gis.geos import Point
from django.db import transaction

from . import models


@transaction.atomic
def loaddata(category, iterable, row_number):

    datarows = []
    logs = []
    for idx, row in enumerate(iterable):
        line_no = row_number+idx+1
        row_list = list(row.values())
        error_lines = []
        if "longitude" not in row:
            error_lines.append([line_no, "longitude", "Missing Header Longitude"])

        if "latitude" not in row:
            error_lines.append([line_no, "latitude", "Missing Header Latitude"])

        if "name" not in row:
            error_lines.append([line_no, "name", "Missing Header Name"])

        location = row.pop("name").strip()
        longitude = row.pop("longitude")
        latitude = row.pop("latitude")

        if not location.strip():
            error_lines.append([line_no, "Name", "Empty value for Name"])

        try:
            longitude = float(longitude)
        except Exception as e:
            if not longitude:
                error_lines.append([line_no, "longitude", "Empty value for longitude"])
            elif isinstance(longitude, str) and not longitude.isdigit():
                error_lines.append([line_no, "longitude", "Invalid value passed for longitude %s" % longitude])
            else:
                error_lines.append([line_no, "longitude", e])

        try:
            latitude = float(latitude)
        except Exception as e:
            if not latitude:
                error_lines.append([line_no, "latitude", "Empty value for latitude"])
            elif isinstance(latitude, str) and not latitude.isdigit():
                error_lines.append([line_no, "latitude", "Invalid value passed for latitude %s" % latitude])
            else:
                error_lines.append([line_no, "latitude", e])

        try:
            coordinates = Point(longitude, latitude)
        except Exception as e:
            error_lines.append([line_no, "Coordinates", "Issue while creating coordinates %s " % e])

        if error_lines:
            logs.append([error_lines, row_list])
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
