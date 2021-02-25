from collections import OrderedDict

import pytest

from wazimap_ng.profile.serializers.subindicator_sorter import (
    SubindicatorSorter
)


@pytest.fixture
def subindicators():
    return OrderedDict(a="x", b="y", c="z")

@pytest.fixture
def group_subindicators():
    return {
        "group1": {
            "a": {"c1": 10, "c2": 20, "c3": 30},
            "b": {"c1": 100, "c2": 200, "c3": 300},
            "c": {"c1": 1000, "c2": 2000, "c3": 3000}
        },
        "group2": {
            "x": {"c1": 40, "c2": 50, "c3": 60},
            "y": {"c1": 400, "c2": 500, "c3": 600},
            "z": {"c1": 4000, "c2": 5000, "c3": 6000}
        }
    }

@pytest.fixture
def sorter():
    group_orders = {
        "group1": ["b", "c", "a"],
        "group2": ["z", "y", "x"],
        "group3": ["c2", "c3", "c1"],
    }
    sorter = SubindicatorSorter(group_orders)

    return sorter

@pytest.fixture
def alternative_sorter():
    group_orders = {
        "group1": ["c", "a", "b"],
        "group2": ["x", "z", "y"],
        "group3": ["c3", "c1", "c2"],
    }
    sorter = SubindicatorSorter(group_orders)

    return sorter

class TestSubindicatorSorter:
    def test_subindicator_sort(self, sorter, subindicators):
        sort_order = ["b", "c", "a"]

        sorted_subindicators = sorter.sort_subindicators(subindicators, "group1")
        assert sorted_subindicators == OrderedDict(b="y", c="z", a="x")

        sort_order = ["c", "a", "b"]
        sorter._group_orders["group1"] = sort_order

        sorted_subindicators = sorter.sort_subindicators(subindicators, "group1")
        assert sorted_subindicators == OrderedDict(c="z", a="x", b="y")

    def test_subindicator_sort_with_missing_order(self, sorter, subindicators):
        sorted_subindicators = sorter.sort_subindicators(subindicators, "missing group")
        assert sorted_subindicators == OrderedDict(a="x", b="y", c="z")

    def test_subindicator_sort_with_incomplete_order(self, sorter, subindicators):
        sorter._group_orders["group1"] = ["b", "c"]
        sorted_subindicators = sorter.sort_subindicators(subindicators, "group1")

        assert sorted_subindicators == OrderedDict(b="y", c="z", a="x")

    def test_subindicator_sort_with_extra_order_element(self, sorter, subindicators):
        sorter._group_orders["group1"] = ["b", "c", "a", "z"]
        sorted_subindicators = sorter.sort_subindicators(subindicators, "group1")

        assert sorted_subindicators == OrderedDict(b="y", c="z", a="x")

    def test_subindicator_duplicate_keys_are_ignored(self, sorter, subindicators):
        sorter._group_orders["group1"] = ["b", "c", "a", "b"]

        sorted_subindicators = sorter.sort_subindicators(subindicators, "group1")
        assert sorted_subindicators == OrderedDict(b="y", c="z", a="x")

    def test_subindicator_no_side_effects(self, sorter, subindicators):
        sort_order = ["b", "c", "a"]

        sorted_subindicators = sorter.sort_subindicators(subindicators, "group1")
        sorted_subindicators["dummy"] = "XXX"
        assert "dummy" not in subindicators

    def test_group_sort(self, sorter, group_subindicators):
        sorted_groups = sorter.sort_groups(group_subindicators, "group3")
        sorted_group1 = sorted_groups["group1"]
        sorted_group2 = sorted_groups["group2"]

        assert list(sorted_group1.keys()) == ["b", "c", "a"]
        assert isinstance(sorted_group1, OrderedDict)

        sorted_group1_group3 = list(sorted_group1.values())
        assert sorted_group1_group3[0] == OrderedDict(c2=200, c3=300, c1=100)
        assert sorted_group1_group3[1] == OrderedDict(c2=2000, c3=3000, c1=1000)
        assert sorted_group1_group3[2] == OrderedDict(c2=20, c3=30, c1=10)

        assert list(sorted_group2.keys()) == ["z", "y", "x"]
        assert isinstance(sorted_group2, OrderedDict)
        sorted_group2_group3 = list(sorted_group2.values())
        assert sorted_group2_group3[0] == OrderedDict(c2=5000, c3=6000, c1=4000)
        assert sorted_group2_group3[1] == OrderedDict(c2=500, c3=600, c1=400)
        assert sorted_group2_group3[2] == OrderedDict(c2=50, c3=60, c1=40)

    def test_alternative_group_sort(self, alternative_sorter, group_subindicators):
        sorter = alternative_sorter
        sorted_groups = sorter.sort_groups(group_subindicators, "group3")
        sorted_group1 = sorted_groups["group1"]
        sorted_group2 = sorted_groups["group2"]

        assert list(sorted_group1.keys()) == ["c", "a", "b"]
        assert isinstance(sorted_group1, OrderedDict)

        sorted_group1_group3 = list(sorted_group1.values())
        assert sorted_group1_group3[0] == OrderedDict(c3=3000, c1=1000, c2=2000)
        assert sorted_group1_group3[1] == OrderedDict(c3=30, c1=10, c2=20)
        assert sorted_group1_group3[2] == OrderedDict(c3=300, c1=100, c2=200)

        assert list(sorted_group2.keys()) == ["x", "z", "y"]
        assert isinstance(sorted_group2, OrderedDict)

        sorted_group2_group3 = list(sorted_group2.values())
        assert sorted_group2_group3[0] == OrderedDict(c3=60, c1=40, c2=50)
        assert sorted_group2_group3[1] == OrderedDict(c3=6000, c1=4000, c2=5000)
        assert sorted_group2_group3[2] == OrderedDict(c3=600, c1=400, c2=500)

    def test_group_subset(self, sorter, group_subindicators):
        del group_subindicators["group1"]

        sorted_groups = sorter.sort_groups(group_subindicators, "group3")
        assert len(sorted_groups) == 1

        sorted_group1 = sorted_groups["group2"]
        assert list(sorted_group1.keys()) == ["z", "y", "x"]

    def test_group_empty(self, sorter, group_subindicators):
        group_subindicators["group4"] = group_subindicators["group1"]
        del group_subindicators["group1"]
        del group_subindicators["group2"]

        sorted_groups = sorter.sort_groups(group_subindicators, "group3")
        assert len(sorted_groups) == 1

        sorted_group4 = sorted_groups["group4"]
        assert list(sorted_group4.keys()) == ["a", "b", "c"]

    def test_group_no_side_effects(self, sorter, group_subindicators):
        sorted_groups = sorter.sort_groups(group_subindicators, "group3")
        sorted_groups["dummy"] = "XXX"

        assert "dummy" not in group_subindicators
