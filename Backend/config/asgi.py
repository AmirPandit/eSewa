import os
import django
from django.core.asgi import get_asgi_application
from socketio import ASGIApp

# Set Django settings FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

# Import Socket.IO app AFTER Django setup
from apps.chat.socketio_server import sio_app  # Keep existing event handlers

# Create ASGI applications
django_asgi_app = get_asgi_application()
application = ASGIApp(sio_app, other_asgi_app=django_asgi_app, socketio_path='socket.io'
)