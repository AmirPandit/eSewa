from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ChatRoom, RoomMembership, Message
from .serializers import ChatRoomSerializer, RoomMembershipSerializer, MessageSerializer
from accounts.serializers import CustomUserSerializer
from rest_framework.exceptions import PermissionDenied, ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def real_time_chat(instance, request):
    document_url = (
        request.build_absolute_uri(instance.document.url) if instance.document else None
    )
    message = instance.message if instance.message else None
    user_data = None
    receiver_data = None

    if instance.sender:
        user_data = CustomUserSerializer(
            instance.sender, context={"request": request}
        ).data

    channel_layer = get_channel_layer()

    message_data = {
        "type": "chat",
        "id": instance.id,
        "sender": user_data if instance.sender else None,
        "department": None,
        "receiver": receiver_data if instance.receiver else None,
        "document": document_url if instance.document else None,
        "message": message,
    }
    async_to_sync(channel_layer.group_send)(f"{instance.receiver.id}", message_data)

class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatRoom.objects.all().order_by('-created_at')
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='create', permission_classes=[permissions.IsAuthenticated])
    def create_room(self, request):
        serializer = ChatRoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()
            RoomMembership.objects.create(user=request.user, room=room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='join', permission_classes=[permissions.IsAuthenticated])
    def join_room(self, request, pk=None):
        room = self.get_object()
        membership, created = RoomMembership.objects.get_or_create(user=request.user, room=room)
        if created:
            return Response({"status": "joined"}, status=status.HTTP_200_OK)
        return Response({"status": "already joined"}, status=status.HTTP_400_BAD_REQUEST)
    
class RoomMembershipViewSet(viewsets.ModelViewSet):
    queryset = RoomMembership.objects.all()
    serializer_class = RoomMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        room_id = self.request.query_params.get('room_id')

        if not room_id:
            raise ValidationError({"message":"room_id parameter is required."})

        is_member = RoomMembership.objects.filter(user=user, room_id=room_id).exists()
        if not is_member:
            raise PermissionDenied({"message":"You are accessed to this room."})
        return self.queryset.filter(room_id=room_id)

    def perform_create(self, serializer):
        room = serializer.validated_data['room']
        user = self.request.user
        is_member = RoomMembership.objects.filter(user=user, room=room).exists()
        if not is_member:
            raise PermissionDenied({"message":"You are not subscribed to this room."})
        serializer.save(sender=user)
