import json

from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_q.tasks import async_task

from .base_admin_model import DatasetBaseAdminModel, delete_selected_data
from .. import models
from .. import hooks
from .views import MetaDataInline
from .forms import DatasetAdminForm
from wazimap_ng.general.widgets import description

from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.admin import filters

def set_to_public(modeladmin, request, queryset):
    queryset.make_public()

def set_to_private(modeladmin, request, queryset):
    queryset.make_private()

def get_source(dataset):
    if hasattr(dataset, "metadata"):
        return dataset.metadata.source
    return None 

class PermissionTypeFilter(filters.DatasetFilter):
    title = "Permission Type"
    parameter_name = "permission_type"

    def lookups(self, request, model_admin):
        return [("private", "Mine"), ("public", "Public")]


@admin.register(models.Dataset)
class DatasetAdmin(DatasetBaseAdminModel):
    exclude = ("groups", )
    inlines = (MetaDataInline,)
    actions = (set_to_public, set_to_private, delete_selected_data,)
    list_display = ("name", "permission_type", "geography_hierarchy", "profile", description("source", get_source))
    list_filter = (
        PermissionTypeFilter, filters.GeographyHierarchyFilter,
        filters.ProfileFilter, filters.DatasetMetaDataFilter
    )
    form = DatasetAdminForm
    search_fields = ("name", )

    fieldsets = (
        ("", {
            "fields": (
                "profile", "name", "geography_hierarchy",
                "permission_type"
            )
        }),
        ("Dataset Imports", {
            "fields": (
                "import_dataset", "imported_dataset",
            )
        }),
    )

    readonly_fields = ("imported_dataset", )

    class Media:
        js = ("/static/js/geography_hierarchy.js",)


    def imported_dataset(self, obj):

        def get_url(file_obj):
            return '<a href="%s">%s</a>' % (reverse(
                'admin:%s_%s_change' % (
                    file_obj._meta.app_label, file_obj._meta.model_name
                ),  args=[file_obj.id]
            ), F"{file_obj.name}-{file_obj.id}")

        if obj:
            dataset_file_links = [
                get_url(file_obj) for file_obj in models.DatasetFile.objects.filter(
                    dataset_id=obj.id, dataset_id__isnull=False
                )
            ]
            if dataset_file_links:
                return mark_safe(", ".join(dataset_file_links))
        return "-"

    imported_dataset.short_description = 'Previously Imported'

    def get_related_fields_data(self, obj):

        return [{
                "name": "dataset data",
                "count": obj.datasetdata_set.count()
            }, {
                "name": "indicator",
                "count": obj.indicator_set.count()
        }]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk == None and change == False
        is_profile_updated = change and "profile" in form.changed_data

        super().save_model(request, obj, form, change)

        if is_new or is_profile_updated:
            assign_perms_to_group(obj.profile.name, obj, is_profile_updated)

        dataset_import_file = form.cleaned_data.get("import_dataset", None)

        if dataset_import_file:
            datasetfile_obj = models.DatasetFile.objects.create(
                name=obj.name,
                document=dataset_import_file,
                dataset_id=obj.id
            )
            task = async_task(
                "wazimap_ng.datasets.tasks.process_uploaded_file",
                datasetfile_obj, obj,
                task_name=f"Uploading data: {obj.name}",
                hook="wazimap_ng.datasets.hooks.process_task_info",
                key=request.session.session_key,
                type="upload", assign=True, notify=True
            )
            hooks.add_to_task_list(request.session, task)
            hooks.custom_admin_notification(
                request.session,
                "info",
                "Data upload for %s started. We will let you know when process is done." % (
                    obj.name
                )
            )
        return obj

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if "autocomplete" in request.path:

            dataset_ids = queryset.values_list("id", flat=True)
            in_progress_uploads = models.DatasetFile.objects.filter(
                task_id=None, dataset_id__in=dataset_ids
            ).values_list("dataset_id", flat=True)

            queryset = queryset.exclude(id__in=in_progress_uploads)

        return queryset, use_distinct
