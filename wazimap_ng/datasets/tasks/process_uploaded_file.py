import os
import pandas as pd
import logging

from django.db import transaction
from django.conf import settings

from ..dataloader import loaddata
from .. import models

from wazimap_ng.general.services.permissions import assign_perms_to_group

logger = logging.getLogger(__name__)


@transaction.atomic
def process_uploaded_file(dataset_file, dataset, **kwargs):
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
    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)

    columns = None
    error_logs = []
    warning_logs = []
    row_number = 1

    if ".csv" in filename:
        df = pd.read_csv(dataset_file.document.open(), nrows=1, dtype=str, sep=",")
        df.dropna(how='all', axis='columns', inplace=True)
        columns = df.columns.str.lower()

        for df in pd.read_csv(dataset_file.document.open(), chunksize=chunksize, dtype=str, sep=",", header=None, skiprows=1):
            df.dropna(how='all', axis='columns', inplace=True)
            df.columns = columns
            errors, warnings = process_file_data(df, dataset, row_number)
            error_logs = error_logs + errors
            warning_logs = warning_logs + warnings
            row_number = row_number + chunksize
    else:
        skiprows = 1
        i_chunk = 0
        df = pd.read_excel(dataset_file.document.open(), nrows=1, dtype=str)
        df.dropna(how='any', axis='columns', inplace=True)
        columns = df.columns.str.lower()
        while True:
            df = pd.read_excel(
                dataset_file.document.open(), nrows=chunksize, skiprows=skiprows, header=None
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

    dataset.groups =  list(set(groups + dataset.groups))
    dataset.save()

    if error_logs:
        logdir = settings.MEDIA_ROOT + "/logs/dataset/errors/"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logfile = logdir + "%s_%d_error_log.csv" % (dataset.name.replace(" ", "_"), dataset_file.id)
        df = pd.DataFrame(error_logs)
        df.to_csv(logfile, header=["Line Number", "Field Name", "Error Details"], index=False)
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
        "name": dataset.name,
        "id": dataset_file.id,
        "dataset_id": dataset.id,
        "error_log": error_logs or None,
        "warning_log": warning_logs or None
    }