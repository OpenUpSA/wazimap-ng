import pandas as pd

from .. import models
from django.contrib import admin
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.datasets import hooks

@admin.register(models.CoordinateFile)
class CoordinateFileAdmin(BaseAdminModel):
    fieldsets = (
        ("Uploaded Dataset", {
            "fields": ("name", "get_document",)
        }),
        ("Task Details", {
            "fields": (
            	"get_status", "get_task_link", "get_errors",
            )
        }),
    )

    readonly_fields = (
       "name", "get_document", "get_status", "get_task_link",
       "get_errors",
    )

    def get_document(self, obj):
        return mark_safe(
            f'<a href="{obj.document.url}" download="{obj.name}-{obj.id}.csv">{obj.name}-{obj.id}.csv</a>'
        )
    get_document.short_description = 'Document'

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

    def get_errors(self, obj):
        if obj.task and not obj.task.success:
            result = obj.task.result
            if "CustomDataParsingException" in result:
                logdir = settings.MEDIA_ROOT + "/logs/points/"
                filename = "%s_%d_log.csv" % ("point_file", obj.id)
                download_url = settings.MEDIA_URL + "logs/points/"
                df = pd.read_csv(logdir+filename, header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()

                result = render_to_string(
                    'custom/render_task_errors.html', { 'errors': error_list, 'download_url': download_url + filename}
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
