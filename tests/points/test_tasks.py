import csv
import codecs
from io import BytesIO

import pytest

from tests.points.factories import (
    CategoryFactory,
    CoordinateFileFactory,
)
from wazimap_ng.points.tasks import process_uploaded_file
from wazimap_ng.points.models import CoordinateFile, Location


def generate_file(data, header, encoding="utf8"):
    buffer = BytesIO()
    StreamWriter = codecs.getwriter(encoding)
    text_buffer = StreamWriter(buffer)

    writer = csv.writer(text_buffer)
    writer.writerow(header)
    writer.writerows(data)

    buffer.seek(0)
    return buffer


def create_point_file(csv_data, header, encoding):
    buffer = generate_file(csv_data, header, encoding)
    return CoordinateFileFactory(document__data=buffer.read())


good_data = [
    (123.45678, 36.84302, "PointFile1"),
    (150.12345, 30.12345, "PointFile2"),
]

data_with_different_case = [
    (123.45678, 36.84302, "PointFile1"),
    (150.12345, 30.12345, "PointFile2"),
]

data_with_different_encodings = [
    (123.45678, 36.84302, "PointFile1’"),
    (150.12345, 30.12345, "€ŠPointFile1®®"),
]

good_header = ["longitude", "latitude", "name"]

to_be_fixed_header = [" longitude ", " latitude", "name "]


@pytest.fixture(
    params=[
        (good_data, good_header, "utf8"),
        (good_data, to_be_fixed_header, "utf8"),
        (data_with_different_case, good_header, "utf8"),
        (data_with_different_encodings, good_header, "Windows-1252"),
    ]
)
def data(request):
    return request.param


@pytest.mark.django_db
class TestUploadFile:
    def test_process_upload_file(self, data):
        csv_data, header, encoding = data
        point_file = create_point_file(csv_data, header, encoding)

        category = CategoryFactory()
        process_uploaded_file(point_file, category)
        point_file_data = CoordinateFile.objects.all()
        location_data = Location.objects.all()

        assert len(point_file_data) == 1
        assert len(location_data) == len(csv_data)

        for dd, ed in zip(location_data, csv_data):
            assert pytest.approx(dd.coordinates.x) == ed[0]
            assert pytest.approx(dd.coordinates.y) == ed[1]
