from wazimap_ng.datasets.models import Indicator, Dataset, DatasetData, Group


class TestGroup:
    def test_create_group(self):
        g = Group(name="Hello")
        assert len(g.subindicators) == 0
        assert g.name == "Hello"


    def test_str(self):
        g = Group(name="Hello")
        assert str(g) == "Hello"
