import math

import numpy

from django.db import transaction

from . import models

cache = {}
def load_geography(geo_code):
    if geo_code not in cache:
        geography = models.Geography.objects.get(code=geo_code)
        cache[geo_code] = geography
    return cache[geo_code]

@transaction.atomic
def loaddata(name, iterable):
    dataset = models.Dataset.objects.create(name=name)
    datarows = []

    for idx, row in enumerate(iterable):
        geo_code = row["Geography"]
        try:
            geography = load_geography(geo_code)
        except models.Geography.DoesNotExist:
            print(f"Geography {geo_code} not found - skipping it.")
            continue

        count = row["Count"]
        if math.isnan(count):
            print(f"Missing data for {geo_code} - skipping it.")
            continue


        del row["Geography"]
        print(row)

        dd = models.DatasetData(dataset=dataset, geography=geography, data=row)
        datarows.append(dd)

        if len(datarows) >= 10000:
            models.DatasetData.objects.bulk_create(datarows, 1000)
            datarows = []
    models.DatasetData.objects.bulk_create(datarows, 1000)