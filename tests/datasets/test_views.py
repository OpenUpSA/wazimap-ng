import csv

from io import StringIO
from test_plus import APITestCase

from wazimap_ng.datasets.models import DatasetData, Dataset

from tests.profile.factories import ProfileFactory
from tests.datasets.factories import (
    GeographyFactory, GeographyHierarchyFactory, DatasetFactory,
    DatasetDataFactory, IndicatorFactory, IndicatorDataFactory,
    VersionFactory,
)
from tests.boundaries.factories import GeographyBoundaryFactory

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
        self.version = VersionFactory()
        geography = GeographyFactory(code="ZA")
        GeographyBoundaryFactory(geography=geography, version=self.version)
        self.geography_hierarchy = GeographyHierarchyFactory(
            root_geography=geography,
            configuration={
                "default_version": self.version.name,
            }
        )
        self.profile = ProfileFactory(geography_hierarchy=self.geography_hierarchy)
        self.group = Group.objects.create(name=self.profile.name)

        # Dataset specific data
        self.dataset = DatasetFactory(
            name="dataset-1", profile=self.profile, groups=["test"],
            version=self.version
        )
        DatasetDataFactory(
            dataset=self.dataset, geography=geography,
            data={'test': 'y1', 'count': '22'}
        )

        # Indicator specific data
        self.variable = IndicatorFactory(dataset=self.dataset, name="test-indicator")
        IndicatorDataFactory(
            indicator=self.variable, geography=geography,
            data=[{'test': 'y1', 'count': '22'}]
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

        qualitative_content = [
            ["Geography", "Contents"],
            ["ZA", "This is an example"]
        ]

        content = self.create_csv_file(qualitative_content).encode("utf-8")
        self.qualitative_csv_file = SimpleUploadedFile(
            name="qualitative.csv", content=content, content_type='text/csv'
        )

        self.qualitative_dataset = DatasetFactory(
            name="dataset-2", profile=self.profile, groups=["Contents"],
            version=self.version, content_type="qualitative"
        )
        DatasetDataFactory(
            dataset=self.qualitative_dataset, geography=geography,
            data={'contents': 'Example'}
        )

        # Indicator specific data
        self.qualitative_variable = IndicatorFactory(
            dataset=self.qualitative_dataset, name="test-indicator"
        )
        IndicatorDataFactory(
            indicator=self.qualitative_variable, geography=geography,
            data=[{'contents': 'Example'}]
        )


    def test_anonymous_user_request_for_new_dataset(self):
        response = self.post("dataset", data={
            "file": self.csv_file,
            "profile": self.profile.id,
            "name": "dataset-2",
            "version": self.version.id
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
            "profile": self.profile.id,
            "name": "dataset-2",
            "version": self.version.id
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

    def test_invalid_file_for_new_dataset(self):
        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        data = [["test"], ["x1"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
                name="invalid.csv", content=content, content_type='text/csv'
        )
        response = client.post(url, data={
            "file": csv_file,
            "profile": self.profile.id,
            "name": "dataset-2",
            "version": self.version.id
        }, format='multipart')

        assert response.status_code == 400
        assert (
            response.data["detail"] ==
            "Invalid File passed. We were not able to find Required header : Geography "
        )

        data = [["Geography", "test"], ["ZA", "x1"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
                name="invalid.csv", content=content, content_type='text/csv'
        )
        response = client.post(url, data={
            "file": csv_file,
            "profile": self.profile.id,
            "name": "dataset-2",
            "version": self.version.id
        }, format='multipart')

        assert response.status_code == 400
        assert (
            response.data["detail"] ==
            "Invalid File passed. We were not able to find Required header : Count "
        )

    def test_validation_for_creating_dataset(self):

        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        response = client.post(url, data={
            "file": self.csv_file,
            "profile": self.profile.id,
        }, format='multipart')

        assert response.status_code == 400
        assert str(response.data["name"][0]) == "This field is required."
        assert str(response.data["version"][0]) == "This field is required."

    def test_successful_request_for_new_dataset(self):
        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        assert Dataset.objects.filter(name="dataset-3").exists() == False

        response = client.post(url, data={
            "file": self.csv_file,
            "profile": self.profile.id,
            "name": "dataset-3",
            "version": self.version.id
        }, format='multipart')

        assert response.status_code == 201
        assert response.data["name"] == "dataset-3"
        assert Dataset.objects.filter(name="dataset-3").exists() == True
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True
        assert task.name == "Uploading data: dataset-3"

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
        assert data.data == [{'test': 'y1', 'count': '22'}]
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
        assert data.data == [
            {'test': 'y1', 'count': '22'},
            {'test': 'x1', 'count': '11'}
        ]
        assert self.dataset.datasetdata_set.count() == 2

    def test_updating_dataset_with_indicator_update_and_overwrite(self):

        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)

        data = self.variable.indicatordata_set.all().first()
        assert data.data == [{'test': 'y1', 'count': '22'}]
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
        assert data.data == [{'test': 'x1', 'count': '11'}]
        assert self.dataset.datasetdata_set.count() == 1

    def test_invalid_file_for_qualitative_dataset_upload(self):
        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        data = [["test"], ["x1"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
                name="invalid.csv", content=content, content_type='text/csv'
        )
        response = client.post(url, data={
            "file": csv_file,
            "profile": self.profile.id,
            "name": "dataset-2",
            "version": self.version.id,
            "content_type": "qualitative"
        }, format='multipart')

        assert response.status_code == 400
        assert (
            response.data["detail"] ==
            "Invalid File passed. We were not able to find Required header : Geography "
        )

        data = [["Geography", "test"], ["ZA", "x1"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
                name="invalid.csv", content=content, content_type='text/csv'
        )
        response = client.post(url, data={
            "file": csv_file,
            "profile": self.profile.id,
            "name": "dataset-2",
            "version": self.version.id,
            "content_type": "qualitative"
        }, format='multipart')

        assert response.status_code == 400
        assert (
            response.data["detail"] ==
            "Invalid File passed. We were not able to find Required header : Contents "
        )

    def test_request_for_adding_qualitative_dataset(self):
        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)
        url = reverse('dataset')

        assert Dataset.objects.filter(name="dataset-3").exists() == False

        response = client.post(url, data={
            "file": self.qualitative_csv_file,
            "profile": self.profile.id,
            "name": "dataset-3",
            "version": self.version.id,
            "content_type": "qualitative"
        }, format='multipart')

        assert response.status_code == 201
        assert response.data["name"] == "dataset-3"
        assert Dataset.objects.filter(name="dataset-3").exists() == True
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True
        assert task.name == "Uploading data: dataset-3"

        dataset = Dataset.objects.get(id=response.data["id"])
        assert DatasetData.objects.filter(dataset=dataset).count() == 1
        data = DatasetData.objects.filter(dataset=dataset).first()
        assert data.data == {'contents': 'This is an example'}

    def test_updating_qualitative_dataset(self):
        user1 = self.make_user("user1")
        self.group.user_set.add(user1)
        token, created = Token.objects.get_or_create(user=user1)
        client = APIClient()
        client.force_authenticate(user=user1, token=token)

        url = reverse('dataset-upload', args=(self.qualitative_dataset.id,))
        response = client.post(url, data={
            "file": self.qualitative_csv_file,
            "update": True,
            "overwrite": True
        }, format='multipart')
        assert response.status_code == 200
        self.assertTrue("upload_task_id" in response.data)

        task = fetch(response.data["upload_task_id"])
        assert task.success == True
        assert self.qualitative_dataset.id == response.data["id"]

        data = self.qualitative_variable.indicatordata_set.first()
        assert data.data == [
            {'contents': 'This is an example'},
        ]
        assert self.qualitative_dataset.datasetdata_set.count() == 1


class TestVersionData(APITestCase):
    def setUp(self):
        self.version1 = VersionFactory()
        self.version2 = VersionFactory()
        hierarchy = GeographyHierarchyFactory(
            configuration={
                "default_version": self.version1.name,
            }
        )
        self.profile = ProfileFactory(geography_hierarchy=hierarchy)

    def test_version_list_view(self):
        response = self.get(
            'versions', extra={'format': 'json'}
        )

        assert response.status_code == 200
        data = response.data
        assert data["count"] == 2

    def test_version_detail_view(self):
        response = self.get(
            'version', pk=self.version1.id,
            extra={'format': 'json'}
        )

        assert response.status_code == 200
        data = response.data
        assert data["id"] == self.version1.id

    def test_version_by_profile_view(self):
        response = self.get(
            'versions-by-profile', profile_id=self.profile.id,
            extra={'format': 'json'}
        )

        assert response.status_code == 200
        data = response.data
        assert data["count"] == 1
        assert data["results"][0]["id"] == self.version1.id
