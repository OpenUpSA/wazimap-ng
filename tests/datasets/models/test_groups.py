from wazimap_ng.datasets.models import Indicator, Dataset, DatasetData, Group

from unittest.mock import patch
from unittest.mock import Mock

class TestGroup:
    def test_create_group(self):
        dataset = Dataset(name="test dataset")
        g = Group(name="Hello", dataset=dataset)
        assert len(g.subindicators) == 0
        assert g.name == "Hello"
        assert g.dataset == dataset


    def test_str(self):
        g = Group(name="Hello")
        assert str(g) == "Hello"
