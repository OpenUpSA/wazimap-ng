import codecs
import os
import logging

from django.db import transaction
from django.conf import settings
from chardet.universaldetector import UniversalDetector
import pandas as pd

from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.services.csv_helpers import csv_logger

from ..dataloader import loaddata
from .. import models

logger = logging.getLogger(__name__)


def detect_encoding(buffer):
    detector = UniversalDetector()
    for line in buffer:
        detector.feed(line)
        if detector.done: break
    detector.close()
    return detector.result["encoding"]


def process_headers(df):
    old_columns = df.columns.str.lower().str.strip()
    df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    new_columns = df.columns.str.lower().str.strip()
    return old_columns, new_columns


def process_df(df, old_columns, new_columns):
    df.dropna(how='all', axis='index', inplace=True)
    df.columns = old_columns
    df = df.loc[:, new_columns]
    df.fillna('', inplace=True)
    return df


def process_file_data(df, dataset, row_number):
    df = df.applymap(lambda s: s.strip().capitalize() if type(s) == str else s)
    datasource = (dict(d[1]) for d in df.iterrows())
    return loaddata(dataset, datasource, row_number)


def process_csv(dataset, buffer, chunksize=1000000):
    encoding = detect_encoding(buffer)
    StreamReader = codecs.getreader(encoding)
    wrapper_file = StreamReader(buffer)
    wrapper_file.seek(0)
    row_number = 1
    df = pd.read_csv(wrapper_file, nrows=1, dtype=str, sep=",", encoding=encoding)
    old_columns, new_columns = process_headers(df)
    error_logs = []
    warning_logs = []

    wrapper_file.seek(0)
    for df in pd.read_csv(wrapper_file, chunksize=chunksize, dtype=str, sep=",", header=None, skiprows=1, encoding=encoding):
        df = process_df(df, old_columns, new_columns)
        errors, warnings = process_file_data(df, dataset, row_number)
        error_logs = error_logs + errors
        warning_logs = warning_logs + warnings
        row_number = row_number + chunksize

    return {
        "error_logs": error_logs,
        "warning_logs": warning_logs,
        "columns": new_columns
    }


def process_xls(dataset, document, chunksize=1000000):
    skiprows = 1
    i_chunk = 0
    error_logs = []
    warning_logs = []
    row_number = 1

    df = pd.read_excel(document.open(), nrows=1, dtype=str)
    old_columns, new_columns = process_headers(df)
    while True:

        df = pd.read_excel(
            document.open(), nrows=chunksize, skiprows=skiprows,
            header=None, dtype=str
        )
        skiprows += chunksize
        # When there is no data, we know we can break out of the loop.
        if not df.shape[0]:
            break
        else:
            df = process_df(df, old_columns, new_columns)
            errors, warnings = process_file_data(df, dataset, row_number)
            error_logs = error_logs + errors
            warning_logs = warning_logs + warnings
            row_number = row_number + chunksize
        i_chunk += 1

    return {
        "error_logs": error_logs,
        "warning_logs": warning_logs,
        "columns": new_columns
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

    if ".csv" in filename:
        logger.debug(f"Processing as csv")
        csv_output = process_csv(dataset, dataset_file.document.open("rb"), chunksize)
        error_logs = csv_output["error_logs"]
        warning_logs = csv_output["warning_logs"]
        columns = csv_output["columns"]
    else:
        logger.debug("Process as other filetype")
        xls_output = process_xls(dataset, dataset_file.document, chunksize)
        error_logs = xls_output["error_logs"]
        warning_logs = xls_output["warning_logs"]
        columns = xls_output["columns"]

    if len(dataset.groups) == 0:
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
