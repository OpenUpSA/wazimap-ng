import pytest
import json
from test_plus import APITestCase

from wazimap_ng.utils import error_handler
from rest_framework import status


@pytest.mark.django_db
class TestErrorResponseData(APITestCase):

    def test_error_json(self):
        request = self.get('/foo/bar')

        response = error_handler(request)
        content_type = response['Content-Type']

        data = json.loads(response.content)

        assert content_type == 'application/json'
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert data['error']['type'] == 'server_error'

    def test_error_format(self):
        expected_response = {
            'error': {
                "message": {
                    "detail": 'Not found.'
                },
                'type': 'not_found',
                'code': status.HTTP_404_NOT_FOUND
            }
        }

        response = self.get('dataset-detail', pk=234)

        data = json.loads(response.content)

        assert data == expected_response
