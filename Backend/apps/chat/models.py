import datetime
import uuid
from django.db import models
from django.conf import settings
from accounts.models import CustomUser
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel
from django.conf import settings



class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='created_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class RoomMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='room_memberships'
    )
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"


# class MessageCassendra(DjangoCassandraModel):
#     id = columns.UUID(primary_key=True, default=uuid.uuid4)
#     room = columns.UUID(required=True)
#     sender = columns.UUID(required=True)
#     content = columns.Text(required=True)
#     document = columns.Text()  # Store file path or URL
#     created_at = columns.DateTime(default=datetime.datetime.now)  # Renamed field

#     class Meta:
#         get_pk_field = 'id'
#         # table_name = 'messages'
#         # ordering = ['-timestamp/']

#     def __str__(self):
#         return f"{self.sender_id}: {self.content[:20]}..."

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}..."
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    