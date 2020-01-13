from wazimap_ng.datasets.models import (
    Dataset,
    DatasetData,
    Geography,
    Indicator,
    Profile,
)

from rest_framework import status
from rest_framework.reverse import reverse
from django.test import TestCase
from django.core.cache import cache


class IndicatorsDetailTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.first_dataset = Dataset.objects.create(name="first")
        self.geography = Geography.objects.create(
            path="first_path",
            depth=0,
            name="first_geog",
            code="first_code",
            level="first_level",
        )
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.geography,
            data={"Count": 1, "Language": "first_language"},
        )
        self.geography_2 = Geography.objects.create(
            path="second_path",
            depth=0,
            name="second_geog",
            code="second_code",
            level="second_level",
        )
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.geography_2,
            data={"Count": 2, "Language": "second_language",},
        )
        self.indicator = Indicator.objects.create(
            groups=["Language"],
            name="first_indicator",
            label="first_label",
            dataset=self.first_dataset,
        )

    def test_correct_indicator_data_returned(self):
        url = reverse("indicator-data-view", kwargs={"indicator_id": self.indicator.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 2)
        results = response.data["results"]

        self.assertEqual(results[0]["data"]["Language"], "first_language")
        self.assertEqual(results[0]["data"]["Count"], 1)
        self.assertEqual(results[0]["data"]["geography"], "first_code")

        self.assertEqual(results[1]["data"]["Language"], "second_language")
        self.assertEqual(results[1]["data"]["Count"], 2)
        self.assertEqual(results[1]["data"]["geography"], "second_code")

    def test_filtering_works(self):
        url = reverse("indicator-data-view", kwargs={"indicator_id": self.indicator.pk})
        data = {"values": "Language:first_language"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 1)

        results = response.data["results"]
        self.assertEqual(results[0]["data"]["Language"], "first_language")
        self.assertEqual(results[0]["data"]["Count"], 1)
        self.assertEqual(results[0]["data"]["geography"], "first_code")


class IndicatorsGeographyTestCase(TestCase):
    def setUp(self):
        cache.clear()
        get = lambda node_id: Geography.objects.get(pk=node_id)
        self.first_dataset = Dataset.objects.create(name="first")
        self.root = Geography.add_root(
            name="first_geog", code="first_code", level="first_level"
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

    def test_correct_data_returned(self):
        url = reverse(
            "indicator-data-view-geography",
            kwargs={
                "indicator_id": self.indicator.pk,
                "geography_code": self.root_2.code,
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 2)

        results = response.data["results"]
        self.assertEqual(results[0]["data"]["Language"], "second_language")
        self.assertEqual(results[0]["data"]["Count"], 2)
        self.assertEqual(results[0]["data"]["geography"], "second_code")

        self.assertEqual(results[1]["data"]["Language"], "third_language")
        self.assertEqual(results[1]["data"]["Count"], 3)
        self.assertEqual(results[1]["data"]["geography"], "second_code")

    def test_filtering_works(self):
        url = reverse(
            "indicator-data-view-geography",
            kwargs={
                "indicator_id": self.indicator.pk,
                "geography_code": self.root_2.code,
            },
        )
        data = {"values": "Language:second_language"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 1)

        results = response.data["results"]
        self.assertEqual(results[0]["data"]["Language"], "second_language")
        self.assertEqual(results[0]["data"]["Count"], 2)
        self.assertEqual(results[0]["data"]["geography"], "second_code")

    def test_parent_filtering_works(self):
        url = reverse(
            "indicator-data-view-geography",
            kwargs={
                "indicator_id": self.indicator.pk,
                "geography_code": self.root_2.code,
            },
        )
        data = {"parent": True}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 1)

        results = response.data["results"]
        self.assertEqual(results[0]["data"]["Language"], "child_language")
        self.assertEqual(results[0]["data"]["Count"], 4)
        self.assertEqual(results[0]["data"]["geography"], "child_geog")

    def test_incorrect_geography_throws_404(self):
        profile = Profile.objects.create(name="test")
        url = reverse(
            "profile-geography-data",
            kwargs={"profile_id": profile.pk, "geography_code": "TEST"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
