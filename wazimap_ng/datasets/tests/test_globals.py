from wazimap_ng.datasets.models import (
    Dataset,
    DatasetData,
    Geography,
    Indicator,
    Profile,
    ProfileData,
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
        data = {"groups": [], "name": "test", "dataset": 1}
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

    def test_indicator_data_view_geography_is_readonly(self):
        url = reverse(
            "indicator-data-view-geography",
            kwargs={"indicator_id": 2, "geography_code": "Test"},
        )
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

    def test_profile_geography_data_is_readonly(self):
        url = reverse(
            "profile-geography-data", kwargs={"profile_id": 2, "geography_code": "Test"}
        )
        data = {"data": {"Language": "Unspecified", "Count": 0, "geography": "TEST123"}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_profile_detail_is_readonly(self):
        pk = 1
        url = reverse("profile-detail", kwargs={"pk": pk})
        data = {
            "subcategory": "Youth",
            "category": "Youth Demographics",
            "key_metric": False,
            "label": "Youth population by gender",
            "indicator": {},
            "universe": {},
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
        Geography.add_root(
            name=f"geography-1", code=f"code-1", level=f"test-level-1",
        )
        for i in range(25):
            Dataset.objects.create(name=f"dataset-{i}")
            Profile.objects.create(name=f"profile-{i}")
            ProfileData.objects.create(
                profile=Profile.objects.first(),
                geography=Geography.objects.first(),
                data={"Count": i},
            )
            Indicator.objects.create(
                groups=[],
                name=f"indicator-{i}",
                dataset=Dataset.objects.first(),
            )
            DatasetData.objects.create(
                dataset=Dataset.objects.first(),
                geography=Geography.objects.first(),
                data={"Count": i},
            )

    def test_dataset_list_is_paginated(self):
        url = reverse("dataset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 10)

    def test_dataset_indicator_list_is_paginated(self):
        dataset_id = Dataset.objects.first().pk
        url = reverse("dataset-indicator-list", kwargs={"dataset_id": dataset_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data)
        self.assertEqual(number_of_results, 10)

    def test_indicator_list_is_paginated(self):
        url = reverse("indicator-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 10)

    def test_indicator_data_view_is_paginated(self):
        indicator_id = Indicator.objects.first().pk
        url = reverse("indicator-data-view", kwargs={"indicator_id": indicator_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Note that pagination for indicator data view is 20 items per page
        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 20)

    def test_indicator_data_view_geography_is_paginated(self):
        indicator_id = Indicator.objects.first().pk
        geography_code = Geography.objects.first().code
        url = reverse(
            "indicator-data-view-geography",
            kwargs={"indicator_id": indicator_id, "geography_code": geography_code},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Note that pagination for indicator data view is 20 items per page
        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 20)

    def test_profile_list_is_paginated(self):
        url = reverse("profile-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_results = len(response.data["results"])
        self.assertEqual(number_of_results, 10)
