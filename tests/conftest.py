import pytest
from factory.declarations import List

from tests.datasets.factories import (
    DatasetDataFactory,
    DatasetFactory,
    DatasetFileFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    GroupFactory,
    IndicatorDataFactory,
    IndicatorFactory,
    LicenceFactory,
    MetaDataFactory
)
from tests.profile.factories import (
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory,
    ProfileFactory,
    ProfileHighlightFactory,
    ProfileIndicatorFactory,
    ProfileKeyMetricsFactory
)
from wazimap_ng.datasets.models import Geography, GeographyHierarchy
from wazimap_ng.profile.models import Profile

from django.test import RequestFactory

from tests.general.factories import (
    UserFactory, AuthGroupFactory
)

from guardian.shortcuts import (
    get_perms_for_model, assign_perm
)


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_superuser(self):
        return True


@pytest.fixture
def profile_admin_group():
    return AuthGroupFactory(name="ProfileAdmin")

@pytest.fixture
def profile_admin_user(profile_admin_group):
    user = UserFactory(is_staff=True)
    user.groups.add(profile_admin_group)
    return user

@pytest.fixture
def superuser():
    return MockSuperUser()

@pytest.fixture
def factory():
    return RequestFactory()

@pytest.fixture
def mocked_request(factory, superuser):
    request = factory.get('/get/request')
    request.method = 'GET'
    request.user = superuser
    return request

@pytest.fixture
def mocked_request_profileadmin(factory, profile_admin_user):
    request = factory.get('/get/request')
    request.method = 'GET'
    request.user = profile_admin_user
    return request

from django.test import RequestFactory


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_superuser(self):
        return True


@pytest.fixture
def superuser():
    return MockSuperUser()


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def mocked_request(factory, superuser):
    request = factory.get('/get/request')
    request.method = 'GET'
    request.user = superuser
    return request


@pytest.fixture
def licence():
    return LicenceFactory(name="licence name", url="abc url")


@pytest.fixture
def geographies():
    root = GeographyFactory(code="ROOT_GEOGRAPHY")
    geo1 = GeographyFactory(code="GEOCODE_1", version=root.version)
    geo2 = GeographyFactory(code="GEOCODE_2", version=root.version)

    return [root, geo1, geo2]


@pytest.fixture
def geography(geographies):
    return geographies[0]


@pytest.fixture
def other_geographies(geographies):
    return geographies[1:]


@pytest.fixture
def geography_hierarchy(geography):
    hierarchy = GeographyHierarchyFactory(root_geography=geography)

    return hierarchy


@pytest.fixture
def child_geographies(geography):
    return [
        geography.add_child(code=f"child{i}_geo", version=geography.version)
        for i in range(2)
    ]


@pytest.fixture
def profile(geography_hierarchy):

    configuration = {
        "urls": ["some_domain.com"]
    }

    return ProfileFactory(geography_hierarchy=geography_hierarchy, configuration=configuration)

@pytest.fixture
def profile_group(profile):
    profile_group = AuthGroupFactory(name=profile.name)
    for perm in get_perms_for_model(Profile):
        assign_perm(perm, profile_group, profile)

    return profile_group

@pytest.fixture
def private_profile(geography_hierarchy):
    return ProfileFactory(
        name="private profile", permission_type="private",
        geography_hierarchy=geography_hierarchy
    )

@pytest.fixture
def private_profile_group(private_profile):
    profile_group = AuthGroupFactory(name=private_profile.name)
    for perm in get_perms_for_model(Profile):
        assign_perm(perm, profile_group, private_profile)

    return profile_group


@pytest.fixture
def dataset(profile):
    return DatasetFactory(profile=profile)


@pytest.fixture
def groups(dataset):
    return [
        GroupFactory(dataset=dataset, name="gender", subindicators=[
                     "male", "female"], can_aggregate=True, can_filter=True),
        GroupFactory(dataset=dataset, name="language", subindicators=[
                     "isiXhosa", "isiZulu"], can_aggregate=True, can_filter=True),
    ]


@pytest.fixture
def indicator(dataset):
    subindicators = ["male", "female"]
    groups = ["gender"]
    return IndicatorFactory(dataset=dataset, subindicators=subindicators, groups=groups)


@pytest.fixture
def datasetdata(indicator, geography):
    dataset = indicator.dataset

    return [
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "15", "language": "isiXhosa", "count": 1}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "15", "language": "isiZulu", "count": 2}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "16", "language": "isiXhosa", "count": 3}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "16", "language": "isiZulu", "count": 4}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "17", "language": "isiXhosa", "count": 5}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "17", "language": "isiZulu", "count": 6}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "15", "language": "isiXhosa", "count": 7}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "15", "language": "isiZulu", "count": 8}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "16", "language": "isiXhosa", "count": 9}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "16", "language": "isiZulu", "count": 10}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "17", "language": "isiXhosa", "count": 11}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "17", "language": "isiZulu", "count": 12}),
    ]


@pytest.fixture
def child_datasetdata(datasetdata, geography):
    def gendict(d, g): return {**d.data, **{"geography": g.pk}}
    dataset = datasetdata[0].dataset

    new_datasetdata = [
        DatasetDataFactory(dataset=dataset, geography=g, data=gendict(d, g))
        for g in geography.get_children()
        for d in datasetdata
    ]

    return new_datasetdata


