import pandas as pd

from django.db import transaction

from . import models
from .dataloader import loaddata

@transaction.atomic
def process_uploaded_file(dataset_file):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.

    Get header index for geography & count and create Result objects.
    """
    filename = dataset_file.document.name

    if ".csv" in filename:
        df = pd.read_csv(dataset_file.document, sep=",")
    else:
        df = pd.read_excel(dataset_file.document, engine="xlrd")


    datasource = (dict(d[1]) for d in df.iterrows())
    loaddata(dataset_file.title, datasource)


    # print(header)
    # geography_header_index = header.index("geography")
    # count_header_index = header.index("count")

    # dataset = models.Dataset.objects.create(name=document.title)

    # data_rows = []
    # for line in data[1:]:
    #     extra_params = {}
    #     geo_code = line[geography_header_index]
    #     count = line[count_header_index]
    #     for index, value in enumerate(line):
    #         if index != geography_header_index:
    #             extra_params[header[index]] = value
    #     geography = geolookup[geo_code]


    #     data_rows.append(
    #         models.DatasetData(
    #             dataset=dataset, geography=geography, data=extra_params
    #         )
    #     )

    # models.DatasetData.objects.bulk_create(data_rows, 1000)
