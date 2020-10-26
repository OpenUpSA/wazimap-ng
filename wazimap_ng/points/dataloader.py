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
            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "longitude",
                "Error Details": "Missing Header Longitude"
            })

        if "latitude" not in row:
            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "latitude",
                "Error Details": "Missing Header Latitude"
            })

        if "name" not in row:
            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "name",
                "Error Details": "Missing Header Name"
            })

        location = row.pop("name").strip()
        longitude = row.pop("longitude")
        latitude = row.pop("latitude")

        if not location.strip():
            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "Name",
                "Error Details": "Empty value for Name"
            })


        try:
            longitude = float(longitude)
        except Exception as e:
            if not longitude:
                msg = "Empty value for longitude"
            elif isinstance(longitude, str) and not longitude.isdigit():
                msg = F"Invalid value passed for longitude {longitude}"
            else:
                msg = e

            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "longitude",
                "Error Details": msg
            })

        try:
            latitude = float(latitude)
        except Exception as e:
            if not latitude:
                msg = "Empty value for latitude"
            elif isinstance(latitude, str) and not latitude.isdigit():
                msg = F"Invalid value passed for latitude {latitude}"
            else:
                msg = e

            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "latitude",
                "Error Details": msg
            })

        try:
            coordinates = Point(longitude, latitude)
        except Exception as e:
            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "Coordinates",
                "Error Details": F"Issue while creating coordinates {e}"
            })

        if error_lines:
            logs.append({
                "line_error": error_lines,
                "values": row_list
            })
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
