from unittest.mock import patch
import csv
import tempfile

import pytest

from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv
from tests.datasets.factories import DatasetFactory, GeographyFactory, GeographyHierarchyFactory

def generate_file(data, encoding="utf8"):
    fp = tempfile.NamedTemporaryFile("w", delete=False, encoding=encoding)
    writer = csv.writer(fp)
    writer.writerow(["Geography", "field1", "field2", "count"])
    writer.writerows(data)
    filename = fp.name
    fp.close()

    return filename


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

@pytest.fixture(params=[good_data, data_with_different_case, data_with_different_encodings])
def data(request):
    return request.param


@pytest.mark.django_db
class TestUploadFile:
    def test_process_csv(self, dataset, data, geographies):
        filename = generate_file(data)
        process_csv(dataset, filename)

        datasetdata = dataset.datasetdata_set.all()

        assert len(datasetdata) == len(data)

        for dd, ed in zip(datasetdata, data):
            assert dd.geography.code == ed[0]
            assert dd.data["field1"] == ed[1]
            assert dd.data["field2"] == ed[2]
            assert dd.data["count"] == str(ed[3])
