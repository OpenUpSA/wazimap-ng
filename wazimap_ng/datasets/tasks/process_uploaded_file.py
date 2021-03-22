import logging
from typing import BinaryIO, Dict, List

import pandas as pd
from django.conf import settings
from django.db import transaction
from pandas import DataFrame

from wazimap_ng.datasets.models.dataset import Dataset
from wazimap_ng.general.services.csv_helpers import csv_logger
from wazimap_ng.utils import clean_columns, get_stream_reader

from ..dataloader import loaddata

logger = logging.getLogger(__name__)


def process_file_data(df: DataFrame, dataset: Dataset, row_number: int) -> List[Dict]:
    df = df.applymap(lambda s: s.strip() if type(s) == str else s)
    datasource = (dict(d[1]) for d in df.iterrows())
    return loaddata(dataset, datasource, row_number)


def process_csv(dataset: Dataset, buffer: BinaryIO, chunksize: int = 1000000):
    encoding, wrapper_file = get_stream_reader(buffer)
    _, columns = clean_columns(wrapper_file)
    row_number = 1
    error_logs = []
    warning_logs = []

    wrapper_file.seek(0)
    for df in pd.read_csv(wrapper_file, chunksize=chunksize, dtype=str, sep=",", header=None, skiprows=1, encoding=encoding):
        df.dropna(how='all', axis='columns', inplace=True)
        df.columns = columns
        errors, warnings = process_file_data(df, dataset, row_number)
        error_logs = error_logs + errors
        warning_logs = warning_logs + warnings
        row_number = row_number + chunksize

    return {
        "error_logs": error_logs,
        "warning_logs": warning_logs,
        "columns": columns
    }


@transaction.atomic
def process_uploaded_file(dataset_file, dataset, **kwargs):
    logger.debug(f"process_uploaded_file: {dataset_file}")
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.

    Get header index for geography & count and create Result objects.
    """

    filename = dataset_file.document.name
    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)
    logger.debug(f"Processing: {filename}")

    columns = None
    error_logs = []
    warning_logs = []
    row_number = 1

    if ".csv" in filename:
        logger.debug(f"Processing as csv")
        csv_output = process_csv(dataset, dataset_file.document.open("rb"), chunksize)
        error_logs = csv_output["error_logs"]
        warning_logs = csv_output["warning_logs"]
        columns = csv_output["columns"]
    else:
        logger.debug("Process as other filetype")
        skiprows = 1
        i_chunk = 0
        df = pd.read_excel(dataset_file.document.open(), nrows=1, dtype=str)
        df.dropna(how='any', axis='columns', inplace=True)
        columns = df.columns.str.lower().str.strip()
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

    dataset.groups = list(set(groups + dataset.groups))
    dataset.save()

    error_file_log = incorrect_file_log = None
    if error_logs:
        error_file_log, incorrect_file_log = csv_logger(
            dataset, dataset_file, "error", error_logs, columns
        )

    if warning_logs:
        warning_logs, = csv_logger(
            dataset, dataset_file, "warning", warning_logs, columns
        )

    return {
        "model": "datasetfile",
        "name": dataset.name,
        "id": dataset_file.id,
        "dataset_id": dataset.id,
        "error_log": error_file_log,
        "incorrect_rows_log": incorrect_file_log,
        "warning_log": warning_logs or None
    }
