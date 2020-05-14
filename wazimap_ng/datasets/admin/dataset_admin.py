import json

from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group

from django_q.tasks import async_task
from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm

from .base_admin_model import BaseAdminModel
from .. import models
from .. import hooks
from .views import (
    InitialDataUploadChangeView, VariableInlinesChangeView, 
    VariableInlinesAddView, InitialDataUploadAddView
)
from wazimap_ng.admin_utils import GroupPermissionWidget
from wazimap_ng.general.services import permissions
from wazimap_ng.general.models import MetaData

def set_to_public(modeladmin, request, queryset):
    queryset.make_public()

def set_to_private(modeladmin, request, queryset):
    queryset.make_private()


class DatasetAdminForm(forms.ModelForm):
    source = forms.CharField(widget=forms.TextInput(attrs={'class': 'vTextField'}), required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField'}), required=False)
    licence = forms.ModelChoiceField(queryset=models.Licence.objects.all(), required=False)
    group_permissions = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=GroupPermissionWidget)

    class Meta:
        model = models.Dataset
        widgets = {
          'permission_type': forms.RadioSelect,
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            if self.instance.metadata:
                metadata = self.instance.metadata
                self.fields["source"].initial = metadata.source
                self.fields["description"].initial = metadata.description
                self.fields["licence"].initial = metadata.licence

        self.fields["group_permissions"].widget.init_parameters(self.current_user, self.instance, self.instance.permission_type)

    def save(self, commit=True):
        if self.has_changed():
            metadata = {
                key: self.cleaned_data.get(key) for key in [
                    "source", "description", "licence"
                ]
            }
            if not self.instance.id:
                self.instance.metadata = MetaData.objects.create(**metadata)
            else:
                MetaData.objects.filter(id=self.instance.metadata.id).update(**metadata)
        return super().save(commit=commit)

@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):

    form = DatasetAdminForm
    exclude = ("groups", )
    fieldsets = (
        ("", {
            'fields': ('name', )
        }),
        ("Permissions", {
            'fields': ('permission_type', 'group_permissions', )

        }),
        ("MetaData", {
          'fields': ('source', 'description', 'licence', )
        }),
    )
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
        inlines = (InitialDataUploadChangeView,)

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
        super().save_model(request, obj, form, change)

        permissions_added = json.loads(request.POST.get("permissions_added", "{}"))
        permissions_removed = json.loads(request.POST.get("permissions_removed", "{}"))

        for group_id, perms in permissions_removed.items():
            group = Group.objects.filter(id=group_id).first()
            if group:
                for perm in perms:
                    remove_perm(perm, group, obj)

        for group_id, perms in permissions_added.items():
            group = Group.objects.filter(id=group_id).first()
            if group:
                for perm in perms:
                    assign_perm(perm, group, obj)

        if not change:
            for perm in get_perms_for_model(models.Dataset):
                assign_perm(perm, request.user, obj)
        return obj

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = (InitialDataUploadAddView,)
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

        return permissions.has_owner_permission(request.user, obj, "delete_dataset")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.target = obj
        return form
