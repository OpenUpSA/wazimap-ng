import codecs
import os

import pandas as pd
from django.conf import settings
from chardet.universaldetector import UniversalDetector


def get_log_filename(name, type, file_id):
    return F"{name}_{file_id}_{type}_log.csv"


def write_csv(log, logfile, headers):
    df = pd.DataFrame(log, columns=headers)
    df.to_csv(logfile, header=headers, index=False)
    return logfile


def csv_error_logger(logdir, target_name, target_id, logs, headers):
    errors = []
    incorrect_rows = []

    for idx, log in enumerate(logs):
        line_no = idx + 1
        for error in log["line_error"]:
            error["Error Line Number"] = line_no
            errors.append(error)
        incorrect_rows.append(log["values"])

    error_file_name = get_log_filename(target_name, "errors", target_id)
    error_headers = ['Error Line Number', 'CSV Line Number', 'Field Name', 'Error Details']
    error_file_log = write_csv(
        errors, F"{logdir}/{error_file_name}", error_headers
    )

    incorrect_file_name = get_log_filename(
        target_name, "incorrect_rows", target_id
    )
    incorrect_file_log = write_csv(
        incorrect_rows, F"{logdir}/{incorrect_file_name}", headers
    )
    return [error_file_log, incorrect_file_log]


def csv_logger(target_obj, file_obj, type, logs, headers):
    results=[]
    logdir=F"{settings.MEDIA_ROOT}/logs/{target_obj._meta.verbose_name}/{type}"
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    target_name=target_obj.name.replace(" ", "_")
    target_id=file_obj.id

    if type == "error":
        results=csv_error_logger(logdir, target_name, target_id, logs, headers)
    else:
        log_file_name = get_log_filename(target_name, type, target_id)
        file_log = write_csv(logs, F"{logdir}/{log_file_name}", headers)
        results.append(file_log)
    return results


def detect_encoding(buffer):
    detector = UniversalDetector()
    for line in buffer:
        detector.feed(line)
        if detector.done: break
    detector.close()
    return detector.result["encoding"]


def get_csv_header(buffer):
    encoding = detect_encoding(buffer)
    StreamReader = codecs.getreader(encoding)
    wrapper_file = StreamReader(buffer)
    wrapper_file.seek(0)
    df = pd.read_csv(wrapper_file, nrows=1, dtype=str, sep=",", encoding=encoding)
    return df.columns.str.lower().str.strip()
