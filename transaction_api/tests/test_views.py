import pytest
from transaction_api.models import *
from mixer.backend.django import mixer
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from transaction_api.helpers import *
pytestmark = pytest.mark.django_db


class TestAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_create_works(self):
        input_data = {
            "username": "ugokingsl",
            "email": "ug@gmail.com",
            "last_transaction_time": now1,
            "date_created": now1,
        }
        url = reverse("register_api")
        # call the url
        response = self.client.post(url, data=input_data)
        assert response.json() != None
        assert response.status_code == 200
