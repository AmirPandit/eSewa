from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ChatRoom
from .serializers import ChatRoomSerializer
from accounts.serializers import CustomUserSerializer
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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    