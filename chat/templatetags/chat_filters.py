from django import template
from django.db.models import Q

register = template.Library()

@register.filter
def get_interlocutor(chat, user):
    return chat.participants.exclude(id=user.id).first()

@register.filter
def get_interlocutor_photo(chat, user):
    interlocutor = chat.participants.exclude(id=user.id).first()
    return interlocutor.photo.url

@register.filter
def not_read_admin_messages(chat, user):
    return chat.admin_chat_messages.filter(~Q(author=user) & Q(read=False)).count()

@register.filter
def not_read_premium_messages(chat, user):
    return chat.premium_chat_messages.filter(~Q(author=user) & Q(read=False)).count()

