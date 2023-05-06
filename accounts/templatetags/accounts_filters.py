from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def get_local_time(visiting_time, user):
    return timezone.localtime(visiting_time, timezone=user.timezone)