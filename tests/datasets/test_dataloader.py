from unittest.mock import patch
from unittest.mock import Mock

from django_mock_queries.query import MockSet, MockModel
import pytest

from wazimap_ng.datasets import dataloader
from wazimap_ng.datasets import models
from .factories import GroupFactory
from tests.datasets.factories import DatasetFactory, DatasetDataFactory

pytestmark = pytest.mark.django_db

@patch('wazimap_ng.datasets.models.Geography.objects.get', side_effect=lambda code, version: (code, version))
def test_load_geography(mock_objects):
    o = ("X", "Y")
    assert  dataloader.load_geography(*o) == o

@patch('wazimap_ng.datasets.models.Geography.objects.get', side_effect=lambda code, version: (code, version))
def test_correct_geography_cache(mock_objects):
    o = ("X", "Y")
    assert  dataloader.load_geography(*o) == o

    p = ("X", "Z")
    assert  dataloader.load_geography(*p) == p
    
    q = ("Z", "Y")
    assert  dataloader.load_geography(*q) == q


@pytest.fixture
def good_input():
    return [
        {"geography": "XXX", "count": 111},
        {"geography": "YYY", "count": 222},
    ]

@pytest.fixture
def good_input_with_groups():
    return [
        {"geography": "XXX", "count": 111, "group1": "A", "group2": "X"},
        {"geography": "YYY", "count": 222, "group1": "B", "group2": "X"},
    ]

@pytest.fixture
@pytest.mark.django_db
def create_geography_code():
    data = models.Geography.objects.create(
        name='Test Location', code='sa',
        version='1.0', level='B', depth=50
    )
    yield
    data.delete()

@pytest.mark.django_db
class TestLoadData:
    pytestmark = pytest.mark.django_db

    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bulk_create_lt_10000(self, load_geography, MockDatasetData, good_input):
        dataset = Mock()
        dataset.geography_hierarchy.version = 9999

        dataloader.loaddata(dataset, good_input, 0)

        MockDatasetData.objects.bulk_create.assert_called_once()
        load_geography.called_with("YYY", 222)

    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bulk_create_gt_10000(self, load_geography, MockDatasetData, good_input):
        dataset = Mock()
        load_geography.return_value = "XXX"

        input_data = [dict(good_input[0]) for i in range(20001)]

        dataloader.loaddata(dataset, input_data, 0)

        assert MockDatasetData.objects.bulk_create.call_count == 3

    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bulk_check_load_geography_call(self, load_geography, MockDatasetData, good_input):
        dataset = Mock()
        dataset.geography_hierarchy.version = 9999
        load_geography.return_value = "XXX"

        dataloader.loaddata(dataset, good_input, 0)

        load_geography.assert_called_with("YYY", 9999)

    @pytest.mark.django_db
    def test_correct_geography_code(self, create_geography_code):
        code = 'sa'
        version = '1.0'
        try:
            data = dataloader.load_geography(code, version)
            assert data.code == code and data.version == version
        except models.Geography.DoesNotExist:
            pytest.fail('Unexpected Geography not found error...')

    @pytest.mark.django_db
    def test_wrong_geography_code(self, create_geography_code):
        with pytest.raises(models.Geography.DoesNotExist):
            dataloader.load_geography('SA', '1.0')

    @pytest.mark.django_db
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_missing_geography(self, load_geography, MockDatasetData, good_input):
        dataset = Mock()
        load_geography.side_effect = models.Geography.DoesNotExist()

        try:
            (errors, warnings) = dataloader.loaddata(dataset, good_input, 0)
            assert len(warnings) == 2
            assert len(errors) == 0
        except models.Geography.DoesNotExist:
            assert False

        assert MockDatasetData.objects.bulk_create.call_count == 1
        MockDatasetData.objects.bulk_create.assert_called_with([], 1000)

    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bad_count(self, load_geography):
        dataset = Mock()
        input_data = [{"geography": "XXX", "count": ""}]

        (errors, warnings) = dataloader.loaddata(dataset, input_data, 0)
        assert len(warnings) == 0
        assert len(errors) == 1

    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    @patch('wazimap_ng.datasets.dataloader.create_groups')
    def test_datasetdata_created(self, create_groups, load_geography, MockDatasetData, good_input_with_groups):
        data = good_input_with_groups
        dataset = Mock(spec=models.Dataset)

        dataloader.loaddata(dataset, data, 0)

        assert MockDatasetData.call_count == 2
        args1 = MockDatasetData.call_args_list[0][1]
        args2 = MockDatasetData.call_args_list[1][1]
        assert args1["data"] == data[0]
        assert args1["dataset"] == dataset
        assert args2["data"] == data[1]
        assert args2["dataset"] == dataset

    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    @patch('wazimap_ng.datasets.dataloader.create_groups')
    def test_create_groups_called(self, create_groups, load_geography, MockDatasetData, good_input_with_groups):
        data = good_input_with_groups
        dataset = Mock(spec=models.Dataset)

        dataloader.loaddata(dataset, data, 0)

        assert create_groups.call_count == 1
        create_groups.assert_called_with(dataset, ["group1", "group2"])

    datasetdata = MockSet()
    datasetdata_objects = patch('wazimap_ng.datasets.models.DatasetData.objects', datasetdata)


