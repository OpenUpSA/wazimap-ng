from unittest.mock import patch
import csv
import tempfile

import pytest

from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv
from tests.datasets.factories import DatasetFactory, GeographyFactory, GeographyHierarchyFactory

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
def csv_file(geographies):
    fp = tempfile.NamedTemporaryFile("w", delete=False)
    writer = csv.writer(fp)
    writer.writerow(["Geography", "field1", "field2", "count"])
    writer.writerow([geographies[0].code, "F1_value_1", "F2_value_1", 111])
    writer.writerow([geographies[1].code, "F1_value_2", "F2_value_2", 222])
    filename = fp.name
    fp.close()

    return filename


@pytest.mark.django_db
class TestUploadFile:

    def test_process_csv(self, dataset, csv_file, geographies):
        process_csv(dataset, csv_file)
        datasetdata = dataset.datasetdata_set.all()
        assert len(datasetdata) == 2

        dd1 = datasetdata[0]
        dd2 = datasetdata[1]

        assert dd1.geography == geographies[0]
        assert dd2.geography == geographies[1]


        assert dd1.data["field1"] == "F1_value_1"
        assert dd1.data["field2"] == "F2_value_1"
        assert dd2.data["field1"] == "F1_value_2"
        assert dd2.data["field2"] == "F2_value_2"