import pytest

from tests.profile.factories import ProfileFactory, ProfileIndicatorFactory, IndicatorSubcategoryFactory
from tests.datasets.factories import GeographyFactory, IndicatorDataFactory, MetaDataFactory, DatasetFactory, \
    IndicatorFactory
from wazimap_ng.profile.models import ProfileKeyMetrics

from wazimap_ng.profile.serializers.indicator_data_serializer import get_indicator_data
from wazimap_ng.profile.serializers.metrics_serializer import absolute_value


@pytest.fixture
def profile():
    return ProfileFactory()

@pytest.fixture
def geography():
    return GeographyFactory()

@pytest.fixture
def profile_indicators(profile):
    pi1 = ProfileIndicatorFactory(profile=profile, label="PI1")
    pi2 = ProfileIndicatorFactory(profile=profile, label="PI2")
    return [
        pi1, pi2
    ]

@pytest.fixture
def indicator_data(geography, profile_indicators):
    idata = []

    for pi in profile_indicators:
        indicator = pi.indicator
        idatum = IndicatorDataFactory(geography=geography, indicator=indicator)
        idata.append(idatum)


    return idata

@pytest.fixture
def metadata(indicator_data):
    dataset = indicator_data[0].indicator.dataset
    return MetaDataFactory(source="A source", url="http://example.com", description="A description", dataset=dataset)

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
    assert output[0]["profile_indicator_label"] == "PI1"
    assert output[1]["profile_indicator_label"] == "PI2"

    pi1.order = 2
    pi1.save()

    pi2.order = 1
    pi2.save()

    output = get_indicator_data(profile, geography)
    assert output[0]["profile_indicator_label"] == "PI2"
    assert output[1]["profile_indicator_label"] == "PI1"

@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_profile_indicator_metadata(geography, profile_indicators, metadata):
    profile = profile_indicators[0].profile
    output = get_indicator_data(profile, geography)
    assert output[0]["metadata_source"] == "A source"
    assert output[0]["metadata_description"] == "A description"
    assert output[0]["metadata_url"] == "http://example.com"

@pytest.fixture
def profile():
    return ProfileFactory(name="Test Profile")


@pytest.fixture
def geography_data():
    return GeographyFactory(name="XYZ", code="12131", version="ABC", level="adada")


@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_not_available_subindicator(geography_data, profile, metadata):
    dataset = DatasetFactory(
        geography_hierarchy=profile.geography_hierarchy,
        groups=["age group", "gender"],
        profile=profile,
    )
    indicator_obj = IndicatorFactory(
        name="Age by Gender",
        dataset=dataset,
        groups=["gender"],
        subindicators=[{"subindicators": None}],
    )
    indicator_subcategory = IndicatorSubcategoryFactory(
        name="test_IndicatorSubcategory", description="this is test"
    )
    profile_key_metrics = ProfileKeyMetrics(
        profile=profile,
        label="test",
        variable=indicator_obj,
        subcategory=indicator_subcategory,
        denominator="absolute_value",
        subindicator=0,
    )
    profile_key_metrics.save()

    IndicatorDataFactory(geography=geography_data, indicator=indicator_obj)
    result = absolute_value(profile_key_metrics, geography_data)
    assert result == "N/A"