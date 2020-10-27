from unittest.mock import patch
import csv
import tempfile

import pytest

from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv
from tests.datasets.factories import DatasetFactory, GeographyFactory, GeographyHierarchyFactory

def generate_file(data):
    fp = tempfile.NamedTemporaryFile("w", delete=False)
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

@pytest.fixture
def good_data(geographies):
    return [
        (geographies[0].code, "F1_value_1", "F2_value_1", 111),
        (geographies[1].code, "F1_value_2", "F2_value_2", 222),
    ]

@pytest.mark.django_db
class TestUploadFile:

    def test_process_csv(self, dataset, good_data, geographies):
        filename = generate_file(good_data)
        process_csv(dataset, filename)

        datasetdata = dataset.datasetdata_set.all()

        assert len(datasetdata) == len(good_data)

        for dd, ed in zip(datasetdata, good_data):
            assert dd.geography.code == ed[0]
            assert dd.data["field1"] == ed[1]
            assert dd.data["field2"] == ed[2]
            assert dd.data["count"] == str(ed[3])
