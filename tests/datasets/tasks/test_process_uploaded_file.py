import codecs
import csv
from io import BytesIO

import pytest

from tests.datasets.factories import (
    DatasetFactory,
    DatasetFileFactory,
    GeographyFactory,
    GeographyHierarchyFactory
)
from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv


def generate_file(data, header, encoding="utf8"):
    buffer = BytesIO()
    StreamWriter = codecs.getwriter(encoding)
    text_buffer = StreamWriter(buffer)

    writer = csv.writer(text_buffer)
    writer.writerow(header)
    writer.writerows(data)

    buffer.seek(0)
    return buffer


def create_datasetfile(csv_data, encoding, header):
    buffer = generate_file(csv_data, header, encoding)
    return DatasetFileFactory(document__data=buffer.read())


@pytest.fixture
def geography_hierarchy():
    hierarchy = GeographyHierarchyFactory()

    return hierarchy

@pytest.fixture
def geographies(geography_hierarchy):
    geo1 = GeographyFactory(code="GEOCODE_1", version=geography_hierarchy.version)
    geo2 = GeographyFactory(code="GEOCODE_2", version=geography_hierarchy.version)

    return [geo1, geo2]

@pytest.fixture
def dataset(geography_hierarchy):
    return DatasetFactory(geography_hierarchy=geography_hierarchy)

good_data = [
    ("GEOCODE_1", "F1_value_1", "F2_value_1", 111),
    ("GEOCODE_2", "F1_value_2", "F2_value_2", 222),
]

data_with_different_case = [
    ("GEOCODE_1", "f1_VALue_1", "F2_value_1", 111),
    ("GEOCODE_2", "F1_value_2", "f2_valUE_2", 222),
]

data_with_different_encodings = [
    ("GEOCODE_1", "‘F1_value_1", "F2_value_1’", 111),
    ("GEOCODE_2", "€ŠF1_value_2", "F2_value_2®®", 222),
]

good_header = ["Geography", "field1", "field2", "count"]

to_be_fixed_header = ["Geography", "field1", "field2", "count "]

@pytest.fixture(params=[(good_data, good_header, "utf8"), (good_data, to_be_fixed_header, "utf8"), (data_with_different_case, good_header, "utf8"), (data_with_different_encodings, good_header, "Windows-1252")])
def data(request):
    return request.param


@pytest.mark.django_db
class TestUploadFile:
    def test_process_csv(self, dataset, data, geographies):
        csv_data, header, encoding = data
        datasetfile = create_datasetfile(csv_data, encoding, header)

        process_csv(dataset, datasetfile.document.open("rb"))
        datasetdata = dataset.datasetdata_set.all()

        assert len(datasetdata) == len(csv_data)

        for dd, ed in zip(datasetdata, csv_data):
            assert dd.geography.code == ed[0]
            assert dd.data["field1"] == ed[1]
            assert dd.data["field2"] == ed[2]
            assert dd.data["count"] == str(ed[3])
