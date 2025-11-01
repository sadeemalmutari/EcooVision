# home/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/video/', consumers.EnterCameraVideoStreamConsumer.as_asgi()),  # WebSocket endpoint
    path('ws/exit/', consumers.ExitCameraVideoStreamConsumer.as_asgi()),  # WebSocket endpoint
]
