from django.contrib.sessions.models import Session
from django.urls import reverse

import json

class Notify:

    generic_messages = {
        "delete" : {
            "success": "Data deleted for %s",
            "error": "Error in deleting data for %s",
        },
        "upload" : {
            "success": "Imported File successfully for %s",
            "error": "Error in uploading file for %s.",
        }
    }

    upload_message = {
        "success": "Imported File successfully for model %s with name %s. For more details check : <a href='%s'>Click Here</a>",
        "error": "Error in uploading file for model %s with name %s. For more details check : <a href='%s'>Click Here</a>",
    }

    @classmethod
    def get_nofitification_details(self, notification_type, obj, task_type):

        func_name = "get_%s_messages" % (task_type)
        notification_message = getattr(self, func_name, "get_generic_message")
        message = notification_message(notification_type, obj)
        return message

    @classmethod
    def get_upload_messages(self, notification_type, obj):
        """
        Get message for data upload.
        """
        model = obj.__class__.__name__.lower()
        admin_url = reverse(
            'admin:%s_%s_change' % (obj._meta.app_label,  obj._meta.model_name),  args=[obj.id]
        )
        return self.upload_message[notification_type] % (model, obj, admin_url)

    @classmethod
    def get_generic_message(self, notification_type, obj, task_type):
        """
        Get Generic message according to notification type.
        """
        message = self.generic_messages[task_type][notification_type]
        return message % obj

def process_task_info(task):
    """
    Process task
    """
    notify = task.kwargs.get("notify", False)
    assign_task = task.kwargs.get("assign", False)
    obj = next(iter(task.args))

    if assign_task:
        obj.task = task
        obj.save()

    if notify:
        notification_type = "success" if task.success else "error"

        session_key = task.kwargs.get("key", False)
        task_type = task.kwargs.get("type", False)

        # Get message
        notify = Notify()
        message = notify.get_nofitification_details(notification_type, obj, task_type)

        # Add message to user
        notify_user(notification_type, session_key, message)

def notify_user(notification_type, session_key, message):
    """
    Call back function after the task has been executed.
    This function gets passed the complete Task object as its argument.

    We get session key from kwargs of the task object and data of created object
    is passes through results value in task object.
    """
    session = Session.objects.filter(session_key=session_key).first()

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