@pytest.fixture
def dataset():
    return DatasetFactory()

@pytest.fixture
def datasetData(dataset):
    DatasetDataFactory(
        dataset=dataset,
        data={
            'group1': 'A', 'group2': 'X'
        }
    )
    DatasetDataFactory(
        dataset=dataset,
        data={
            'group1': 'B', 'group2': 'Y'
        }
    )

@pytest.fixture
def subindicatorGroup(dataset):
    subindicators = {
        "group1": ["A", "B"],
        "group2": ["X", "Y"]
    }
    for name in ["group1", "group2"]:
        GroupFactory(
            dataset=dataset, name=name,
            subindicators=subindicators[name]
        )


@pytest.mark.django_db
class TestCreateGroups:

    def test_create_groups_without_subindicator_in_datasatdata(self, dataset):
        assert dataset.group_set.count() == 0

        dataloader.create_groups(dataset, ["group1", "group2"])
        groups = dataset.group_set.all()

        assert groups.count() == 2
        assert groups[0].name == "group1"
        assert groups[0].dataset == dataset
        assert groups[0].subindicators == []
        assert groups[1].name == "group2"
        assert groups[1].dataset == dataset
        assert groups[1].subindicators == []

    def test_groups_with_subindicators_in_datasetdata(self, dataset, datasetData):

        groups = dataloader.create_groups(dataset, ["group1", "group2"])
        assert len(groups) == 2
        assert groups[0].subindicators == ["A", "B"]
        assert groups[1].subindicators == ["X", "Y"]

    def test_duplicate_groups(self, dataset, subindicatorGroup):
        assert dataset.group_set.count() == 2
        groups = dataset.group_set.values_list("name", flat=True)
        assert groups[0] == "group1"
        assert groups[1] == "group2"

        dataloader.create_groups(dataset, ["group1", "group2"])

        assert dataset.group_set.count() == 2
        groups = dataset.group_set.values_list("name", flat=True)
        assert groups[0] == "group1"
        assert groups[1] == "group2"

    def test_duplicate_subindicators(self, dataset, datasetData, subindicatorGroup):
        assert dataset.group_set.count() == 2

        DatasetDataFactory(
            dataset=dataset,
            data={
                'group1': 'A', 'group2': 'X'
            }
        )

        groups = dataloader.create_groups(dataset, ["group1", "group2"])

        assert len(groups) == 2
        assert groups[0].subindicators == ["A", "B"]
        assert groups[1].subindicators == ["X", "Y"]

    def test_subindicators_update(self, dataset, datasetData, subindicatorGroup):
        assert dataset.group_set.count() == 2

        DatasetDataFactory(
            dataset=dataset, data={
                'group1': 'C', 'group2': 'X'
            }
        )

        groups = dataloader.create_groups(dataset, ["group1", "group2"])

        assert len(groups) == 2
        assert groups[0].subindicators == ["A", "B", "C"]
        assert groups[1].subindicators == ["X", "Y"]

    def test_new_dataset_subindicators(self, dataset, datasetData, subindicatorGroup):
        # Re-instantiate DatasetFactory to get a new dataset ID, create groups with unique subindicators and check that only subindicators from this dataset exist
        dataset = DatasetFactory()

        DatasetDataFactory(
            dataset=dataset, data={
                'group1': 'D', 'group2': 'Z'
            }
        )

        groups = dataloader.create_groups(dataset, ["group1", "group2"])

        assert len(groups) == 2
        assert groups[0].subindicators == ["D"]
        assert groups[1].subindicators == ["Z"]

