from unittest.mock import Mock, patch

import pytest
from django_mock_queries.query import MockModel, MockSet

from wazimap_ng.datasets import dataloader, models

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

    @patch('wazimap_ng.datasets.models.Group.objects')
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_datasetdata_created(self, load_geography, MockDatasetData, group_objects, good_input_with_groups):
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


class TestCreateGroups:
    @patch('wazimap_ng.datasets.models.Group.objects')
    @patch('wazimap_ng.datasets.models.DatasetData.objects')
    def test_create_groups(self, mock_datasetdata_objects, mock_objects):
        dataset = Mock(spec=models.Dataset)

        dataloader.create_groups(dataset, ["group1", "group2"])

        assert mock_objects.create.call_count == 2
        args1 = mock_objects.create.call_args_list[0][1]
        args2 = mock_objects.create.call_args_list[1][1]
        assert args1["name"] == "group1"
        assert args2["name"] == "group2"
        assert args1["dataset"] == dataset
        assert args2["dataset"] == dataset

    @patch("wazimap_ng.datasets.models.Group.objects")
    def test_returns_groups(self, mock_objects):
        dataset = Mock(spec=models.Dataset)

        mock_objects.create.side_effect = lambda **kwargs: MockModel(**kwargs)

        groups = dataloader.create_groups(dataset, ["group1", "group2"])
        assert len(groups) == 2
        assert groups[0].name == "group1"
        assert groups[1].name == "group2"

    @patch("wazimap_ng.datasets.models.Group.objects")
    @patch("wazimap_ng.datasets.models.DatasetData.objects")
    def test_populates_subindicators(self, mock_datasetdata_objects, mock_group_objects):
        dataset = Mock(spec=models.Dataset)

        mock_group_objects.create.side_effect = lambda **kwargs: MockModel(**kwargs)
        mock_datasetdata_objects.get_unique_subindicators.side_effect = lambda group_name: {"group1": ["A", "B"], "group2": ["X"]}[group_name]

        groups = dataloader.create_groups(dataset, ["group1", "group2"])
        assert groups[0].subindicators == ["A", "B"]
        assert groups[1].subindicators == ["X"]
