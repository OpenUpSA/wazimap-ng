import pytest
import json
from test_plus import APITestCase

from wazimap_ng.utils import error_handler

from django.test import RequestFactory


@pytest.mark.django_db
class TestErrorResponseData(APITestCase):

    def test_error_handler(self):
        factory = RequestFactory()
        request = factory.get('/api/v1/jkhj')

        response = error_handler(request)
        status = response.status_code
        content_type = response['Content-Type']

        assert status == 500 and content_type == 'application/json'

    def test_error_not_json(self):
        factory = RequestFactory()
        request = factory.get('/foo/bar')

        response = error_handler(request)
        content_type = response['Content-Type']

        assert content_type != 'application/json'

    def test_error_format(self):
        from wazimap_ng.renderer import CustomRenderer

        expected_response = {
            'error': {
                "message": {
                    "detail": 'Not Found'
                },
                'type': None,
                'code': 404
            }
        }

        response = self.get('dataset-detail', pk=234)

        renderer = CustomRenderer()

        renderer_context = dict(response=response)

        data = renderer.render(
            data=dict(detail='Not Found'),
            renderer_context=renderer_context).decode('utf-8')

        data = json.loads(data)

        assert data == expected_response
