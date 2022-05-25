import pytest
import csv
from io import StringIO

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestCategoryAdmin:
    def create_csv_file(self, data):
        csvfile = StringIO()
        csv.writer(csvfile).writerows(data)
        return csvfile.getvalue()

    def test_uploading_file_with_no_longitude(self, client, superuser):
        """
        Test validation for uploading a file without Longitude
        """
        client.force_login(user=superuser)
        url = reverse("admin:points_category_add")
        data = [["name", "latitude", "id", "status", "status last updated", "class", "volume",
                 "discharges into"],
                ["Molopo Millitary Base WWTW", "-25.7632126977988", "S_2688", "Bad",
                 "16th March 2022", "Class E", "700 Kl/day", "Unknown"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
            name="test.csv", content=content, content_type='text/csv'
        )
        form_data = {
            'import_collection': csv_file,
        }
        res = client.post(url, form_data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form
        errors = form.errors

        assert errors["__all__"].data[
                   0].message == 'Invalid File passed. We were not able to find Required header : Longitude'

    def test_uploading_file_with_no_latitude(self, client, superuser):
        """
        Test validation for uploading a file without Latitude
        """
        client.force_login(user=superuser)
        url = reverse("admin:points_category_add")
        data = [["name", "longitude", "id", "status", "status last updated", "class", "volume",
                 "discharges into"],
                ["Molopo Millitary Base WWTW", "25.6223485469818", "S_2688", "Bad",
                 "16th March 2022", "Class E", "700 Kl/day", "Unknown"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
            name="test.csv", content=content, content_type='text/csv'
        )
        form_data = {
            'import_collection': csv_file,
        }
        res = client.post(url, form_data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form
        errors = form.errors

        assert errors["__all__"].data[
                   0].message == 'Invalid File passed. We were not able to find Required header : Latitude'

    def test_uploading_file_with_no_name(self, client, superuser):
        """
        Test validation for uploading a file without Name
        """
        client.force_login(user=superuser)
        url = reverse("admin:points_category_add")
        data = [["longitude", "latitude", "id", "status", "status last updated", "class", "volume",
                 "discharges into"],
                ["25.6223485469818", "-25.7632126977988", "S_2688", "Bad",
                 "16th March 2022", "Class E", "700 Kl/day", "Unknown"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
            name="test.csv", content=content, content_type='text/csv'
        )
        form_data = {
            'import_collection': csv_file,
        }
        res = client.post(url, form_data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form
        errors = form.errors

        assert errors["__all__"].data[
                   0].message == 'Invalid File passed. We were not able to find Required header : Name'

    def test_uploading_file_missing_non_required_column(self, client, superuser):
        """
        Test validation for uploading a file without id. There should be no validation errors
        """
        client.force_login(user=superuser)
        url = reverse("admin:points_category_add")
        data = [["name", "longitude", "latitude", "status", "status last updated", "class", "volume",
                 "discharges into"],
                ["Molopo Millitary Base WWTW", "25.6223485469818", "-25.7632126977988", "Bad",
                 "16th March 2022", "Class E", "700 Kl/day", "Unknown"]]
        content = self.create_csv_file(data).encode("utf-8")
        csv_file = SimpleUploadedFile(
            name="test.csv", content=content, content_type='text/csv'
        )
        form_data = {
            'import_collection': csv_file,
        }
        res = client.post(url, form_data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form
        errors = form.errors

        assert (('__all__' in errors) is False)
