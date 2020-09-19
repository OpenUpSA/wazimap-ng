from collections import OrderedDict

import pytest

from wazimap_ng.profile.serializers.indicator_data_serializer import sort_subindicators

@pytest.fixture
def subindicators():
    return OrderedDict(a="x", b="y", c="z")

class TestSubindicatorSort:

    def test_correct_sort(self, subindicators):
        sort_order = ["b", "c", "a"]

        sorted_subindicators = sort_subindicators(subindicators, sort_order)
        assert list(sorted_subindicators.keys()) == sort_order
        assert list(sorted_subindicators.values()) == [subindicators[k] for k in sort_order]

        sort_order = ["c", "a", "b"]

        sorted_subindicators = sort_subindicators(subindicators, sort_order)
        assert list(sorted_subindicators.keys()) == sort_order
        assert list(sorted_subindicators.values()) == [subindicators[k] for k in sort_order]

    def test_sort_with_missing_order(self, subindicators):
        sorted_subindicators = sort_subindicators(subindicators, None)
        assert list(sorted_subindicators.keys()) == list(subindicators.keys())
        assert list(sorted_subindicators.values()) == list(subindicators.values())

        sorted_subindicators = sort_subindicators(subindicators, [])
        assert list(sorted_subindicators.keys()) == list(subindicators.keys())
        assert list(sorted_subindicators.values()) == list(subindicators.values())

    def test_sort_with_incomplete_order(self, subindicators):
        sort_order = ["b", "c"]
        sorted_subindicators = sort_subindicators(subindicators, sort_order)
        assert list(sorted_subindicators.keys()) == ["b", "c", "a"]
        assert list(sorted_subindicators.values()) == [subindicators[k] for k in ["b", "c", "a"]]

    def test_that_return_dict_is_ordereda(self, subindicators):
        sorted_subindicators = sort_subindicators(subindicators, ["a", "c", "b"])


        assert type(sorted_subindicators) == OrderedDict

    def test_duplicate_keys_are_ignored(self, subindicators):
        sort_order = ["b", "c", "a", "b"]

        sorted_subindicators = sort_subindicators(subindicators, sort_order)
        assert list(sorted_subindicators.keys()) == ["b", "c", "a"]
        assert list(sorted_subindicators.values()) == [subindicators[k] for k in ["b", "c", "a"]]

