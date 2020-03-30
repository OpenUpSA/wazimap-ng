from django.contrib import admin

from django_q.tasks import async_task

from .base_admin_model import BaseAdminModel
from .. import models
from .. import hooks
from .views import InitialDataUploadChangeView, VariableInlinesChangeView, VariableInlinesAddView, InitialDataUploadAddView

@admin.register(models.Dataset)
class DatasetAdmin(BaseAdminModel):

    exclude = ("groups", )
    inlines = ()

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        inlines = (InitialDataUploadChangeView, )

        if object_id:
            dataset_obj = models.Dataset.objects.get(id=object_id)
            if dataset_obj and dataset_obj.datasetfile.task and dataset_obj.datasetfile.task.success:

                if dataset_obj.indicator_set.count():
                    inlines = inlines + (VariableInlinesChangeView,)
                inlines = inlines + (VariableInlinesAddView, )

        self.inlines = inlines
        return super().change_view(request, object_id)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (InitialDataUploadAddView, )
        return super().add_view(request)
