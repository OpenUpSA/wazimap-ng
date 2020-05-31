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
        d = Dataset(name="Test Dataset")
        g = Group(name="Hello", dataset=d)
        assert str(g) == f"Test Dataset|Hello"
