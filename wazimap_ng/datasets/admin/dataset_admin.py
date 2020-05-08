import json

from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from wazimap_ng.config.common import STAFF_GROUPS

from django_q.tasks import async_task
from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm

from .base_admin_model import BaseAdminModel
from .. import models
from .. import hooks
from .views import (
    InitialDataUploadChangeView, VariableInlinesChangeView, 
    VariableInlinesAddView, InitialDataUploadAddView, MetaDataInline
)
from wazimap_ng.admin_utils import GroupPermissionWidget
from wazimap_ng.general.services import permissions

def set_to_public(modeladmin, request, queryset):
    queryset.make_public()

def set_to_private(modeladmin, request, queryset):
    queryset.make_private()

@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    exclude = ("groups", )
    inlines = ()
    actions = (set_to_public, set_to_private)
    list_display = ("name", "permission_type")
    list_filter = ("permission_type",)


    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }

    def get_related_fields_data(self, obj):

        return [{
                "name": "dataset data",
                "count": obj.datasetdata_set.count()
            }, {
                "name": "indicator",
                "count": obj.indicator_set.count()
        }]

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        if formset.model == models.DatasetFile:
            instances = formset.save()
            for instance in instances:
                async_task(
                    "wazimap_ng.datasets.tasks.process_uploaded_file",
                    instance, task_name=f"Uploading data: {instance}",
                    hook="wazimap_ng.datasets.hooks.process_task_info",
                    key=request.session.session_key,
                    type="upload", assign=True, notify=True
                )
                hooks.custom_admin_notification(
                    request.session,
                    "info",
                    "Data upload for %s started. We will let you know when process is done." % (
                        instance
                    )
                )

        if formset.model == models.Indicator:
            instances = formset.save(commit=False)
            for instance in instances:
                instance_is_new = not bool(instance.id)
                instance.save()
                if instance_is_new:
                    async_task(
                        "wazimap_ng.datasets.tasks.indicator_data_extraction",
                        instance,
                        task_name=f"Data Extraction: {instance.name}",
                        hook="wazimap_ng.datasets.hooks.process_task_info",
                        key=request.session.session_key,
                        type="data_extraction", notify=True
                    )
                    hooks.custom_admin_notification(
                        request.session,
                        "info",
                        "Process of Data extraction started for %s. We will let you know when process is done." % (
                            instance.name
                        )
                    )

            if formset.deleted_objects:
                variables_queryset = models.Indicator.objects.filter(id__in=[obj.id for obj in formset.deleted_objects])
                variable_names = ", ".join(variables_queryset.values_list("name", flat=True))
                async_task(
                    'wazimap_ng.datasets.tasks.delete_data',
                    variables_queryset, variable_names,
                    task_name=f"Deleting data: {variable_names}",
                    hook="wazimap_ng.datasets.hooks.process_task_info",
                    key=request.session.session_key,
                    type="delete", notify=True, message=f"Deleted data for variable: {variable_names}"
                )
                hooks.custom_admin_notification(
                    request.session,
                    "info",
                    "Process of Data deletion started for %s. We will let you know when process is done." % (
                        variable_names
                    )
                )

        return super().save_formset(request, form, formset, change)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        inlines = (InitialDataUploadChangeView, MetaDataInline,)

        if object_id:
            dataset_obj = models.Dataset.objects.get(id=object_id)
            is_loaded = hasattr(dataset_obj, "datasetfile") and dataset_obj.datasetfile.task and dataset_obj.datasetfile.task.success
            if is_loaded:
                if dataset_obj.indicator_set.count():
                    inlines = inlines + (VariableInlinesChangeView,)
                inlines = inlines + (VariableInlinesAddView,)

        self.inlines = inlines
        return super().change_view(request, object_id)

    def save_model(self, request, obj, form, change):
        old_permission = obj.permission_type
        super().save_model(request, obj, form, change)

        if obj.permission_type == "private" and not request.user.is_superuser:
            group = request.user.groups.all().exclude(name__in=STAFF_GROUPS).first()
            if group and (not change or old_permission != "private"):
                for perm in get_perms_for_model(models.Dataset):
                    assign_perm(perm, group, obj)
        return obj

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (InitialDataUploadAddView, MetaDataInline,)
        return super().add_view(request)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return permissions.get_objects_for_user(request.user, 'view', models.Dataset, qs)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return super().has_change_permission(request, obj)

        return permissions.has_permission(request.user, obj, "change_dataset")

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return super().has_delete_permission(request, obj)

        return permissions.has_permission(request.user, obj, "delete_dataset")
