import csv

from io import StringIO
from test_plus import APITestCase

from wazimap_ng.datasets.models import DatasetData, Dataset

from tests.profile.factories import ProfileFactory
from tests.datasets.factories import (
    GeographyFactory, GeographyHierarchyFactory, DatasetFactory,
    DatasetDataFactory, IndicatorFactory, IndicatorDataFactory
)

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django_q.tasks import fetch


class TestDatasetUploadView(APITestCase):

    def create_csv_file(self, data):
        csvfile = StringIO()
        csv.writer(csvfile).writerows(data)
        return csvfile.getvalue()

    def setUp(self):

        # General data
        geography = GeographyFactory(code="ZA")
        self.geography_hierarchy = GeographyHierarchyFactory(root_geography=geography)
        self.profile = ProfileFactory(geography_hierarchy=self.geography_hierarchy)
        self.group = Group.objects.create(name=self.profile.name)

        # Dataset specific data
        self.dataset = DatasetFactory(
            name="dataset-1", profile=self.profile, groups=["test"],
            geography_hierarchy=self.geography_hierarchy
        )
        DatasetDataFactory(
            dataset=self.dataset, geography=geography,
            data={'test': 'y1', 'count': '22'}
        )

        # Indicator specific data
        self.variable = IndicatorFactory(dataset=self.dataset)
        IndicatorDataFactory(
            indicator=self.variable, geography=geography,
            data={'groups': {}, 'subindicators': {'y1': 22.0}}
        )
        
        # Upload csv related data
        data = [
            ["Geography", "test", "Count"],
            ["ZA", "x1", "11"]
        ]
        content = self.create_csv_file(data).encode("utf-8")
        self.csv_file = SimpleUploadedFile(
                name="test.csv", content=content, content_type='text/csv'
        )


    def test_anonymous_user_request_for_new_dataset(self):
        response = self.post("dataset", data={
            "file": self.csv_file,
            "geography_hierarchy": self.geography_hierarchy.id,
            "profile": self.profile.id,
            "name": "dataset-2",
        })

        assert response.status_code == 403
        assert response.data["detail"] == "You do not have permission to upload to this profile"


    def test_anonymous_user_request_for_updating_dataset(self):

        response = self.post("dataset-upload", dataset_id=self.dataset.id, data={
            "file": self.csv_file,
            "update": True
        })

        assert response.status_code == 403
        assert response.data["detail"] == "You do not have permission to upload to this profile"


    def test_non_profile_user_request_for_new_dataset(self):
        user1 = self.make_user("user1")
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        response = client.post(url, data={
            "file": self.csv_file,
            "geography_hierarchy": self.geography_hierarchy.id,
            "profile": self.profile.id,
            "name": "dataset-2",
        }, format='multipart')

        assert response.status_code == 403
        assert response.data["detail"] == "You do not have permission to upload to this profile"


    def test_non_profile_user_request_for_updating_dataset(self):
        user1 = self.make_user("user1")
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)

        url = reverse('dataset-upload', args=(self.dataset.id,))
        response = client.post(url, data={
            "file": self.csv_file,
            "update": True
        }, format='multipart')

        assert response.status_code == 403
        assert response.data["detail"] == "You do not have permission to upload to this profile"


    def test_successful_request_for_new_dataset(self):
        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        assert Dataset.objects.filter(name="dataset-2").exists() == False

        response = client.post(url, data={
            "file": self.csv_file,
            "geography_hierarchy": self.geography_hierarchy.id,
            "profile": self.profile.id,
            "name": "dataset-2",
        }, format='multipart')

        assert response.status_code == 201
        assert response.data["name"] == "dataset-2"
        assert Dataset.objects.filter(name="dataset-2").exists() == True
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True
        assert task.name == "Uploading data: dataset-2"

        dataset = Dataset.objects.get(id=response.data["id"])
        assert DatasetData.objects.filter(dataset=dataset).count() == 1
        data = DatasetData.objects.filter(dataset=dataset).first()
        assert data.data == {'test': 'x1', 'count': '11'}

    def test_successful_request_for_updating_dataset(self):

        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset-upload', args=(self.dataset.id,))
        
        response = client.post(url, data={
            "file": self.csv_file,
        }, format='multipart')

        assert response.status_code == 200
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True
        assert task.name == "Uploading data: dataset-1"
        
        assert self.dataset.id == response.data["id"]
        assert DatasetData.objects.filter(dataset=self.dataset).count() == 2
        data = DatasetData.objects.filter(dataset=self.dataset)
        assert data.first().data == {'test': 'y1', 'count': '22'}
        assert data.last().data == {'test': 'x1', 'count': '11'}


    def test_updating_dataset_with_overwrite(self):

        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset-upload', args=(self.dataset.id,))
        

        assert DatasetData.objects.filter(dataset=self.dataset).count() == 1
        data = DatasetData.objects.filter(dataset=self.dataset).first()
        assert data.data == {'test': 'y1', 'count': '22'}

        response = client.post(url, data={
            "file": self.csv_file,
            "overwrite": True
        }, format='multipart')

        assert response.status_code == 200
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True
        assert task.name == "Uploading data: dataset-1"

        assert self.dataset.id == response.data["id"]
        assert DatasetData.objects.filter(dataset=self.dataset).count() == 1
        data = DatasetData.objects.filter(dataset=self.dataset).first()
        assert data.data == {'test': 'x1', 'count': '11'}


    def test_updating_dataset_with_indicator_update(self):

        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)

        data = self.variable.indicatordata_set.all().first()
        assert data.data == {'groups': {}, 'subindicators': {'y1': 22.0}}
        assert self.dataset.datasetdata_set.count() == 1

        url = reverse('dataset-upload', args=(self.dataset.id,))
        response = client.post(url, data={
            "file": self.csv_file,
            "update": True
        }, format='multipart')

        assert response.status_code == 200
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True

        assert self.dataset.id == response.data["id"]
        data = self.variable.indicatordata_set.all().first()
        assert data.data == {'groups': {}, 'subindicators': {'x1': 11.0, 'y1': 22.0}}
        assert self.dataset.datasetdata_set.count() == 2


    def test_updating_dataset_with_indicator_update_and_overwrite(self):

        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)

        data = self.variable.indicatordata_set.all().first()
        assert data.data == {'groups': {}, 'subindicators': {'y1': 22.0}}
        assert self.dataset.datasetdata_set.count() == 1

        url = reverse('dataset-upload', args=(self.dataset.id,))
        response = client.post(url, data={
            "file": self.csv_file,
            "update": True,
            "overwrite": True
        }, format='multipart')

        assert response.status_code == 200
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True

        assert self.dataset.id == response.data["id"]
        data = self.variable.indicatordata_set.all().first()
        assert data.data == {'groups': {}, 'subindicators': {'x1': 11.0}}
        assert self.dataset.datasetdata_set.count() == 1
