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
    dataset_upload_data_fixture_data, default_result_set, required_headers_fixture_data
)


@pytest.fixture
def geography():
    return GeographyFactory(code="ZA")


@pytest.fixture
def geography_hierarchy(geography):
    return GeographyHierarchyFactory(root_geography=geography)


@pytest.fixture
def profile(geography_hierarchy):
    return ProfileFactory(geography_hierarchy=geography_hierarchy)


@pytest.fixture
def create_dataset(profile, geography_hierarchy):
    def _make_dataset_record(profile=profile, hierarchy=geography_hierarchy, name="TestDataset", groups=[]):
        return DatasetFactory(
            profile=profile, name=name,
            geography_hierarchy=geography_hierarchy, groups=groups
        )
    return _make_dataset_record


def create_csv_file(data):
    csvfile = StringIO()
    csv.writer(csvfile).writerows(data)
    return csvfile.getvalue()


def create_xls_file(data):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    pd.DataFrame(data).to_excel(writer, index=False, header=False)
    writer.save()
    return output.getvalue()


@pytest.fixture
def create_dataset_file():
    def _make_datasetfile_record(data, dataset_id, test_type="csv", name='test'):
        content = None
        if test_type == "csv":
            content = create_csv_file(data).encode("utf-8")
        elif test_type == "xls":
            content = create_xls_file(data)
        return DatasetFileFactory(
            name=name, dataset_id=dataset_id,
            document=SimpleUploadedFile(
                name=F"{name}.{test_type}", content=content
            )
        )
    return _make_datasetfile_record


@pytest.fixture
def create_datasetdata(geography):
    def _make_datasetdata_records(dataset, geography=geography, data_count=1):
        for i in range(1, data_count+1):
            data = {"x": F"x{i}", "y": F"y{i}", "count": F"{i}{i}"}
            DatasetDataFactory(
                dataset=dataset, geography=geography, data=data
            )
    return _make_datasetdata_records


@pytest.fixture
def create_groups():
    def _make_group_records(dataset, data_count=1):
        for group in dataset.groups:
            subindicators = [F"{group}{i}" for i in range(1, data_count+1)]
            GroupFactory(
                name=group, dataset=dataset, subindicators=subindicators
            )
    return _make_group_records


@pytest.fixture
def create_indicators():
    def _make_indicator_records(dataset):
        for group in dataset.groups:
            indicator = IndicatorFactory(
                name=F"indicator-{group}", dataset=dataset, groups=[group]
            )
            assert indicator.indicatordata_set.all().count() == 0
            indicator_data_extraction(indicator)
            assert indicator.indicatordata_set.all().count() == 1
    return _make_indicator_records


@pytest.fixture(params=dataset_upload_data_fixture_data)
def dataset_fixture_key(request):
    return request.param


@pytest.fixture
def test_data(dataset_fixture_key):
    dataset = dataset_upload_data_fixture_data[dataset_fixture_key]
    return dataset["rows"]


@pytest.fixture
def expected_result(dataset_fixture_key):
    dataset = dataset_upload_data_fixture_data[dataset_fixture_key]
    return dataset.get("results", default_result_set)


@pytest.mark.django_db
class TestSuccessfulDatasetUpload:

    def test_upload_csv(self, test_data, expected_result, create_dataset, create_dataset_file):
        dataset = create_dataset()
        dataset_file = create_dataset_file(test_data, dataset.id)

        # assert that dataset does not have dataset data objs
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 0

        # process dataset file
        data = process_uploaded_file(dataset_file, dataset)

        # Asserts
        assert data["model"] == "datasetfile"
        assert data["name"] == dataset.name
        assert data["dataset_id"] == dataset.id
        assert data["error_log"] == None
        assert data["warning_log"] == None
        data_objs = DatasetData.objects.filter(dataset_id=dataset.id)
        assert data_objs.count() == len(expected_result)

        for idx, obj in enumerate(data_objs):
            assert obj.geography.code == "ZA"
            assert obj.data == expected_result[idx]


    def test_upload_xls(self, test_data, expected_result, create_dataset, create_dataset_file):
        dataset = create_dataset()
        dataset_file = create_dataset_file(
            test_data, dataset.id, test_type="xls"
        )

        # assert that dataset does not have dataset data objs
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 0

        # process dataset file
        data = process_uploaded_file(dataset_file, dataset)

        # Asserts
        assert data["model"] == "datasetfile"
        assert data["name"] == dataset.name
        assert data["dataset_id"] == dataset.id
        assert data["error_log"] == None
        assert data["warning_log"] == None
        data_objs = DatasetData.objects.filter(dataset_id=dataset.id)
        assert data_objs.count() == len(expected_result)

        for idx, obj in enumerate(data_objs):
            assert obj.geography.code == "ZA"
            assert obj.data == expected_result[idx]


