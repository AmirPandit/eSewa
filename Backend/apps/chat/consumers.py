import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.chat.models import ChatRoom
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["group_name"]
        self.room_group_name = f'chat_{self.room_name}'

        if not await self.room_exists(self.room_name):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat(self, event):
        try:
            document = event["document"]
        except KeyError:
            document = None

        sender = event["sender"]
        id = event["id"]
        message = event["message"]

        await self.send(
            text_data=json.dumps(
                {
                    "id": id,
                    "sender": sender,
                    "document": document if document else None,
                    "message": message,
                }
            )
        )

    @database_sync_to_async
    def room_exists(self, room_name):
        '''
        Check if the room exists in the database.
        
        Args:
            room_name (str): The name of the chat room to check.
        returns:
            bool: True if the room exists, False otherwise.
        '''
        try:
            room = ChatRoom.objects.get(name=room_name)
            return True
        except ChatRoom.DoesNotExist:
            return False
