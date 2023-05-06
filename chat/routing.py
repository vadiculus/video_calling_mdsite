from django.urls import re_path
from .consumers import PremiumConsumer, AdminConsumer, CallConsumer

websocket_urlpatterns = [
    re_path(r"ws/premium_chat/(?P<chat_id>[A-Za-z0-9_-]+)", PremiumConsumer.as_asgi()),
    re_path(r"ws/admin_chat/(?P<chat_id>[A-Za-z0-9_-]+)", AdminConsumer.as_asgi()),
    re_path(r"ws/ordered_call/(?P<call_id>[A-Za-z0-9_-]+)", CallConsumer.as_asgi()),
]