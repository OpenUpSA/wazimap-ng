import pytest

from tests.datasets.factories import (
    GeographyFactory,
    IndicatorDataFactory,
    MetaDataFactory,
    DatasetFactory,
    IndicatorFactory,
    VersionFactory,
    GeographyHierarchyFactory,
    GroupFactory
)
from tests.profile.factories import (
    ProfileFactory,
    ProfileIndicatorFactory,
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory
)

from tests.boundaries.factories import GeographyBoundaryFactory

from wazimap_ng.datasets.models import Group, Geography
from wazimap_ng.profile.models import Profile
from wazimap_ng.profile.serializers import IndicatorDataSerializerForChildren

@pytest.fixture
def root_geo():
    return Geography.add_root(code="ZA", level="country")

@pytest.fixture
def geo1(root_geo):
    return root_geo.add_child(code="WC", level="province")

@pytest.fixture
def geo2(root_geo):
    return root_geo.add_child(code="EC", level="province")

@pytest.fixture
def version1():
    return VersionFactory(name="v1")

@pytest.fixture
def version2():
    return VersionFactory(name="v2")

@pytest.fixture
def create_boundaries(root_geo, geo1, geo2, version1, version2):
    """
    Root belongs to version1 & version2
    geo1 belongs to version1 & version2
    geo2 only belongs to version2
    """
    GeographyBoundaryFactory(geography=root_geo, version=version1)
    GeographyBoundaryFactory(geography=root_geo, version=version2)
    GeographyBoundaryFactory(geography=geo1, version=version1)
    GeographyBoundaryFactory(geography=geo1, version=version2)
    GeographyBoundaryFactory(geography=geo2, version=version2)


@pytest.fixture
def geography_hierarchy(version1, version2, root_geo):
    return GeographyHierarchyFactory(
        root_geography=root_geo,
        configuration = {
            "default_version": version1.name,
            "versions": [version1.name, version2.name]
        }
    )

@pytest.fixture
def profile(geography_hierarchy):
    return ProfileFactory(
        name="profile",
        geography_hierarchy=geography_hierarchy
    )

@pytest.fixture
def profile_indicators(profile, version1, version2):
    datasetv1 = DatasetFactory(profile=profile, version=version1)
    datasetv2 = DatasetFactory(profile=profile, version=version2)
    GroupFactory(
        dataset=datasetv1, name="gender", subindicators=["male", "female"],
        can_aggregate=True, can_filter=True
    )
    GroupFactory(
        dataset=datasetv1, name="language",
        subindicators=["isiXhosa", "isiZulu"], can_aggregate=True, can_filter=True
    )
    GroupFactory(
        dataset=datasetv2, name="gender", subindicators=["male", "female"],
        can_aggregate=True, can_filter=True
    )
    GroupFactory(
        dataset=datasetv2, name="language",
        subindicators=["isiXhosa", "isiZulu"], can_aggregate=True, can_filter=True
    )
    indicatorv1 = IndicatorFactory(dataset=datasetv1)
    indicatorv2 = IndicatorFactory(dataset=datasetv2)
    category = IndicatorCategoryFactory(profile=profile)
    subcategory = IndicatorSubcategoryFactory(category=category)
    pi1 = ProfileIndicatorFactory(
        profile=profile, label="PI1", subcategory=subcategory,
        indicator=indicatorv1
    )
    pi2 = ProfileIndicatorFactory(
        profile=profile, label="PI2", subcategory=subcategory,
        indicator=indicatorv2
    )
    return [
        pi1, pi2
    ]

@pytest.fixture
def indicator_data(geo1, geo2, profile_indicators, indicatordata_json):
    for pi in profile_indicators:
        IndicatorDataFactory(
            geography=geo1, indicator=pi.indicator, data=indicatordata_json
        )
        IndicatorDataFactory(
            geography=geo2, indicator=pi.indicator, data=indicatordata_json
        )

@pytest.fixture
def indicator_data_geo2(geo2, profile_indicators, indicatordata_json):
    idata = []
    for pi in profile_indicators:
        idatum = IndicatorDataFactory(
            geography=geo2, indicator=pi.indicator, data=indicatordata_json
        )
        idata.append(indicatordata_json)
    return idata

@pytest.mark.django_db
class TestIndicatorSerializerForChildren:
    def test_children_indicator_data_for_version1(
        self, profile, root_geo, version1, profile_indicators, create_boundaries,
        indicator_data,
    ):
        """
        For version1
        geography access : root_geo(ZA) & geo1(WC)
        In this  case we should only get data for geo1
        """
        pi = profile_indicators[0]
        category = pi.subcategory.category
        subcategory =pi.subcategory
        data = IndicatorDataSerializerForChildren(profile, root_geo, version1)
        pi_data = data[category.name]["subcategories"][subcategory.name]["indicators"][pi.label]["data"]
        assert "WC" in pi_data
        assert pi_data["WC"] == pi.indicator.indicatordata_set.get(geography__code="WC").data

    def test_children_indicator_data_for_version2(
        self, profile, root_geo, version2, profile_indicators, create_boundaries,
        indicator_data
    ):
        """
        For version2
        geography access : root_geo(ZA) & geo1(WC), geo2(EC)
        In this  case we should only get data for geo1 & geo2
        """
        pi = profile_indicators[1]
        category = pi.subcategory.category
        subcategory = pi.subcategory
        data = IndicatorDataSerializerForChildren(profile, root_geo, version2)
        print(dict(data))
        pi_data = data[category.name]["subcategories"][subcategory.name]["indicators"][pi.label]["data"]
        assert "WC" in pi_data
        assert "EC" in pi_data
        assert pi_data["WC"] == pi.indicator.indicatordata_set.get(geography__code="WC").data
        assert pi_data["EC"] == pi.indicator.indicatordata_set.get(geography__code="EC").data
