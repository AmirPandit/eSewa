import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _make_user(**kwargs):
        return CustomUser.objects.create_user(
            username=kwargs.get("username", "testuser"),
            email=kwargs.get("email", "test@example.com"),
            password=kwargs.get("password", "strongpassword"),
            first_name=kwargs.get("first_name", "Test"),
            last_name=kwargs.get("last_name", "User"),
            role=kwargs.get("role", "user")
        )
    return _make_user


def test_user_model(create_user):
    user = create_user()
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("strongpassword")
    assert user.get_full_name() == "Test User"


def test_register_user_as_admin(api_client, django_user_model):
    admin = django_user_model.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass"
    )
    api_client.force_authenticate(user=admin)

    url = reverse("register")
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User",
        "role": "user"
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(email="newuser@example.com").exists()


def test_login_valid_credentials(api_client, create_user):
    create_user()
    url = reverse("login")
    payload = {"email": "test@example.com", "password": "strongpassword"}

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data["message"]
    assert "refresh" in response.data["message"]


def test_login_invalid_credentials(api_client):
    url = reverse("login")
    payload = {"email": "wrong@example.com", "password": "wrongpass"}

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_logout_valid_token(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    payload = {"refresh_token": str(refresh)}

    url = reverse("logout")
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_205_RESET_CONTENT or response.status_code == status.HTTP_200_OK


def test_logout_invalid_token(api_client):
    url = reverse("logout")
    payload = {"refresh_token": "invalidtoken"}

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED or response.status_code == status.HTTP_400_BAD_REQUEST
