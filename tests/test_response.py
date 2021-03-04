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

        assert status == 500

    def test_view_exception(self):

        from django.test import Client

        client = Client()

        with pytest.raises(Exception):
            client.get('/api/v1/error_handler/test')

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
