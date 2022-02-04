import pytest

from tests.datasets.factories import (
    GeographyFactory,
    IndicatorDataFactory,
    MetaDataFactory,
    DatasetFactory,
    IndicatorFactory,
)
from tests.profile.factories import (
    ProfileFactory,
    ProfileIndicatorFactory,
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory,
)
from wazimap_ng.datasets.models.group import Group
from wazimap_ng.profile.models import Profile
from wazimap_ng.profile.serializers.indicator_data_serializer_without_children import (
    IndicatorDataSerializerWithoutChildren
)
from wazimap_ng.profile.serializers.utils import (
    get_dataset_groups,
    get_profile_data
)
from wazimap_ng.profile.serializers.profile_serializer import (
    ExtendedProfileSerializer
)


@pytest.fixture
def profile_indicators(profile):
    version = profile.geography_hierarchy.root_geography.geographyboundary_set.get().version
    dataset1 = DatasetFactory(profile=profile, version=version)
    dataset2 = DatasetFactory(profile=profile, version=version)
    indicator1 = IndicatorFactory(dataset=dataset1)
    indicator2 = IndicatorFactory(dataset=dataset2)
    category = IndicatorCategoryFactory(profile=profile)
    subcategory = IndicatorSubcategoryFactory(category=category)
    pi1 = ProfileIndicatorFactory(profile=profile, label="PI1", subcategory=subcategory)
    pi2 = ProfileIndicatorFactory(profile=profile, label="PI2", subcategory=subcategory)
    return [
        pi1, pi2
    ]


@pytest.fixture
def indicator_data(geography, profile_indicators, version):
    idata = []
    for pi in profile_indicators:
        dataset = pi.indicator.dataset
        dataset.version = version
        dataset.save()
        indicator = pi.indicator
        idatum = IndicatorDataFactory(geography=geography, indicator=indicator)
        idata.append(idatum)

    return idata


@pytest.fixture
def metadata(indicator_data):
    dataset = indicator_data[0].indicator.dataset
    return MetaDataFactory(
        source="A source", url="http://example.com",
        description="A description", dataset=dataset
    )


@pytest.mark.django_db
@pytest.mark.usefixtures("groups")
class TestIndicatorSerializerWithoutChildren:
    def test(self, profile, geography, version, profile_indicator, category, subcategory):
        serializer = IndicatorDataSerializerWithoutChildren(profile, geography, version)
        pi_data = serializer[category.name]["subcategories"][subcategory.name]["indicators"][profile_indicator.label]
        assert pi_data["id"] == profile_indicator.id
        assert pi_data["dataset_content_type"] == "quantitative"

@pytest.mark.django_db
@pytest.mark.usefixtures("qualitative_groups")
class TestQualitativeData:

    @pytest.mark.usefixtures("qualitative_indicatordata")
    def test_with_qualitative_data(self, profile, geography, version, qualitative_profile_indicator):
        serializer = IndicatorDataSerializerWithoutChildren(profile, geography, version)
        subcategory = qualitative_profile_indicator.subcategory
        pi_data = serializer[subcategory.category.name]["subcategories"][subcategory.name]["indicators"][qualitative_profile_indicator.label]
        assert pi_data["dataset_content_type"] == "qualitative"
        assert pi_data["data"] == [{'content': 'This is example text'}, {'content': 'www.test.com'}]


@pytest.mark.django_db
class TestExtendedProfileSerializer:
    def test_basic_serializer(
        self, profile, profile_indicator, groups, indicatordata_json
    ):
        version = profile.geography_hierarchy.root_geography.geographyboundary_set.get().version
        indicator = profile_indicator.indicator
        geography = indicator.indicatordata_set.first().geography

        data = ExtendedProfileSerializer(
            profile, geography, version, skip_children=True
        )

        # assert logo
        assert "logo" in data
        assert data["logo"]["url"] == "/"

        # assert geography
        assert "geography" in data
        assert data["geography"]["code"] == geography.code

        # assert profile data
        assert "profile_data" in data
        profile_data = data["profile_data"]

        category_name = profile_indicator.subcategory.category.name
        subcategory_name = profile_indicator.subcategory.name
        assert category_name in profile_data
        assert "subcategories" in profile_data[category_name]
        assert subcategory_name in profile_data[category_name]["subcategories"]
        assert "indicators" in profile_data[category_name]["subcategories"][subcategory_name]
        indicator_data = profile_data[category_name]["subcategories"][subcategory_name]["indicators"]
        assert "child_data" not in indicator_data[profile_indicator.label]
        assert "data" in indicator_data[profile_indicator.label]
        assert indicator_data[profile_indicator.label]["data"] == indicatordata_json

        # assert highlight
        assert "highlights" in data
        assert data["highlights"] == []

        # assert overview
        assert "overview" in data
        assert data["overview"]["name"] == "Profile"
