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


class GeneralReadOnlyTestCase(TestCase):
    def test_dataset_list_is_readonly(self):
        url = reverse("dataset")
        data = {"name": "test"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_dataset_indicator_list_is_readonly(self):
        dataset_id = 1
        url = reverse("dataset-indicator-list", kwargs={"dataset_id": dataset_id})
        data = {
            "groups": [],
            "name": "test",
            "label": "test-label",
            "dataset": dataset_id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_indicator_list_is_readonly(self):
        url = reverse("indicator-list")
        data = {"groups": [], "name": "test", "label": "test-label", "dataset": 1}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_indicator_data_view_is_readonly(self):
        indicator_id = 2
        url = reverse("indicator-data-view", kwargs={"indicator_id": indicator_id})
        data = {"data": {"Language": "Unspecified", "Count": 0, "geography": "TEST123"}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_profile_list_is_readonly(self):
        url = reverse("profile-list")
        data = {"name": "test"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_profile_detail_is_readonly(self):
        pk = 1
        url = reverse("profile-detail", kwargs={"pk": pk})
        data = {
            "subcategory": "Youth",
            "category": "Youth Demographics",
            "key_metric": False,
            "name": "Youth population by gender",
            "label": "Youth population by gender",
            "indicator": {
                "id": 4,
                "groups": ["Gender"],
                "name": "Youth population by gender",
                "label": "Youth population by gender",
                "dataset": {"id": 1, "name": "Census 2011 - Language"},
            },
            "universe": {
                "id": 1,
                "filters": {"Age__in": ["15 - 19", "20 - 24"]},
                "name": "Youth",
                "label": "Youth (15 - 24)",
                "dataset": {"id": 1, "name": "Census 2011 - Language"},
            },
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class GeneralPaginationTestCase(TestCase):
    def setUp(self):
        cache.clear()
        for i in range(15):
            Dataset.objects.create(name=f"dataset-{i}")
            Profile.objects.create(name=f"profile-{i}")
            Indicator.objects.create(
                groups=[],
                name=f"indicator-{i}",
                label=f"test-label-{i}",
                dataset=Dataset.objects.first(),
            )
            Geography.objects.create(
                path=f"PATH-{i}",
                depth=0,
                name=f"geography-{i}",
                code=f"code-{i}",
                level=f"test-level-{i}",
            )
            data = {
                "data": {
                    "Language": f"language-{i}",
                    "Count": i,
                    "geography": f"GEO-{i}",
                }
            }
            DatasetData.objects.create(
                dataset=Dataset.objects.first(),
                geography=Geography.objects.first(),
                data=data,
            )

    def test_dataset_list_is_paginated(self):
        url = reverse("dataset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 10)

    # def test_dataset_indicator_list_is_paginated(self):
    #     # TODO: Fails now!
    #     dataset_id = Dataset.objects.first().pk
    #     url = reverse("dataset-indicator-list", kwargs={"dataset_id": dataset_id})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     number_of_results = len(response.data)
    #     self.assertEqual(number_of_results, 10)

    def test_indicator_list_is_paginated(self):
        url = reverse("indicator-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 10)

    # def test_indicator_data_view_is_paginated(self):
    #     # TODO: Fails now
    #     indicator_id = Indicator.objects.first().pk
    #     url = reverse("indicator-data-view", kwargs={"indicator_id": indicator_id})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     # print(response.data)
    #     number_of_results = len(response.data["results"])
    #     self.assertEqual(number_of_results, 10)

    def test_profile_list_is_paginated(self):
        url = reverse("profile-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 10)


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
            data={"Count": 100, "Language": "first_language", "another": 333},
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
            data={"Count": 1, "Language": "second_language", "another": 1},
        )
        self.indicator = Indicator.objects.create(
            groups=[],
            name="first_indicator",
            label="first_label",
            dataset=self.first_dataset,
        )

    def test_correct_indicator_data_returned(self):
        url = reverse("indicator-data-view", kwargs={"indicator_id": self.indicator.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data)
        # self.assertEqual(number_of_results, 2)
        results = response.data["results"]
        # self.assertEqual(results[0]["data"]["Language"], "first_language")
        self.assertEqual(results[0]["data"]["Count"], 100)
        self.assertEqual(results[0]["data"]["geography"], "first_code")

        # self.assertEqual(results[1]["data"]["Language"], "second_language")
        self.assertEqual(results[1]["data"]["Count"], 1)
        self.assertEqual(results[1]["data"]["geography"], "second_code")

    def test_filtering_works(self):
        # TODO: fails now
        url = reverse("indicator-data-view", kwargs={"indicator_id": self.indicator.pk})
        data = {"values": "Language:first_language"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 1)
        results = response.data["results"]
        self.assertEqual(results[0]["data"]["Count"], 100)


class IndicatorsGeographyTestCase(TestCase):
    def setUp(self):
        cache.clear()
        pass

    def test_correct_data_returned(self):
        pass

    def test_filtering_works(self):
        pass


