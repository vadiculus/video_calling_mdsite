from django import template

register = template.Library()

@register.filter
def get_interlocutor(chat, user):
    return chat.participants.exclude(id=user.id).first().full_name