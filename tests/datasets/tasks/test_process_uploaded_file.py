import csv
import codecs
from io import BytesIO

import pytest

from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv
from tests.datasets.factories import DatasetFactory, GeographyFactory, GeographyHierarchyFactory, DatasetFileFactory

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


qualitative_data = [
    ("GEOCODE_1", "F1_value_1"),
    ("GEOCODE_2", "F1_value_2"),
]
qualitative_data_header = ["Geography", "content"]

@pytest.fixture(params=[(qualitative_data, qualitative_data_header, "utf8")])
def qualitative_data(request):
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

@pytest.mark.django_db
class TestQualitativeFileUpload:
    def test_process_csv(self, dataset, qualitative_data, geographies):
        csv_data, header, encoding = qualitative_data
        datasetfile = create_datasetfile(csv_data, encoding, header)

        # Check if quantative data can be uploaded without count
        assert dataset.content_type == "quantitative"
        with pytest.raises(KeyError) as e_info:
            process_csv(dataset, datasetfile.document.open("rb"))
        assert str(e_info.value) == "'count'"

        # Change content type to qualitative
        dataset2 = DatasetFactory(profile=dataset.profile, content_type="qualitative")
        process_csv(dataset2, datasetfile.document.open("rb"))
        datasetdata = dataset2.datasetdata_set.all()

        for dd, ed in zip(datasetdata, csv_data):
            assert dd.geography.code == ed[0]
            assert dd.data["content"] == ed[1]
