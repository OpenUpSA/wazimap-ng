import csv
import codecs
from io import BytesIO

import pytest

from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv, detect_encoding
from tests.datasets.factories import DatasetFactory, GeographyFactory, GeographyHierarchyFactory, DatasetFileFactory

def generate_file(data, encoding="utf8"):
    buffer = BytesIO()
    StreamWriter = codecs.getwriter(encoding)
    text_buffer = StreamWriter(buffer)

    writer = csv.writer(text_buffer)
    writer.writerow(["Geography", "field1", "field2", "count"])
    writer.writerows(data)

    buffer.seek(0)
    return buffer


def create_datasetfile(csv_data, encoding):
    buffer = generate_file(csv_data, encoding)
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

@pytest.fixture(params=[(good_data, "utf8"), (data_with_different_case, "utf8"), (data_with_different_encodings, "Windows-1252")])
def data(request):
    return request.param

def test_detect_encoding():
    buffer = generate_file(data_with_different_encodings, "Windows-1252")
    encoding = detect_encoding(buffer)
    assert encoding == "Windows-1252"

@pytest.mark.django_db
class TestUploadFile:

    def test_process_csv(self, dataset, data, geographies):
        csv_data, encoding = data
        datasetfile = create_datasetfile(csv_data, encoding)

        process_csv(dataset, datasetfile.document.open("rb"))
        datasetdata = dataset.datasetdata_set.all()

        assert len(datasetdata) == len(csv_data)

        for dd, ed in zip(datasetdata, csv_data):
            assert dd.geography.code == ed[0]
            assert dd.data["field1"] == ed[1]
            assert dd.data["field2"] == ed[2]
            assert dd.data["count"] == str(ed[3])
