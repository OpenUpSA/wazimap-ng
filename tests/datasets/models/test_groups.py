from wazimap_ng.datasets.models import Indicator, Dataset, DatasetData, Group

from unittest.mock import patch
from unittest.mock import Mock

import pytest

@pytest.fixture
def dataset():
    return Dataset(name="test dataset")

@pytest.fixture
def group(dataset):
    return Group(name="Hello", dataset=dataset)

class TestGroup:
    def test_create_group(self, dataset, group):
        assert len(group.subindicators) == 0
        assert group.name == "Hello"
        assert group.dataset == dataset


    def test_str(self, dataset, group):
        assert str(group) == f"test dataset|Hello"

    def test_can_filter_default(self, group):
        assert group.can_filter == True

    def test_can_aggregate_default(self, group):
        assert group.can_aggregate == False
