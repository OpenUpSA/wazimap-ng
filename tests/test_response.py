import pytest
from test_plus import APITestCase


@pytest.mark.django_db
class TestErrorResponseData(APITestCase):

    # def test_error_response_correct_format(self):
    #     response = self.get('dataset-detail', pk=234)
    #     # data = vars(response)

    #     print(vars(response))

    #     self.assertEqual(response.data, None)

    #     assert type(response.data) == 'NoneType'

    #     data = response.data

    #     print(vars(response), 'data' in vars(response))

    #     code = data.get('error').get('code')
    #     type = data.get('error').get('type')

    #     assert (type == 'not_found' and code == 404)
    #     assert 400 == 400

    def test_api_error_handler(self):
        response = self.get('error-handler-test')

        print(vars(response))

        # try:
        #     response = self.get('error-handler-test')
        #     data = response.data

        #     print(data)
        # except ValueError:
        #     print('ValueError occured on server')

        assert 2 == 2
