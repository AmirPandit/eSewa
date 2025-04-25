from django.contrib import admin
from .models import ChatRoom, RoomMembership, Message
# Register your models here.

admin.site.register(ChatRoom)
admin.site.register(RoomMembership)
admin.site.register(Message)


