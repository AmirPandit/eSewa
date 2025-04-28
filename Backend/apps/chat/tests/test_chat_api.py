# test_chat_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.chat.models import ChatRoom, RoomMembership, Message
from accounts.models import CustomUser

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return CustomUser.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def another_user():
    return CustomUser.objects.create_user(
        email='another@example.com',
        username='anotheruser',
        password='testpass123'
    )

@pytest.fixture
def test_room(test_user):
    room = ChatRoom.objects.create(name="Test Room", created_by=test_user)
    RoomMembership.objects.create(user=test_user, room=room)
    return room

@pytest.mark.django_db
class TestChatRoomAPI:
    def test_create_room(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('chatroom-create')
        data = {'name': 'New Room'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert ChatRoom.objects.count() == 1
        assert RoomMembership.objects.filter(user=test_user).count() == 1

    def test_join_room(self, api_client, test_user, test_room):
        api_client.force_authenticate(user=test_user)
        url = reverse('chatroom-join', kwargs={'pk': test_room.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'already joined'

    def test_join_room_new_user(self, api_client, another_user, test_room):
        api_client.force_authenticate(user=another_user)
        url = reverse('chatroom-join', kwargs={'pk': test_room.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'joined'
        assert RoomMembership.objects.filter(user=another_user).count() == 1

@pytest.mark.django_db
class TestRoomMembershipAPI:
    def test_list_memberships(self, api_client, test_user, test_room):
        api_client.force_authenticate(user=test_user)
        url = reverse('roommembership-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_unsubscribe(self, api_client, test_user, test_room):
        api_client.force_authenticate(user=test_user)
        url = reverse('roommembership-unsubscribe', kwargs={'pk': test_room.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not RoomMembership.objects.filter(user=test_user).exists()

@pytest.mark.django_db
class TestMessageAPI:
    def test_send_message(self, api_client, test_user, test_room):
        api_client.force_authenticate(user=test_user)
        url = reverse('message-list')
        data = {'room': test_room.id, 'content': 'Hello world'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Message.objects.count() == 1

    def test_get_messages(self, api_client, test_user, test_room):
        # Create a test message
        Message.objects.create(
            room=test_room,
            sender=test_user,
            content='Test message'
        )
        
        api_client.force_authenticate(user=test_user)
        url = reverse('message-list') + f'?room_id={test_room.id}'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['content'] == 'Test message'

    def test_send_message_not_member(self, api_client, another_user, test_room):
        api_client.force_authenticate(user=another_user)
        url = reverse('message-list')
        data = {'room': test_room.id, 'content': 'Hello world'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN