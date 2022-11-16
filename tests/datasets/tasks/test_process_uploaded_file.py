import csv
import codecs
from io import StringIO

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv
from tests.datasets.factories import DatasetFactory, GeographyFactory, GeographyHierarchyFactory, DatasetFileFactory, VersionFactory


def create_csv_file(data):
    csvfile = StringIO()
    csv.writer(csvfile).writerows(data)
    return csvfile.getvalue()

def create_datasetfile(file_data, encoding, header, dataset_id):
    file_data = [header] + file_data
    content = create_csv_file(file_data).encode("utf-8")
    csv_file = SimpleUploadedFile(
        name="test.csv", content=content, content_type='text/csv'
    )
    file_obj = DatasetFileFactory(
        document=csv_file, dataset_id=dataset_id
    )
    file_obj.full_clean()
    return file_obj

good_data = [
    ["GEOCODE_1", "F1_value_1", "F2_value_1", 111],
    ["GEOCODE_2", "F1_value_2", "F2_value_2", 222],
    ["GEOCODE_2", "F1_value_3", "F2_value_3", -333],
]

data_with_different_case = [
    ["GEOCODE_1", "f1_VALue_1", "F2_value_1", 111],
    ["GEOCODE_2", "F1_value_2", "f2_valUE_2", 222],
    ["GEOCODE_2", "F1_VALUE_3", "f2_VALUE_3", -333],
]

data_with_different_encodings = [
    ["GEOCODE_1", "‘F1_value_1", "F2_value_1’", 111],
    ["GEOCODE_2", "€ŠF1_value_2", "F2_value_2®®", 222],
]

good_header = ["Geography", "field1", "field2", "count"]

to_be_fixed_header = ["Geography", "field1", "field2", "count "]


@pytest.fixture(params=[(good_data, good_header, "utf8"), (good_data, to_be_fixed_header, "utf8"), (data_with_different_case, good_header, "utf8"), (data_with_different_encodings, good_header, "Windows-1252")])
def data(request):
    return request.param


qualitative_content = [
    ("GEOCODE_1", "F1_value_1"),
    ("GEOCODE_2", "F1_value_2"),
]
qualitative_data_header = ["Geography", "Contents"]

@pytest.fixture
def qualitative_data():
    return (qualitative_content, qualitative_data_header, "utf8")


@pytest.mark.django_db
class TestUploadFile:
    def test_process_csv(self, dataset, data, geographies, version):
        csv_data, header, encoding = data
        datasetfile = create_datasetfile(csv_data, encoding, header, dataset.id)

        process_csv(dataset, datasetfile.document.open("rb"))
        datasetdata = dataset.datasetdata_set.all()
        assert len(datasetdata) == len(csv_data)

        for dd, ed in zip(datasetdata, csv_data):
            assert dd.geography.code == ed[0]
            assert dd.data["field1"] == ed[1]
            assert dd.data["field2"] == ed[2]
            assert dd.data["count"] == str(ed[3])

@pytest.mark.django_db
class TestQualitativeFileUpload:
    def test_process_csv(self, dataset, qualitative_data, geographies, version):
        csv_data, header, encoding = qualitative_data

        # Check if quantative data can be uploaded without count
        assert dataset.content_type == "quantitative"
        with pytest.raises(Exception) as e_info:
            datasetfile = create_datasetfile(csv_data, encoding, header, dataset.id)
        assert "Count" in e_info.value.messages[0]

        # Change content type to qualitative
        dataset2 = DatasetFactory(profile=dataset.profile, content_type="qualitative", version=version)
        datasetfile = create_datasetfile(csv_data, encoding, header, dataset2.id)
        process_csv(dataset2, datasetfile.document.open("rb"))
        datasetdata = dataset2.datasetdata_set.all()

        for dd, ed in zip(datasetdata, csv_data):
            assert dd.geography.code == ed[0]
            assert dd.data["contents"] == ed[1]
