
import csv
import pytest
import pandas as pd
from io import StringIO, BytesIO
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.datasets.factories import (
    GeographyFactory, GeographyHierarchyFactory, DatasetFactory,
    DatasetFileFactory, IndicatorFactory, GroupFactory, DatasetDataFactory
)
from tests.profile.factories import ProfileFactory
from wazimap_ng.datasets.models import DatasetData, Group
from wazimap_ng.datasets.tasks import process_uploaded_file, indicator_data_extraction

from .upload_data import (
    dataset_upload_data, default_result_set, required_headers
)


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
            csv_data["rows"], dataset.id, groups=[]
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


@pytest.mark.django_db
class TestRequiredHeaders(TestBaseDatasetUpload):

    @pytest.mark.parametrize(
        ["name"], [(name,) for name in required_headers.keys()]
    )
    def test_required_headers_for_csv_upload(self, name):
        data = required_headers[name]
        dataset = self.create_dataset()
        error_msg = F"Invalid File passed. We were not able to find Required header : {name}"
        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

    @pytest.mark.parametrize(
        ["name"], [(name,) for name in required_headers.keys()]
    )
    def test_required_headers_for_xls_upload(self, name):
        data = required_headers[name]
        dataset = self.create_dataset()
        error_msg = F"Invalid File passed. We were not able to find Required header : {name}"
        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id, test_type="xls")
            assert str(excinfo.value) == error_msg