@pytest.fixture
def metadata(licence):
    return MetaDataFactory(source="XYZ", url="http://example.com", description="ABC", licence=licence)


@pytest.fixture
def indicatordata_json():
    return [
        {"gender": "male", "age": "15", "language": "isiXhosa", "count": 1},
        {"gender": "male", "age": "15", "language": "isiZulu", "count": 2},
        {"gender": "male", "age": "16", "language": "isiXhosa", "count": 3},
        {"gender": "male", "age": "16", "language": "isiZulu", "count": 4},
        {"gender": "male", "age": "17", "language": "isiXhosa", "count": 5},
        {"gender": "male", "age": "17", "language": "isiZulu", "count": 6},
        {"gender": "female", "age": "15", "language": "isiXhosa", "count": 7},
        {"gender": "female", "age": "15", "language": "isiZulu", "count": 8},
        {"gender": "female", "age": "16", "language": "isiXhosa", "count": 9},
        {"gender": "female", "age": "16", "language": "isiZulu", "count": 10},
        {"gender": "female", "age": "17", "language": "isiXhosa", "count": 11},
        {"gender": "female", "age": "17", "language": "isiZulu", "count": 12},
    ]


@pytest.fixture
def indicatordata(indicator, indicatordata_json, geography):

    return [
        IndicatorDataFactory(indicator=indicator, geography=geography, data=indicatordata_json)
    ]


@pytest.fixture
def other_geographies_indicatordata(indicator, indicatordata_json, other_geographies):
    return [
        IndicatorDataFactory(indicator=indicator, geography=g, data=indicatordata_json)
        for g in other_geographies
    ]


@pytest.fixture
def child_indicatordata(indicator, indicatordata_json, child_geographies):
    def mult_count(js, factor): return {"count": js["count"] * factor}
    def merge(d1, d2): return {**d1, **d2}
    def dup_data(factor): return [merge(js, mult_count(js, factor)) for js in indicatordata_json]

    return [
        IndicatorDataFactory(indicator=indicator, geography=g, data=dup_data(idx + 1))
        for idx, g in enumerate(child_geographies)
    ]


@pytest.fixture
def profile_indicator(profile, indicatordata):
    indicator = indicatordata[0].indicator
    return ProfileIndicatorFactory(profile=profile, indicator=indicator)


@pytest.fixture
def category(profile_indicator):
    c = profile_indicator.subcategory.category
    c.profile_id = profile_indicator.profile_id
    c.name = "A test category"
    c.save()
    return c


@pytest.fixture
def subcategory(profile_indicator, category):
    s = profile_indicator.subcategory
    s.category = category
    s.name = "A test subcategory"
    s.save()
    return s


@pytest.fixture
def profile_key_metric(profile, indicatordata):
    FEMALE_GROUP_INDEX = 1
    indicator = indicatordata[0].indicator
    return ProfileKeyMetricsFactory(profile=profile, variable=indicator, subindicator=FEMALE_GROUP_INDEX)


@pytest.fixture
def profile_highlight(profile, indicatordata):
    FEMALE_GROUP_INDEX = 1
    indicator = indicatordata[0].indicator
    return ProfileHighlightFactory(profile=profile, indicator=indicator, subindicator=FEMALE_GROUP_INDEX)


# Qualitative content indicator

@pytest.fixture
def qualitative_dataset(profile):
    return DatasetFactory(profile=profile, content_type="qualitative")

@pytest.fixture
def qualitative_groups(qualitative_dataset):
    return [
        GroupFactory(
            dataset=qualitative_dataset,
            name="content",
            subindicators=["This is example text", "www.test.com"],
            can_aggregate=True, can_filter=True),
    ]

@pytest.fixture
def qualitative_indicator(qualitative_dataset):
    subindicators = ["This is example text", "www.test.com"]
    groups = ["content"]
    return IndicatorFactory(dataset=qualitative_dataset, subindicators=subindicators, groups=groups)

@pytest.fixture
def qualitative_indicatordata(qualitative_indicator, geography):
    return [
        IndicatorDataFactory(
            indicator=qualitative_indicator,
            geography=geography,
            data=[
                  {
                    "content": "This is example text"
                  },
                  {
                    "content": "www.test.com"
                  }
            ]
        )
    ]

@pytest.fixture
def qualitative_profile_indicator(profile, qualitative_indicatordata):
    indicator = qualitative_indicatordata[0].indicator
    return ProfileIndicatorFactory(
        profile=profile, indicator=indicator,
        label="qualitative content"
    )


@pytest.fixture
def qualitative_category(qualitative_profile_indicator):
    c = qualitative_profile_indicator.subcategory.category
    c.profile_id = qualitative_profile_indicator.profile_id
    c.name = "A test category"
    c.save()
    return c


@pytest.fixture
def qualitative_subcategory(qualitative_profile_indicator, category):
    s = qualitative_profile_indicator.subcategory
    s.category = category
    s.name = "A test subcategory"
    s.save()
    return s