@pytest.fixture(params=required_headers_fixture_data)
def required_headers_fixture_key(request):
    return request.param


@pytest.fixture
def test_headers_data(required_headers_fixture_key):
    return required_headers_fixture_data[required_headers_fixture_key]


@pytest.mark.django_db
class TestRequiredHeaders:

    def test_required_headers_for_csv_upload(self, test_headers_data, required_headers_fixture_key, create_dataset, create_dataset_file):
        dataset = create_dataset()
        error_msg = F"Invalid File passed. We were not able to find Required header : {required_headers_fixture_key}"
        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(test_headers_data, dataset.id)
            assert str(excinfo.value) == error_msg


    def test_required_headers_for_xls_upload(self, test_headers_data, required_headers_fixture_key, create_dataset, create_dataset_file):
        dataset = create_dataset()
        error_msg = F"Invalid File passed. We were not able to find Required header : {required_headers_fixture_key}"
        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(test_headers_data, dataset.id, test_type="xls")
            assert str(excinfo.value) == error_msg


@pytest.mark.django_db
class TestDatasetReUpload:

    def test_required_header_geography(self, create_dataset, create_groups, create_datasetdata, create_dataset_file):
        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset)
        create_groups(dataset)

        data = [
            ["x", "y", "Count"],
            ["x2", "y2", "22"]
        ]
        error_msg = F"Invalid File passed. We were not able to find Required header : Geography"
        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id, test_type="xls")
            assert str(excinfo.value) == error_msg

    def test_required_header_count(self, create_dataset, create_groups, create_datasetdata, create_dataset_file):
        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset)
        create_groups(dataset)

        data = [
            ["Geography", "x", "y"],
            ["ZA", "x2", "y2"]
        ]
        error_msg = F"Invalid File passed. We were not able to find Required header : Count"
        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id, test_type="xls")
            assert str(excinfo.value) == error_msg

    def test_required_header_groups(self, create_dataset, create_groups, create_datasetdata, create_dataset_file):
        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset)
        create_groups(dataset)

        data = [
            ["Geography", "x", "Count"],
            ["ZA", "x2", "22"]
        ]
        error_msg = F"Invalid File passed. We were not able to find Required header : Y"
        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

    def test_required_extra_added_groups(self, create_dataset, create_groups, create_datasetdata, create_dataset_file):
        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset)
        create_groups(dataset)

        data = [
            ["Geography", "x", "Y", "Z", "Count"],
            ["ZA", "x2", "y2", "z2", "22"]
        ]
        error_msg = "Invalid File passed for re-upload. We found extra headers in uploaded file : y,z"
        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

        with pytest.raises(ValidationError) as excinfo:
            create_dataset_file(data, dataset.id)
            assert str(excinfo.value) == error_msg

    def test_successful_reupload(self, create_dataset, create_groups, create_datasetdata, create_dataset_file):
        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset)
        create_groups(dataset)
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "22"]
        ]
        dataset_file = create_dataset_file(
            data, dataset.id
        )
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 1
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        response = list(DatasetData.objects.filter(
            dataset_id=dataset.id
        ).values_list("data", flat=True))
        assert response[0] == {'x': 'x1', 'y': 'y1', 'count': '11'}
        assert response[1] == {'x': 'x2', 'y': 'y2', 'count': '22'}

        # overwrite dataset data using same subindicators but different count
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "55"]
        ]

        dataset_file = create_dataset_file(data, dataset.id)

        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        response = list(DatasetData.objects.filter(
            dataset_id=dataset.id
        ).values_list("data", flat=True))
        assert response[0] == {'x': 'x1', 'y': 'y1', 'count': '11'}
        assert response[1] == {'x': 'x2', 'y': 'y2', 'count': '55'}

    def test_group_updates_after_reupload(self, create_dataset, create_groups, create_datasetdata, create_dataset_file):
        def assert_subindicators(group_name, expected):
            assert groups.filter(name=group_name).count() == 1
            actual = groups.filter(name=group_name).first().subindicators
            assert set(actual) == set(expected)

        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset, data_count=2)
        create_groups(dataset, data_count=2)

        groups = dataset.group_set.all()
        assert groups.count() == 2
        assert_subindicators("x", ["x1", "x2"])
        assert_subindicators("y", ["y1", "y2"])

        # Assert when reuploaded with new data
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x3", "y3", "33"]
        ]
        dataset_file = create_dataset_file(data, dataset.id)

        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 3

        # assert groups
        groups = dataset.group_set.all()
        assert groups.count() == 2
        assert_subindicators("x", ["x1", "x2", "x3"])
        assert_subindicators("y", ["y1", "y2", "y3"])

    def test_variable_updates_after_reupload(self, create_dataset, create_groups, create_datasetdata, create_indicators, create_dataset_file):
        dataset = create_dataset(groups=["x", "y"])
        create_datasetdata(dataset)
        create_groups(dataset)
        create_indicators(dataset)

        indicator_x = dataset.indicator_set.get(name="indicator-x")
        indicator_y = dataset.indicator_set.get(name="indicator-y")
        indicator_data_x = indicator_x.indicatordata_set.first().data
        assert indicator_data_x["groups"] == {'y': {'y1': [{'x': 'x1', 'count': 11.0}]}}
        assert indicator_data_x["subindicators"] == {'x1': 11.0}

        indicator_data_y = indicator_y.indicatordata_set.first().data
        assert indicator_data_y["groups"] == {'x': {'x1': [{'y': 'y1', 'count': 11.0}]}}
        assert indicator_data_y["subindicators"] == {'y1': 11.0}

        # Assert when reuploaded with new data
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "22"]
        ]
        dataset_file = create_dataset_file(data, dataset.id)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 1
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        indicator_x = dataset.indicator_set.get(name="indicator-x")
        indicator_y = dataset.indicator_set.get(name="indicator-y")
        indicator_data_x = indicator_x.indicatordata_set.first().data
        assert indicator_data_x["groups"] == {'y': {'y1': [{'x': 'x1', 'count': 11.0}], 'y2': [{'x': 'x2', 'count': 22.0}]}}
        assert indicator_data_x["subindicators"] == {'x1': 11.0, 'x2': 22.0}

        indicator_data_y = indicator_y.indicatordata_set.first().data

        assert indicator_data_y["groups"] == {'x': {'x1': [{'y': 'y1', 'count': 11.0}], 'x2': [{'y': 'y2', 'count': 22.0}]}}
        assert indicator_data_y["subindicators"] == {'y1': 11.0, 'y2': 22.0}

        # Assert when reupload changes dataset count for duplicte line
        data = [
            ["Geography", "x", "y", "Count"],
            ["ZA", "x2", "y2", "33"]
        ]
        dataset_file = create_dataset_file(data, dataset.id)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2
        process_uploaded_file(dataset_file, dataset)
        assert DatasetData.objects.filter(dataset_id=dataset.id).count() == 2

        indicator_x = dataset.indicator_set.get(name="indicator-x")
        indicator_y = dataset.indicator_set.get(name="indicator-y")
        indicator_data_x = indicator_x.indicatordata_set.first().data
        assert indicator_data_x["groups"] == {'y': {'y1': [{'x': 'x1', 'count': 11.0}], 'y2': [{'x': 'x2', 'count': 33.0}]}}
        assert indicator_data_x["subindicators"] == {'x1': 11.0, 'x2': 33.0}

        indicator_data_y = indicator_y.indicatordata_set.first().data
        assert indicator_data_y["groups"] == {'x': {'x1': [{'y': 'y1', 'count': 11.0}], 'x2': [{'y': 'y2', 'count': 33.0}]}}
        assert indicator_data_y["subindicators"] == {'y1': 11.0, 'y2': 33.0}
