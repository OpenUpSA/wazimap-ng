from django.contrib.sessions.models import Session
from django.urls import reverse

import json

def get_notification_details(success, model, name, idx):
    """
    Notification details according to the model.
    """
    admin_url_base = "admin:datasets_%s_%s"

    messages_according_to_model = {
        "indicator" : {
            "success": "Data has been processed for %s named %s. Please check it out on <a href='%s'>this link</a>" %(
                model, name, reverse(admin_url_base % (model, "change"), args=(idx,))
            ),
            "error": "Data processing failed for %s name %s. To restart process visit <a href='%s'>this link</a>" %(
                model, name, reverse(admin_url_base % (model, "change"), args=(idx,))
            ),
        },
        "datasetfile" : {
            "success": "Dataset Imported successfully for %s" % name,
            "error": "Error in uploading file %s. Re-upload file at <a href='%s'>this link</a>" % (
                name, reverse(admin_url_base % (model, "add"))
            ),
        }
    }

    return messages_according_to_model[model][success]

def get_message_according_type(task, task_type, notification_type):
    """
    return message according to type of task.
    Use for generic things like data created or deleted
    """
    messages = {
            "delete" : {
                "success": "Data deleted for %s"  % list(task.args)[1],
                "error": "Error in deleting data for %s"  % list(task.args)[1],
            },
            "file_upload" : {
                "success": "Imported File successfully for %s" % list(task.args)[1],
                "error": "Error in uploading file for %s." % list(task.args)[1],
            }
        }

    return messages[task_type][notification_type]

def notify_user(task):
    """
    Call back function after the task has been executed.
    This function gets passed the complete Task object as its argument.

    We get session key from kwargs of the task object and data of created object
    is passes through results value in task object.
    """
    success = task.success
    notification_type = "success" if success else "error"

    if "type" in task.kwargs:

        message = get_message_according_type(task, task.kwargs["type"], notification_type)
    else:
        # Task results
        if success:
            result = task.result

        else:
            obj = next(iter(task.args))
            result = {
                "name": getattr(obj, name, False) or obj.title,
                "id": obj.id,
                "model": obj.__class__.__name__.lower()
            }

        message = get_notification_details(
            notification_type, result["model"], result["name"], result["id"]
        )
    # Session variables
    session_key = session_key=task.kwargs["key"]
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