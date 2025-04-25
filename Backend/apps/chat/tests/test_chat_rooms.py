import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.chat.models import ChatRoom

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='testuser', email='test@example.com', password='pass123'
    )

@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def chat_room(user):
    return ChatRoom.objects.create(name="Test Room", created_by=user)


# Test: Authenticated user can list chat rooms
def test_list_chat_rooms(auth_client, chat_room):
    url = reverse('chatroom-list')
    response = auth_client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert any(room["name"] == "Test Room" for room in response.data)


# Test: Authenticated user can create a chat room
def test_create_chat_room(auth_client):
    url = reverse('chatroom-create-room')  # from @action(url_path='create')
    data = {"name": "Created Room"}

    response = auth_client.post(url, data)

    assert response.status_code == 201
    assert ChatRoom.objects.filter(name="Created Room").exists()


# Test: Authenticated user can retrieve a single chat room
# def test_retrieve_chat_room(auth_client, chat_room):
#     url = reverse("chatroom-detail", args=[chat_room.id])
#     response = auth_client.get(url)

#     assert response.status_code == 200
#     assert response.data["name"] == chat_room.name
#     assert response.data["id"] == chat_room.id


# Test: Unauthenticated user is denied access
def test_auth_required_for_list():
    client = APIClient()
    url = reverse("chatroom-list")
    response = client.get(url)

    assert response.status_code == 401


# Optional: Test creating a chat room without a name (bad request)
def test_create_chat_room_missing_name(auth_client):
    url = reverse("chatroom-create-room")
    response = auth_client.post(url, {})  # No name field provided

    assert response.status_code == 400
    assert "name" in response.data
