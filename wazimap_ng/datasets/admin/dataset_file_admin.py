import pandas as pd

from .. import models
from .base_admin_model import BaseAdminModel
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from wazimap_ng.general.services import permissions
from wazimap_ng.general.admin import filters


# Filters
def filter_custom_queryset(self, request, queryset):
    value = self.value()
    if value is None:
        return queryset
    user_datasets = permissions.get_objects_for_user(
        request.user, models.Dataset
    ).filter(**{self.parameter_name: value}).values_list(
        "id", flat=True
    )
    return queryset.filter(dataset_id__in=user_datasets)


class CustomPermissionTypeFilter(admin.SimpleListFilter):
    title = "Permission Type"
    parameter_name = 'permission_type'

    def lookups(self, request, model_admin):
        return [("private", "Mine"), ("public", "Public")]

    def queryset(self, request, queryset):
        return filter_custom_queryset(self, request, queryset)


class CustomGeographyHierarchyFilter(filters.GeographyHierarchyFilter):
    def queryset(self, request, queryset):
        return filter_custom_queryset(self, request, queryset)

class CustomProfileFilter(filters.ProfileFilter):
    def queryset(self, request, queryset):
        return filter_custom_queryset(self, request, queryset)

class CustomMetadataFilter(filters.DatasetMetaDataFilter):
    def queryset(self, request, queryset):
        return filter_custom_queryset(self, request, queryset)


@admin.register(models.DatasetFile)
class DatasetFileAdmin(BaseAdminModel):

    fieldsets = (
        ("Uploaded Dataset", {
            "fields": ("name", "get_document", "get_dataset_link",)
        }),
        ("Task Details", {
            "fields": (
            	"get_status", "get_task_link",
            	"get_warnings", "get_errors",
            )
        }),
    )

    readonly_fields = (
       "name", "get_document", "get_status", "get_task_link",
       "get_warnings", "get_errors",
    )

    list_filter = (
        CustomPermissionTypeFilter, CustomGeographyHierarchyFilter,
        CustomProfileFilter, CustomMetadataFilter
    )
    list_display = (
        "name", 'get_dataset_name'
    )

    def get_dataset_name(self, obj):
        if obj:
            dataset = models.Dataset.objects.filter(id=obj.dataset_id).first()
            return dataset.name if dataset else "-"
        return '-'

    get_dataset_name.short_description = 'Dataset'

    def get_document(self, obj):
        return mark_safe(
            f'<a href="{obj.document.url}" download="{obj.name}-{obj.id}.csv">{obj.name}-{obj.id}.csv</a>'
        )

    get_document.short_description = 'Document'

    def get_dataset_link(self, obj):
        if obj:
            dataset = models.Dataset.objects.filter(id=obj.dataset_id).first()

            if not dataset:
                return "-"

            url = reverse('admin:%s_%s_change' % (
                dataset._meta.app_label,  dataset._meta.model_name
            ),  args=[dataset.id] )
            return mark_safe(
                f'<a href="{url}">{dataset.name}</a>'
            )
        return "-"

    get_dataset_link.short_description = 'Dataset'

    def get_status(self, obj):
        if obj.id and obj.task:
                return "Processed" if obj.task.success else "Failed"
        return "In Queue"

    get_status.short_description = 'Status'

    def get_task_link(self, obj):
        if obj.task:
            task_type = "success" if obj.task.success else "failure"
            admin_url = reverse(
                'admin:%s_%s_change' % (
                    obj.task._meta.app_label, task_type
                ),  args=[obj.task.id]
            )

            return mark_safe('<a href="%s">%s</a>' % (admin_url, obj.task.id))
        return "-"

    get_task_link.short_description = 'Task Link'

    def get_warnings(self, obj):
        if obj.task:
            result = obj.task.result
            if obj.task.success and result["warning_log"]:
                download_url = result["warning_log"].replace("/app", "")
                result = render_to_string(
                    'custom/variable_task_warnings.html', {'download_url': download_url}
                )
                return mark_safe(result)
        return "-"

    get_warnings.short_description = 'Warnings'

    def get_errors(self, obj):
        if obj.task:
            result = obj.task.result
            if not obj.task.success:
                return obj.task.result
            elif result["error_log"]:
                download_url = result["error_log"].replace("/app", "")
                df = pd.read_csv(result["error_log"], header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()
                result = render_to_string(
                    'custom/variable_task_errors.html', { 'errors': error_list,'download_url': download_url}
                )
                return mark_safe(result)
        return "None"

    get_errors.short_description = 'Errors'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

