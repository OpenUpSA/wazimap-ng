import pytest

from tests.profile.factories import ProfileFactory, ProfileIndicatorFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory
from tests.datasets.factories import GeographyFactory, IndicatorDataFactory, DatasetFactory, IndicatorFactory

from wazimap_ng.profile.serializers.indicator_data_serializer import get_indicator_data, get_child_indicator_data
from wazimap_ng.datasets.models import Geography

@pytest.fixture
def profile():
    return ProfileFactory()

@pytest.fixture
def geography(profile):
    return profile.geography_hierarchy.root_geography

@pytest.fixture
def dataset(profile):
    return DatasetFactory(profile=profile, geography_hierarchy=profile.geography_hierarchy)

@pytest.fixture
def indicators(dataset):
    return [
        IndicatorFactory(dataset=dataset),
        IndicatorFactory(dataset=dataset),
    ]

@pytest.fixture
def category(profile):
    return IndicatorCategoryFactory(profile=profile)

@pytest.fixture
def subcategory(category):
    return IndicatorSubcategoryFactory(category=category)


@pytest.fixture
def child_geographies(geography):
    g1 = geography.add_child(code="child1_code", name="child1", version=geography.version, level="child_level")
    g2 = geography.add_child(code="child2_code", name="child2", version=geography.version, level="child_level")

    return [g1, g2]


@pytest.fixture
def profile_indicators(profile, indicators, subcategory):
    return [
        ProfileIndicatorFactory(profile=profile, label=f"PI{idx}", indicator=indicator, subcategory=subcategory)
        for (idx, indicator) in enumerate(indicators)
    ]

@pytest.fixture
def indicator_data(profile_indicators, geography, child_geographies):
    idata = []
    for geography in Geography.objects.all():

        for pi in profile_indicators:
            indicator = pi.indicator
            idatum = IndicatorDataFactory(geography=geography, indicator=indicator)
            idata.append(idatum)


    return idata

@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_profile_indicator_order(geography, profile_indicators):
    profile = profile_indicators[0].profile
    pi1, pi2 = profile_indicators

    pi1.order = 1
    pi1.save()

    pi2.order = 2
    pi2.save()

    output = get_indicator_data(profile, geography)
    assert output[0]["profile_indicator_label"] == "PI0"
    assert output[1]["profile_indicator_label"] == "PI1"

    pi1.order = 2
    pi1.save()

    pi2.order = 1
    pi2.save()

    output = get_indicator_data(profile, geography)
    assert output[0]["profile_indicator_label"] == "PI1"
    assert output[1]["profile_indicator_label"] == "PI0"

@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_child_geographies(profile, geography):
    output = get_child_indicator_data(profile, geography)

    assert len(output) == 4
    assert output[0]["profile_indicator_label"] == "PI0"
    assert output[1]["profile_indicator_label"] == "PI1"
    assert output[2]["profile_indicator_label"] == "PI0"
    assert output[3]["profile_indicator_label"] == "PI1"
