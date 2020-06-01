from django import template
import json

register = template.Library()

@register.filter(name='get_notifications')
def get_messages(session):
    messages = session.pop("notifications", [])

    task_list = session.get("task_list", [])
    for message in messages:
    	if "task_id" in message and task_list:
    		task_list.remove(message["task_id"])

    session["task_list"] = task_list
    return messages

@register.filter(name='get_task_list')
def get_task_list(session):
    task_list = session.get("task_list", [])
    if not task_list:
        return []
    return task_list


@register.filter(name='get_all')
def get_all(session):
    return session.session_key