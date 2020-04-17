from django.contrib import admin
from django import forms

from django_q.tasks import async_task
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user, get_perms_for_model, assign_perm

from .base_admin_model import BaseAdminModel
from .. import models
from .. import hooks
from .views import (
    InitialDataUploadChangeView, VariableInlinesChangeView, 
    VariableInlinesAddView, InitialDataUploadAddView, MetaDataInline
)


class DatasetAdminForm(forms.ModelForm):
    class Meta:
        model = models.Dataset
        widgets = {
          'dataset_type': forms.RadioSelect,
        }
        fields = '__all__'

@admin.register(models.Dataset)
class DatasetAdmin(GuardedModelAdmin):

    form = DatasetAdminForm
    exclude = ("groups", )
    inlines = ()


    class Media:
        css = {
             'all': ('/static/css/admin-custom.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return ("dataset_type", ) + self.readonly_fields
        return self.readonly_fields


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
            if dataset_obj and hasattr(dataset_obj, "datasetfile") and dataset_obj.datasetfile.task and dataset_obj.datasetfile.task.success:

                if dataset_obj.indicator_set.count():
                    inlines = inlines + (VariableInlinesChangeView,)
                inlines = inlines + (VariableInlinesAddView,)

        self.inlines = inlines
        return super().change_view(request, object_id)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            for perm in get_perms_for_model(models.Dataset):
                assign_perm(perm, request.user, obj)
        return obj

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (InitialDataUploadAddView, MetaDataInline,)
        return super().add_view(request)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        datasets = qs.exclude(dataset_type="private")
        datasets |= get_objects_for_user(request.user, 'datasets.view_dataset', accept_global_perms=False)
        return datasets

    def has_change_permission(self, request, obj=None):
        if not obj:
            return super().has_change_permission(request, obj)

        if obj.dataset_type == "public":
            return True
        return request.user.has_perm("change_dataset", obj)

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return super().has_delete_permission(request, obj)
        if obj.dataset_type == "public":
            return True
        return request.user.has_perm("delete_dataset", obj)
