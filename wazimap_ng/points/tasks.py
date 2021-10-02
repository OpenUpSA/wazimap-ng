import logging

from django.db import transaction
from django.conf import settings

from .dataloader import loaddata
import pandas as pd
from wazimap_ng.general.services.csv_helpers import csv_logger
from wazimap_ng.utils import get_stream_reader, clean_columns

logger = logging.getLogger(__name__)


@transaction.atomic
def process_uploaded_file(point_file, subtheme, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.
    """
    buffer = point_file.document.open("rb")
    encoding, wrapper_file = get_stream_reader(buffer)
    old_columns, new_columns = clean_columns(wrapper_file)

    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)
    row_number = 1
    error_logs = []

    for df in pd.read_csv(
        wrapper_file,
        chunksize=chunksize,
        skiprows=1,
        sep=",",
        header=None,
        keep_default_na=False,
        encoding=encoding,
        dtype=str
    ):
        df.columns = old_columns
        df = df.loc[:, new_columns]
        datasource = (dict(d[1]) for d in df.iterrows())
        logs = loaddata(subtheme, datasource, row_number)

        error_logs = error_logs + logs
        logger.info(logs)
        row_number = row_number + chunksize

    error_file_log = incorrect_file_log = None
    if error_logs:
        error_file_log, incorrect_file_log = csv_logger(
            subtheme, point_file, "error", error_logs, new_columns
        )

    return {
        "category_id": subtheme.id,
        "error_log": error_file_log,
        "incorrect_rows_log": incorrect_file_log,
    }
