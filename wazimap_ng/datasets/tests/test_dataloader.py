from unittest.mock import patch
from unittest.mock import Mock

from wazimap_ng.datasets import dataloader
from wazimap_ng.datasets import models
# import pytest.mark.django_db
import pytest

@patch('wazimap_ng.datasets.models.Geography.objects.get', side_effect=lambda code, version: (code, version))
def test_load_geography(mock_objects):
    o = ("X", "Y")
    assert  dataloader.load_geography(*o) == o


class TestLoadData:
    def setup_method(self):
        self.good_input = [
            {"geography": "XXX", "count": 111},
            {"geography": "YYY", "count": 222},
        ]

    @pytest.mark.django_db
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bulk_create_lt_10000(self, load_geography, MockDatasetData):
        dataset = Mock()
        dataset.geography_hierarchy.version = 9999

        dataloader.loaddata(dataset, self.good_input, 0)

        MockDatasetData.objects.bulk_create.assert_called_once()
        load_geography.called_with("YYY", 222)

    @pytest.mark.django_db
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bulk_create_gt_10000(self, load_geography, MockDatasetData):
        dataset = Mock()
        load_geography.return_value = "XXX"

        input_data = [dict(self.good_input[0]) for i in range(20001)]

        dataloader.loaddata(dataset, input_data, 0)

        assert MockDatasetData.objects.bulk_create.call_count == 3

    @pytest.mark.django_db
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bulk_check_load_geography_call(self, load_geography, MockDatasetData):
        dataset = Mock()
        dataset.geography_hierarchy.version = 9999
        load_geography.return_value = "XXX"

        dataloader.loaddata(dataset, self.good_input, 0)

        load_geography.assert_called_with("YYY", 9999)

    @pytest.mark.django_db
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_missing_geography(self, load_geography, MockDatasetData):
        dataset = Mock()
        load_geography.side_effect = models.Geography.DoesNotExist()

        try:
            (errors, warnings) = dataloader.loaddata(dataset, self.good_input, 0)
            assert len(warnings) == 2
            assert len(errors) == 0
        except models.Geography.DoesNotExist:
            assert False

        assert MockDatasetData.objects.bulk_create.call_count == 1
        MockDatasetData.objects.bulk_create.assert_called_with([], 1000)

    @pytest.mark.django_db
    @patch('wazimap_ng.datasets.models.DatasetData')
    @patch('wazimap_ng.datasets.dataloader.load_geography')
    def test_bad_count(self, load_geography, MockDatasetData):
        dataset = Mock()
        input_data = [{"geography": "XXX", "count": ""}]

        (errors, warnings) = dataloader.loaddata(dataset, input_data, 0)
        assert len(warnings) == 0
        assert len(errors) == 1
