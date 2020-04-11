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


