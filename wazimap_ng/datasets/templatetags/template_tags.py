import logging

from django import template
import json

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter(name='get_notifications')
def get_messages(session):
    messages = session.pop("notifications", [])

    task_list = session.get("task_list", [])
    for message in messages:
        try:
            task_id = message["task_id"]
            task_list.remove(task_id)
        except (ValueError, KeyError) as e:
            logger.info("Error removed a message from the task list. Probably missing.")

    session["task_list"] = task_list
    return messages

@register.filter(name='get_task_list')
def get_task_list(session):
    task_list = session.get("task_list", [])
    if not task_list:
        return []
    return task_list