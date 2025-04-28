# test_auth_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }

@pytest.mark.django_db
class TestAuthAPI:
    def test_register(self, api_client, user_data):
        url = reverse('register')
        response = api_client.post(url, user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1

    def test_login(self, api_client, user_data):
        # First register
        User.objects.create_user(**user_data)
        
        url = reverse('login')
        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        response = api_client.post(url, login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_protected_endpoint(self, api_client, user_data):
        # Register and login
        User.objects.create_user(**user_data)
        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        login_response = api_client.post(reverse('login'), login_data)
        response = login_response
        
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_login(self, api_client, user_data):
        User.objects.create_user(**user_data)
        
        url = reverse('login')
        response = api_client.post(url, {
            'email': user_data['email'],
            'password': 'wrongpassword'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST