from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.cache import SessionStore
from django.urls import reverse

import json

def notify_user(task):
    """
    Call back function after the task has been executed.
    This function gets passed the complete Task object as its argument.

    We get session key from kwargs of the task object and data of created object
    is passes through results value in task object.
    """
    url_base = "admin:datasets_%s_change"
    # Task results
    success = task.success
    if success:
        result = task.result
    else:
        error_msg = task.result
        obj = next(iter(task.args))
        result = {
            "name": obj.name,
            "id": obj.id,
            "model": obj.__class__.__name__.lower()
        }

    # Session variables
    session_key = session_key=task.kwargs["key"]
    session = Session.objects.filter(session_key=session_key).first()

    # message to show user
    url = reverse(url_base % result["model"], args=(result["id"],))

    if success:
        message = "Data has been processed for %s named %s. Please check it out on <a href='%s'>this link</a>" % (
            result["model"], result["name"], url
        )
    else:
        message = "Data processing failed for %s name %s. To restart process visit <a href='%s'>this link</a>" % (
            result["model"], result["name"], url
        )

    notification_type = "success" if success else "error"

    if session:
        decoded_session = custom_admin_notification(
            session.get_decoded(), notification_type, message
        )
        session.session_data = Session.objects.encode(decoded_session)
        session.save()


def custom_admin_notification(session, notification_type, message):
    """
    Function for implementing custom admin notifications.
    notifications are stored in session and show to user when user refreshes page.

    A valid session object must be passed to this function with notification type and message
    
    Type of notifications:
        * success
        * info
        * warning
        * error

    message is able to parse html so we can use html tags and classes while creating message
    """
    notification = {"type": notification_type, "message": message}
    messages = []

    if "notifications" in session:
        messages = session['notifications']
    messages.append(notification)
    session['notifications'] = messages

    return session