@pytest.mark.django_db
class TestDatasetReUpload(TestBaseDatasetUpload):

    def create_indicators(self, dataset):
        for group in dataset.groups:
            indicator = IndicatorFactory(
                name=F"indicator-{group}", dataset=dataset, groups=[group]
            )
            assert indicator.indicatordata_set.all().count() == 0
            indicator_data_extraction(indicator)
            assert indicator.indicatordata_set.all().count() == 1

    def create_groups(self, dataset, data_count=1):
        for group in dataset.groups:

            subindicators = [
                F"{group}{i}".capitalize() for i in range(1, data_count+1)
            ]
            GroupFactory(
                name=group, dataset=dataset, subindicators=subindicators
            )

    def setUpData(self, data_count=1, create_indicators=False):
        dataset = self.create_dataset()
        for i in range(1, data_count+1):
            data = {"x": F"X{i}", "y": F"Y{i}", "count": F"{i}{i}"}
            DatasetDataFactory(
                dataset=dataset, geography=self.ZA_geo, data=data
            )
        dataset.groups = ["x", "y"]
        dataset.save()
        self.create_groups(dataset, data_count)

        if create_indicators:
            self.create_indicators(dataset)
        return dataset

    def test_required_header_geography(self):
        dataset = self.setUpData()
        data = [
            ["x", "y", "Count"],
            ["x2", "y2", "22"]
        ]
        error_msg = F"Invalid File passed. We were not able to find Required header : Geography"
        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id, test_type="xls")
            assert str(excinfo.value) == error_msg

    def test_required_header_count(self):
        dataset = self.setUpData()
        data = [
            ["Geography", "x", "y"],
            ["ZA", "x2", "y2"]
        ]
        error_msg = F"Invalid File passed. We were not able to find Required header : Count"
        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id, test_type="xls")
            assert str(excinfo.value) == error_msg

    def test_required_header_groups(self):
        dataset = self.setUpData()
        data = [
            ["Geography", "x", "Count"],
            ["ZA", "x2", "22"]
        ]
        error_msg = F"Invalid File passed. We were not able to find Required header : Y"
        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

    def test_required_extra_added_groups(self):
        dataset = self.setUpData()

        data = [
            ["Geography", "x", "Y", "Z", "Count"],
            ["ZA", "x2", "y2", "z2", "22"]
        ]
        error_msg = "Invalid File passed for re-upload. We found extra headers in uploaded file : y,z"
        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            self.create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

    def test_successful_reupload(self):
        dataset = self.setUpData()
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "22"]
        ]
        dataset_file = self.create_dataset_file(
            data, dataset.id
        )
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 1
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        response = list(DatasetData.objects.filter(
            dataset_id=dataset.id
        ).values_list("data", flat=True))
        assert response[0] == {'x': 'X1', 'y': 'Y1', 'count': '11'}
        assert response[1] == {'x': 'X2', 'y': 'Y2', 'count': '22'}

        # overwrite dataset data using same subindicators but different count
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "55"]
        ]

        dataset_file = self.create_dataset_file(data, dataset.id)

        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        response = list(DatasetData.objects.filter(
            dataset_id=dataset.id
        ).values_list("data", flat=True))
        assert response[0] == {'x': 'X1', 'y': 'Y1', 'count': '11'}
        assert response[1] == {'x': 'X2', 'y': 'Y2', 'count': '55'}

    def test_group_updates_after_reupload(self):
        def assert_subindicators(group_name, expected):
            assert groups.filter(name=group_name).count() == 1
            actual = groups.filter(name=group_name).first().subindicators
            assert set(actual) == set(expected)

        dataset = self.setUpData(data_count=2)
        groups = dataset.group_set.all()
        assert groups.count() == 2
        assert_subindicators("x", ["X1", "X2"])
        assert_subindicators("y", ["Y1", "Y2"])

        # Assert when reuploaded with new data
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x3", "y3", "33"]
        ]
        dataset_file = self.create_dataset_file(data, dataset.id)

        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 3

        # assert groups
        groups = dataset.group_set.all()
        assert groups.count() == 2
        assert_subindicators("x", ["X1", "X2", "X3"])
        assert_subindicators("y", ["Y1", "Y2", "Y3"])

    def test_variable_updates_after_reupload(self):
        dataset = self.setUpData(create_indicators=True)
        indicator_x = dataset.indicator_set.get(name="indicator-x")
        indicator_y = dataset.indicator_set.get(name="indicator-y")
        indicator_data_x = indicator_x.indicatordata_set.first().data
        assert indicator_data_x["groups"] == {'y': {'Y1': [{'x': 'X1', 'count': 11.0}]}}
        assert indicator_data_x["subindicators"] == {'X1': 11.0}

        indicator_data_y = indicator_y.indicatordata_set.first().data
        assert indicator_data_y["groups"] == {'x': {'X1': [{'y': 'Y1', 'count': 11.0}]}}
        assert indicator_data_y["subindicators"] == {'Y1': 11.0}

        # Assert when reuploaded with new data
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "22"]
        ]
        dataset_file = self.create_dataset_file(data, dataset.id)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 1
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        indicator_x = dataset.indicator_set.get(name="indicator-x")
        indicator_y = dataset.indicator_set.get(name="indicator-y")
        indicator_data_x = indicator_x.indicatordata_set.first().data
        assert indicator_data_x["groups"] == {'y': {'Y1': [{'x': 'X1', 'count': 11.0}], 'Y2': [{'x': 'X2', 'count': 22.0}]}}
        assert indicator_data_x["subindicators"] == {'X1': 11.0, 'X2': 22.0}

        indicator_data_y = indicator_y.indicatordata_set.first().data

        assert indicator_data_y["groups"] == {'x': {'X1': [{'y': 'Y1', 'count': 11.0}], 'X2': [{'y': 'Y2', 'count': 22.0}]}}
        assert indicator_data_y["subindicators"] == {'Y1': 11.0, 'Y2': 22.0}

        # Assert when reupload changes dataset count for duplicte line
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "33"]
        ]
        dataset_file = self.create_dataset_file(data, dataset.id)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        indicator_x = dataset.indicator_set.get(name="indicator-x")
        indicator_y = dataset.indicator_set.get(name="indicator-y")
        indicator_data_x = indicator_x.indicatordata_set.first().data
        assert indicator_data_x["groups"] == {'y': {'Y1': [{'x': 'X1', 'count': 11.0}], 'Y2': [{'x': 'X2', 'count': 33.0}]}}
        assert indicator_data_x["subindicators"] == {'X1': 11.0, 'X2': 33.0}

        indicator_data_y = indicator_y.indicatordata_set.first().data
        assert indicator_data_y["groups"] == {'x': {'X1': [{'y': 'Y1', 'count': 11.0}], 'X2': [{'y': 'Y2', 'count': 33.0}]}}
        assert indicator_data_y["subindicators"] == {'Y1': 11.0, 'Y2': 33.0}
