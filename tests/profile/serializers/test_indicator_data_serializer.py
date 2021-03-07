import pytest

from wazimap_ng.profile.serializers.indicator_data_serializer import get_indicator_data, get_profile_data


@pytest.mark.django_db
def test_profile_indicator_order(geography, profile_indicators):
    profile = profile_indicators[0].profile
    pi1, pi2 = profile_indicators

    pi1.order = 1
    pi1.save()

    pi2.order = 2
    pi2.save()

    output = get_indicator_data(profile, profile.indicators.all(), [geography])
    assert output[0]["profile_indicator_label"] == "PI1"
    assert output[1]["profile_indicator_label"] == "PI2"

    pi1.order = 2
    pi1.save()

    pi2.order = 1
    pi2.save()

    output = get_indicator_data(profile, profile.indicators.all(), [geography])
    assert output[0]["profile_indicator_label"] == "PI2"
    assert output[1]["profile_indicator_label"] == "PI1"

@pytest.mark.django_db
def test_profile_indicator_metadata(geography, grouped_profile_indicator):
    profile = grouped_profile_indicator.profile
    indicator = grouped_profile_indicator.indicator
    output = get_indicator_data(profile, [indicator], [geography])
    assert output[0]["metadata_source"] == "A source"
    assert output[0]["metadata_description"] == "A description"
    assert output[0]["metadata_url"] == "http://example.com"
