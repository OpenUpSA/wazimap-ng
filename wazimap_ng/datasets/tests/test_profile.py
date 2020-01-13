from wazimap_ng.datasets.models import (
    Dataset,
    Indicator,
    IndicatorSubcategory,
    IndicatorCategory,
    Profile,
    ProfileIndicator,
    Geography,
    ProfileData,
    DatasetData,
)

from rest_framework import status
from rest_framework.reverse import reverse
from django.test import TestCase
from django.core.cache import cache


class ProfileTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.first_dataset = Dataset.objects.create(name="test")
        self.first_profile = Profile.objects.create(name="first_profile")
        indicator = Indicator.objects.create(
            name="first_indicator",
            groups=["first_group"],
            label="first_label",
            dataset=self.first_dataset,
        )
        indicator_category = IndicatorCategory.objects.create(
            name="category_1", profile=self.first_profile
        )
        indicator_subcategory = IndicatorSubcategory.objects.create(
            name="sub_category_1", category=indicator_category
        )
        ProfileIndicator.objects.create(
            profile=self.first_profile,
            indicator=indicator,
            subcategory=indicator_subcategory,
        )

        self.second_profile = Profile.objects.create(name="second_profile")
        indicator_category_2 = IndicatorCategory.objects.create(
            name="category_2", profile=self.second_profile
        )
        indicator_subcategory_2 = IndicatorSubcategory.objects.create(
            name="sub_category_2", category=indicator_category_2
        )
        ProfileIndicator.objects.create(
            profile=self.second_profile,
            indicator=indicator,
            subcategory=indicator_subcategory_2,
        )

    def test_correct_profile_list_returned(self):
        url = reverse("profile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "first_profile")
        self.assertEqual(results[1]["name"], "second_profile")

    def test_correct_profile_returned(self):
        pk = self.first_profile.pk
        url = reverse("profile-detail", kwargs={"pk": pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(results["name"], "first_profile")
        self.assertEqual(results["indicators"][0]["subcategory"], "sub_category_1")
        self.assertEqual(results["indicators"][0]["category"], "category_1")


class ProfileGeographyTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.profile = Profile.objects.create(name="profile-1")
        get = lambda node_id: Geography.objects.get(pk=node_id)
        self.first_dataset = Dataset.objects.create(name="first")
        self.root = Geography.add_root(
            name="first_geog", code="first_code", level="first_level"
        )
        indicator_category = IndicatorCategory.objects.create(
            name="category_1", profile=self.profile
        )
        indicator_subcategory = IndicatorSubcategory.objects.create(
            name="sub_category_1", category=indicator_category
        )
        self.profile_data = ProfileData.objects.create(
            profile=self.profile, geography=self.root, data={"data": 2}
        )
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.root,
            data={"Count": 1, "Language": "first_language"},
        )
        self.root_2 = get(self.root.pk).add_sibling(
            name="second_geog", code="second_code", level="second_level"
        )
        self.child = get(self.root_2.pk).add_child(
            name="child", code="child_geog", level="child_level"
        )
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.root_2,
            data={"Count": 2, "Language": "second_language"},
        )
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.root_2,
            data={"Count": 3, "Language": "third_language"},
        )
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.child,
            data={"Count": 4, "Language": "child_language"},
        )
        self.indicator = Indicator.objects.create(
            groups=["Language", "parent"],
            name="first_indicator",
            label="first_label",
            dataset=self.first_dataset,
        )
        ProfileIndicator.objects.create(
            profile=self.profile,
            indicator=self.indicator,
            subcategory=indicator_subcategory,
            key_metric=True,
            name="profile_indicator",
            label="profile_indicator_label",
        )

    def test_correct_data_returned(self):
        url = reverse(
            "profile-geography-data",
            kwargs={"profile_id": self.profile.pk, "geography_code": self.root.code},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(results["geography"]["name"], "first_geog")
        self.assertEqual(results["geography"]["code"], "first_code")
        self.assertEqual(results["geography"]["level"], "first_level")
        self.assertEqual(results["key_metrics"][0]["label"], "first_label")
        self.assertEqual(results["key_metrics"][0]["value"], "-")

    def test_incorrect_geography_throws_404(self):
        url = reverse(
            "profile-geography-data",
            kwargs={"profile_id": self.profile.pk, "geography_code": "TEST"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
