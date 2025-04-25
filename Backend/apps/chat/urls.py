from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, RoomMembershipViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')
router.register(r'memberships', RoomMembershipViewSet, basename='roommembership')
router.register(r'messages', MessageViewSet, basename='message')
urlpatterns = [
    path('', include(router.urls)),
]
