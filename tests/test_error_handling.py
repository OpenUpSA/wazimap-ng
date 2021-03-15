from test_plus import APITestCase

from rest_framework import status


class TestErrorResponseData(APITestCase):

    def test_404_error_format(self):
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

        assert response.data == expected_response

    def test_custom_exception(self):
        response = self.get('/api/v1/datasets/3452/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['error']['type'] == 'not_found'
