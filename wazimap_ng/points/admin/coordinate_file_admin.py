import os

import pandas as pd
from django.contrib import admin
from django.http.request import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe

from wazimap_ng.general.admin.admin_base import BaseAdminModel
from wazimap_ng.points.models import CoordinateFile


@admin.register(CoordinateFile)
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

    def get_document(self, obj: CoordinateFile) -> str:
        _, file_extension = os.path.splitext(obj.document.name)
        doc_name = f'{obj.name}-{obj.id}{file_extension}'
        return mark_safe(
            f'<a href="{obj.document.url}" download="{doc_name}">{doc_name}</a>'
        )
    get_document.short_description = 'Document'

    def get_status(self, obj: CoordinateFile) -> str:
        if obj.id and obj.task:
            return "Processed" if obj.task.success else "Failed"
        return "In Queue"

    get_status.short_description = 'Status'

    def get_task_link(self, obj: CoordinateFile) -> str:
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

    def get_errors(self, obj: CoordinateFile) -> str:
        if obj.task:
            result = obj.task.result
            if not obj.task.success:
                return obj.task.result
            elif result["error_log"]:
                download_url = result["error_log"].replace("/app", "")
                incorrect_csv = result["incorrect_rows_log"].replace("/app", "")
                df = pd.read_csv(result["error_log"], header=None, sep=",", nrows=10, skiprows=1)
                error_list = df.values.tolist()
                result = render_to_string(
                    'custom/variable_task_errors.html', {
                        'errors': error_list, 'download_url': download_url,
                        'incorrect_csv': incorrect_csv
                    }
                )
                return mark_safe(result)
        return "None"

    get_errors.short_description = 'Errors'

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: CoordinateFile = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: CoordinateFile = None) -> bool:
        return False
