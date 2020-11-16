import logging

from notifications.models import Notification

logger = logging.getLogger(__name__)


def get_notification_verb(task_type, notification_type):
    """
    Get notification verb
    """
    msgs = {
        "upload": {
            "success": "Successfully uploaded",
            "error": "Failed to upload"
        },
        "extraction": {
            "success": "Successfully extracted",
            "error": "Failed to extract data"
        },
        "delete": {
            "success": "Successfully deleted",
            "error": "Failed to delete"
        }
    }
    msg = msgs.get(task_type, None)
    if msg:
        return msg.get(notification_type, None)
    return None


def process_task_info(task):
    """
    Process task
    """
    notify = task.kwargs.get("notify", False)

    if notify:
        notification_type = "success" if task.success else "error"
        task_type = task.kwargs.get("type", False)
        notification = Notification.objects.filter(data__icontains=task.id).first()

        if notification:
            notification.level = notification_type
            verb = get_notification_verb(task_type, notification_type)
            if verb:
                notification.verb = verb
            notification.unread = True
            notification.save()
