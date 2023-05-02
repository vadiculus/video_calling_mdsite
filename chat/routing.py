from django.urls import re_path
from .consumers import PremiumConsumer, AdminConsumer

websocket_urlpatterns = [
    re_path(r"ws/premium_chat/(?P<chat_id>[A-Za-z0-9_-]+)", PremiumConsumer.as_asgi()),
    re_path(r"ws/admin_chat/(?P<chat_id>[A-Za-z0-9_-]+)", AdminConsumer.as_asgi()),
]