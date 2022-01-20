import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import FieldError
from django.contrib.admin.models import LogEntry
from django.utils import timezone


class Command(BaseCommand):
    help = 'Port django admin log to simple history'

    def handle(self, *args, **options):

        log_entry_objs = LogEntry.objects.all()
        print(f"Started process for {log_entry_objs.count()} log entry objects")
        for log_entry in log_entry_objs:
            ct = log_entry.content_type
            try:
                instance_model = ct.model_class()
            except Exception as e:
                continue
            try:
                instance = instance_model.objects.get(id=log_entry.object_id)
            except (instance_model.DoesNotExist, FieldError):
                continue

            try:
                manager = instance.history
            except AttributeError:
                continue

            action_type = None
            history_type = None
            if log_entry.action_flag == 1:
                action_type = "created"
                history_type = "+"
            elif log_entry.action_flag == 2:
                action_type = "updated"
                history_type = "~"
            else:
                continue

            attrs = {}
            fields = instance._meta.fields
            for field in fields:
            	attrs[field.attname] = getattr(instance, field.attname)

            history_date = getattr(instance, action_type, timezone.now())
            history_user = log_entry.user
            history_change_reason = log_entry.get_change_message()
            history_type = history_type

            history_instance = manager.model(
                history_date=history_date,
                history_type=history_type,
                history_user=history_user,
                history_change_reason=history_change_reason,
                **attrs,
            )
            history_instance.save()

        print("Process Completed")
