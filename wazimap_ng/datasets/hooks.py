import logging

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.urls import reverse

from django_q.tasks import async_task
from .models import Indicator

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from wazimap_ng.config.common import STAFF_EMAIL_ADDRESS

import json

logger = logging.getLogger(__name__)

class Notify:

    generic_messages = {
        "delete" : {
            "success": "Data deleted for %s - %s",
            "error": "Error in deleting data for %s",
        },
        "upload" : {
            "success": "Imported File successfully for %s",
            "error": "Error in uploading file for %s.",
        },

        "data_extraction" : {
            "success": "Data extraction successful for %s",
            "error": "Data extraction failed for %s.",
        }
    }

    upload_message = {
        "success": "Imported File successfully for model %s with name %s. For more details check : <a href='%s'>Click Here</a>",
        "error": "Error in uploading file for model %s with name %s. For more details check : <a href='%s'>Click Here</a>",
    }


    @classmethod
    def get_nofitification_details(self, notification_type, obj, task_type, results=None):

        func_name = "get_%s_messages" % (task_type)
        notification_message = getattr(self, func_name, self.get_generic_message)
        message = notification_message(notification_type, obj, task_type, results)
        return message

    @classmethod
    def get_upload_messages(self, notification_type, obj, task_type=None, results=None):
        """
        Get message for data upload.
        """
        model = obj.__class__.__name__.lower()
        obj_id = obj.id
        model_name = obj._meta.model_name

        if notification_type == "success":
            if obj._meta.model_name == "datasetfile":
                model_name = "dataset"
                obj_id = results.get("dataset_id", None)

            if obj._meta.model_name == "coordinatefile":
                model_name = "category"
                obj_id = results.get("category_id", None)
        else:
            model_name = obj._meta.model_name
            obj_id = obj.id

        admin_url = reverse(
            'admin:%s_%s_change' % (obj._meta.app_label,  model_name),  args=[obj_id]
        )
        return self.upload_message[notification_type] % (model, obj, admin_url)

    @classmethod
    def get_generic_message(self, notification_type, obj, task_type, results):
        """
        Get Generic message according to notification type.
        """
        name = results["data"]
        if isinstance(name, list) and len(name):
            if len(name) > 1:
                name = f"{name[0]} and {len(name) - 1} others."
            else:
                name = name[0]

        message = self.generic_messages[task_type][notification_type]
        return message % (results["object_name"], name)

def process_task_info(task):
    """
    Process task
    """
    notify = task.kwargs.get("notify", False)
    assign_task = task.kwargs.get("assign", False)
    update_indicators = task.kwargs.get("update_indicators", False)
    session_key = task.kwargs.get("key", False)
    email_notification_on_failure_only = task.kwargs.get(
        "email_on_failure", True
    )
    user_id = task.kwargs.get("user_id", False)
    results = task.result or {}
    task_type = task.kwargs.get("type", False)
    obj = next(iter(task.args))

    if assign_task:
        obj.task = task
        obj.save()

    if notify:
        notification_type = "success" if task.success else "error"

        message = task.kwargs.get("message", None)

        # Get message
        notify = Notify()
        if not message:
            message = notify.get_nofitification_details(notification_type, obj, task_type, results)

        # Add message to user
        notify_user(notification_type, session_key, message, task.id)

    if update_indicators:
        if "dataset_id" in results:
            indicators = Indicator.objects.filter(dataset_id=int(results["dataset_id"]))
            for obj in indicators:
                async_task(
                    "wazimap_ng.datasets.tasks.indicator_data_extraction",
                    obj,
                    task_name=f"Data Extraction: {obj.name}",
                    hook="wazimap_ng.datasets.hooks.process_task_info",
                    key=session_key,
                    type="data_extraction", assign=False, notify=False,
                    user_id=user_id, email=email_notification_on_failure_only
                )

    if email_notification_on_failure_only and user_id and not task.success:
        user = User.objects.filter(id=user_id).first()
        complete_type = "Success" if task.success else "Failure"

        if user and user.email:
            if task_type == "upload":
                dataset = task.args[1]
                subject = F"{complete_type} Report: Upload complete for dataset {dataset.name}"

                context = {
                    "dataset": dataset,
                    "task": task,
                    "user": user,
                    "subject": subject
                }
                html_message = render_to_string('emailTemplates/upload_task_notification.html', context)

            elif task_type == "data_extraction":
                indicator = obj
                subject = F"{complete_type} Report: Indicator data extraction completed for {indicator.name}"

                context = {
                    "indicator": indicator,
                    "task": task,
                    "user": user,
                    "subject": subject
                }
                html_message = render_to_string('emailTemplates/indicator_extraction_task_notification.html', context)

            plain_message = strip_tags(html_message)
            from_email = F'From <{STAFF_EMAIL_ADDRESS}>'
            to = user.email
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def notify_user(notification_type, session_key, message, task_id=None):
    """
    Call back function after the task has been executed.
    This function gets passed the complete Task object as its argument.

    We get session key from kwargs of the task object and data of created object
    is passes through results value in task object.
    """
    session = Session.objects.filter(session_key=session_key).first()

    if session:
        decoded_session = custom_admin_notification(
            session.get_decoded(), notification_type, message, task_id
        )
        session.session_data = Session.objects.encode(decoded_session)
        session.save()

def custom_admin_notification(session, notification_type, message, task_id=None):
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

    if task_id:
        notification["task_id"] = task_id

    if "notifications" in session:
        messages = session['notifications']
    messages.append(notification)
    session['notifications'] = messages
    return session

def add_to_task_list(session, task):
    """
    Add task id to session task_list
    """
    task_list = session.get("task_list", [])
    task_list.append(task)
    session["task_list"] = task_list
