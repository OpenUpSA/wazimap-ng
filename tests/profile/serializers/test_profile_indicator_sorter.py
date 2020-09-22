import pytest
import unittest

from tests.profile import factoryboy as profile_factoryboy
from tests.datasets import factoryboy as datasets_factoryboy

from wazimap_ng.profile.serializers.profile_indicator_sorter import ProfileIndicatorSorter

"""
groups = (Group.objects
        .filter(dataset__indicator__profileindicator__profile=profile)
        .order_by("dataset")
        .values("name", "dataset", "subindicators")
        )
return groups

    """
@pytest.fixture
def profile():
    return profile_factoryboy.ProfileFactory()

@pytest.fixture
def profile_indicators(profile):
    profile_indicator1 = profile_factoryboy.ProfileIndicatorFactory(profile=profile)
    profile_indicator2 = profile_factoryboy.ProfileIndicatorFactory(profile=profile)
    profile_indicator3 = profile_factoryboy.ProfileIndicatorFactory()

    return [profile_indicator1, profile_indicator2, profile_indicator3]

@pytest.fixture
def datasets(profile_indicators):
    return [
        profile_indicators[0].indicator.dataset,
        profile_indicators[1].indicator.dataset,
        profile_indicators[2].indicator.dataset,
    ]

@pytest.fixture
def groups(datasets):
    subindicators1 = ["g1s1", "g1s2", "g1s3"]
    subindicators2 = ["g2s1", "g2s2", "g2s3"]
    subindicators3 = ["g3s1", "g3s2", "g3s3"]
    subindicators4 = ["a", "b"]

    return [
        datasets_factoryboy.GroupFactory(name="group1", dataset=datasets[0], subindicators=subindicators1),
        datasets_factoryboy.GroupFactory(name="group2", dataset=datasets[0], subindicators=subindicators2),
        datasets_factoryboy.GroupFactory(name="group3", dataset=datasets[1], subindicators=subindicators3),
        datasets_factoryboy.GroupFactory(name="unrelated group", dataset=datasets[2], subindicators=subindicators4),
    ]

@pytest.fixture
def profile_indicator_sorter(profile):
    return ProfileIndicatorSorter(profile)

@pytest.mark.django_db
class TestProfileIndicatorSorter:
    def test_create_profile_indicator_sorter(self, datasets, groups, profile_indicator_sorter):

        sorters = profile_indicator_sorter._sorters

        assert len(sorters) == 2
        assert list(sorters.keys()) == [datasets[0].id, datasets[1].id]

        subindicator_sorter1 = sorters[datasets[0].id]
        si_groups1 = subindicator_sorter1._group_orders
        assert list(si_groups1.keys()) == [groups[0].name, groups[1].name]
        assert si_groups1[groups[0].name] == groups[0].subindicators
        assert si_groups1[groups[1].name] == groups[1].subindicators

        subindicator_sorter2 = sorters[datasets[1].id]
        si_groups2 = subindicator_sorter2._group_orders
        assert list(si_groups2.keys()) == [groups[2].name]
        assert si_groups2[groups[2].name] ==  groups[2].subindicators

