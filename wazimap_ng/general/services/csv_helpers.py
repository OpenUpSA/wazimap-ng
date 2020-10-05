import os

import pandas as pd
from django.conf import settings


def get_log_filename(name, type, file_id):
    return F"{name}_{file_id}_{type}_log.csv"


def write_csv(logs, logfile, headers):
    df = pd.DataFrame(logs)
    df.to_csv(logfile, header=headers, index=False)
    return logfile


def csv_error_logger(logdir, target_name, target_id, logs, headers):
    errors = []
    incorrect_rows = []

    for idx, log in enumerate(logs):
        errors = errors + [[idx+1] + error for error in log[0]]
        incorrect_rows.append(log[1])

    error_file_name = get_log_filename(target_name, "errors", target_id)
    error_file_log = write_csv(
        errors, F"{logdir}/{error_file_name}", [
            "Error file line no.", "Actual csv line no.", "Field Name",
            "Error Details"
        ]
    )
    incorrect_file_name = get_log_filename(
        target_name, "incorrect_rows", target_id
    )
    incorrect_file_log = write_csv(
        incorrect_rows, F"{logdir}/{incorrect_file_name}", headers
    )

    return error_file_log, incorrect_file_log


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
