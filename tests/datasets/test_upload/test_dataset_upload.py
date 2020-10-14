from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from wazimap_ng.datasets.models import DatasetFile, Dataset, GeographyHierarchy, Geography, DatasetData
from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.tasks import process_uploaded_file
import logging

from io import StringIO, BytesIO
import csv
import pandas as pd
import pytest

from tests.profile.factories import ProfileFactory
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory, DatasetFactory, DatasetFileFactory

from .upload_data import dataset_upload_data, default_result_set

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestBaseDatasetUpload:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.ZA_geo = GeographyFactory(code="ZA")
        self.hierarchy = GeographyHierarchyFactory(root_geography=self.ZA_geo)
        self.profile = ProfileFactory(geography_hierarchy=self.hierarchy)

    def setup_data(self):
        result = []
        for name, value in dataset_upload_data.items():
            rows, result_set = self.get_data(name)
            result.append([name, row, result_set])
        return result

    def get_data(self, name):
        data = dataset_upload_data[name]
        result_set = data.get("results", default_result_set)
        return data, result_set

    def process_upload_with_asserts(self, dataset_file, dataset, result_set):
        data = process_uploaded_file(dataset_file, dataset)
        assert data["model"] == "datasetfile"
        assert data["name"] == dataset.name
        assert data["dataset_id"] == dataset.id
        assert data["error_log"] == None
        assert data["warning_log"] == None
        data_objs = DatasetData.objects.filter(dataset_id=dataset.id)
        assert data_objs.count() == len(result_set)

        for idx, obj in enumerate(data_objs):
            assert obj.geography.code == "ZA"
            assert obj.data == result_set[idx]

    def create_dataset(
        self, profile=None, hierarchy=None, name="TestDataset"
    ):
        if not profile:
            profile = self.profile
        if not hierarchy:
            hierarchy = self.hierarchy

        return DatasetFactory(
            profile=profile, name="TestDataset",
            geography_hierarchy=hierarchy
        )

    def create_csv_file(self, data):
        csvfile = StringIO()
        csv.writer(csvfile).writerows(data)
        return csvfile.getvalue()

    def create_xls_file(self, data):
        output = BytesIO()
        writer = pd.ExcelWriter(output)
        pd.DataFrame(data).to_excel(writer, index=False, header=False)
        writer.save()
        return output.getvalue()

    def create_dataset_file(
        self, data, dataset_id, test_type="csv", name='test'
    ):
        content = None
        if test_type == "csv":
            content = self.create_csv_file(data).encode("utf-8")
        elif test_type == "xls":
            content = self.create_xls_file(data)

        return DatasetFileFactory(
            name=name, dataset_id=dataset_id,
            document=SimpleUploadedFile(
                name=F"{name}.{test_type}", content=content
            )
        )

@pytest.mark.django_db
class TestSuccessfulDatasetUpload(TestBaseDatasetUpload):

    @pytest.mark.parametrize(
        ["name"], [(name,) for name in dataset_upload_data.keys()]
    )
    def test_upload_csv(self, name):
        csv_data, result_set = self.get_data(name)
        dataset = self.create_dataset()

        dataset_file = self.create_dataset_file(
            csv_data["rows"], dataset.id
        )
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 0
        self.process_upload_with_asserts(dataset_file, dataset, result_set)

    @pytest.mark.parametrize(
        ["name"], [(name,) for name in dataset_upload_data.keys()]
    )
    def test_upload_xls(self, name):
        csv_data, result_set = self.get_data(name)
        dataset = self.create_dataset()

        dataset_file = self.create_dataset_file(
            csv_data["rows"], dataset.id, test_type="xls"
        )
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 0
        self.process_upload_with_asserts(dataset_file, dataset, result_set)
