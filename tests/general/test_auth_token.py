from test_plus import APITestCase
import pytest

from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from tests.datasets.factories import DatasetFactory



class TestAuthToken(APITestCase):
        

    def test_auth_token_generation(self):
        user1 = self.make_user('user1')

        response = self.post('/api/v1/api-token-auth/', data={
            'username': 'user1',
            'password': 'password',
        }, extra={'format': 'json'})

        self.assert_http_200_ok()
        assert "token" in response.data

        token, created = Token.objects.get_or_create(user=user1)
        assert created == False
        assert token.key == response.data["token"]
