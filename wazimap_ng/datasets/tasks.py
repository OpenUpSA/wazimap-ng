import json
import os
import time
import os
import pandas as pd

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import Count
from django.db.models.query import QuerySet
from django.conf import settings

from . import models
from .dataloader import loaddata
from itertools import groupby


@transaction.atomic
def process_uploaded_file(dataset_file, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.

    Get header index for geography & count and create Result objects.
    """
    def process_file_data(df, dataset, row_number):
        df = df.applymap(lambda s:s.capitalize().strip() if type(s) == str else s)
        datasource = (dict(d[1]) for d in df.iterrows())
        return loaddata(dataset, datasource, row_number)

    filename = dataset_file.document.name
    file_path = dataset_file.document.path
    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)

    columns = None
    dataset = dataset_file.dataset
    error_logs = []
    warning_logs = []
    row_number = 1

    if ".csv" in filename:
        df = pd.read_csv(file_path, nrows=1, dtype=str, sep=",")
        df.dropna(how='all', axis='columns', inplace=True)
        columns = df.columns.str.lower()

        for df in pd.read_csv(file_path, chunksize=chunksize, dtype=str, sep=",", header=None, skiprows=1):
            df.dropna(how='any', axis='columns', inplace=True)
            df.columns = columns
            errors, warnings = process_file_data(df, dataset, row_number)
            error_logs = error_logs + errors
            warning_logs = warning_logs + warnings
            row_number = row_number + chunksize
    else:
        skiprows = 1
        i_chunk = 0
        df = pd.read_excel(file_path, nrows=1, dtype=str)
        df.dropna(how='any', axis='columns', inplace=True)
        columns = df.columns.str.lower()
        while True:
            df = pd.read_excel(
                file_path, nrows=chunksize, skiprows=skiprows, header=None
            )
            skiprows += chunksize
            # When there is no data, we know we can break out of the loop.
            if not df.shape[0]:
                break
            else:
                df.dropna(how='any', axis='columns', inplace=True)
                df.columns = columns
                errors, warnings = process_file_data(df, dataset, row_number)
                error_logs = error_logs + errors
                warning_logs = warning_logs + warnings
                row_number = row_number + chunksize
            i_chunk += 1

    groups = [group for group in columns.to_list() if group not in ["geography", "count"]]
    dataset.groups = groups
    dataset.save()

    if error_logs:
        logdir = settings.MEDIA_ROOT + "/logs/dataset/errors/"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logfile = logdir + "%s_%d_error_log.csv" % (datasetfile.title.replace(" ", "_"), datasetfile.id)
        df = pd.DataFrame(error_logs[0])
        df.to_csv(logfile_1, header=["Line Number", "Field Name", "Error Details"], index=False)
        error_logs = logfile

    if warning_logs:
        logdir = settings.MEDIA_ROOT + "/logs/dataset/warnings/"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logfile = logdir + "%s_%d_warnings.csv" % (dataset.name.replace(" ", "_"), dataset.id)
        df = pd.DataFrame(warning_logs)
        df.to_csv(logfile, header=columns, index=False)
        warning_logs = logfile

    return {
        "model": "datasetfile",
        "name": dataset_file.dataset.name,
        "id": dataset_file.id,
        "error_log": error_logs or None,
        "warning_log": warning_logs or None
    }

@transaction.atomic
def indicator_data_extraction(indicator, **kwargs):
    """
    Data extraction for indicator data object.

    Create Indicator data object for indicator object and all geography.

    This task populates the Json field in indicator data object.

    Data json field should be populated with json of group name in groups of indicator
    and total count of that group according to geography.

    So for Gender group object should look like : {"Gender": "Male", "count": 123, ...}
    """
    # Delete already existing Indicator Data objects for specific indicator
    models.IndicatorData.objects.filter(indicator=indicator).delete()

    # Fetch filters for universe
    filters = {}
    if indicator.universe is not None:
        filters = indicator.universe.filters
        if filters and isinstance(filters, dict):
            filters = {f"data__{k}": v for k, v in filters.items()}

    # Format groups & Count
    groups = ["data__" + i for i in indicator.groups]
    c = Cast(KeyTextTransform("count", "data"), FloatField())

    filter_query = {
        "dataset": indicator.dataset,
        "data__has_keys": indicator.groups
    }

    if filters:
        filter_query.update(filters)

    qs = models.DatasetData.objects.filter(**filter_query).exclude(data__count="").order_by("geography_id")

    if len(groups) > 1:
        subindicators = ["/".join(val) for val in list(set(list(qs.values_list(*groups).distinct())))]
    elif len(groups) == 1:
        subindicators = [val[0] for val in list(set(list(qs.values_list(*groups).distinct())))]
    else:
        subindicators = []

    # Group data according to geography_id and get sum of data__count
    data = groupby(qs.values(*groups, "geography_id").annotate(count=Sum(c)), lambda x: x["geography_id"])

    datarows = []

    # Create indicator data
    for key, group in data:
        data_dump = json.dumps(list(group))
        grouped = json.loads(data_dump.replace("data__", ""))

        for item in grouped:
            item.pop("geography_id")

        datarows.append(models.IndicatorData(
            indicator=indicator, geography_id=key, data=grouped
        ))

    if len(datarows) > 0:
        models.IndicatorData.objects.bulk_create(datarows, 1000)

    indicator.subindicators = subindicators
    indicator.save()

    return {
        "model": "indicator",
        "name": indicator.name,
        "id": indicator.id,
    }

@transaction.atomic
def delete_data(data, object_name, **kwargs):
    """
    Delete data
    """
    data.delete()

    is_queryset = isinstance(data, QuerySet)

    return {
        "is_queryset": is_queryset,
        "data": data,
        "object_name": object_name,
    }
