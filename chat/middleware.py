from chat.models import PremiumChatMessage, PremiumChat, AdminChatMessage, AdminChat
from django.db.models import Prefetch, Q


class PremiumMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            chats = PremiumChat.objects.prefetch_related(
                'participants', Prefetch('premium_chat_messages',PremiumChatMessage.objects.filter(~Q(author=request.user) &
                                                                                                   Q(read=False))))\
                .filter(participants=request.user)

            request.new_premium_messages_count = 0

            for chat in chats:
                request.new_premium_messages_count += chat.premium_chat_messages.count()
        response = self.get_response(request, *args, **kwargs)

        return response

class AdminMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            chats = AdminChat.objects.prefetch_related(
                'participants', Prefetch('admin_chat_messages',AdminChatMessage.objects.filter(~Q(author=request.user) &
                                                                                                   Q(read=False))))\
                .filter(participants=request.user)

            request.new_admin_messages_count = 0

            for chat in chats:
                request.new_admin_messages_count += chat.admin_chat_messages.count()
        response = self.get_response(request, *args, **kwargs)

        return response