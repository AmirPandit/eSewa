import time
import socketio
from django.contrib.auth import get_user_model
from apps.chat.models import Message, ChatRoom, RoomMembership
from apps.chat.serializers import MessageSerializer
from channels.db import database_sync_to_async
import base64
import uuid
from django.core.files.base import ContentFile

sio_app = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True
)

User = get_user_model()

@sio_app.event
async def connect(sid, environ, auth):
    auth = environ.get('HTTP_AUTHORIZATION') or environ.get('QUERY_STRING', '').split('token=')[-1]
    if not auth:
        await sio_app.disconnect(sid)
        return False
    
    print(f"Client connected: {sid}")

@sio_app.event
async def disconnect(sid):
    print(f"Client disconnected")

@sio_app.event
async def send_message(sid, data):
    try:
        token = data.get('token')
        if not token:
            raise ValueError("Token missing")

        room_id = data.get('room_id')
        content = data.get('content')
        document = data.get('document')

        user = await get_user_from_token(token)
        if not user:
            await sio_app.emit('error', {'message': 'Invalid authentication'}, to=sid)
            return

        if not await check_membership(user, room_id):
            await sio_app.emit('error', {'message': 'You are not a member of this room'}, to=sid)
            return

        message = await save_message(user, room_id, content, document)
        serialized_message = serialize_message_for_socket(message)

        await sio_app.emit('receive_message', serialized_message, room=f"chat_{room_id}")

    except Exception as e:
        print(f"Error in send_message: {e}")
        await sio_app.emit('error', {'message': str(e)}, room=sid)

@sio_app.event
async def join_room(sid, data):
    room_id = data.get('room_id')
    await sio_app.enter_room(sid, f"chat_{room_id}")
    print(f"User joined room chat_{room_id}")

# Helper functions

@database_sync_to_async
def get_user_from_token(token):
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import InvalidToken

    try:
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        elif not isinstance(token, str):
            token = str(token)

        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except Exception as e:
        print(f"Token validation failed: {str(e)}")
        return None

@database_sync_to_async
def check_membership(user, room_id):
    is_member = RoomMembership.objects.filter(user=user, room_id=room_id).exists()
    print(f"User {user.id} membership in room {room_id}: {is_member}")
    return is_member
@database_sync_to_async
def save_message(user, room_id, content, document_base64):
    room = ChatRoom.objects.get(id=room_id)
    message = Message(sender=user, room=room, content=content)

    if document_base64:
        format, imgstr = document_base64.split(';base64,')
        ext = format.split('/')[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        message.document = ContentFile(base64.b64decode(imgstr), name=file_name)

    message.save()
    return message

# NEW - Fix UUID and datetime serialization
def serialize_message_for_socket(message):
    """Properly serialize message object for WebSocket emission."""
    return {
        'id': str(message.id) if message.id else f"ws-{int(time.time() * 1000)}",  # Ensuring the id is either from the message or generated
        'content': message.content,
        'sender': {
            'email': message.sender.email if hasattr(message.sender, 'email') else 'suyog@mail.com',
            'first_name': message.sender.first_name if hasattr(message.sender, 'first_name') else 'suyog',
            'last_name': message.sender.last_name if hasattr(message.sender, 'last_name') else 'luitel'
        },
        'timestamp': message.created_at.isoformat() if hasattr(message, 'created_at') and message.created_at else None
    }
