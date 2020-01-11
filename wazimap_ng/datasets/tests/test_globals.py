from wazimap_ng.datasets.models import (
    Dataset,
    DatasetData,
    Geography,
    Indicator,
    Profile,
)

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.test import TestCase
from faker import Faker

fake = Faker(seed=123456789)


from functools import wraps

from django.db import transaction
from mock import patch


def rollback_db_changes(func):
    """Decorate a function so that it will be rolled back once completed."""
    @wraps(func)
    @transaction.commit_manually
    def new_f(*args, **kwargs):
        def fake_commit(using=None):
            # Don't properly commit the transaction, so we can roll it back
            transaction.set_clean(using)
        patcher = patch('django.db.transaction.commit', fake_commit)
        patcher.start()
        try:
            return func(*args, **kwargs)
        finally:
            patcher.stop()
            transaction.rollback()
    return new_f


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
        for i in range(15):
            Dataset.objects.create(name=f"dataset-{i}")
            Profile.objects.create(name=fake.name())
            Indicator.objects.create(
                groups=[],
                name=fake.name(),
                label=f"test-label-{i}",
                dataset=Dataset.objects.first(),
            )
            Geography.objects.create(
                path=f"PATH-{i}",
                depth=0,
                name=fake.name(),
                code=f"code-{i}",
                level=f"test-level-{i}",
            )
            data = {
                "data": {
                    "Language": fake.name(),
                    "Count": fake.random_int(),
                    "geography": f"GEO-{i}",
                }
            }
            DatasetData.objects.create(
                dataset=Dataset.objects.first(),
                geography=Geography.objects.first(),
                data=data,
            )

    def tearDown(self):
        Dataset.objects.all().delete()
        Profile.objects.all().delete()
        Indicator.objects.all().delete()
        Geography.objects.all().delete()
        DatasetData.objects.all().delete()

    def test_dataset_list_is_paginated(self):
        url = reverse("dataset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(response.data)
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
        print("setup")
        self.first_dataset = Dataset.objects.create(name="first")
        self.geography = Geography.objects.create(
            path="first_path",
            depth=0,
            name="first_geog",
            code="first_code",
            level="first_level",
        )
        data = {
                "Count": 100,
                "deneme": "123",
                "another": 333,
                # "amk": "first_language",
                # "geography": "first_code",
            }

        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.geography,
            data=data,
        )
        self.geography_2 = Geography.objects.create(
            path="second_path",
            depth=0,
            name="second_geog",
            code="second_code",
            level="second_level",
        )
        data = {
                "Count": 1,
                # "oespu": "second_language",
                # "geography": "second_code",
            }
        DatasetData.objects.create(
            dataset=self.first_dataset,
            geography=self.geography_2,
            data=data,
        )
        self.indicator = Indicator.objects.create(
            groups=[],
            name="first_indicator",
            label="first_label",
            dataset=self.first_dataset,
        )

    def tearDown(self):
        print("teardown")

    def test_correct_indicator_data_returned(self):
        url = reverse("indicator-data-view", kwargs={"indicator_id": self.indicator.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        number_of_results = response.data["count"]
        self.assertEqual(number_of_results, 2)
        results = response.data["results"]
        print(results)
        # self.assertEqual(results[0]["data"]["Language"], "first_language")
        self.assertEqual(results[0]["data"]["Count"], 0)
        self.assertEqual(results[0]["data"]["geography"], "first_code")

        # self.assertEqual(results[1]["data"]["Language"], "second_language")
        self.assertEqual(results[1]["data"]["Count"], 1)
        self.assertEqual(results[1]["data"]["geography"], "second_code")

    def test_filtering_works(self):
        url = reverse("indicator-data-view", kwargs={"indicator_id": self.indicator.pk})
        data = {"values": "Language:first_language"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # print(response.data)
        # number_of_results = response.data["count"]
        # self.assertEqual(number_of_results, 1)
        # results = response.data["results"]


class IndicatorsGeographyTestCase(TestCase):
    def setUp(self):
        pass

    def test_correct_data_returned(self):
        pass

    def test_filtering_works(self):
        pass


