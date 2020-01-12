from wazimap_ng.datasets.models import (
    Dataset,
    Indicator,
    IndicatorSubcategory,
    IndicatorCategory,
    Profile,
    ProfileIndicator,
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
            name="category_1",
            profile=self.first_profile,
        )
        indicator_subcategory = IndicatorSubcategory.objects.create(
            name="sub_category_1",
            category=indicator_category,
        )
        ProfileIndicator.objects.create(
            profile=self.first_profile,
            indicator=indicator,
            subcategory=indicator_subcategory,
        )
        self.second_profile = Profile.objects.create(name="second_profile")

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
