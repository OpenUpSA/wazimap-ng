import math

import numpy

from django.db import transaction

from . import models

# TODO should add a memoize decorator here
cache = {}
def load_geography(geo_code, version):
    geo_code = str(geo_code).upper()
    if geo_code not in cache:
        geography = models.Geography.objects.get(code=geo_code, version=version)
        cache[geo_code] = geography
    return cache[geo_code]

@transaction.atomic
def loaddata(dataset, iterable, row_number):  
    datarows = []
    errors = []
    warnings = []

    version = dataset.geography_hierarchy.version

    for idx, row in enumerate(iterable):
        geo_code = row["geography"]
        try:
            geography = load_geography(geo_code, version)
        except models.Geography.DoesNotExist:
            warnings.append(list(row.values()))
            continue

        try:
            count = float(row["count"])
            if math.isnan(count):
                errors.append([row_number+idx, "count", "Missing data for count"])
                continue
        except (TypeError, ValueError):
            errors.append([row_number+idx, "count", f"Expected a number in the 'count' column, received '{count}'"])
            continue

        del row["geography"]

        dd = models.DatasetData(dataset=dataset, geography=geography, data=row)
        datarows.append(dd)

        if len(datarows) >= 10000:
            models.DatasetData.objects.bulk_create(datarows, 1000)
            datarows = []
    models.DatasetData.objects.bulk_create(datarows, 1000)

    return [errors, warnings]
