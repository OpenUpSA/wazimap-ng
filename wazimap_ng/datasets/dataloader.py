import functools
import logging
import math
from typing import Dict, List, Tuple

import numpy
from django.db import transaction

from wazimap_ng.datasets.models import Dataset, Geography
from wazimap_ng.datasets.models.group import Group

from . import models

logger = logging.getLogger(__name__)

# TODO should add a memoize decorator here


@functools.lru_cache()
def load_geography(geo_code: str, version: str) -> Geography:
    geo_code = str(geo_code).upper()
    geography = models.Geography.objects.get(code=geo_code, version=version)
    return geography


def create_groups(dataset: Dataset, group_names: List[str]) -> List[Group]:
    groups = []
    for g in group_names:
        subindicators = list(models.DatasetData.objects.get_unique_subindicators(g))

        group, created = models.Group.objects.get_or_create(
            name=g, dataset=dataset
        )
        group.subindicators = subindicators
        group.save()
        groups.append(group)
    return groups


@transaction.atomic
def loaddata(dataset: Dataset, iterable, row_number: int) -> List[List]:
    datarows = []
    errors = []
    warnings = []
    groups = set()

    version = dataset.geography_hierarchy.version

    for idx, row in enumerate(iterable):
        groups |= set(x for x in row.keys())
        geo_code = row["geography"]
        line_no = row_number+idx+1
        error_lines = []
        try:
            geography = load_geography(geo_code, version)
        except models.Geography.DoesNotExist:
            warnings.append(list(row.values()))
            continue

        try:
            count = float(row["count"])
            if math.isnan(count):
                error_lines.append({
                    "CSV Line Number": line_no,
                    "Field Name": "count",
                    "Error Details": "Missing data for count"
                })

        except (TypeError, ValueError):
            error_lines.append({
                "CSV Line Number": line_no,
                "Field Name": "count",
                "Error Details": f"Expected a number in the 'count' column, received {row['count']}"
            })

        if error_lines:
            errors.append({
                "line_error": error_lines,
                "values": list(row.values())
            })
            continue

        del row["geography"]

        dd = models.DatasetData(dataset=dataset, geography=geography, data=row)
        datarows.append(dd)

        if len(datarows) >= 10000:
            models.DatasetData.objects.bulk_create(datarows, 1000)
            datarows = []
    models.DatasetData.objects.bulk_create(datarows, 1000)

    group_list = sorted(g for g in groups if g.lower() not in ("count", "geography"))

    create_groups(dataset, group_list)

    return [errors, warnings]
