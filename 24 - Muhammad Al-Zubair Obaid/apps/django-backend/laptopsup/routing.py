from django.urls import re_path
from api import consumers

websocket_urlpatterns = [
    re_path(r'ws/support/$', consumers.SupportChatConsumer.as_asgi()),
]