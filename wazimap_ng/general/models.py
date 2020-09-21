from django.contrib.gis.db import models
from django.urls import reverse

from notifications.base.models import AbstractNotification, NotificationQuerySet
from model_utils import Choices
from swapper import swappable_setting

from .handlers import notify_handler
from .signals import notify


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class MetaData(BaseModel):
    source = models.CharField(max_length=60, null=False, blank=True)
    description = models.TextField(blank=True)
    licence = models.ForeignKey(
        'datasets.Licence', null=True, blank=True, on_delete=models.SET_NULL,
    )


class CustomNotificationQuerySet(NotificationQuerySet):

    def in_progress(self):
        return self.filter(level="in_progress", deleted=False)

    def filtered_qs(self):
        return self.filter(deleted=False).exclude(level="in_progress")

    def active_qs(self):
        return self.filter(deleted=False)


class Notification(AbstractNotification):

    # Changing Levels to include In progress option
    LEVELS = Choices('success', 'info', 'warning', 'error', 'in_progress')
    level = models.CharField(choices=LEVELS, default=LEVELS.info, max_length=20)

    # For linking task in progress with user
    task_id = models.CharField(max_length=32, null=True, blank=True)
    objects = CustomNotificationQuerySet.as_manager()

    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = "general"
        swappable = swappable_setting('general', 'Notification')

    def get_target_link(self):
        url = "#"
        if self.target:
            url = reverse('admin:%s_%s_change' % (
                self.target._meta.app_label,  self.target._meta.model_name
            ),  args=[self.target.id] )
        return url

    def get_action_object_link(self):
        url = "#"
        if self.action_object:
            url =  reverse('admin:%s_%s_change' % (
                self.action_object._meta.app_label,  self.action_object._meta.model_name
            ),  args=[self.action_object.id] )
        return url

# connect the Notification signal
notify.connect(
    notify_handler, dispatch_uid='wazimap_ng.general.models.notification'
)
