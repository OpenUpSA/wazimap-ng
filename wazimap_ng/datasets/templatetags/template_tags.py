from django import template
import json

register = template.Library()

@register.filter(name='get_notifications')
def get_messages(session):
    messages = session.pop("notifications", [])
    return messages